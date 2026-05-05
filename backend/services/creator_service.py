"""
Creator service — the only place that reads/writes the Creator ORM AND
keeps Pinecone in sync. Agents and API routers call this, not the ORM directly.
"""
from __future__ import annotations

from loguru import logger
from sqlalchemy.orm import Session

from backend.models.creator import Creator
from backend.schemas.creator import CreatorOnboard, CreatorUpdate
from backend.services.vector_store import get_vector_store


def _vector_metadata(c: Creator) -> dict:
    """Non-PII payload for Pinecone filters."""
    platforms = []
    if c.instagram_handle:
        platforms.append("instagram")
    if c.tiktok_handle:
        platforms.append("tiktok")
    if c.youtube_channel:
        platforms.append("youtube")
    if c.facebook_page:
        platforms.append("facebook")
    if c.twitter_handle:
        platforms.append("twitter")

    return {
        "country": c.country or "",
        "city": c.city or "",
        "niches": c.niches or [],
        "languages": c.languages or [],
        "total_followers": c.total_followers,
        "avg_engagement_rate": float(c.avg_engagement_rate or 0),
        "platforms": platforms,
        "is_verified": bool(c.is_verified),
        "open_to_collabs": bool(c.open_to_collabs),
        "audience_countries": c.audience_countries or [],
    }


def create_creator(db: Session, payload: CreatorOnboard) -> Creator:
    if not payload.has_at_least_one_handle():
        raise ValueError("At least one social handle is required.")

    existing = db.query(Creator).filter(Creator.email == payload.email).one_or_none()
    if existing:
        raise ValueError(f"Creator with email {payload.email} already exists.")

    creator = Creator(
        full_name=payload.full_name,
        display_name=payload.display_name,
        email=payload.email,
        phone=payload.phone,
        instagram_handle=payload.instagram_handle,
        tiktok_handle=payload.tiktok_handle,
        youtube_channel=payload.youtube_channel,
        facebook_page=payload.facebook_page,
        twitter_handle=payload.twitter_handle,
        website=payload.website,
        instagram_followers=payload.instagram_followers,
        tiktok_followers=payload.tiktok_followers,
        youtube_subscribers=payload.youtube_subscribers,
        total_followers=payload.total_followers(),
        avg_engagement_rate=payload.avg_engagement_rate,
        avg_views=payload.avg_views,
        bio=payload.bio,
        niches=payload.niches,
        languages=payload.languages,
        country=payload.country,
        city=payload.city,
        audience_countries=payload.audience_countries,
        audience_age_range=payload.audience_age_range,
        audience_gender_split=payload.audience_gender_split,
        min_rate_usd=payload.min_rate_usd,
        open_to_collabs=payload.open_to_collabs,
        preferred_collab_types=payload.preferred_collab_types,
    )
    db.add(creator)
    db.commit()
    db.refresh(creator)

    # Sync to vector DB (fire-and-forget — skip if Pinecone not configured)
    try:
        vs = get_vector_store()
        if vs is not None:
            vs.upsert_creator(
                creator_id=creator.id,
                text=creator.embedding_text(),
                metadata=_vector_metadata(creator),
            )
            creator.vector_indexed = True
            db.commit()
    except Exception as e:  # noqa: BLE001
        logger.error(f"Pinecone upsert failed for {creator.id}: {e}")

    return creator


def update_creator(db: Session, creator: Creator, payload: CreatorUpdate) -> Creator:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(creator, field, value)

    ig = creator.instagram_followers or 0
    tt = creator.tiktok_followers or 0
    yt = creator.youtube_subscribers or 0
    creator.total_followers = ig + tt + yt

    db.commit()
    db.refresh(creator)

    try:
        vs = get_vector_store()
        if vs is not None:
            vs.upsert_creator(
                creator_id=creator.id,
                text=creator.embedding_text(),
                metadata=_vector_metadata(creator),
            )
    except Exception as e:  # noqa: BLE001
        logger.error(f"Pinecone re-sync failed for {creator.id}: {e}")

    return creator


def reindex_all(db: Session) -> int:
    """Re-build the entire Pinecone index from the relational DB."""
    vs = get_vector_store()
    creators = db.query(Creator).all()
    items = [(c.id, c.embedding_text(), _vector_metadata(c)) for c in creators]
    n = vs.upsert_many(items)
    for c in creators:
        c.vector_indexed = True
    db.commit()
    return n


def get_by_id(db: Session, creator_id: str) -> Creator | None:
    return db.query(Creator).filter(Creator.id == creator_id).one_or_none()


def get_many(db: Session, ids: list[str]) -> list[Creator]:
    if not ids:
        return []
    return db.query(Creator).filter(Creator.id.in_(ids)).all()
