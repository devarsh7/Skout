"""
Scheduled Instagram maintenance.

Long-lived tokens last 60 days and can be refreshed any time after they're
24h old. We refresh any token entering its final 10 days, daily, so a creator
who connected once stays connected indefinitely (as long as they don't revoke
access and the job runs at least once every ~50 days).

Wired into the FastAPI lifespan via APScheduler (see backend/main.py).
Note: with multiple workers/instances, run the scheduler in only one process.
"""
from __future__ import annotations

from datetime import datetime, timedelta

from loguru import logger

from backend.core.database import SessionLocal
from backend.models.creator import Creator
from backend.services.instagram import refresh_long_lived_token

REFRESH_WINDOW_DAYS = 10  # refresh tokens expiring within this many days


def refresh_expiring_tokens() -> dict:
    """Refresh all Instagram tokens expiring within REFRESH_WINDOW_DAYS."""
    db = SessionLocal()
    refreshed, failed, skipped = 0, 0, 0
    try:
        cutoff = datetime.utcnow() + timedelta(days=REFRESH_WINDOW_DAYS)
        creators = (
            db.query(Creator)
            .filter(
                Creator.instagram_access_token.isnot(None),
                Creator.instagram_token_expires_at.isnot(None),
                Creator.instagram_token_expires_at <= cutoff,
            )
            .all()
        )
        for creator in creators:
            # Already expired → can't refresh; creator must reconnect
            if creator.instagram_token_expires_at < datetime.utcnow():
                skipped += 1
                continue
            result = refresh_long_lived_token(creator.instagram_access_token)
            if result and result.get("access_token"):
                creator.instagram_access_token = result["access_token"]
                creator.instagram_token_expires_at = datetime.utcnow() + timedelta(
                    seconds=result.get("expires_in", 5184000)
                )
                refreshed += 1
            else:
                failed += 1
                logger.warning(f"Instagram token refresh failed for creator {creator.id}")
        db.commit()
    except Exception as exc:
        logger.error(f"Instagram token refresh job error: {exc}")
        db.rollback()
    finally:
        db.close()

    summary = {"refreshed": refreshed, "failed": failed, "expired_skipped": skipped}
    logger.info(f"Instagram token refresh job: {summary}")
    return summary
