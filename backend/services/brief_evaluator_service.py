"""
SKOUT Brief Evaluator — decodes inbound brand briefs for creators.

Pipeline:
  1. Structured LLM call extracts: deliverables, pay, usage, timeline, exclusivity
  2. Compare proposed pay to creator's calculated fair rate
  3. Detect red flags from a curated rules library
  4. Draft a counter-proposal in the creator's voice
"""
from __future__ import annotations

import json
import re
from typing import Optional

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.creator import Creator
from backend.services import rate_calculator_service as rcs


# ── Red-flag rules ────────────────────────────────────────────────────────────

_RED_FLAG_PATTERNS: list[tuple[re.Pattern, str, str]] = [
    (re.compile(r"\bexposure\b|\bgreat\s+exposure\b", re.I),
     "Paid in exposure",
     "Brands offering 'exposure' instead of money typically have no budget — push for at least gifted-product + cash floor."),
    (re.compile(r"\bperpetual\b|\bin perpetuity\b|\bforever\b", re.I),
     "Perpetual usage rights",
     "They want to use your content forever. Standard ask is 30-90 days — extend pricing accordingly (1.5-2.5x base)."),
    (re.compile(r"\bfull\s+rights\b|\ball\s+rights\b|\bbuyout\b", re.I),
     "Full rights / buyout",
     "Full buyout = brand owns the asset. Charge minimum 2x your base rate, and usually 3x+."),
    (re.compile(r"\bexclusiv\w+\b", re.I),
     "Exclusivity clause",
     "Exclusivity blocks competitor work. Confirm duration & category — and add +20-40% to rate."),
    (re.compile(r"\b(net\s*60|net\s*90|net\s*120)\b", re.I),
     "Slow payment terms",
     "Net-60+ is brutal for cashflow. Counter with Net-30 or 50% upfront."),
    (re.compile(r"\bedits?\b.*\bunlimited\b|\bunlimited\s+(revisions|edits|rounds)\b", re.I),
     "Unlimited revisions",
     "Cap revisions at 2 rounds. Anything more = +$X per revision in the contract."),
    (re.compile(r"\bwhitelisting\b|\bspark\s*ads?\b|\bdark\s*post\b", re.I),
     "Paid amplification",
     "Brand wants to run your content as ads. Standard markup: +40-60% per 30-day window."),
    (re.compile(r"\b(asap|tomorrow|by\s+(monday|tuesday|wednesday|thursday|friday|sunday|saturday))\b", re.I),
     "Rush timeline",
     "Tight deadlines deserve a 15-30% rush fee — name it in the counter."),
    (re.compile(r"\bno\s+budget\b|\bsmall\s+budget\b|\btight\s+budget\b", re.I),
     "Stated budget constraint",
     "Often a negotiation opener, not a hard cap. Counter with your rate + value justification."),
]


def _detect_red_flags(brief_text: str) -> list[dict]:
    found: list[dict] = []
    seen: set[str] = set()
    for pattern, label, advice in _RED_FLAG_PATTERNS:
        if pattern.search(brief_text) and label not in seen:
            found.append({"label": label, "advice": advice})
            seen.add(label)
    return found


# ── Structured extraction ─────────────────────────────────────────────────────

_EXTRACT_PROMPT = """You are SKOUT's brief evaluator. Read the brand brief below and
return a single JSON object — no prose, no code fences — with these fields:

{{
  "brand_name":   "<brand name or null>",
  "deliverables": "<short summary, e.g. '1 IG Reel + 3 Stories'>",
  "offered_usd":  <number or null — total pay in USD if mentioned, convert if other currency stated>,
  "usage":        "<organic|paid_30d|paid_60d|reuse_brand|full_rights|unspecified>",
  "exclusivity":  "<none|30d|60d|90d|180d|unspecified>",
  "timeline":     "<short summary or 'unspecified'>",
  "platform":     "<instagram|tiktok|youtube|unspecified>",
  "key_clauses":  ["<short bullet>", "<short bullet>"]
}}

Brief:
{brief}

JSON:"""


def _call_groq(messages: list[dict], max_tokens: int = 500, temperature: float = 0.2) -> str:
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    resp = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.groq_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.groq_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


def _strip_code_fence(text: str) -> str:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`").split("\n", 1)[-1]
        if t.endswith("```"):
            t = t[:-3]
    return t.strip()


def extract_brief(brief_text: str) -> dict:
    """Return a parsed dict — best effort. Falls back to mostly-unknown skeleton."""
    skeleton = {
        "brand_name": None,
        "deliverables": "unspecified",
        "offered_usd": None,
        "usage": "unspecified",
        "exclusivity": "unspecified",
        "timeline": "unspecified",
        "platform": "unspecified",
        "key_clauses": [],
    }
    try:
        out = _call_groq([{"role": "user", "content": _EXTRACT_PROMPT.format(brief=brief_text)}])
        parsed = json.loads(_strip_code_fence(out))
        if not isinstance(parsed, dict):
            return skeleton
        # Merge over skeleton to enforce shape
        for k in skeleton:
            if k in parsed:
                skeleton[k] = parsed[k]
        return skeleton
    except Exception as exc:
        logger.warning(f"Brief extraction failed: {exc}")
        return skeleton


# ── Counter-proposal ──────────────────────────────────────────────────────────

_COUNTER_PROMPT = """You are SKOUT's brief evaluator helping a creator counter-propose.

Creator name: {creator_name}
Creator's fair rate (USD, calculated from their followers + engagement + market): ${fair_rate}
Brand offered (USD): {offered}
Red flags detected: {red_flags}

Write a counter-proposal email — direct, professional, friendly, 4-6 short sentences.
Lead with what you'll deliver. Then state your rate clearly. Address ONE biggest red flag if relevant.
End with one question to keep the convo moving. No "I'm thrilled to be considered" fluff.

Counter-proposal:"""


def draft_counter(
    creator_name: str,
    fair_rate: int,
    offered: Optional[float],
    red_flags: list[dict],
) -> str:
    rf_summary = ", ".join(rf["label"] for rf in red_flags) or "none"
    try:
        return _call_groq(
            [
                {"role": "system", "content": "You write short, confident creator counter-proposal emails. No fluff."},
                {"role": "user",   "content": _COUNTER_PROMPT.format(
                    creator_name=creator_name,
                    fair_rate=fair_rate,
                    offered=offered if offered is not None else "not stated",
                    red_flags=rf_summary,
                )},
            ],
            max_tokens=350,
            temperature=0.5,
        )
    except Exception as exc:
        logger.warning(f"Counter-proposal LLM failed: {exc}")
        # Deterministic fallback
        offered_line = (
            f"You offered ${offered:,.0f}, "
            if offered is not None
            else "Thanks for the brief. "
        )
        return (
            f"Hi — thanks for the brief.\n\n"
            f"{offered_line}for the deliverables described my rate is ${fair_rate:,} USD. "
            f"This reflects my current reach, engagement, and the local Toronto market.\n\n"
            f"Happy to talk timeline and creative direction once we're aligned on scope. "
            f"Anything flexible on usage rights?\n\n"
            f"— {creator_name}"
        )


# ── Public API ────────────────────────────────────────────────────────────────

def evaluate_brief(db: Session, creator: Creator, brief_text: str) -> dict:
    extracted = extract_brief(brief_text)
    red_flags = _detect_red_flags(brief_text)

    # Map extracted usage/exclusivity to calculator's vocabulary
    usage_for_calc = extracted["usage"] if extracted["usage"] != "unspecified" else "organic"
    excl_for_calc  = extracted["exclusivity"] if extracted["exclusivity"] != "unspecified" else "none"
    platform_for_calc = (
        extracted["platform"] if extracted["platform"] != "unspecified" else "instagram"
    )

    # Calculate a fair rate using their best-default deliverable
    default_deliverable = {
        "instagram": "reel", "tiktok": "video", "youtube": "integration",
    }.get(platform_for_calc, "reel")

    rate = rcs.calculate_rate(
        db, creator,
        platform=platform_for_calc,
        deliverable=default_deliverable,
        quantity=1,
        usage=usage_for_calc,
        exclusivity=excl_for_calc,
    )
    fair = rate["quoted_usd"]

    # Pay analysis
    offered = extracted.get("offered_usd")
    pay_analysis: dict[str, object] = {
        "fair_rate_usd": fair,
        "offered_usd":   offered,
    }
    if offered is None:
        pay_analysis["verdict"]  = "no_offer"
        pay_analysis["headline"] = "No dollar amount stated — name your number first."
    else:
        ratio = offered / max(fair, 1)
        pay_analysis["ratio"] = round(ratio, 2)
        if ratio >= 0.95:
            pay_analysis["verdict"]  = "fair"
            pay_analysis["headline"] = f"Offer is roughly in line with your fair rate (${fair:,})."
        elif ratio >= 0.6:
            pay_analysis["verdict"]  = "below"
            pay_analysis["headline"] = (
                f"Offer is {(1-ratio)*100:.0f}% below your fair rate of ${fair:,}. "
                f"Worth countering up."
            )
        else:
            pay_analysis["verdict"]  = "lowball"
            pay_analysis["headline"] = (
                f"This is a lowball at {ratio*100:.0f}% of your fair rate (${fair:,}). "
                f"Counter at the full rate or walk."
            )

    # Counter
    counter = draft_counter(
        creator.display_name or creator.full_name or "",
        fair,
        offered,
        red_flags,
    )

    return {
        "extracted":     extracted,
        "red_flags":     red_flags,
        "pay_analysis":  pay_analysis,
        "counter_draft": counter,
        "rate_basis":    rate,
    }
