"""
SKOUT Brand-fact memory service.

What it does
------------
Keeps a small, durable set of facts about each SMB user (their budget,
their preferences, their constraints, their goals) so the agent never
asks twice and feels like a real account manager.

How it works
------------
1. After every user message + assistant reply, we call extract_facts()
   on the last 2 turns. This runs a small LLM call (cheap with Haiku)
   to pull out durable facts.
2. New facts are merged into the brand_facts table — exact duplicates
   are skipped, near-duplicates increase the existing fact's confidence.
3. When building the agent system prompt, we inject the top N facts
   by `confidence` (and by recency as tiebreak) — typically 15.

Privacy
-------
Facts are scoped to the SMB user. Deletion via the API removes them.
"""
from __future__ import annotations

import json
from typing import Iterable

import httpx
from loguru import logger
from sqlalchemy import desc
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.brand_fact import BrandFact, CATEGORIES


# Maximum facts to inject in the system prompt
MAX_FACTS_IN_PROMPT = 15
# Maximum total facts to retain per SMB user (older + lower-confidence get pruned)
MAX_FACTS_PER_SMB = 60


# ── Extraction prompt ─────────────────────────────────────────────────────────

_EXTRACT_PROMPT = """You are SKOUT's memory extractor. From the conversation snippet below,
extract NEW, durable facts about the small-business user that will be useful
to remember for the NEXT conversation. Skip anything that's only relevant right now.

Rules:
- Each fact must be 1 short declarative sentence in third-person about the user/business.
  ("Prefers nano creators under 10K", "Budget is $300 per piece", "Sells DTC skincare in Toronto")
- Use the categories: budget, preference, constraint, context, goal, outcome, other.
- Confidence 0.0-1.0. Only include facts you're at least 0.5 confident about.
- Skip transient mentions ("today", "right now", "just one campaign").
- If nothing new is durable, return [].
- Output STRICT JSON only — array of {{"fact": "...", "category": "...", "confidence": 0.0-1.0}}.
- No prose. No code fences. No additional fields.

Conversation snippet:
{snippet}

JSON:"""


def _call_groq(messages: list[dict], max_tokens: int = 400, temperature: float = 0.1) -> str:
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
        timeout=20.0,
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


# ── Public: extraction + persistence ──────────────────────────────────────────

def extract_facts(snippet: str) -> list[dict]:
    """LLM call. Best-effort. Returns [] on any failure."""
    if not snippet or len(snippet.strip()) < 20:
        return []
    try:
        out = _call_groq([{"role": "user", "content": _EXTRACT_PROMPT.format(snippet=snippet)}])
        parsed = json.loads(_strip_code_fence(out))
        if not isinstance(parsed, list):
            return []
        cleaned: list[dict] = []
        for item in parsed:
            if not isinstance(item, dict) or "fact" not in item:
                continue
            fact = str(item["fact"]).strip().rstrip(".")
            if not fact or len(fact) > 200:
                continue
            category = item.get("category", "other")
            if category not in CATEGORIES:
                category = "other"
            try:
                conf = float(item.get("confidence", 0.7))
            except (TypeError, ValueError):
                conf = 0.7
            conf = max(0.0, min(1.0, conf))
            if conf < 0.5:
                continue
            cleaned.append({"fact": fact, "category": category, "confidence": conf})
        return cleaned
    except Exception as exc:
        logger.warning(f"Fact extraction failed: {exc}")
        return []


def _normalize_fact(fact: str) -> str:
    """Lowercase + strip whitespace for similarity comparison."""
    return " ".join(fact.lower().strip().split())


def upsert_facts(db: Session, smb_id: str, facts: Iterable[dict], source: str = "chat") -> int:
    """
    Insert new facts, increase confidence on near-duplicates, prune oldest if over cap.
    Returns the number of newly created rows.
    """
    facts = list(facts)
    if not facts:
        return 0

    existing = (
        db.query(BrandFact)
        .filter(BrandFact.smb_id == smb_id)
        .all()
    )
    existing_lookup = {_normalize_fact(f.fact): f for f in existing}

    added = 0
    for f in facts:
        key = _normalize_fact(f["fact"])
        if key in existing_lookup:
            # Bump confidence up to 1.0 if we've seen this fact again
            row = existing_lookup[key]
            row.confidence = min(1.0, row.confidence + 0.1)
        else:
            db.add(BrandFact(
                smb_id=smb_id,
                fact=f["fact"],
                category=f["category"],
                confidence=f["confidence"],
                source=source,
            ))
            added += 1

    # Prune to cap if needed (lowest confidence + oldest go first)
    if added > 0:
        total = len(existing) + added
        if total > MAX_FACTS_PER_SMB:
            to_prune = total - MAX_FACTS_PER_SMB
            losers = (
                db.query(BrandFact)
                .filter(BrandFact.smb_id == smb_id)
                .order_by(BrandFact.confidence.asc(), BrandFact.updated_at.asc())
                .limit(to_prune)
                .all()
            )
            for l in losers:
                db.delete(l)

    db.commit()
    return added


def get_facts(db: Session, smb_id: str, limit: int = MAX_FACTS_IN_PROMPT) -> list[BrandFact]:
    return (
        db.query(BrandFact)
        .filter(BrandFact.smb_id == smb_id)
        .order_by(desc(BrandFact.confidence), desc(BrandFact.updated_at))
        .limit(limit)
        .all()
    )


def list_all_facts(db: Session, smb_id: str) -> list[BrandFact]:
    return (
        db.query(BrandFact)
        .filter(BrandFact.smb_id == smb_id)
        .order_by(desc(BrandFact.confidence), desc(BrandFact.updated_at))
        .all()
    )


def delete_fact(db: Session, smb_id: str, fact_id: str) -> bool:
    row = (
        db.query(BrandFact)
        .filter(BrandFact.smb_id == smb_id, BrandFact.id == fact_id)
        .first()
    )
    if not row:
        return False
    db.delete(row)
    db.commit()
    return True


def add_manual_fact(db: Session, smb_id: str, fact: str, category: str = "other") -> BrandFact:
    if category not in CATEGORIES:
        category = "other"
    row = BrandFact(
        smb_id=smb_id,
        fact=fact.strip().rstrip("."),
        category=category,
        confidence=1.0,    # user-added = trust fully
        source="manual",
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


# ── Prompt-block helper ───────────────────────────────────────────────────────

def build_facts_block(db: Session, smb_id: str) -> str:
    """Compact lines for injection into the agent's system prompt."""
    facts = get_facts(db, smb_id)
    if not facts:
        return ""
    by_cat: dict[str, list[str]] = {}
    for f in facts:
        by_cat.setdefault(f.category, []).append(f.fact)

    parts = ["\n\nWHAT YOU REMEMBER ABOUT THIS USER (durable facts from prior chats):"]
    for cat in ["budget", "preference", "constraint", "context", "goal", "outcome", "other"]:
        items = by_cat.get(cat)
        if not items:
            continue
        for item in items:
            parts.append(f"- [{cat}] {item}")
    parts.append("\nUse these facts naturally — don't re-ask things you already know.")
    return "\n".join(parts)
