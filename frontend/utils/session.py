"""
Browser-session persistence across Streamlit page refreshes.

Read    : st.context.cookies  (Streamlit 1.37+ built-in — no extra packages)
Write   : 0-height JS component  (sets cookie client-side after login)
Logout  : server-side token denylist (@st.cache_resource) — the cookie stays in
          the browser but the server refuses to honour it, so logout is permanent
          for the life of the server process.
"""
from __future__ import annotations

import streamlit as st
import streamlit.components.v1 as _c

_KEY     = "skout_token"
_MAX_AGE = 60 * 60 * 24 * 7   # 7 days


@st.cache_resource
def _denylist() -> set:
    """
    Tokens explicitly logged out.  Shared across every Streamlit session in
    this process — survives st.rerun() / st.switch_page(), cleared only on
    server restart (acceptable because JWTs expire on their own anyway).
    """
    return set()


def save_session(token: str) -> None:
    """Persist JWT in a browser cookie.  Call right after successful login."""
    _c.html(
        f'<script>'
        f'document.cookie="{_KEY}={token};max-age={_MAX_AGE};path=/;SameSite=Lax"'
        f'</script>',
        height=0,
    )


def clear_session() -> None:
    """
    Logout: denylist the current token so restore_session() will never
    honour it again, then wipe session state.
    No JS needed — the denylist is the real guard.
    """
    token = st.session_state.get("user_token", "")
    if token:
        _denylist().add(token)

    for k in ("user", "user_token"):
        st.session_state.pop(k, None)


def restore_session() -> None:
    """
    If session_state has no user, try to restore from browser cookie.
    Silently skips if the token was explicitly logged out this process lifetime.
    Call at the top of every protected page, before the auth guard.
    """
    if st.session_state.get("user"):
        return

    token: str = st.context.cookies.get(_KEY, "")
    if not token or token in _denylist():
        return

    from frontend.utils.api_client import APIError, _req
    try:
        user = _req("GET", "/auth/me", headers={"Authorization": f"Bearer {token}"})
        if user:
            st.session_state["user"]       = user
            st.session_state["user_token"] = token
    except APIError:
        _denylist().add(token)   # expired / invalid — denylist it
