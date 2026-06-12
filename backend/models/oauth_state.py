"""
Instagram OAuth state — replaces the old in-memory dicts so the flow
survives server restarts (e.g. uvicorn --reload) and works across workers.

Lifecycle:
  pending → row created when an auth URL is issued (TTL 5 min)
  ready   → onboarding mode only: callback stores fetched profile/reels/token
            as JSON payload for one-time pickup by the frontend (TTL 15 min)
  deleted → on pickup, on use (logged-in mode), or by pruning when expired
"""
from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class InstagramOAuthState(Base):
    __tablename__ = "instagram_oauth_states"

    state: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)  # None = onboarding mode
    phase: Mapped[str] = mapped_column(String(10), default="pending")       # pending | ready
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)        # JSON {profile, reels, token} when ready
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
