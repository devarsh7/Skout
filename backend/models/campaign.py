"""
Campaign + outreach-tracker models.
Drives the retention loop: once a brand is tracking a campaign, churn drops.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("brand_users.id"))
    name: Mapped[str] = mapped_column(String(200))
    brief: Mapped[str | None] = mapped_column(Text)
    filters: Mapped[dict] = mapped_column(JSON, default=dict)
    status: Mapped[str] = mapped_column(String(20), default="active")  # active | paused | closed
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OutreachRecord(Base):
    __tablename__ = "outreach_records"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"))
    creator_id: Mapped[str] = mapped_column(String(36), ForeignKey("creators.id"))
    status: Mapped[str] = mapped_column(String(30), default="drafted")
    # drafted | sent | opened | replied | negotiating | booked | declined
    draft_subject: Mapped[str | None] = mapped_column(String(300))
    draft_body: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
