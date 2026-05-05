"""
SKOUT Agent Chat Service — intent detection, context building, LLM call, DB persistence.

FREE API  : Groq (cloud, free tier — llama-3.3-70b-versatile).
            Get a free key at console.groq.com → add GROQ_API_KEY to .env.

PRODUCTION: Uncomment the Anthropic Claude section in _call_llm() and set
            ANTHROPIC_API_KEY + LLM_PROVIDER=anthropic in .env.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.agent_conversation import AgentConversation
from backend.models.creator import Creator
from backend.models.user import User

# ── System prompt ─────────────────────────────────────────────────────────────

_SYSTEM = (
    "You are SKOUT Assistant, an AI agent helping small business owners find and work "
    "with local content creators. You have access to the SMB's business profile and a "
    "list of matching creators. Always be concise, action-oriented, and end each "
    "response with one clear next step. Never use marketing jargon. Talk like a "
    "helpful friend who knows marketing."
)

# ── Intent detection ──────────────────────────────────────────────────────────

_INTENT_KEYWORDS: dict[str, list[str]] = {
    "find_creator": [
        "find", "search", "look for", "creator", "influencer", "who",
        "recommend", "suggest", "show me", "list", "discover", "get me",
    ],
    "write_brief": [
        "brief", "campaign plan", "strategy", "proposal", "outline",
        "draft a", "help me write", "campaign idea", "plan for",
    ],
    "analyze_campaign": [
        "campaign", "performance", "metrics", "results", "analytics",
        "how is", "how did", "roi", "return", "stats", "report",
    ],
    "send_outreach": [
        "message", "outreach", "email", "dm", "contact", "reach out",
        "write to", "send", "draft a message",
    ],
}


def detect_intent(message: str) -> str:
    msg = message.lower()
    for intent, keywords in _INTENT_KEYWORDS.items():
        if any(kw in msg for kw in keywords):
            return intent
    return "get_advice"


# ── Context builders ──────────────────────────────────────────────────────────

def _creator_context(db: Session, user: User, message: str) -> list[dict]:
    """Return up to 5 creators matching the SMB's city/categories."""
    meta = user.profile_meta or {}
    city = meta.get("target_city") or ""
    target_cats: list[str] = meta.get("target_categories") or []

    q = db.query(Creator).filter(Creator.open_to_collabs.is_(True))
    if city:
        q = q.filter(Creator.city.ilike(f"%{city}%"))
    rows = q.order_by(Creator.avg_engagement_rate.desc()).limit(10).all()

    if target_cats and rows:
        matched = [c for c in rows if any(n in target_cats for n in (c.niches or []))]
        rows = matched[:5] if matched else rows[:5]
    else:
        rows = rows[:5]

    return [
        {
            "id": c.id,
            "name": c.display_name or c.full_name,
            "city": c.city,
            "niches": c.niches,
            "total_followers": c.total_followers,
            "engagement_pct": round(c.avg_engagement_rate * 100, 2),
            "instagram": c.instagram_handle,
            "tiktok": c.tiktok_handle,
            "min_rate_usd": c.min_rate_usd,
        }
        for c in rows
    ]


def _campaign_context(db: Session, smb_id: str) -> list[dict]:
    """Return recent campaigns owned by this SMB user."""
    from backend.models.campaign import Campaign

    rows = (
        db.query(Campaign)
        .filter(Campaign.owner_id == smb_id)
        .order_by(Campaign.created_at.desc())
        .limit(5)
        .all()
    )
    return [
        {
            "id": c.id,
            "name": c.name,
            "status": c.status,
            "brief": c.brief,
            "created_at": c.created_at.isoformat(),
        }
        for c in rows
    ]


# ── Proactive notifications ───────────────────────────────────────────────────

def get_proactive_notifications(db: Session, smb_id: str, user: User) -> list[str]:
    """Return a list of human-readable notification strings to surface on session start."""
    notes: list[str] = []
    try:
        from backend.models.campaign import Campaign, OutreachRecord

        campaigns = db.query(Campaign).filter(Campaign.owner_id == smb_id).all()
        campaign_ids = [c.id for c in campaigns]

        if campaign_ids:
            cutoff = datetime.utcnow() - timedelta(days=5)

            # Outreach sent 5+ days ago with no reply
            stale = (
                db.query(OutreachRecord)
                .filter(
                    OutreachRecord.campaign_id.in_(campaign_ids),
                    OutreachRecord.status == "sent",
                    OutreachRecord.updated_at < cutoff,
                )
                .count()
            )
            if stale:
                notes.append(
                    f"📬 {stale} outreach message{'s' if stale > 1 else ''} sent 5+ days "
                    "ago with no reply — want me to draft follow-ups?"
                )

            # Closed campaigns with no notes/review
            unreviewed = [c for c in campaigns if c.status == "closed" and not c.brief]
            if unreviewed:
                names = ", ".join(f'"{c.name}"' for c in unreviewed[:2])
                notes.append(
                    f"📊 Campaign{'s' if len(unreviewed) > 1 else ''} {names} "
                    "completed — no results logged yet."
                )

        # New creators in SMB city since last login
        meta = user.profile_meta or {}
        city = meta.get("target_city") or ""
        if city and user.last_login:
            new_count = (
                db.query(Creator)
                .filter(
                    Creator.city.ilike(f"%{city}%"),
                    Creator.created_at > user.last_login,
                )
                .count()
            )
            if new_count:
                notes.append(
                    f"✨ {new_count} new creator{'s' if new_count > 1 else ''} "
                    f"in {city} since you last logged in."
                )
    except Exception as exc:
        logger.warning(f"Proactive notifications skipped: {exc}")

    return notes


# ── LLM call ──────────────────────────────────────────────────────────────────

def _call_llm(messages: list[dict[str, Any]]) -> str:
    """
    FREE API — Groq (llama-3.3-70b-versatile).
    Set GROQ_API_KEY in .env.  Free key at console.groq.com.

    ── PRODUCTION: switch to Anthropic Claude ──────────────────────────────────
    1. pip install anthropic
    2. Set ANTHROPIC_API_KEY and LLM_PROVIDER=anthropic in .env
    3. Comment out the Groq block and uncomment the Claude block below.
    ────────────────────────────────────────────────────────────────────────────
    """
    # ── FREE: Groq ────────────────────────────────────────────────────────────
    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free API key at console.groq.com "
            "and add  GROQ_API_KEY=your_key  to your .env file."
        )

    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.groq_model,
            "messages": messages,
            "max_tokens": 800,
            "temperature": 0.7,
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

    # ── PRODUCTION: Anthropic Claude ──────────────────────────────────────────
    # import anthropic
    # client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    # system_msg = next((m["content"] for m in messages if m["role"] == "system"), "")
    # chat_msgs  = [m for m in messages if m["role"] != "system"]
    # response = client.messages.create(
    #     model=settings.anthropic_model,   # claude-sonnet-4-6
    #     max_tokens=800,
    #     system=system_msg,
    #     messages=chat_msgs,
    # )
    # return response.content[0].text
    # ─────────────────────────────────────────────────────────────────────────


# ── Action data builder ───────────────────────────────────────────────────────

def _build_action_data(
    intent: str,
    creators: list[dict],
    response_text: str,
) -> dict | None:
    if intent == "find_creator" and creators:
        return {"type": "creator_list", "creators": creators, "actions": ["save_creators"]}
    if intent == "write_brief":
        return {"type": "brief", "brief_text": response_text, "actions": ["use_brief"]}
    if intent == "send_outreach" and creators:
        c = creators[0]
        return {
            "type": "outreach",
            "creator_id": c["id"],
            "creator_name": c["name"],
            "actions": ["send_outreach"],
        }
    return None


# ── Public API ────────────────────────────────────────────────────────────────

def chat(db: Session, smb_id: str, user_message: str) -> dict:
    """
    Process one user message, call the LLM with full context, persist both turns,
    and return the assistant message dict (including action_data).
    """
    user = db.query(User).filter(User.id == smb_id).first()
    if not user:
        raise ValueError("User not found")

    meta = user.profile_meta or {}
    intent = detect_intent(user_message)

    # Build context blocks
    creators_ctx: list[dict] = []
    context_block = ""

    if intent in ("find_creator", "send_outreach"):
        creators_ctx = _creator_context(db, user, user_message)
        if creators_ctx:
            context_block = "\n\nMATCHING CREATORS (JSON):\n" + json.dumps(creators_ctx, indent=2)

    elif intent == "analyze_campaign":
        campaigns = _campaign_context(db, smb_id)
        if campaigns:
            context_block = "\n\nCAMPAIGN DATA (JSON):\n" + json.dumps(campaigns, indent=2)

    smb_block = (
        "\n\nSMB PROFILE:"
        f"\n- Company  : {meta.get('company_name', 'Unknown')}"
        f"\n- Industry : {meta.get('industry', 'Unknown')}"
        f"\n- City     : {meta.get('target_city', 'Unknown')}"
        f"\n- Budget   : {meta.get('budget', 'Unknown')}"
        f"\n- Goals    : {meta.get('goals', 'Not specified')}"
        f"\n- Categories: {', '.join(meta.get('target_categories') or [])}"
    )

    system_content = _SYSTEM + smb_block + context_block

    # Load last 18 turns (9 exchanges)
    history = (
        db.query(AgentConversation)
        .filter(AgentConversation.smb_id == smb_id)
        .order_by(AgentConversation.timestamp.desc())
        .limit(18)
        .all()
    )
    history.reverse()

    messages: list[dict] = [{"role": "system", "content": system_content}]
    for h in history:
        messages.append({"role": h.role, "content": h.content})
    messages.append({"role": "user", "content": user_message})

    response_text = _call_llm(messages)
    action_data = _build_action_data(intent, creators_ctx, response_text)

    # Persist both turns
    db.add(AgentConversation(smb_id=smb_id, role="user", content=user_message, intent=intent))
    assistant_row = AgentConversation(
        smb_id=smb_id,
        role="assistant",
        content=response_text,
        action_data=json.dumps(action_data) if action_data else None,
    )
    db.add(assistant_row)
    db.commit()
    db.refresh(assistant_row)

    return assistant_row.to_dict()


def get_history(db: Session, smb_id: str, limit: int = 20) -> list[dict]:
    rows = (
        db.query(AgentConversation)
        .filter(AgentConversation.smb_id == smb_id)
        .order_by(AgentConversation.timestamp.desc())
        .limit(limit)
        .all()
    )
    rows.reverse()
    return [r.to_dict() for r in rows]
