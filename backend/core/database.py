"""
SQLAlchemy setup.

- SQLite is used by default for frictionless dev.
- Switch to Postgres in prod by setting DATABASE_URL in `.env`.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.core.config import settings

connect_args = (
    {"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {}
)

engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db():
    """FastAPI dependency — yields a DB session and guarantees close."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Called on API startup."""
    from backend.models import creator, user, campaign  # noqa: F401
    from backend.models import post, benchmark, neighbourhood  # noqa: F401
    from backend.models import agent_conversation  # noqa: F401
    from backend.models import creator_conversation  # noqa: F401
    from sqlalchemy import inspect, text

    Base.metadata.create_all(bind=engine)

    # Safe column migrations for SQLite (add new columns if absent)
    insp = inspect(engine)

    existing_users = {c["name"] for c in insp.get_columns("users")}
    with engine.begin() as conn:
        if "profile_meta" not in existing_users:
            conn.execute(text("ALTER TABLE users ADD COLUMN profile_meta TEXT"))

    existing_creators = {c["name"] for c in insp.get_columns("creators")}
    with engine.begin() as conn:
        for col, ddl in [
            ("audience_location_data",  "TEXT"),
            ("content_categories",      "TEXT"),
            ("authenticity_score",      "REAL"),
            ("availability_status",     "VARCHAR(20)"),
            ("neighbourhood",           "VARCHAR(120)"),
            ("location_confidence",     "VARCHAR(10)"),
            ("location_sources",        "TEXT"),
            ("location_tags_confirmed", "BOOLEAN DEFAULT 0"),
            ("nlp_location_confirmed",  "BOOLEAN DEFAULT 0"),
        ]:
            if col not in existing_creators:
                conn.execute(text(f"ALTER TABLE creators ADD COLUMN {col} {ddl}"))
