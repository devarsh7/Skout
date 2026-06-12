"""
Instagram OAuth routes.

Flow:
  1. Frontend calls GET /instagram/auth-url?user_id=X  → gets a URL + state token
  2. Frontend opens that URL in the browser (same tab or popup)
  3. Creator authorises on Instagram
  4. Instagram redirects → GET /instagram/callback?code=X&state=Y
  5. We exchange code → short-lived token → long-lived token (60 days)
  6. Fetch profile + all media, persist to DB, redirect back to frontend
  7. Frontend sees ?ig_connected=1 in the URL and updates its UI

Token refresh:
  Call GET /instagram/refresh-token?user_id=X any time within the 60-day window.
  Run this on a weekly cron to keep tokens alive.
"""
from __future__ import annotations

import json
import secrets
from datetime import datetime, timedelta

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.core.database import get_db
from backend.models.creator import Creator
from backend.models.user import User
from backend.services.instagram import (
    exchange_code_for_token,
    fetch_profile_via_graph_api,
    fetch_all_media,
    fetch_reels_via_graph_api,
    save_posts_to_db,
    exchange_for_long_lived_token,
    refresh_long_lived_token,
)

from backend.models.oauth_state import InstagramOAuthState

router = APIRouter(prefix="/instagram", tags=["instagram"])

_TTL = 300          # 5 minutes (pending auth)
_RESULT_TTL = 900   # 15 minutes (fetched data waiting for pickup)


def _prune(db: Session):
    db.query(InstagramOAuthState).filter(
        InstagramOAuthState.expires_at < datetime.utcnow()
    ).delete()
    db.commit()


@router.get("/auth-url")
def auth_url(user_id: str | None = Query(default=None), db: Session = Depends(get_db)):
    """
    Return a fresh Instagram OAuth URL.
    With user_id    → callback persists data to that creator (post-login connect).
    Without user_id → onboarding mode: callback stashes fetched data under the
                      state token; frontend retrieves it via GET /instagram/data/{state}.
    """
    if not settings.instagram_app_id:
        raise HTTPException(status_code=503, detail="Instagram app not configured.")

    if user_id is not None:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.creator_id:
            raise HTTPException(status_code=404, detail="Creator not found.")

    _prune(db)
    state = secrets.token_urlsafe(16)
    db.add(InstagramOAuthState(
        state=state,
        user_id=user_id,
        phase="pending",
        expires_at=datetime.utcnow() + timedelta(seconds=_TTL),
    ))
    db.commit()

    url = (
        "https://www.instagram.com/oauth/authorize"
        f"?client_id={settings.instagram_app_id}"
        f"&redirect_uri={settings.instagram_redirect_uri}"
        f"&scope=instagram_business_basic,instagram_business_manage_insights"
        f"&response_type=code"
        f"&state={state}"
    )
    return {"url": url, "state": state}


@router.get("/callback")
def oauth_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    Instagram redirects here after creator authorises.
    Exchanges code → short token → long-lived token (60d),
    fetches all posts and persists everything to the DB.
    """
    _prune(db)

    def _fail(reason: str, onboarding: bool = True):
        """Redirect the user back to the frontend with a readable error code."""
        path = "/creator/onboarding" if onboarding else ""
        return RedirectResponse(url=f"{settings.frontend_url}{path}?ig_error={reason}")

    entry = (
        db.query(InstagramOAuthState)
        .filter(
            InstagramOAuthState.state == state,
            InstagramOAuthState.phase == "pending",
            InstagramOAuthState.expires_at >= datetime.utcnow(),
        )
        .first()
    )
    if not entry:
        return _fail("expired")

    user_id = entry.user_id

    # ── Onboarding mode (no account yet): fetch data, stash for pickup ────────
    if user_id is None:
        short_token = exchange_code_for_token(code)
        if not short_token:
            db.delete(entry)
            db.commit()
            return _fail("token_exchange")
        long_token_data = exchange_for_long_lived_token(short_token)
        access_token = long_token_data.get("access_token", short_token)

        profile, reels = {}, []
        try:
            profile = fetch_profile_via_graph_api(access_token)
        except Exception:
            profile = {"found": False}
        try:
            reels = fetch_reels_via_graph_api(access_token, limit=20)
        except Exception:
            pass

        entry.phase = "ready"
        entry.payload = json.dumps({
            "profile": profile,
            "reels":   reels,
            "token":   access_token,
        })
        entry.expires_at = datetime.utcnow() + timedelta(seconds=_RESULT_TTL)
        db.commit()
        return RedirectResponse(
            url=f"{settings.frontend_url}/creator/onboarding?ig_state={state}"
        )

    # ── Logged-in mode: persist directly to the creator ───────────────────────
    db.delete(entry)  # state is single-use
    db.commit()
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.creator_id:
        return _fail("not_found", onboarding=False)

    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator:
        return _fail("not_found", onboarding=False)

    # Step 1: short-lived token
    short_token = exchange_code_for_token(code)
    if not short_token:
        return _fail("token_exchange", onboarding=False)

    # Step 2: exchange for long-lived token (60 days)
    long_token_data = exchange_for_long_lived_token(short_token)
    access_token = long_token_data.get("access_token", short_token)
    expires_in = long_token_data.get("expires_in", 5184000)  # default 60 days

    # Step 3: fetch profile and update creator
    try:
        profile = fetch_profile_via_graph_api(access_token)
        if profile.get("found"):
            creator.instagram_followers = profile.get("followers", creator.instagram_followers)
            creator.bio = creator.bio or profile.get("bio", "")
            creator.instagram_user_id = profile.get("ig_user_id")
    except Exception:
        pass

    # Step 4: fetch all media and save posts
    try:
        media_items = fetch_all_media(access_token, limit=50)
        save_posts_to_db(db, creator.id, media_items)
        # Update avg engagement rate from real post data
        _update_creator_engagement(db, creator)
    except Exception:
        pass

    # Step 5: persist token
    creator.instagram_access_token = access_token
    creator.instagram_token_expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    db.commit()

    return RedirectResponse(url=f"{settings.frontend_url}?ig_connected=1")


@router.get("/data/{state}")
def oauth_data(state: str, db: Session = Depends(get_db)):
    """
    One-time pickup of onboarding OAuth results (profile + reels + token).
    Frontend calls this after landing back with ?ig_state=...
    """
    _prune(db)
    entry = (
        db.query(InstagramOAuthState)
        .filter(
            InstagramOAuthState.state == state,
            InstagramOAuthState.phase == "ready",
        )
        .first()
    )
    if not entry:
        raise HTTPException(status_code=404, detail="No data for this state (expired or already retrieved).")
    result = json.loads(entry.payload or "{}")
    db.delete(entry)
    db.commit()
    return {
        "profile": result.get("profile", {}),
        "reels":   result.get("reels", []),
        "token":   result.get("token", ""),
    }


@router.get("/refresh-token")
def refresh_token(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Refresh the long-lived token before it expires (valid within 60-day window).
    Call this on a weekly cron job per creator.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.creator_id:
        raise HTTPException(status_code=404, detail="Creator not found.")

    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator or not creator.instagram_access_token:
        raise HTTPException(status_code=400, detail="No Instagram token found. Re-connect Instagram.")

    result = refresh_long_lived_token(creator.instagram_access_token)
    if not result:
        raise HTTPException(status_code=502, detail="Token refresh failed. Creator needs to re-connect.")

    creator.instagram_access_token = result["access_token"]
    creator.instagram_token_expires_at = datetime.utcnow() + timedelta(seconds=result.get("expires_in", 5184000))
    db.commit()

    return {"status": "refreshed", "expires_at": creator.instagram_token_expires_at.isoformat()}


@router.post("/sync-posts")
def sync_posts(user_id: str = Query(...), db: Session = Depends(get_db)):
    """
    Pull latest posts for a creator. Call this after a creator posts new content,
    or on a daily cron for all connected creators.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.creator_id:
        raise HTTPException(status_code=404, detail="Creator not found.")

    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator or not creator.instagram_access_token:
        raise HTTPException(status_code=400, detail="Instagram not connected.")

    if creator.instagram_token_expires_at and creator.instagram_token_expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Instagram token expired. Re-connect Instagram.")

    media_items = fetch_all_media(creator.instagram_access_token, limit=20)
    new_count = save_posts_to_db(db, creator.id, media_items)
    _update_creator_engagement(db, creator)
    db.commit()

    return {"synced": new_count}


def _update_creator_engagement(db: Session, creator: Creator):
    """Recompute avg_engagement_rate from actual Post rows."""
    from backend.models.post import Post
    posts = (
        db.query(Post)
        .filter(Post.creator_id == creator.id, Post.engagement_rate > 0)
        .order_by(Post.posted_at.desc())
        .limit(30)
        .all()
    )
    if posts:
        creator.avg_engagement_rate = sum(p.engagement_rate for p in posts) / len(posts)
        creator.avg_views = int(sum(p.views for p in posts) / len(posts))
