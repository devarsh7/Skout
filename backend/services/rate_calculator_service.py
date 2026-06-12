"""
SKOUT Rate Calculator — deterministic pricing engine for creators.

Approach: a transparent formula based on industry CPMs, then a short LLM
explanation of *why* the number landed where it did, plus a local
market range from local_market_service so the creator sees how their
rate compares to peers.

The formula is intentionally simple and explainable — creators should
understand exactly how their rate was computed, not just trust a black box.

Base CPM (Cost Per Mille / per 1,000 followers) is the anchor:
    Instagram  Reel       : $10 - $15 per 1K followers
    Instagram  Carousel   : $6  - $9  per 1K
    Instagram  Story      : $3  - $5  per 1K
    TikTok     Video      : $8  - $12 per 1K
    YouTube    Integration: $15 - $25 per 1K
    YouTube    Dedicated  : $30 - $50 per 1K

Multipliers stack on top:
    engagement_multiplier  : (creator_eng / 2.5%)  clamped to [0.7, 2.0]
    usage_multiplier       : organic 1.0 / paid 1.5 / reuse 1.8 / full rights 2.5
    exclusivity_multiplier : none 1.0 / 30d 1.2 / 90d 1.4 / 180d+ 1.6
    city_multiplier        : Toronto/NYC/LA/London 1.1, Tier-1 IN 0.7, etc.
    niche_multiplier       : finance 1.4, B2B/tech 1.3, beauty 1.15, lifestyle 1.0, ...
"""
from __future__ import annotations

import json
from typing import Optional

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.creator import Creator
from backend.services.local_market_service import get_benchmark


# ── Constants ─────────────────────────────────────────────────────────────────

# Base CPM in USD per 1,000 followers
_BASE_CPM: dict[tuple[str, str], float] = {
    ("instagram", "reel"):        12.0,
    ("instagram", "carousel"):    7.5,
    ("instagram", "static"):      6.0,
    ("instagram", "story"):       4.0,
    ("instagram", "bundle"):      18.0,   # reel + 3 stories
    ("tiktok",    "video"):       10.0,
    ("tiktok",    "bundle"):      15.0,
    ("youtube",   "integration"): 20.0,   # 60-90s mention
    ("youtube",   "dedicated"):   40.0,   # full video
    ("youtube",   "short"):       8.0,
}

_USAGE_MULT = {
    "organic":      1.0,
    "paid_30d":     1.4,
    "paid_60d":     1.6,
    "reuse_brand":  1.8,
    "full_rights":  2.5,
}

_EXCLUSIVITY_MULT = {
    "none":   1.0,
    "30d":    1.2,
    "60d":    1.3,
    "90d":    1.4,
    "180d":   1.6,
}

# Higher-CPM markets where brands pay more
_CITY_MULT = {
    # North America Tier-1
    "toronto": 1.10, "new york": 1.25, "los angeles": 1.20, "chicago": 1.10,
    "san francisco": 1.30, "boston": 1.10, "miami": 1.10, "vancouver": 1.05,
    # Europe Tier-1
    "london": 1.20, "paris": 1.10, "berlin": 1.05, "amsterdam": 1.05,
    # APAC Tier-1
    "singapore": 1.10, "tokyo": 1.10, "sydney": 1.10, "dubai": 1.15,
    # India Tier-1 (lower brand CPMs)
    "mumbai": 0.70, "delhi": 0.65, "new delhi": 0.65, "bangalore": 0.70,
    "bengaluru": 0.70, "hyderabad": 0.55, "chennai": 0.55, "pune": 0.55,
    "kolkata": 0.50, "ahmedabad": 0.50, "goa": 0.60,
}

# Niches with higher buyer-side budgets
_NICHE_MULT: dict[str, float] = {
    "finance": 1.40, "fintech": 1.40, "b2b": 1.35, "saas": 1.30, "tech": 1.25,
    "crypto": 1.30, "real estate": 1.25, "automotive": 1.20, "luxury": 1.30,
    "wellness": 1.15, "beauty": 1.15, "skincare": 1.15, "fashion": 1.10,
    "food": 1.05, "travel": 1.10, "fitness": 1.05, "parenting": 1.10,
    "lifestyle": 1.00, "gaming": 1.10, "education": 1.10,
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _engagement_multiplier(eng_pct: float) -> float:
    """Engagement vs 2.5% baseline, clamped [0.7, 2.0]."""
    if eng_pct <= 0:
        return 0.9   # no data → mild discount
    raw = eng_pct / 2.5
    return max(0.7, min(2.0, raw))


def _city_multiplier(city: Optional[str]) -> float:
    if not city:
        return 1.0
    return _CITY_MULT.get(city.lower(), 1.0)


def _niche_multiplier(niches: list[str] | None) -> float:
    if not niches:
        return 1.0
    # Take the highest-paying niche the creator has
    best = 1.0
    for n in niches:
        m = _NICHE_MULT.get(n.lower(), 1.0)
        if m > best:
            best = m
    return best


def _cpm_for(platform: str, deliverable: str) -> float:
    key = (platform.lower(), deliverable.lower())
    return _BASE_CPM.get(key, 8.0)   # safe default


# ── Public API ────────────────────────────────────────────────────────────────

def calculate_rate(
    db: Session,
    creator: Creator,
    platform: str,
    deliverable: str,
    quantity: int = 1,
    usage: str = "organic",
    exclusivity: str = "none",
    add_story_bundle: bool = False,
) -> dict:
    """
    Returns a full breakdown the UI can display step-by-step.
    """
    # Pick followers for the selected platform
    platform_lower = platform.lower()
    if platform_lower == "instagram":
        followers = creator.instagram_followers or creator.total_followers or 0
    elif platform_lower == "tiktok":
        followers = creator.tiktok_followers or creator.total_followers or 0
    elif platform_lower == "youtube":
        followers = creator.youtube_subscribers or creator.total_followers or 0
    else:
        followers = creator.total_followers or 0

    eng = creator.avg_engagement_rate or 0.0
    eng_mult     = round(_engagement_multiplier(eng), 2)
    city_mult    = round(_city_multiplier(creator.city), 2)
    niche_mult   = round(_niche_multiplier(creator.niches), 2)
    usage_mult   = round(_USAGE_MULT.get(usage.lower(), 1.0), 2)
    excl_mult    = round(_EXCLUSIVITY_MULT.get(exclusivity.lower(), 1.0), 2)
    base_cpm     = _cpm_for(platform, deliverable)

    # Base = CPM × (followers / 1000) — one deliverable at full audience reach
    base_unit = base_cpm * (followers / 1000)

    # Story bundle adds ~30% of base
    if add_story_bundle:
        base_unit *= 1.30

    per_deliverable = base_unit * eng_mult * city_mult * niche_mult
    subtotal        = per_deliverable * max(quantity, 1)
    total           = subtotal * usage_mult * excl_mult

    # Round to nearest $25 for "quote-ready" feel
    quoted = round(total / 25) * 25 or 25

    # Local market range from benchmark
    market = None
    if creator.city and creator.niches:
        bench = get_benchmark(db, creator.city, creator.niches[0])
        if bench.get("creator_count", 0) > 0:
            # Heuristic: market low/high = quoted × 0.7 and × 1.4
            market = {
                "city": creator.city,
                "niche": creator.niches[0],
                "creator_count": bench["creator_count"],
                "low":  round(quoted * 0.7 / 25) * 25,
                "high": round(quoted * 1.4 / 25) * 25,
            }

    return {
        "quoted_usd":      int(quoted),
        "currency":        "USD",
        "followers_used":  int(followers),
        "platform":        platform_lower,
        "deliverable":     deliverable.lower(),
        "quantity":        quantity,
        "engagement_pct":  round(eng, 2),
        "breakdown": {
            "base_cpm":              base_cpm,
            "base_unit_usd":         round(base_unit, 2),
            "engagement_multiplier": eng_mult,
            "city_multiplier":       city_mult,
            "niche_multiplier":      niche_mult,
            "usage_multiplier":      usage_mult,
            "exclusivity_multiplier": excl_mult,
            "per_deliverable_usd":   round(per_deliverable, 2),
            "subtotal_usd":          round(subtotal, 2),
            "total_before_rounding": round(total, 2),
        },
        "inputs": {
            "platform": platform_lower,
            "deliverable": deliverable.lower(),
            "quantity": quantity,
            "usage": usage,
            "exclusivity": exclusivity,
            "add_story_bundle": add_story_bundle,
        },
        "market_range": market,
    }


# ── LLM explanation ───────────────────────────────────────────────────────────

_EXPLAIN_PROMPT = """You are SKOUT's rate-calculator co-pilot for creators.

Given this creator's rate breakdown, write a short, confident explanation
(2-3 short sentences, max 60 words) of WHY the rate is what it is.
Be specific — cite the engagement multiplier, city, and usage rights if relevant.
Speak directly to the creator (\"You\", not \"the creator\"). No fluff,
no marketing-speak. End with one tactical sentence about how to negotiate up.

Breakdown JSON:
{breakdown}

Explanation:"""


def explain_rate(rate_data: dict) -> str:
    """Call Groq Llama for a tight 2-3 sentence rationale."""
    if not settings.groq_api_key:
        # Deterministic fallback if no LLM available
        b = rate_data["breakdown"]
        return (
            f"Your rate of ${rate_data['quoted_usd']:,} is based on "
            f"{rate_data['followers_used']:,} followers and a "
            f"{rate_data['engagement_pct']:.1f}% engagement rate "
            f"(multiplier: {b['engagement_multiplier']}x). "
            f"To negotiate up: ask for paid usage rights (+40-60%) or a longer exclusivity window."
        )

    try:
        resp = httpx.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.groq_api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": settings.groq_model,
                "messages": [
                    {"role": "system", "content": "You explain creator rates in 2-3 short sentences. Direct, specific, no fluff."},
                    {"role": "user",   "content": _EXPLAIN_PROMPT.format(breakdown=json.dumps(rate_data))},
                ],
                "max_tokens": 180,
                "temperature": 0.4,
            },
            timeout=15.0,
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        logger.warning(f"Rate explanation LLM failed: {exc}")
        b = rate_data["breakdown"]
        return (
            f"${rate_data['quoted_usd']:,} reflects your "
            f"{rate_data['followers_used']:,} followers × ${b['base_cpm']} CPM, "
            f"adjusted by your {b['engagement_multiplier']}x engagement multiplier."
        )


# ── Quote text generator ──────────────────────────────────────────────────────

def build_quote_text(creator: Creator, rate_data: dict) -> str:
    """A copy-paste-ready quote the creator can send to a brand."""
    name = creator.display_name or creator.full_name
    inputs = rate_data["inputs"]
    deliverable_label = {
        "reel": "Instagram Reel",
        "carousel": "Instagram Carousel",
        "static": "Instagram Static Post",
        "story": "Instagram Story",
        "bundle": "Instagram Reel + Stories Bundle",
        "video": "TikTok Video",
        "integration": "YouTube Integration",
        "dedicated": "YouTube Dedicated Video",
        "short": "YouTube Short",
    }.get(inputs["deliverable"], inputs["deliverable"].title())

    usage_label = {
        "organic":     "Organic-only usage",
        "paid_30d":    "Paid whitelisting (30 days)",
        "paid_60d":    "Paid whitelisting (60 days)",
        "reuse_brand": "Brand reuse on owned channels",
        "full_rights": "Full usage rights (perpetual)",
    }.get(inputs["usage"], inputs["usage"])

    excl_label = {
        "none": "no category exclusivity",
        "30d":  "30-day category exclusivity",
        "60d":  "60-day category exclusivity",
        "90d":  "90-day category exclusivity",
        "180d": "180-day category exclusivity",
    }.get(inputs["exclusivity"], inputs["exclusivity"])

    qty = inputs["quantity"]
    qty_text = f"{qty}x {deliverable_label}" if qty > 1 else deliverable_label

    return (
        f"Hi — thanks for the brief.\n\n"
        f"Here's my quote for {qty_text}:\n"
        f"• Deliverable: {qty_text}\n"
        f"• Usage: {usage_label}\n"
        f"• Exclusivity: {excl_label}\n"
        f"• Total: ${rate_data['quoted_usd']:,} USD\n\n"
        f"This is based on my current {rate_data['followers_used']:,} followers "
        f"and {rate_data['engagement_pct']:.1f}% engagement rate. "
        f"Happy to discuss timeline and creative direction next.\n\n"
        f"— {name}"
    )
