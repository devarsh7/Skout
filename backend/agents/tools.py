"""
SKOUT Brand Agent — tool registry.

Each tool is described in OpenAI function-calling schema (which Groq accepts
on llama-3.3-70b) AND implemented as a plain Python function on a Session.

The agent's job is to pick the right tools and chain them. Replacing the
old keyword-intent classifier with real tool use means the agent can:
  • discover_creators → filter_creators → draft_outreach in one chain
  • call get_local_benchmark before recommending a budget
  • save_brand_fact when the user states a constraint

If the LLM is unavailable or tool calls fail, we fall back to a single
plain-text response.
"""
from __future__ import annotations

import json
from typing import Any, Callable

from loguru import logger
from sqlalchemy.orm import Session

from backend.models.campaign import Campaign, OutreachRecord
from backend.models.creator import Creator
from backend.models.user import User


# ── Tool schemas (OpenAI function-calling format) ─────────────────────────────

TOOL_SCHEMAS: list[dict] = [
    {
        "type": "function",
        "function": {
            "name": "discover_creators",
            "description": (
                "Find creators that match a natural-language brief. "
                "Use when the user asks to find / suggest / search for creators."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query":         {"type": "string", "description": "Brief / keywords describing the ideal creator."},
                    "city":          {"type": "string", "description": "Optional city filter (e.g. 'Toronto')."},
                    "niche":         {"type": "string", "description": "Optional niche / category filter."},
                    "min_followers": {"type": "integer", "description": "Optional min total followers."},
                    "max_followers": {"type": "integer", "description": "Optional max total followers."},
                    "limit":         {"type": "integer", "description": "Max results to return (default 8, max 20)."},
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "filter_creators",
            "description": (
                "Filter / refine a previously surfaced creator list by stricter criteria. "
                "Use when the user says 'narrow it down', 'only the ones with X', 'remove Y'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "creator_ids":    {"type": "array", "items": {"type": "string"}, "description": "Creator IDs to filter."},
                    "engagement_min": {"type": "number",  "description": "Min avg_engagement_rate (percent, e.g. 3.0)."},
                    "follower_min":   {"type": "integer", "description": "Min total followers."},
                    "follower_max":   {"type": "integer", "description": "Max total followers."},
                    "niche":          {"type": "string",  "description": "Must include this niche."},
                    "city":           {"type": "string",  "description": "Must match city."},
                    "open_only":      {"type": "boolean", "description": "Only open-to-collabs creators."},
                },
                "required": ["creator_ids"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_creator_profile",
            "description": "Fetch the full public profile of a specific creator by ID. Use before drafting outreach.",
            "parameters": {
                "type": "object",
                "properties": {"creator_id": {"type": "string"}},
                "required": ["creator_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "draft_outreach_message",
            "description": (
                "Draft a short outreach DM/email for a specific creator. "
                "Use when the user asks to 'message', 'reach out', or 'draft an email'."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "creator_id":   {"type": "string", "description": "Target creator ID."},
                    "brief":        {"type": "string", "description": "What the brand wants — product, deliverable, vibe."},
                    "tone":         {"type": "string", "description": "Tone: warm, professional, casual, playful (default warm)."},
                },
                "required": ["creator_id", "brief"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_campaign_status",
            "description": "Return the user's recent campaigns with outreach counts and statuses.",
            "parameters": {
                "type": "object",
                "properties": {
                    "campaign_id": {"type": "string", "description": "Optional — narrow to one campaign."},
                    "limit":       {"type": "integer", "description": "Max campaigns to return (default 5)."},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_local_benchmark",
            "description": (
                "Get the local industry benchmark (avg engagement, avg followers) for a city × category. "
                "Use when the user asks 'what's normal for X in Y?' or before recommending a budget."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "city":     {"type": "string"},
                    "category": {"type": "string", "description": "e.g. 'food', 'fitness', 'beauty'"},
                },
                "required": ["city", "category"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "save_brand_fact",
            "description": (
                "Persist a durable fact about the user / brand so future chats can reference it. "
                "Use when the user states a budget, preference, constraint, or goal explicitly."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "fact":     {"type": "string", "description": "Short declarative sentence about the brand."},
                    "category": {
                        "type": "string",
                        "enum": ["budget", "preference", "constraint", "context", "goal", "outcome", "other"],
                    },
                },
                "required": ["fact", "category"],
            },
        },
    },
]


# ── Tool implementations ──────────────────────────────────────────────────────

def _public_creator(c: Creator) -> dict:
    return {
        "id":                  c.id,
        "name":                c.display_name or c.full_name,
        "city":                c.city,
        "country":             c.country,
        "niches":              c.niches,
        "total_followers":     c.total_followers,
        "instagram_followers": c.instagram_followers,
        "tiktok_followers":    c.tiktok_followers,
        "engagement_pct":      round((c.avg_engagement_rate or 0) * 100, 2)
                                if (c.avg_engagement_rate or 0) <= 1
                                else round(c.avg_engagement_rate or 0, 2),
        "min_rate_usd":        c.min_rate_usd,
        "open_to_collabs":     c.open_to_collabs,
        "instagram_handle":    c.instagram_handle,
        "tiktok_handle":       c.tiktok_handle,
    }


def tool_discover_creators(
    db: Session,
    smb_id: str,
    *,
    query: str,
    city: str | None = None,
    niche: str | None = None,
    min_followers: int | None = None,
    max_followers: int | None = None,
    limit: int = 8,
) -> dict:
    limit = max(1, min(20, int(limit or 8)))
    q = db.query(Creator).filter(Creator.open_to_collabs.is_(True))
    if city:
        q = q.filter(Creator.city.ilike(f"%{city}%"))
    if min_followers is not None:
        q = q.filter(Creator.total_followers >= int(min_followers))
    if max_followers is not None:
        q = q.filter(Creator.total_followers <= int(max_followers))
    rows = q.order_by(Creator.avg_engagement_rate.desc()).limit(200).all()

    # Score with keyword overlap, like discovery_agent's _sql_fallback
    from backend.agents.discovery_agent import _tokenize
    tokens = _tokenize(query)
    if niche:
        tokens.extend(_tokenize(niche))

    def score(c: Creator) -> int:
        if not tokens:
            return 0
        hay = " ".join([
            c.display_name or "", c.full_name or "", c.bio or "",
            " ".join(c.niches or []), c.city or "", c.country or "",
            " ".join(c.languages or []),
        ]).lower()
        return sum(1 for t in tokens if t in hay)

    if niche:
        rows = [r for r in rows if any(niche.lower() in (n or "").lower() for n in (r.niches or []))]

    if tokens:
        scored = sorted(
            [(score(c), c) for c in rows],
            key=lambda x: (x[0], x[1].total_followers or 0),
            reverse=True,
        )
        rows = [c for s, c in scored if s > 0][:limit] or rows[:limit]
    else:
        rows = rows[:limit]

    return {
        "count":    len(rows),
        "creators": [_public_creator(c) for c in rows],
        "query":    query,
        "filters":  {"city": city, "niche": niche, "min_followers": min_followers, "max_followers": max_followers},
    }


def tool_filter_creators(
    db: Session,
    smb_id: str,
    *,
    creator_ids: list[str],
    engagement_min: float | None = None,
    follower_min: int | None = None,
    follower_max: int | None = None,
    niche: str | None = None,
    city: str | None = None,
    open_only: bool = False,
) -> dict:
    if not creator_ids:
        return {"count": 0, "creators": []}
    q = db.query(Creator).filter(Creator.id.in_(creator_ids))
    if follower_min is not None:
        q = q.filter(Creator.total_followers >= int(follower_min))
    if follower_max is not None:
        q = q.filter(Creator.total_followers <= int(follower_max))
    if city:
        q = q.filter(Creator.city.ilike(f"%{city}%"))
    if open_only:
        q = q.filter(Creator.open_to_collabs.is_(True))
    rows = q.all()
    if engagement_min is not None:
        emin = float(engagement_min)
        # engagement may be stored as percent (5.4) or fraction (0.054)
        def eng(c: Creator) -> float:
            e = c.avg_engagement_rate or 0.0
            return e * 100 if e <= 1 else e
        rows = [c for c in rows if eng(c) >= emin]
    if niche:
        rows = [c for c in rows if any(niche.lower() in (n or "").lower() for n in (c.niches or []))]
    return {"count": len(rows), "creators": [_public_creator(c) for c in rows]}


def tool_get_creator_profile(db: Session, smb_id: str, *, creator_id: str) -> dict:
    c = db.query(Creator).filter(Creator.id == creator_id).first()
    if not c:
        return {"error": "Creator not found"}
    return _public_creator(c) | {"bio": c.bio, "preferred_collab_types": c.preferred_collab_types or []}


def tool_draft_outreach_message(
    db: Session,
    smb_id: str,
    *,
    creator_id: str,
    brief: str,
    tone: str = "warm",
) -> dict:
    c = db.query(Creator).filter(Creator.id == creator_id).first()
    if not c:
        return {"error": "Creator not found"}
    user = db.query(User).filter(User.id == smb_id).first()
    meta = (user.profile_meta if user else None) or {}
    company = meta.get("company_name", "our brand")
    name = c.display_name or c.full_name
    handle = c.instagram_handle or c.tiktok_handle or ""

    draft = (
        f"Hi {name.split()[0] if name else 'there'} —\n\n"
        f"I run {company}{' here in ' + meta.get('target_city') if meta.get('target_city') else ''}. "
        f"I came across your {handle and '@' + handle or 'work'} and the way you cover "
        f"{c.niches[0] if c.niches else 'your niche'} really resonates with us.\n\n"
        f"Here's what we're thinking: {brief}\n\n"
        f"Open to a quick chat about scope + budget? Happy to share more.\n\n"
        f"— {meta.get('contact_name', '').split()[0] if meta.get('contact_name') else 'the team'}"
    )
    return {
        "creator_id":   creator_id,
        "creator_name": name,
        "tone":         tone,
        "draft":        draft,
    }


def tool_get_campaign_status(
    db: Session,
    smb_id: str,
    *,
    campaign_id: str | None = None,
    limit: int = 5,
) -> dict:
    limit = max(1, min(20, int(limit or 5)))
    q = db.query(Campaign).filter(Campaign.owner_id == smb_id)
    if campaign_id:
        q = q.filter(Campaign.id == campaign_id)
    rows = q.order_by(Campaign.created_at.desc()).limit(limit).all()

    out = []
    for c in rows:
        outreach = db.query(OutreachRecord).filter(OutreachRecord.campaign_id == c.id).all()
        by_status: dict[str, int] = {}
        for r in outreach:
            by_status[r.status] = by_status.get(r.status, 0) + 1
        out.append({
            "id":         c.id,
            "name":       c.name,
            "status":     c.status,
            "brief":      c.brief,
            "created_at": c.created_at.isoformat(),
            "outreach":   {"total": len(outreach), "by_status": by_status},
        })
    return {"count": len(out), "campaigns": out}


def tool_get_local_benchmark(db: Session, smb_id: str, *, city: str, category: str) -> dict:
    from backend.services.local_market_service import get_benchmark
    return get_benchmark(db, city, category)


def tool_save_brand_fact(db: Session, smb_id: str, *, fact: str, category: str = "other") -> dict:
    from backend.services import brand_facts_service
    row = brand_facts_service.add_manual_fact(db, smb_id, fact, category)
    return {"saved": True, "id": row.id, "fact": row.fact, "category": row.category}


# ── Registry ──────────────────────────────────────────────────────────────────

TOOL_HANDLERS: dict[str, Callable[..., dict]] = {
    "discover_creators":      tool_discover_creators,
    "filter_creators":        tool_filter_creators,
    "get_creator_profile":    tool_get_creator_profile,
    "draft_outreach_message": tool_draft_outreach_message,
    "get_campaign_status":    tool_get_campaign_status,
    "get_local_benchmark":    tool_get_local_benchmark,
    "save_brand_fact":        tool_save_brand_fact,
}


def execute_tool(db: Session, smb_id: str, name: str, arguments: dict[str, Any]) -> dict:
    handler = TOOL_HANDLERS.get(name)
    if not handler:
        return {"error": f"Unknown tool: {name}"}
    try:
        return handler(db, smb_id, **arguments)
    except TypeError as exc:
        # Bad arguments shape — surface so the LLM can correct
        logger.warning(f"Tool {name} arg error: {exc}")
        return {"error": f"Bad arguments for {name}: {exc}"}
    except Exception as exc:
        logger.warning(f"Tool {name} failed: {exc}")
        return {"error": str(exc)}


def trace_label(name: str, args: dict[str, Any]) -> str:
    """Human-readable label for the UI status card."""
    if name == "discover_creators":
        bits = []
        if args.get("city"): bits.append(args["city"])
        if args.get("niche"): bits.append(args["niche"])
        if args.get("min_followers") or args.get("max_followers"):
            lo, hi = args.get("min_followers") or 0, args.get("max_followers") or "∞"
            bits.append(f"{lo}-{hi} followers")
        return f"Searching creators · {' · '.join(bits) or args.get('query', '')[:40]}"
    if name == "filter_creators":
        return f"Filtering {len(args.get('creator_ids') or [])} creators"
    if name == "get_creator_profile":
        return "Looking at full profile"
    if name == "draft_outreach_message":
        return "Drafting outreach message"
    if name == "get_campaign_status":
        return "Checking your campaigns"
    if name == "get_local_benchmark":
        return f"Looking up {args.get('city', '')} {args.get('category', '')} benchmark"
    if name == "save_brand_fact":
        return f"Remembering: {args.get('fact', '')[:60]}"
    return name
