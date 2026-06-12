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


# ── Request schemas ────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class RateCalcRequest(BaseModel):
    platform: str = "instagram"
    deliverable: str = "reel"
    quantity: int = 1
    usage: str = "organic"
    exclusivity: str = "none"
    add_story_bundle: bool = False


class EvaluateBriefRequest(BaseModel):
    brief_text: str


class RefreshVoiceRequest(BaseModel):
    samples: list[str] | None = None


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


@router.post("/calculate-rate")
def calculate_rate(
    req: RateCalcRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(_auth),
):
    from backend.models.creator import Creator
    from backend.models.user import User
    from backend.services import rate_calculator_service as rcs

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "creator":
        raise HTTPException(status_code=404, detail="Creator user not found")
    if not user.creator_id:
        raise HTTPException(
            status_code=400,
            detail="Complete onboarding first — your follower data is needed to calculate a rate.",
        )

    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")

    try:
        result = rcs.calculate_rate(
            db, creator,
            platform=req.platform,
            deliverable=req.deliverable,
            quantity=req.quantity,
            usage=req.usage,
            exclusivity=req.exclusivity,
            add_story_bundle=req.add_story_bundle,
        )
        result["explanation"] = rcs.explain_rate(result)
        result["quote_text"]  = rcs.build_quote_text(creator, result)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Rate calculation error: {exc}")


@router.post("/evaluate-brief")
def evaluate_brief(
    req: EvaluateBriefRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(_auth),
):
    from backend.models.creator import Creator
    from backend.models.user import User
    from backend.services import brief_evaluator_service as bes

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.role != "creator":
        raise HTTPException(status_code=404, detail="Creator user not found")
    if not user.creator_id:
        raise HTTPException(
            status_code=400,
            detail="Complete onboarding first — we need your profile to evaluate the brief.",
        )

    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")

    if not req.brief_text or len(req.brief_text.strip()) < 20:
        raise HTTPException(
            status_code=400,
            detail="Paste at least a couple of sentences from the brand brief.",
        )

    try:
        return bes.evaluate_brief(db, creator, req.brief_text.strip())
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Brief evaluation error: {exc}")


@router.get("/voice")
def get_voice(
    db: Session = Depends(get_db),
    user_id: str = Depends(_auth),
):
    from backend.models.creator import Creator
    from backend.models.user import User

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.creator_id:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    return {"voice_description": creator.voice_description or ""}


@router.post("/voice/refresh")
def refresh_voice(
    req: RefreshVoiceRequest,
    db: Session = Depends(get_db),
    user_id: str = Depends(_auth),
):
    from backend.models.creator import Creator
    from backend.models.user import User
    from backend.services import tone_service

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.creator_id:
        raise HTTPException(status_code=404, detail="Creator profile not found")
    creator = db.query(Creator).filter(Creator.id == user.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator profile not found")

    if req.samples:
        voice = tone_service.update_voice(db, creator, req.samples)
    else:
        voice = tone_service.refresh_voice_from_profile(db, creator)

    if not voice:
        raise HTTPException(
            status_code=400,
            detail="Couldn't profile your voice yet — add a bio or paste a few of your captions.",
        )
    return {"voice_description": voice}
