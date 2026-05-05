"""
Seed a handful of demo creators so you can exercise Discovery & Filtering
without having to hand-type a form each time.

Usage:
    python scripts/seed_demo_creators.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Ensure project root is on PYTHONPATH when run as a script
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from loguru import logger

from backend.core.database import SessionLocal, init_db
from backend.schemas.creator import CreatorOnboard
from backend.services.creator_service import create_creator

SEED_FILE = Path(__file__).resolve().parent.parent / "data" / "seed_creators.json"


def main() -> None:
    init_db()
    payloads = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    db = SessionLocal()
    inserted, skipped = 0, 0
    try:
        for p in payloads:
            try:
                dto = CreatorOnboard(**p)
                create_creator(db, dto)
                inserted += 1
                logger.info(f"✅ {p['display_name']}")
            except ValueError as e:
                skipped += 1
                logger.warning(f"⏭️  {p['display_name']}: {e}")
    finally:
        db.close()
    logger.info(f"Done. Inserted={inserted}, skipped={skipped}")


if __name__ == "__main__":
    main()
