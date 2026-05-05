"""Agent conversation history — one row per turn, persisted per SMB user."""
from __future__ import annotations

import json
import uuid
from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class AgentConversation(Base):
    __tablename__ = "agent_conversations"

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid.uuid4())
    )
    smb_id: Mapped[str] = mapped_column(String(36), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(16), nullable=False)   # user | assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str | None] = mapped_column(String(32), nullable=True)
    # JSON string: creator list, brief text, outreach draft — drives action buttons
    action_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "smb_id": self.smb_id,
            "role": self.role,
            "content": self.content,
            "intent": self.intent,
            "action_data": json.loads(self.action_data) if self.action_data else None,
            "timestamp": self.timestamp.isoformat(),
        }
