"""Creator Agent API — /creator-agent/chat, /creator-agent/history"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db

router = APIRouter(prefix="/creator-agent", tags=["creator-agent"])


# ── Auth dependency ────────────────────────────────────────────────────────────

def _auth(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    from backend.services.auth_service import decode_token
    try:
        return decode_token(authorization[7:])["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── Request schema ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


# ── Endpoints ──────────────────────────────────────────────────────────────────

@router.post("/chat")
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(_auth),
):
    from backend.services import creator_agent_service
    try:
        return creator_agent_service.chat(db, user_id, req.message)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}")


@router.get("/history")
def history(
    db: Session = Depends(get_db),
    user_id: str = Depends(_auth),
):
    from backend.services import creator_agent_service
    return creator_agent_service.get_history(db, user_id)
