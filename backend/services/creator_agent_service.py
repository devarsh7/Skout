"""
SKOUT Creator Agent Service — personalized AI career manager for creators.

FREE (active) : Groq  — llama-3.3-70b-versatile, same pattern as the SMB agent.
                Get a free key at console.groq.com → add GROQ_API_KEY to .env.

PRODUCTION    : Uncomment the Anthropic Claude section in _call_llm() and set
                ANTHROPIC_API_KEY + uncomment the model/import in .env / requirements.txt.

System prompt is built dynamically from the creator's verified profile data — never hardcoded.
"""
from __future__ import annotations

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.creator import Creator
from backend.models.creator_conversation import CreatorConversation
from backend.models.user import User

_MAX_TOKENS = 800
_HISTORY_LIMIT = 20   # last 10 exchanges (20 turns)


# ── Profile data helpers ──────────────────────────────────────────────────────

def _audience_gender(split: dict | None) -> str:
    if not split:
        return "not set"
    f = split.get("f", split.get("female", 0)) or 0
    m = split.get("m", split.get("male", 0)) or 0
    parts = []
    if f:
        parts.append(f"{int(float(f) * 100)}% female")
    if m:
        parts.append(f"{int(float(m) * 100)}% male")
    return ", ".join(parts) if parts else "not set"


def _local_audience_pct(location_data: dict | None, city: str | None) -> str:
    if not location_data or not city:
        return "not set"
    city_lower = city.lower()
    for loc, pct in location_data.items():
        if city_lower in loc.lower():
            return str(int(float(pct)))
    # Return the top location % as a fallback
    top_pct = max(location_data.values(), default=None)
    return str(int(float(top_pct))) if top_pct is not None else "not set"


def _build_system_prompt(creator: Creator, completed_deals: int) -> str:
    name = creator.display_name or creator.full_name
    niche = ", ".join(creator.niches) if creator.niches else "not set"
    city = creator.city or "not set"
    followers = creator.total_followers
    eng = creator.avg_engagement_rate or 0.0
    skout_score = (
        f"{creator.authenticity_score:.0f}"
        if creator.authenticity_score is not None
        else "not set"
    )
    availability = creator.availability_status or (
        "Available" if creator.open_to_collabs else "Not available"
    )
    best_format = (
        creator.preferred_collab_types[0]
        if creator.preferred_collab_types
        else (creator.niches[0] if creator.niches else "not set")
    )
    local_pct = _local_audience_pct(creator.audience_location_data, creator.city)
    audience_gender = _audience_gender(creator.audience_gender_split)
    audience_age = creator.audience_age_range or "not set"

    from backend.services import tone_service
    voice_block = tone_service.build_voice_block(creator)

    return (
        f"You are SKOUT Agent, an AI career manager for {name}, "
        f"a creator on the SKOUT platform.\n\n"
        f"Their verified profile data:\n"
        f"- Niche: {niche}\n"
        f"- City: {city}\n"
        f"- Followers: {followers:,}\n"
        f"- Engagement rate: {eng:.2f}%\n"
        f"- SKOUT Score: {skout_score}/100\n"
        f"- Availability: {availability}\n"
        f"- Completed deals: {completed_deals}\n"
        f"- Best performing format: {best_format}\n"
        f"- Local audience: {local_pct}%\n"
        f"- Audience: {audience_gender}, {audience_age}\n"
        f"{voice_block}\n\n"
        f"Always use these real numbers when giving advice. Never invent data. "
        f"If you don't have a data point, say so and suggest they update their profile. "
        f"Be direct, specific, and use actual numbers in every response. "
        f"You help creators with: pricing strategy, rate cards, pitch decks, "
        f"brand negotiation, bio writing, content strategy, and responding to brand inquiries. "
        f"Keep responses concise and actionable. End each response with one clear next step."
    )


# ── LLM call ──────────────────────────────────────────────────────────────────

def _call_llm(system_prompt: str, messages: list[dict]) -> str:
    # ── FREE: Groq (active) ───────────────────────────────────────────────────
    if not settings.groq_api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. Get a free key at console.groq.com "
            "and add  GROQ_API_KEY=your_key  to your .env file."
        )

    full_messages = [{"role": "system", "content": system_prompt}] + messages
    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.groq_model,
            "messages": full_messages,
            "max_tokens": _MAX_TOKENS,
            "temperature": 0.7,
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]

    # ── PRODUCTION: Anthropic Claude (claude-sonnet-4-20250514) ───────────────
    # import anthropic
    # client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    # response = client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=_MAX_TOKENS,
    #     system=system_prompt,
    #     messages=messages,
    # )
    # return response.content[0].text
    # ─────────────────────────────────────────────────────────────────────────


# ── Public API ─────────────────────────────────────────────────────────────────

def get_history(db: Session, user_id: str) -> list[dict]:
    rows = (
        db.query(CreatorConversation)
        .filter(CreatorConversation.creator_user_id == user_id)
        .order_by(CreatorConversation.timestamp.asc())
        .limit(50)
        .all()
    )
    return [r.to_dict() for r in rows]


def chat(db: Session, user_id: str, message: str) -> dict:
    # Load user and verify role
    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "creator":
        raise ValueError("Creator user not found")
    if not user.creator_id:
        raise ValueError(
            "No creator profile linked. Complete onboarding first to use the AI Agent."
        )

    # Load creator profile
    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator:
        raise ValueError("Creator profile not found")

    # Count completed / sent deals (outreach records where this creator was targeted)
    from backend.models.campaign import OutreachRecord
    completed_deals = (
        db.query(OutreachRecord)
        .filter(
            OutreachRecord.creator_id == creator.id,
            OutreachRecord.status.in_(["sent", "booked", "replied", "negotiating"]),
        )
        .count()
    )

    # Build dynamic system prompt from real profile data
    system_prompt = _build_system_prompt(creator, completed_deals)

    # Load recent conversation history
    history_rows = (
        db.query(CreatorConversation)
        .filter(CreatorConversation.creator_user_id == user_id)
        .order_by(CreatorConversation.timestamp.asc())
        .limit(_HISTORY_LIMIT)
        .all()
    )
    messages: list[dict] = [
        {"role": r.role, "content": r.content} for r in history_rows
    ]
    messages.append({"role": "user", "content": message})

    # Call LLM
    try:
        reply = _call_llm(system_prompt, messages)
    except Exception as exc:
        logger.error(f"Creator agent LLM error: {exc}")
        raise RuntimeError(str(exc)) from exc

    # Persist both turns
    db.add(CreatorConversation(creator_user_id=user_id, role="user", content=message))
    db.add(CreatorConversation(creator_user_id=user_id, role="assistant", content=reply))
    db.commit()

    return {"role": "assistant", "content": reply}
