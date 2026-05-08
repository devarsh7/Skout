"""
Tiny HTTP client the Streamlit pages use to talk to the FastAPI backend.
Reads the API URL from env or falls back to localhost.
"""
from __future__ import annotations

import os
from typing import Any

import httpx

API_URL = os.getenv("SKOUT_API_URL", "http://localhost:8000")


class APIError(Exception):
    pass


def _req(method: str, path: str, **kwargs) -> Any:
    url = f"{API_URL}{path}"
    try:
        resp = httpx.request(method, url, timeout=60.0, **kwargs)
    except httpx.ConnectError as e:
        raise APIError(f"Cannot reach API at {API_URL}. Is `uvicorn backend.main:app` running?") from e
    if resp.status_code >= 400:
        try:
            detail = resp.json().get("detail", resp.text)
        except Exception:
            detail = resp.text
        raise APIError(f"{resp.status_code}: {detail}")
    if resp.status_code == 204 or not resp.content:
        return None
    return resp.json()


def onboard_creator(payload: dict) -> dict:
    return _req("POST", "/creators", json=payload)


def list_creators(limit: int = 50) -> list[dict]:
    return _req("GET", f"/creators?limit={limit}") or []


def get_creator(creator_id: str) -> dict:
    return _req("GET", f"/creators/{creator_id}")


def discover(query: str, top_k: int = 20) -> dict:
    return _req("POST", "/agents/discovery", json={"query": query, "top_k": top_k})


def filter_search(filters: dict, query: str | None = None, top_k: int = 20) -> dict:
    return _req(
        "POST",
        "/agents/filter",
        json={"query": query, "filters": filters, "top_k": top_k},
    )


def draft_outreach(payload: dict) -> dict:
    return _req("POST", "/agents/outreach", json=payload)


def reindex() -> dict:
    return _req("POST", "/creators/reindex")


def register_user(username: str, email: str, password: str, role: str = "creator", creator_id: str | None = None) -> dict:
    return _req("POST", "/auth/register", json={
        "username": username, "email": email, "password": password,
        "role": role, "creator_id": creator_id,
    })

def verify_otp(email: str, otp: str) -> dict:
    return _req("POST", "/auth/verify-otp", json={"email": email, "otp": otp})

def resend_otp(email: str) -> dict:
    return _req("POST", "/auth/resend-otp", json={"email": email})

def login_user(email: str, password: str) -> dict:
    return _req("POST", "/auth/login", json={"email": email, "password": password})

def send_otp_email(email: str, name: str = "") -> dict:
    """Send OTP to email — no DB writes. Call before register_creator_verified / register_business_verified."""
    return _req("POST", "/auth/send-otp", json={"email": email, "name": name})

def register_creator_verified(payload: dict) -> dict:
    """Verify OTP + atomically create creator profile + user. payload must include otp field."""
    return _req("POST", "/auth/register-creator", json=payload)

def register_business_verified(payload: dict) -> dict:
    """Verify OTP + create business user. payload must include otp field."""
    return _req("POST", "/auth/register-business", json=payload)

def update_creator(creator_id: str, payload: dict, token: str) -> dict:
    return _req("PATCH", f"/creators/{creator_id}", json=payload,
                headers={"Authorization": f"Bearer {token}"})


def update_me(payload: dict, token: str) -> dict:
    return _req("PATCH", "/auth/me", json=payload, headers={"Authorization": f"Bearer {token}"})

def fetch_instagram_profile(handle: str) -> dict:
    """Fetch public Instagram profile data (followers, bio, name)."""
    return _req("GET", f"/creators/instagram/{handle.lstrip('@')}")


def get_instagram_auth_url() -> dict:
    """Get a fresh Instagram OAuth URL + state token."""
    return _req("GET", "/instagram/auth-url")


def get_instagram_oauth_data(state: str) -> dict:
    """Retrieve profile + reel data after OAuth completes (one-time)."""
    return _req("GET", f"/instagram/data/{state}")


def health() -> dict:
    return _req("GET", "/health")


# ── Agent Chat ────────────────────────────────────────────────────────────────

def agent_chat(message: str, token: str) -> dict:
    return _req("POST", "/agent/chat",
                json={"message": message},
                headers={"Authorization": f"Bearer {token}"})


def agent_history(token: str) -> list[dict]:
    return _req("GET", "/agent/history",
                headers={"Authorization": f"Bearer {token}"}) or []


def agent_notifications(token: str) -> dict:
    return _req("GET", "/agent/notifications",
                headers={"Authorization": f"Bearer {token}"}) or {"notifications": []}


def agent_action_save_creators(creator_ids: list, creator_names: list, token: str) -> dict:
    return _req("POST", "/agent/action/save-creators",
                json={"creator_ids": creator_ids, "creator_names": creator_names},
                headers={"Authorization": f"Bearer {token}"})


def agent_action_use_brief(brief_text: str, campaign_name: str, token: str) -> dict:
    return _req("POST", "/agent/action/use-brief",
                json={"brief_text": brief_text, "campaign_name": campaign_name},
                headers={"Authorization": f"Bearer {token}"})


def agent_action_send_outreach(creator_id: str, token: str, campaign_id: str | None = None) -> dict:
    return _req("POST", "/agent/action/send-outreach",
                json={"creator_id": creator_id, "campaign_id": campaign_id},
                headers={"Authorization": f"Bearer {token}"})


# ── Creator Agent ─────────────────────────────────────────────────────────────

def creator_agent_chat(message: str, token: str) -> dict:
    return _req("POST", "/creator-agent/chat",
                json={"message": message},
                headers={"Authorization": f"Bearer {token}"})


def creator_agent_history(token: str) -> list[dict]:
    return _req("GET", "/creator-agent/history",
                headers={"Authorization": f"Bearer {token}"}) or []


# ── Local Market Intelligence ─────────────────────────────────────────────────

def local_leaderboard(city: str, category: str, month: str | None = None, limit: int = 10) -> list[dict]:
    params = f"city={city}&category={category}&limit={limit}"
    if month:
        params += f"&month={month}"
    return _req("GET", f"/local/leaderboard?{params}") or []


def local_benchmarks(city: str, category: str, month: str | None = None) -> dict:
    params = f"city={city}&category={category}"
    if month:
        params += f"&month={month}"
    return _req("GET", f"/local/benchmarks?{params}") or {}


def local_creator_vs_benchmark(creator_id: str, city: str, category: str) -> dict:
    return _req("GET", f"/local/creator-vs-benchmark/{creator_id}?city={city}&category={category}") or {}


def local_neighbourhoods(city: str) -> list[dict]:
    return _req("GET", f"/local/neighbourhoods?city={city}") or []


def local_neighbourhood_creators(neighbourhood: str, city: str | None = None) -> list[dict]:
    params = f"neighbourhood={neighbourhood}"
    if city:
        params += f"&city={city}"
    return _req("GET", f"/local/neighbourhood-creators?{params}") or []


def local_cities() -> list[dict]:
    return _req("GET", "/local/cities") or []


def local_trending_formats(city: str, category: str) -> dict:
    return _req("GET", f"/local/trending-formats?city={city}&category={category}") or {}


def local_recalculate_benchmarks() -> dict:
    return _req("POST", "/local/benchmarks/recalculate") or {}
