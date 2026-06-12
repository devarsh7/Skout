"""Brand-fact memory — durable facts about an SMB user the agent learns over time.

Examples of facts:
  • "Prefers nano creators under 10K"
  • "Budget is $300 per piece of content"
  • "Wants to launch Q3 in Queen West, Toronto"
  • "Has rejected fitness creators previously"

Facts are scoped to one SMB user (`smb_id`) and have a confidence score (0-1)
plus a category tag. The agent injects the top N facts (by confidence + recency)
into each system prompt.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


# Valid categories for tagging — keep small & clear.
CATEGORIES = (
    "budget",         # spending behavior
    "preference",     # taste / niche / creator profile preferences
    "constraint",     # must-haves or hard-nos
    "context",        # business context (industry, audience, products)
    "goal",           # what they're trying to achieve
    "outcome",        # results from past campaigns
    "other",
)


class BrandFact(Base):
    __tablename__ = "brand_facts"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    smb_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)

    # A short, declarative fact. Plain text, ~1 sentence.
    fact: Mapped[str] = mapped_column(Text, nullable=False)

    # Bucket: budget / preference / constraint / context / goal / outcome / other
    category: Mapped[str] = mapped_column(String(20), nullable=False, default="other")

    # 0.0 - 1.0. New extracted facts default to 0.7; user-confirmed ones go to 1.0.
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)

    # Source for the fact — usually "chat" but could be "onboarding", "manual", etc.
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="chat")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_dict(self) -> dict:
        return {
            "id":         self.id,
            "smb_id":     self.smb_id,
            "fact":       self.fact,
            "category":   self.category,
            "confidence": self.confidence,
            "source":     self.source,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
