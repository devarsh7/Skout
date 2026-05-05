"""Auth business logic — register, verify OTP, login, token."""
from __future__ import annotations

from datetime import datetime, timedelta

import bcrypt as _bcrypt
from jose import jwt
from sqlalchemy.orm import Session

from backend.core.config import settings
from backend.models.user import User
from backend.services.email_service import generate_otp, send_otp

_SECRET  = settings.secret_key
_ALG     = "HS256"
_EXPIRES = settings.access_token_expire_minutes


# ── helpers ───────────────────────────────────────────────────────────────────

def _hash(pw: str) -> str:
    return _bcrypt.hashpw(pw.encode(), _bcrypt.gensalt(rounds=12)).decode()

def _verify(plain: str, hashed: str) -> bool:
    try:
        return _bcrypt.checkpw(plain.encode(), hashed.encode())
    except Exception:
        return False

def _make_token(user_id: str, role: str) -> str:
    exp = datetime.utcnow() + timedelta(minutes=_EXPIRES)
    return jwt.encode({"sub": user_id, "role": role, "exp": exp}, _SECRET, algorithm=_ALG)

def decode_token(token: str) -> dict:
    return jwt.decode(token, _SECRET, algorithms=[_ALG])


# ── registration ──────────────────────────────────────────────────────────────

def register(
    db: Session,
    username: str,
    email: str,
    password: str,
    role: str = "creator",
    creator_id: str | None = None,
) -> tuple[User, str]:
    """
    Create user, send OTP, return (user, otp_code).
    Raises ValueError on duplicate username/email.
    """
    if db.query(User).filter(User.username == username).first():
        raise ValueError("Username already taken.")
    if db.query(User).filter(User.email == email).first():
        raise ValueError("Email already registered.")

    otp, expires = generate_otp()
    user = User(
        username        = username,
        email           = email,
        hashed_password = _hash(password),
        role            = role,
        creator_id      = creator_id,
        otp_code        = otp,
        otp_expires_at  = expires,
        is_verified     = False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    send_otp(email, otp, username)
    return user, otp


# ── OTP verification ──────────────────────────────────────────────────────────

def verify_otp(db: Session, email: str, otp: str) -> User:
    """Mark user verified. Raises ValueError on bad/expired OTP."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Account not found.")
    if user.is_verified:
        return user
    if not user.otp_code or user.otp_code != otp:
        raise ValueError("Invalid OTP.")
    if user.otp_expires_at and datetime.utcnow() > user.otp_expires_at:
        raise ValueError("OTP has expired. Request a new one.")
    user.is_verified   = True
    user.otp_code      = None
    user.otp_expires_at = None
    db.commit()
    db.refresh(user)
    return user


def resend_otp(db: Session, email: str) -> None:
    """Regenerate and resend OTP for an unverified account."""
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise ValueError("Account not found.")
    if user.is_verified:
        raise ValueError("Account is already verified.")
    otp, expires = generate_otp()
    user.otp_code      = otp
    user.otp_expires_at = expires
    db.commit()
    send_otp(email, otp, user.username)


# ── login ─────────────────────────────────────────────────────────────────────

def login(db: Session, email: str, password: str) -> tuple[User, str]:
    """Authenticate and return (user, jwt_token). Raises ValueError on failure."""
    user = db.query(User).filter(User.email == email).first()
    if not user or not _verify(password, user.hashed_password):
        raise ValueError("Invalid email or password.")
    if not user.is_verified:
        raise ValueError("Please verify your email first.")
    user.last_login = datetime.utcnow()
    db.commit()
    return user, _make_token(user.id, user.role)
