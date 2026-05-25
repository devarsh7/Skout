"""
Instagram OAuth routes.

Flow:
  1. Frontend calls GET /instagram/auth-url  → gets a URL + state token
  2. Frontend opens that URL in the browser (same tab)
  3. Creator authorises on Instagram
  4. Instagram redirects → GET /instagram/callback?code=X&state=Y
  5. We exchange code for token, fetch profile + reels, store under state
  6. Redirect browser to Streamlit frontend with ?ig_state=Y in the URL
  7. Frontend calls GET /instagram/data/{state} to retrieve the data (one-time)
"""
from __future__ import annotations

import secrets
import time

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import RedirectResponse

from backend.core.config import settings
from backend.services.instagram import (
    exchange_code_for_token,
    fetch_profile_via_graph_api,
    fetch_reels_via_graph_api,
)

router = APIRouter(prefix="/instagram", tags=["instagram"])

# In-memory pending store: state → {data, expires_at}
# In production, replace with Redis.
_pending: dict[str, dict] = {}
_TTL = 300  # seconds


def _prune():
    now = time.time()
    for k in [k for k, v in _pending.items() if v["expires_at"] < now]:
        del _pending[k]


@router.get("/auth-url")
def auth_url():
    """Return a fresh Instagram OAuth URL with an embedded state token."""
    if not settings.instagram_app_id:
        raise HTTPException(status_code=503, detail="Instagram app not configured.")

    state = secrets.token_urlsafe(16)
    _pending[state] = {"data": None, "expires_at": time.time() + _TTL}

    url = (
        "https://www.facebook.com/dialog/oauth"
        f"?client_id={settings.instagram_app_id}"
        f"&redirect_uri={settings.instagram_redirect_uri}"
        f"&scope=instagram_business_basic"
        f"&response_type=code"
        f"&state={state}"
    )
    return {"url": url, "state": state}


@router.get("/callback")
def oauth_callback(code: str = Query(...), state: str = Query(...)):
    """
    Instagram redirects here after the creator authorises.
    Exchanges code for token, fetches profile + reels, then
    redirects the browser back to the Skout frontend.
    """
    _prune()

    if state not in _pending:
        raise HTTPException(status_code=400, detail="Invalid or expired state. Please try connecting again.")

    token = exchange_code_for_token(code)
    if not token:
        raise HTTPException(status_code=502, detail="Instagram token exchange failed.")

    try:
        profile = fetch_profile_via_graph_api(token)
    except Exception:
        profile = {"found": False}

    try:
        reels = fetch_reels_via_graph_api(token)
    except Exception:
        reels = []

    _pending[state] = {
        "data": {
            "token": token,
            "profile": profile,
            "reels": reels,
        },
        "expires_at": time.time() + _TTL,
    }

    return RedirectResponse(url=f"{settings.frontend_url}?ig_state={state}")


@router.get("/data/{state}")
def get_oauth_data(state: str):
    """
    Frontend retrieves profile + reel data by state key (one-time, then cleared).
    """
    _prune()
    entry = _pending.get(state)
    if not entry or entry["data"] is None:
        raise HTTPException(status_code=404, detail="State not found or OAuth not yet complete.")

    data = entry.pop("data")
    del _pending[state]
    return data
