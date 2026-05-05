"""
Outreach Agent
==============
Drafts a personalized message to a creator based on the brand's brief.

This is a **retention feature** — brands who draft outreach are 4-6x more
likely to stay subscribed than brands who only run searches.
"""
from __future__ import annotations

import json
import re

from loguru import logger
from sqlalchemy.orm import Session

from backend.schemas.agent import OutreachDraft, OutreachRequest
from backend.services.creator_service import get_by_id
from backend.services.llm_service import get_llm


_PROMPT = """You are a senior influencer-marketing manager drafting a first-touch message.

Creator profile:
- Name: {display_name}
- Bio: {bio}
- Niches: {niches}
- Location: {city}, {country}
- Total followers: {total_followers}
- Platforms: {platforms}

Brand: {brand_name}
Brief: {campaign_brief}

Channel: {channel}      # email | instagram_dm | tiktok_dm
Tone: {tone}

Rules:
- Short (120-180 words for email; 60-90 words for DMs).
- Reference something specific from the creator's bio or niche — show you read it.
- Propose a concrete next step (15-min intro call or content sample request).
- No em-dashes, no corporate jargon, no "I hope this message finds you well".
- If channel is a DM, drop the subject line and keep body ≤ 90 words.

Return STRICT JSON only: {{"subject": "...", "body": "..."}}
"""


class OutreachAgent:
    def draft(self, db: Session, req: OutreachRequest) -> OutreachDraft:
        creator = get_by_id(db, req.creator_id)
        if not creator:
            raise ValueError(f"Creator {req.creator_id} not found")

        platforms = [
            p
            for p, ok in [
                ("Instagram", bool(creator.instagram_handle)),
                ("TikTok", bool(creator.tiktok_handle)),
                ("YouTube", bool(creator.youtube_channel)),
            ]
            if ok
        ]

        prompt = _PROMPT.format(
            display_name=creator.display_name or creator.full_name,
            bio=(creator.bio or "").strip() or "—",
            niches=", ".join(creator.niches or []) or "—",
            city=creator.city or "—",
            country=creator.country or "—",
            total_followers=creator.total_followers,
            platforms=", ".join(platforms) or "—",
            brand_name=req.brand_name,
            campaign_brief=req.campaign_brief,
            channel=req.channel,
            tone=req.tone,
        )

        llm = get_llm(temperature=0.6)
        resp = llm.invoke(prompt)
        raw = getattr(resp, "content", str(resp)).strip()

        # Strip accidental code fences
        raw = re.sub(r"^```(?:json)?", "", raw).strip()
        raw = re.sub(r"```$", "", raw).strip()

        try:
            data = json.loads(raw)
            return OutreachDraft(subject=data.get("subject", ""), body=data.get("body", raw))
        except json.JSONDecodeError:
            logger.warning("Outreach LLM didn't return valid JSON; falling back to raw.")
            # Best-effort salvage: use first line as subject, rest as body.
            lines = [ln for ln in raw.splitlines() if ln.strip()]
            subject = lines[0][:120] if lines else "Collab idea"
            body = "\n".join(lines[1:]) or raw
            return OutreachDraft(subject=subject, body=body)
