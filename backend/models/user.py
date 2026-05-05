"""
Unified User model — creators AND brand users share this table.
creator_id links to the Creator profile once onboarded.
"""
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id:              Mapped[str]           = mapped_column(String(36), primary_key=True, default=_uuid)
    username:        Mapped[str]           = mapped_column(String(60),  unique=True, index=True, nullable=False)
    email:           Mapped[str]           = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str]           = mapped_column(String(255), nullable=False)
    role:            Mapped[str]           = mapped_column(String(20),  default="creator")  # creator | business | admin
    is_verified:     Mapped[bool]          = mapped_column(Boolean, default=False)

    # OTP verification
    otp_code:        Mapped[str | None]    = mapped_column(String(6))
    otp_expires_at:  Mapped[datetime | None] = mapped_column(DateTime)

    # Link to creator profile (nullable until onboarding completes)
    creator_id:      Mapped[str | None]    = mapped_column(String(36), ForeignKey("creators.id"), nullable=True)

    # Extra profile data (business: company_name, website, etc.)
    profile_meta:    Mapped[dict | None]    = mapped_column(JSON, nullable=True)

    created_at:      Mapped[datetime]      = mapped_column(DateTime, default=datetime.utcnow)
    last_login:      Mapped[datetime | None] = mapped_column(DateTime)
