"""
SKOUT tone-of-voice memory.

What it does
------------
Profiles a creator's writing voice from samples of their captions
(or their bio) and stores a tight 2-4 sentence "voice card" that the
Career Manager injects into every system prompt — so drafted
counter-proposals, pitches, and bios sound like THEM, not the LLM.

Stored on Creator.voice_description (Text column).
"""
from __future__ import annotations

from typing import Optional

import httpx
from loguru import logger
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.creator import Creator


_PROMPT = """You are SKOUT's voice profiler for creators.

Read these caption / bio samples from one creator and write a 2-4 sentence
"voice card" capturing how they actually write. Focus on:
- sentence rhythm (long vs punchy, all-lowercase, ALL CAPS bursts, ellipses…)
- recurring phrases / signature words
- emoji habits (which ones, how often)
- punctuation tics (em dashes, no periods, exclaims, etc.)
- tone (warm / dry / cocky / earnest / chaotic / professional)

Don't editorialize. Don't praise. Just describe — like a profiler.
Write in second person ("You write in…") — this is the creator reading
their own profile. Max ~80 words.

Samples:
{samples}

Voice card:"""


def _call_groq(content: str, max_tokens: int = 240, temperature: float = 0.3) -> str:
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
            "messages": [
                {"role": "system", "content": "You profile creator voice in 80 words or less. Direct, observational, no praise."},
                {"role": "user",   "content": content},
            ],
            "max_tokens": max_tokens,
            "temperature": temperature,
        },
        timeout=20.0,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"].strip()


# ── Public API ────────────────────────────────────────────────────────────────

def extract_voice(samples: list[str]) -> str | None:
    """Profile voice from a list of caption/bio samples. Returns None on failure."""
    samples = [s.strip() for s in samples if s and s.strip()]
    if not samples:
        return None
    # Cap total chars so we don't blow the context
    joined = "\n---\n".join(samples)[:4000]
    try:
        return _call_groq(_PROMPT.format(samples=joined))
    except Exception as exc:
        logger.warning(f"Voice profiling failed: {exc}")
        return None


def refresh_voice_from_profile(db: Session, creator: Creator) -> Optional[str]:
    """
    Default path: profile from bio + any pre-stored sample captions.
    Onboarding flows can also pass captions explicitly via update_voice().
    """
    samples: list[str] = []
    if creator.bio:
        samples.append(creator.bio)

    # In a future iteration: pull captions from Post table or Instagram API.
    # For now, bio is the minimum viable sample.
    voice = extract_voice(samples)
    if voice:
        creator.voice_description = voice
        db.commit()
        db.refresh(creator)
    return voice


def update_voice(db: Session, creator: Creator, samples: list[str]) -> Optional[str]:
    """Explicit refresh given new samples (e.g. captions returned by IG OAuth)."""
    voice = extract_voice(samples)
    if voice:
        creator.voice_description = voice
        db.commit()
        db.refresh(creator)
    return voice


def build_voice_block(creator: Creator) -> str:
    """Compact line for injection into the Career Manager system prompt."""
    if not creator.voice_description:
        return ""
    return (
        "\n\nYOUR CREATOR'S VOICE (use this when drafting captions, pitches, or DMs — sound like them):\n"
        f"{creator.voice_description}"
    )
