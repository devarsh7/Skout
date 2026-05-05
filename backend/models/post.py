"""Post ORM — individual content pieces from creator social channels.

Each row represents one published post. Powers:
  • Local leaderboard (engagement per city/category/month)
  • Trending format widget (Reel vs Carousel vs Static vs Story)
  • Location confidence source 3 (location_tag present on post)
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)

    # Relationship
    creator_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("creators.id", ondelete="CASCADE"), index=True
    )

    # Content metadata
    platform: Mapped[str | None] = mapped_column(String(20))   # instagram|tiktok|youtube
    format:   Mapped[str | None] = mapped_column(String(20))   # Reel|Carousel|Static|Story|Video
    posted_at: Mapped[datetime | None] = mapped_column(DateTime, index=True)

    # Engagement metrics
    likes:           Mapped[int]   = mapped_column(Integer, default=0)
    comments:        Mapped[int]   = mapped_column(Integer, default=0)
    shares:          Mapped[int]   = mapped_column(Integer, default=0)
    views:           Mapped[int]   = mapped_column(Integer, default=0)
    engagement_rate: Mapped[float] = mapped_column(Float, default=0.0, index=True)

    # Location
    city:    Mapped[str | None] = mapped_column(String(120), index=True)
    country: Mapped[str | None] = mapped_column(String(2))
    has_location_tag: Mapped[bool] = mapped_column(Boolean, default=False)

    # NLP source material
    caption_sample: Mapped[str | None] = mapped_column(Text)
    hashtags:       Mapped[list[str]]  = mapped_column(JSON, default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id":               self.id,
            "creator_id":       self.creator_id,
            "platform":         self.platform,
            "format":           self.format,
            "posted_at":        self.posted_at.isoformat() if self.posted_at else None,
            "likes":            self.likes,
            "comments":         self.comments,
            "shares":           self.shares,
            "views":            self.views,
            "engagement_rate":  self.engagement_rate,
            "city":             self.city,
            "country":          self.country,
            "has_location_tag": self.has_location_tag,
        }
