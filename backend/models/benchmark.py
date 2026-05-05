"""MonthlyBenchmark ORM — cached city × category × month aggregate stats.

Recalculated by POST /local/benchmarks/recalculate (monthly cron or manual).
Drives the Industry Benchmark Widget and Trending Formats Widget.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class MonthlyBenchmark(Base):
    __tablename__ = "monthly_benchmarks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=_uuid)

    # Dimensions
    city:       Mapped[str] = mapped_column(String(120), index=True)
    category:   Mapped[str] = mapped_column(String(60),  index=True)
    month_year: Mapped[str] = mapped_column(String(7),   index=True)  # "2026-04"

    # Core benchmarks
    avg_engagement_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_followers:       Mapped[float] = mapped_column(Float, default=0.0)
    avg_posts_per_week:  Mapped[float] = mapped_column(Float, default=0.0)
    creator_count:       Mapped[int]   = mapped_column(Integer, default=0)

    # Format engagement breakdown (from posts table)
    avg_reel_engagement:     Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_carousel_engagement: Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_static_engagement:   Mapped[float | None] = mapped_column(Float, nullable=True)
    avg_story_engagement:    Mapped[float | None] = mapped_column(Float, nullable=True)
    top_format:              Mapped[str | None]   = mapped_column(String(20), nullable=True)
    top_format_multiplier:   Mapped[float | None] = mapped_column(Float, nullable=True)

    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "city":                     self.city,
            "category":                 self.category,
            "month_year":               self.month_year,
            "avg_engagement_rate":      self.avg_engagement_rate,
            "avg_followers":            self.avg_followers,
            "avg_posts_per_week":       self.avg_posts_per_week,
            "creator_count":            self.creator_count,
            "avg_reel_engagement":      self.avg_reel_engagement,
            "avg_carousel_engagement":  self.avg_carousel_engagement,
            "avg_static_engagement":    self.avg_static_engagement,
            "avg_story_engagement":     self.avg_story_engagement,
            "top_format":               self.top_format,
            "top_format_multiplier":    self.top_format_multiplier,
            "calculated_at":            self.calculated_at.isoformat(),
        }
