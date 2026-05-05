"""
Creator ORM — the canonical record for an onboarded influencer.

IMPORTANT: PII (email, phone) lives here in the relational DB.
Pinecone stores only a public-safe summary vector + the creator's UUID so we
can JOIN back to this table.  Never put PII in vector metadata.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Creator(Base):
    __tablename__ = "creators"

    # Identity
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)
    full_name: Mapped[str] = mapped_column(String(120), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(30))

    # Social handles (all optional except at least one — validated at API layer)
    instagram_handle: Mapped[str | None] = mapped_column(String(80), index=True)
    tiktok_handle: Mapped[str | None] = mapped_column(String(80), index=True)
    youtube_channel: Mapped[str | None] = mapped_column(String(120), index=True)
    facebook_page: Mapped[str | None] = mapped_column(String(120))
    twitter_handle: Mapped[str | None] = mapped_column(String(80))
    website: Mapped[str | None] = mapped_column(String(255))

    # Reach
    instagram_followers: Mapped[int] = mapped_column(Integer, default=0)
    tiktok_followers: Mapped[int] = mapped_column(Integer, default=0)
    youtube_subscribers: Mapped[int] = mapped_column(Integer, default=0)
    total_followers: Mapped[int] = mapped_column(Integer, default=0, index=True)

    # Engagement
    avg_engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_views: Mapped[int] = mapped_column(Integer, default=0)

    # Profile
    bio: Mapped[str | None] = mapped_column(Text)
    niches: Mapped[list[str]] = mapped_column(JSON, default=list)            # ["fashion", "beauty"]
    languages: Mapped[list[str]] = mapped_column(JSON, default=list)         # ["en", "hi"]
    country: Mapped[str | None] = mapped_column(String(2), index=True)       # ISO-3166
    city: Mapped[str | None] = mapped_column(String(120), index=True)
    audience_countries: Mapped[list[str]] = mapped_column(JSON, default=list)
    audience_age_range: Mapped[str | None] = mapped_column(String(20))       # e.g. "18-24"
    audience_gender_split: Mapped[dict] = mapped_column(JSON, default=dict)  # {"f": 0.7, "m": 0.3}

    # Match intelligence fields
    audience_location_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)  # {"Mumbai": 45, "Delhi": 25}
    content_categories: Mapped[dict | None] = mapped_column(JSON, nullable=True)      # {"food": 72, "lifestyle": 18}
    authenticity_score: Mapped[float | None] = mapped_column(Float, nullable=True)    # 0-100
    availability_status: Mapped[str | None] = mapped_column(String(20), nullable=True)  # available|busy|inactive

    # Hyperlocal fields
    neighbourhood: Mapped[str | None] = mapped_column(String(120), nullable=True)  # self-reported sub-area
    # Location confidence (HIGH / MEDIUM / LOW) — derived from 4 sources
    location_confidence: Mapped[str | None] = mapped_column(String(10), nullable=True)
    location_sources: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    # Flags set when post ingestion confirms location via tags / NLP
    location_tags_confirmed: Mapped[bool] = mapped_column(Boolean, default=False)
    nlp_location_confirmed:  Mapped[bool] = mapped_column(Boolean, default=False)

    # Pricing / collab
    min_rate_usd: Mapped[float] = mapped_column(Float, default=0.0)
    open_to_collabs: Mapped[bool] = mapped_column(Boolean, default=True)
    preferred_collab_types: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Internal
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    vector_indexed: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    def to_public_dict(self) -> dict:
        """Public card payload — safe to return to brand users."""
        return {
            "id": self.id,
            "display_name": self.display_name or self.full_name,
            "full_name": self.full_name,
            "bio": self.bio,
            "niches": self.niches,
            "languages": self.languages,
            "country": self.country,
            "city": self.city,
            "total_followers": self.total_followers,
            "instagram_followers": self.instagram_followers,
            "tiktok_followers": self.tiktok_followers,
            "youtube_subscribers": self.youtube_subscribers,
            "avg_engagement_rate": self.avg_engagement_rate,
            "avg_views": self.avg_views,
            "open_to_collabs": self.open_to_collabs,
            "is_verified": self.is_verified,
            "audience_gender_split": self.audience_gender_split,
            "audience_age_range": self.audience_age_range,
            "audience_location_data": self.audience_location_data,
            "content_categories": self.content_categories,
            "authenticity_score": self.authenticity_score,
            "availability_status": self.availability_status,
            "neighbourhood": self.neighbourhood,
            "location_confidence": self.location_confidence,
            "location_sources": self.location_sources,
            "instagram_handle": self.instagram_handle,
            "tiktok_handle": self.tiktok_handle,
            "youtube_channel": self.youtube_channel,
            "handles": {
                "instagram": self.instagram_handle,
                "tiktok": self.tiktok_handle,
                "youtube": self.youtube_channel,
                "facebook": self.facebook_page,
                "twitter": self.twitter_handle,
            },
        }

    def to_contact_dict(self) -> dict:
        """PII payload — only for paying brand users."""
        return {**self.to_public_dict(), "email": self.email, "phone": self.phone}

    def embedding_text(self) -> str:
        """Concatenated text used to build this creator's semantic vector."""
        parts = [
            self.display_name or self.full_name,
            self.bio or "",
            "Niches: " + ", ".join(self.niches or []),
            "Languages: " + ", ".join(self.languages or []),
            f"Based in {self.city or ''}, {self.country or ''}".strip(", "),
            f"Total followers: {self.total_followers}",
        ]
        return " | ".join(p for p in parts if p)
