"""In-memory pre-registration OTP store — zero DB writes until OTP verified."""
from __future__ import annotations

import threading
from datetime import datetime

_store: dict[str, dict] = {}
_lock = threading.Lock()


def save(email: str, otp: str, expires: datetime, name: str = "") -> None:
    with _lock:
        _store[email.lower()] = {"otp": otp, "expires": expires, "name": name}


def verify_and_consume(email: str, otp: str) -> tuple[bool, str]:
    """Validate OTP and remove it. Returns (ok, error_message)."""
    key = email.lower()
    with _lock:
        entry = _store.get(key)
        if not entry:
            return False, "No pending verification for this email. Request a new code."
        if datetime.utcnow() > entry["expires"]:
            del _store[key]
            return False, "OTP has expired. Request a new code."
        if entry["otp"] != otp:
            return False, "Invalid code. Check and try again."
        del _store[key]
        return True, ""


def has_pending(email: str) -> bool:
    with _lock:
        return email.lower() in _store
