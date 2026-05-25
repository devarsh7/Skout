"""
Instagram profile data fetcher.

Two modes:
  1. Official Graph API  — requires INSTAGRAM_APP_ID + INSTAGRAM_APP_SECRET in env.
                           Creator must complete OAuth (use /instagram/auth to start).
  2. Public scrape       — best-effort for public accounts, no credentials needed.
                           Returns followers / bio when Instagram allows the request.
"""
from __future__ import annotations

import json
import re
from typing import Any

import httpx

from backend.core.config import settings

# ── Official Graph API helpers ────────────────────────────────────────────────

def _app_token() -> str | None:
    app_id = settings.instagram_app_id
    secret = settings.instagram_app_secret
    if app_id and secret:
        return f"{app_id}|{secret}"
    return None


def fetch_profile_via_graph_api(user_access_token: str) -> dict[str, Any]:
    """
    Fetch profile using a user access token obtained via OAuth.
    Requires instagram_business_basic permission.
    """
    url = "https://graph.instagram.com/me"
    params = {
        "fields": "id,username,biography,followers_count,media_count,profile_picture_url,name,website",
        "access_token": user_access_token,
    }
    resp = httpx.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return {
        "found":            True,
        "source":           "graph_api",
        "username":         data.get("username", ""),
        "full_name":        data.get("name", ""),
        "bio":              data.get("biography", ""),
        "followers":        data.get("followers_count", 0),
        "media_count":      data.get("media_count", 0),
        "profile_pic_url":  data.get("profile_picture_url", ""),
        "website":          data.get("website", ""),
        "is_private":       False,
    }


def fetch_reels_via_graph_api(user_access_token: str, limit: int = 20) -> list[dict[str, Any]]:
    """
    Fetch recent reels/videos with per-post metrics.
    Requires instagram_business_basic + instagram_business_manage_insights.
    Returns a list of reel dicts sorted by timestamp desc.
    """
    url = "https://graph.instagram.com/me/media"
    params = {
        "fields": "id,caption,media_type,timestamp,like_count,comments_count,thumbnail_url,media_url,permalink",
        "limit": limit,
        "access_token": user_access_token,
    }
    resp = httpx.get(url, params=params, timeout=15)
    resp.raise_for_status()
    items = resp.json().get("data", [])

    reels = []
    for item in items:
        if item.get("media_type") not in ("VIDEO", "REEL"):
            continue
        # Fetch video_views separately via insights endpoint
        views = 0
        reach = 0
        try:
            ins_resp = httpx.get(
                f"https://graph.instagram.com/{item['id']}/insights",
                params={
                    "metric": "video_views,reach,impressions",
                    "access_token": user_access_token,
                },
                timeout=10,
            )
            if ins_resp.status_code == 200:
                for m in ins_resp.json().get("data", []):
                    if m["name"] == "video_views":
                        views = m.get("values", [{}])[0].get("value", 0)
                    elif m["name"] == "reach":
                        reach = m.get("values", [{}])[0].get("value", 0)
        except Exception:
            pass

        reels.append({
            "id":           item.get("id"),
            "caption":      (item.get("caption") or "")[:200],
            "timestamp":    item.get("timestamp"),
            "likes":        item.get("like_count", 0),
            "comments":     item.get("comments_count", 0),
            "video_views":  views,
            "reach":        reach,
            "thumbnail":    item.get("thumbnail_url") or item.get("media_url"),
            "permalink":    item.get("permalink"),
        })

    return reels


# ── Public scrape (best-effort, no auth) ─────────────────────────────────────

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "x-ig-app-id": "936619743392459",
}


def _parse_shared_data(html: str) -> dict | None:
    """Try to extract profile JSON from Instagram's embedded page data."""
    # Try window._sharedData (older format)
    m = re.search(r'window\._sharedData\s*=\s*(\{.+?\});</script>', html, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            user = (
                data.get("entry_data", {})
                    .get("ProfilePage", [{}])[0]
                    .get("graphql", {})
                    .get("user", {})
            )
            if user:
                return user
        except (json.JSONDecodeError, IndexError, KeyError):
            pass

    # Try __NEXT_DATA__ (newer format)
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>', html, re.S)
    if m:
        try:
            data = json.loads(m.group(1))
            # Navigate the nested structure
            props = data.get("props", {}).get("pageProps", {})
            user = props.get("data", {}).get("user", {})
            if not user:
                user = props.get("user", {})
            if user:
                return {"__next": True, **user}
        except (json.JSONDecodeError, KeyError):
            pass

    return None


def fetch_profile_public(handle: str) -> dict[str, Any]:
    """
    Best-effort public profile scrape.
    Works for public accounts; Instagram may block/rate-limit at any time.
    """
    handle = handle.lstrip("@").strip()
    url = f"https://www.instagram.com/{handle}/"

    try:
        resp = httpx.get(url, headers=_HEADERS, timeout=12, follow_redirects=True)
    except httpx.RequestError as e:
        return {"found": False, "error": f"Network error: {e}"}

    if resp.status_code == 404:
        return {"found": False, "error": "Account not found."}
    if resp.status_code != 200:
        return {"found": False, "error": f"Instagram returned HTTP {resp.status_code}."}

    html = resp.text

    # Detect login wall
    if "login" in resp.url.path or "accounts/login" in html[:2000]:
        return {
            "found":   False,
            "error":   "Instagram requires login to view this profile. "
                       "Connect via OAuth to fetch stats automatically.",
            "blocked": True,
        }

    user = _parse_shared_data(html)
    if not user:
        return {
            "found":   False,
            "error":   "Could not parse Instagram profile data. "
                       "Instagram may be rate-limiting this request.",
            "blocked": True,
        }

    # Normalise across old/new data shapes
    if user.get("__next"):
        followers = (user.get("edge_followed_by") or {}).get("count", 0)
        bio       = user.get("biography", "")
        full_name = user.get("full_name", "")
        is_private = user.get("is_private", False)
        media     = (user.get("edge_owner_to_timeline_media") or {}).get("count", 0)
    else:
        followers  = (user.get("edge_followed_by") or {}).get("count", 0)
        bio        = user.get("biography", "")
        full_name  = user.get("full_name", "")
        is_private = user.get("is_private", False)
        media      = (user.get("edge_owner_to_timeline_media") or {}).get("count", 0)

    return {
        "found":      True,
        "source":     "public_scrape",
        "username":   handle,
        "full_name":  full_name,
        "bio":        bio,
        "followers":  followers,
        "media_count": media,
        "is_private": is_private,
    }


# ── OAuth flow helpers (wires up when credentials are configured) ─────────────

def get_oauth_url() -> str | None:
    app_id       = settings.instagram_app_id
    redirect_uri = settings.instagram_redirect_uri
    if not app_id:
        return None
    return (
        f"https://www.instagram.com/oauth/authorize"
        f"?client_id={app_id}"
        f"&redirect_uri={redirect_uri}"
        f"&scope=instagram_business_basic,instagram_business_manage_insights"
        f"&response_type=code"
    )


def exchange_code_for_token(code: str) -> str | None:
    app_id       = settings.instagram_app_id
    secret       = settings.instagram_app_secret
    redirect_uri = settings.instagram_redirect_uri
    if not (app_id and secret):
        return None
    resp = httpx.get(
        "https://graph.facebook.com/v21.0/oauth/access_token",
        params={
            "client_id":     app_id,
            "client_secret": secret,
            "redirect_uri":  redirect_uri,
            "code":          code,
        },
        timeout=10,
    )
    if resp.status_code == 200:
        return resp.json().get("access_token")
    return None
