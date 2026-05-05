"""
Agent Chat API — /agent/chat, /agent/history, /agent/notifications,
                  /agent/action/save-creators, /agent/action/use-brief,
                  /agent/action/send-outreach
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, Header, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.user import User

router = APIRouter(prefix="/agent", tags=["agent-chat"])


# ── Auth dependency ───────────────────────────────────────────────────────────

def _auth(authorization: str | None = Header(default=None)) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    from backend.services.auth_service import decode_token
    try:
        return decode_token(authorization[7:])["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── Request schemas ───────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str


class SaveCreatorsRequest(BaseModel):
    creator_ids: list[str]
    creator_names: list[str] = []


class UseBriefRequest(BaseModel):
    brief_text: str
    campaign_name: str = "Agent Brief"


class SendOutreachRequest(BaseModel):
    creator_id: str
    campaign_id: str | None = None


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/chat")
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    smb_id: str = Depends(_auth),
):
    from backend.services import agent_chat_service

    try:
        return agent_chat_service.chat(db, smb_id, req.message)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Agent error: {exc}")


@router.get("/history")
def history(
    db: Session = Depends(get_db),
    smb_id: str = Depends(_auth),
):
    from backend.services import agent_chat_service

    return agent_chat_service.get_history(db, smb_id)


@router.get("/notifications")
def notifications(
    db: Session = Depends(get_db),
    smb_id: str = Depends(_auth),
):
    from backend.services import agent_chat_service

    user = db.query(User).filter(User.id == smb_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    notifs = agent_chat_service.get_proactive_notifications(db, smb_id, user)
    return {"notifications": notifs}


@router.post("/action/save-creators")
def save_creators(
    req: SaveCreatorsRequest,
    db: Session = Depends(get_db),
    smb_id: str = Depends(_auth),
):
    user = db.query(User).filter(User.id == smb_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    meta = dict(user.profile_meta or {})
    saved: list[dict] = list(meta.get("saved_creators") or [])
    existing_ids = {s["id"] for s in saved}

    added = 0
    for i, cid in enumerate(req.creator_ids):
        if cid not in existing_ids:
            name = req.creator_names[i] if i < len(req.creator_names) else cid
            saved.append({"id": cid, "name": name})
            added += 1

    meta["saved_creators"] = saved
    user.profile_meta = meta
    db.commit()
    return {"saved": len(saved), "added": added, "message": f"Saved {added} creator(s) to your list."}


@router.post("/action/use-brief")
def use_brief(
    req: UseBriefRequest,
    db: Session = Depends(get_db),
    smb_id: str = Depends(_auth),
):
    from backend.models.campaign import Campaign

    campaign = Campaign(owner_id=smb_id, name=req.campaign_name, brief=req.brief_text, status="active")
    db.add(campaign)
    db.commit()
    db.refresh(campaign)
    return {"campaign_id": campaign.id, "message": f'Brief saved as campaign "{req.campaign_name}".'}


@router.post("/action/send-outreach")
def send_outreach(
    req: SendOutreachRequest,
    db: Session = Depends(get_db),
    smb_id: str = Depends(_auth),
):
    from backend.models.campaign import Campaign, OutreachRecord
    from backend.models.creator import Creator

    creator = db.query(Creator).filter(Creator.id == req.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator not found")

    # Resolve or create a campaign to attach the record to
    campaign_id = req.campaign_id
    if not campaign_id:
        default = (
            db.query(Campaign)
            .filter(Campaign.owner_id == smb_id, Campaign.status == "active")
            .first()
        )
        if default:
            campaign_id = default.id
        else:
            c = Campaign(owner_id=smb_id, name="Agent Outreach", status="active")
            db.add(c)
            db.flush()
            campaign_id = c.id

    record = OutreachRecord(campaign_id=campaign_id, creator_id=req.creator_id, status="sent")
    db.add(record)
    db.commit()
    db.refresh(record)

    creator_name = creator.display_name or creator.full_name
    return {
        "outreach_id": record.id,
        "creator": creator_name,
        "message": f"Outreach recorded for {creator_name}.",
    }
