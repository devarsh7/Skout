"""Auth endpoints — register, verify OTP, resend OTP, login, plus verified-registration flows."""
from __future__ import annotations

from typing import Optional

import fastapi
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.user import User
from backend.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _require_auth(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    from backend.services.auth_service import decode_token
    try:
        payload = decode_token(authorization[7:])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ── schemas ───────────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    username:   str
    email:      EmailStr
    password:   str
    role:       str = "creator"
    creator_id: str | None = None

    @field_validator("username")
    @classmethod
    def username_clean(cls, v: str) -> str:
        v = v.strip()
        if len(v) < 3:
            raise ValueError("Username must be at least 3 characters.")
        if len(v) > 30:
            raise ValueError("Username must be 30 characters or fewer.")
        if not v.replace("_", "").replace(".", "").isalnum():
            raise ValueError("Username may only contain letters, numbers, _ and .")
        return v.lower()

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters.")
        return v


class SendOTPRequest(BaseModel):
    email: EmailStr
    name: str = ""


class RegisterCreatorRequest(BaseModel):
    """Full creator + user account — submitted after OTP verified client-side."""
    # user auth
    username:   str
    email:      EmailStr
    password:   str
    otp:        str
    # creator profile
    full_name:              str
    display_name:           Optional[str] = None
    phone:                  Optional[str] = None
    instagram_handle:       Optional[str] = None
    tiktok_handle:          Optional[str] = None
    youtube_channel:        Optional[str] = None
    twitter_handle:         Optional[str] = None
    website:                Optional[str] = None
    instagram_followers:    int = 0
    tiktok_followers:       int = 0
    youtube_subscribers:    int = 0
    avg_engagement_rate:    float = 0.0
    avg_views:              int = 0
    bio:                    Optional[str] = None
    niches:                 list[str] = []
    languages:              list[str] = []
    country:                Optional[str] = None
    city:                   Optional[str] = None
    audience_countries:     list[str] = []
    audience_age_range:     Optional[str] = None
    min_rate_usd:           float = 0.0
    open_to_collabs:        bool = True
    preferred_collab_types: list[str] = []


class RegisterBusinessRequest(BaseModel):
    """Business user account — submitted after OTP verified client-side."""
    username:     str
    email:        EmailStr
    password:     str
    otp:          str
    company_name: Optional[str] = None
    website:      Optional[str] = None
    contact_name: Optional[str] = None
    phone:        Optional[str] = None
    country:      Optional[str] = None
    industry:     Optional[str] = None
    budget:       Optional[str] = None
    platforms:    list[str] = []
    goals:        Optional[str] = None


class UpdateMeRequest(BaseModel):
    company_name:      Optional[str]       = None
    website:           Optional[str]       = None
    contact_name:      Optional[str]       = None
    phone:             Optional[str]       = None
    country:           Optional[str]       = None
    industry:          Optional[str]       = None
    budget:            Optional[str]       = None
    platforms:         Optional[list[str]] = None
    goals:             Optional[str]       = None
    # Match Intelligence targeting
    target_city:       Optional[str]       = None   # e.g. "Toronto"
    target_gender:     Optional[str]       = None   # female | male | all
    target_age_range:  Optional[list[str]] = None   # ["18-24","25-34"]
    target_categories: Optional[list[str]] = None   # ["food","fitness"]


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    otp:   str


class ResendOTPRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email:    EmailStr
    password: str


class AuthResponse(BaseModel):
    user_id:      str
    username:     str
    email:        str
    role:         str
    is_verified:  bool
    token:        str | None = None
    creator_id:   str | None = None
    profile_meta: dict | None = None


# ── helpers ───────────────────────────────────────────────────────────────────

def _username_valid(v: str) -> str:
    v = v.strip().lower()
    if len(v) < 2:
        raise ValueError("Username too short.")
    if len(v) > 30:
        raise ValueError("Username must be 30 characters or fewer.")
    return v


# ── endpoints ─────────────────────────────────────────────────────────────────

@router.post("/send-otp", status_code=200)
def send_otp_endpoint(body: SendOTPRequest):
    """Generate an OTP, store in memory, send to email.
    In dev (no SMTP configured) returns dev_otp in the response so the UI can display it."""
    from backend.core import otp_store
    from backend.services.email_service import generate_otp, send_otp
    otp, expires = generate_otp()
    otp_store.save(body.email, otp, expires, body.name)
    email_sent = send_otp(body.email, otp, body.name or body.email.split("@")[0])
    if email_sent:
        return {"message": "OTP sent."}
    # SMTP not configured — return code so frontend can show it
    return {"message": "OTP sent (dev mode — email not configured).", "dev_otp": otp}


@router.post("/register-creator", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_creator(body: RegisterCreatorRequest, db: Session = Depends(get_db)):
    """Verify OTP then atomically create creator profile + user account (already verified)."""
    from backend.core import otp_store
    from backend.schemas.creator import CreatorOnboard
    from backend.services import creator_service
    from backend.services.auth_service import _hash, _make_token

    valid, err = otp_store.verify_and_consume(body.email, body.otp)
    if not valid:
        raise HTTPException(status_code=400, detail=err)

    username = _username_valid(body.username)
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    creator_payload = CreatorOnboard(
        full_name=body.full_name,
        display_name=body.display_name,
        email=body.email,
        phone=body.phone,
        instagram_handle=body.instagram_handle,
        tiktok_handle=body.tiktok_handle,
        youtube_channel=body.youtube_channel,
        twitter_handle=body.twitter_handle,
        website=body.website,
        instagram_followers=body.instagram_followers,
        tiktok_followers=body.tiktok_followers,
        youtube_subscribers=body.youtube_subscribers,
        avg_engagement_rate=body.avg_engagement_rate,
        avg_views=body.avg_views,
        bio=body.bio,
        niches=body.niches,
        languages=body.languages,
        country=body.country or "US",
        city=body.city,
        audience_countries=body.audience_countries,
        audience_age_range=body.audience_age_range,
        min_rate_usd=body.min_rate_usd,
        open_to_collabs=body.open_to_collabs,
        preferred_collab_types=body.preferred_collab_types,
    )
    try:
        creator = creator_service.create_creator(db, creator_payload)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = User(
        username=username,
        email=body.email,
        hashed_password=_hash(body.password),
        role="creator",
        creator_id=creator.id,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_verified=True,
        token=_make_token(user.id, user.role),
        creator_id=creator.id,
    )


@router.post("/register-business", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register_business(body: RegisterBusinessRequest, db: Session = Depends(get_db)):
    """Verify OTP then create business user account (already verified)."""
    from backend.core import otp_store
    from backend.services.auth_service import _hash, _make_token

    valid, err = otp_store.verify_and_consume(body.email, body.otp)
    if not valid:
        raise HTTPException(status_code=400, detail=err)

    username = _username_valid(body.username)
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already taken.")
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(status_code=400, detail="Email already registered.")

    meta = {k: v for k, v in {
        "company_name": body.company_name,
        "website":      body.website,
        "contact_name": body.contact_name,
        "phone":        body.phone,
        "country":      body.country,
        "industry":     body.industry,
        "budget":       body.budget,
        "platforms":    body.platforms or [],
        "goals":        body.goals,
    }.items() if v not in (None, [], "")}

    user = User(
        username=username,
        email=body.email,
        hashed_password=_hash(body.password),
        role="business",
        is_verified=True,
        profile_meta=meta or None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_verified=True,
        token=_make_token(user.id, user.role),
        profile_meta=user.profile_meta,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    """Legacy standalone registration (used by Sign Up page). Sends OTP, requires /verify-otp."""
    try:
        user, _ = auth_service.register(
            db,
            username=body.username,
            email=body.email,
            password=body.password,
            role=body.role,
            creator_id=body.creator_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return AuthResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        creator_id=user.creator_id,
    )


@router.post("/verify-otp", response_model=AuthResponse)
def verify_otp(body: VerifyOTPRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.verify_otp(db, body.email, body.otp)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    from backend.services.auth_service import _make_token
    return AuthResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        token=_make_token(user.id, user.role),
        creator_id=user.creator_id,
    )


@router.post("/resend-otp", status_code=200)
def resend_otp(body: ResendOTPRequest, db: Session = Depends(get_db)):
    try:
        auth_service.resend_otp(db, body.email)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"message": "OTP sent."}


@router.post("/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    try:
        user, token = auth_service.login(db, body.email, body.password)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
    return AuthResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        role=user.role,
        is_verified=user.is_verified,
        token=token,
        creator_id=user.creator_id,
        profile_meta=user.profile_meta,
    )


@router.get("/me", response_model=AuthResponse)
def get_me(authorization: str = fastapi.Header(None), db: Session = Depends(get_db)):
    user_id = _require_auth(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return AuthResponse(
        user_id=user.id, username=user.username, email=user.email,
        role=user.role, is_verified=user.is_verified,
        creator_id=user.creator_id, profile_meta=user.profile_meta,
    )


@router.patch("/me", response_model=AuthResponse)
def update_me(body: UpdateMeRequest, authorization: str = fastapi.Header(None), db: Session = Depends(get_db)):
    user_id = _require_auth(authorization)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    meta = dict(user.profile_meta or {})

    # company_name: only written if not already set (locked after first save)
    if body.company_name is not None and not meta.get("company_name"):
        meta["company_name"] = body.company_name

    for field in ("website", "contact_name", "phone", "country", "industry", "budget", "goals",
                  "target_city", "target_gender"):
        val = getattr(body, field)
        if val is not None:
            meta[field] = val

    if body.platforms is not None:
        meta["platforms"] = body.platforms
    if body.target_age_range is not None:
        meta["target_age_range"] = body.target_age_range
    if body.target_categories is not None:
        meta["target_categories"] = body.target_categories

    user.profile_meta = meta
    db.commit()
    db.refresh(user)
    return AuthResponse(
        user_id=user.id, username=user.username, email=user.email,
        role=user.role, is_verified=user.is_verified,
        creator_id=user.creator_id, profile_meta=user.profile_meta,
    )
