"""
Creator onboarding + retrieval endpoints.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.creator import Creator
from backend.models.user import User
from backend.services.auth_service import decode_token
from backend.schemas.creator import CreatorContact, CreatorOnboard, CreatorPublic, CreatorUpdate
from backend.services import creator_service
from backend.services.instagram import fetch_profile_public
from backend.services.match_service import calculate_match_score

router = APIRouter(prefix="/creators", tags=["creators"])


@router.post("", response_model=CreatorPublic, status_code=status.HTTP_201_CREATED)
def onboard_creator(payload: CreatorOnboard, db: Session = Depends(get_db)):
    """Creator self-onboarding: stores the profile and indexes it in Pinecone."""
    try:
        c = creator_service.create_creator(db, payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return CreatorPublic(**c.to_public_dict())


@router.get("")
def list_creators(
    db: Session = Depends(get_db),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    smb_id: Optional[str] = Query(None, description="If provided, sort by SKOUT Match Score for this SMB user"),
):
    rows = (
        db.query(Creator)
        .order_by(Creator.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    result = [c.to_public_dict() for c in rows]

    if smb_id:
        user = db.query(User).filter(User.id == smb_id).first()
        if user:
            meta = user.profile_meta or {}
            for c in result:
                c["match_score"] = calculate_match_score(meta, c)
            result.sort(key=lambda c: c["match_score"]["total"], reverse=True)

    return result


@router.get("/{creator_id}", response_model=CreatorContact)
def get_creator(creator_id: str, db: Session = Depends(get_db)):
    """Full (PII-included) creator record. In prod, gate behind tier/auth."""
    c = creator_service.get_by_id(db, creator_id)
    if not c:
        raise HTTPException(status_code=404, detail="Creator not found")
    return CreatorContact(**c.to_contact_dict())


@router.patch("/{creator_id}", response_model=CreatorContact)
def update_creator(
    creator_id: str,
    payload: CreatorUpdate,
    db: Session = Depends(get_db),
    authorization: str | None = Header(None),
):
    """Update an existing creator profile. Requires Bearer token belonging to that creator."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        token_data = decode_token(authorization[7:])
        user_id = token_data["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == user_id).first()
    if not user or user.creator_id != creator_id:
        raise HTTPException(status_code=403, detail="Not authorised to update this profile")

    creator = creator_service.get_by_id(db, creator_id)
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    updated = creator_service.update_creator(db, creator, payload)
    return CreatorContact(**updated.to_contact_dict())


@router.get("/instagram/{handle}")
def instagram_profile(handle: str):
    """
    Fetch public Instagram profile data for a given handle.
    Returns followers, bio, full_name, and whether the account is private.
    Falls back gracefully if Instagram blocks the request.
    """
    result = fetch_profile_public(handle)
    if not result.get("found") and not result.get("blocked"):
        raise HTTPException(status_code=404, detail=result.get("error", "Not found"))
    return result


@router.post("/reindex", status_code=202)
def reindex_vectors(db: Session = Depends(get_db)):
    n = creator_service.reindex_all(db)
    return {"reindexed": n}
