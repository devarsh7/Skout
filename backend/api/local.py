"""Local Market Intelligence — API endpoints.

Full SQL schema (via SQLAlchemy models):
  creators        — extended with neighbourhood, location_confidence, location_sources,
                    location_tags_confirmed, nlp_location_confirmed
  posts           — individual creator posts (platform, format, engagement, city)
  monthly_benchmarks — cached city × category × month aggregates
  neighbourhoods  — city sub-areas with seed data for major cities

Endpoints:
  GET  /local/leaderboard           top creators per city × category × month
  GET  /local/benchmarks            benchmark stats for city × category
  GET  /local/creator-vs-benchmark  compare one creator to local peers
  GET  /local/neighbourhoods        sub-areas with creator counts
  GET  /local/neighbourhood-creators creators in a specific neighbourhood
  GET  /local/cities                cities that have indexed creators
  GET  /local/trending-formats      format engagement breakdown
  POST /local/benchmarks/recalculate  admin / cron — recompute all benchmarks
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services import local_market_service as svc

router = APIRouter(prefix="/local", tags=["local_market"])


# ── 1. Leaderboard ─────────────────────────────────────────────────────────────

@router.get("/leaderboard")
def leaderboard(
    city:       str = Query(..., description="City name, e.g. Toronto"),
    category:   str = Query(..., description="Creator niche, e.g. food"),
    month:      Optional[str] = Query(None, description="YYYY-MM (defaults to current month)"),
    limit:      int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    Top creators in a city × category ranked by engagement rate.
    Each entry includes a SKOUT Location Confidence badge (HIGH / MEDIUM / LOW).
    """
    if not city.strip():
        raise HTTPException(400, "city is required")
    if not category.strip():
        raise HTTPException(400, "category is required")
    return svc.get_leaderboard(db, city.strip(), category.strip(), month, limit)


# ── 2. Benchmarks ──────────────────────────────────────────────────────────────

@router.get("/benchmarks")
def benchmarks(
    city:     str = Query(...),
    category: str = Query(...),
    month:    Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """
    Industry benchmark for city × category:
    avg engagement rate, avg followers, creator count.
    Returns cached MonthlyBenchmark row if available, else live-calculates.
    """
    return svc.get_benchmark(db, city.strip(), category.strip(), month)


# ── 3. Creator vs Benchmark ────────────────────────────────────────────────────

@router.get("/creator-vs-benchmark/{creator_id}")
def creator_vs_benchmark(
    creator_id: str,
    city:       str = Query(...),
    category:   str = Query(...),
    db: Session = Depends(get_db),
):
    """
    Compare a specific creator's engagement to the local average.
    Returns a human-readable message like:
    "6.2% engagement is 2.4x the Toronto Food average of 2.6%"
    """
    result = svc.get_creator_vs_benchmark(db, creator_id, city.strip(), category.strip())
    if "error" in result:
        raise HTTPException(404, result["error"])
    return result


# ── 4. Neighbourhoods ──────────────────────────────────────────────────────────

@router.get("/neighbourhoods")
def neighbourhoods(
    city: str = Query(..., description="City name"),
    db: Session = Depends(get_db),
):
    """
    All sub-areas (neighbourhoods) for a city with creator count badge.
    Only pre-seeded cities return results; creators self-select their neighbourhood.
    """
    return svc.get_neighbourhoods(db, city.strip())


@router.get("/neighbourhood-creators")
def neighbourhood_creators(
    neighbourhood: str = Query(...),
    city:          Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Creators that self-reported a specific neighbourhood, ranked by engagement."""
    return svc.get_creators_in_neighbourhood(db, neighbourhood, city)


# ── 5. Available cities ────────────────────────────────────────────────────────

@router.get("/cities")
def cities(db: Session = Depends(get_db)):
    """Cities that have at least one indexed creator, sorted by creator count."""
    return svc.get_available_cities(db)


# ── 6. Trending Formats ────────────────────────────────────────────────────────

@router.get("/trending-formats")
def trending_formats(
    city:     str = Query(...),
    category: str = Query(...),
    db: Session = Depends(get_db),
):
    """
    Content format breakdown for the last 30 days in city × category.
    Returns data_available=False with reason if posts table is not yet populated.
    """
    return svc.get_trending_formats(db, city.strip(), category.strip())


# ── 7. Benchmark recalculation (admin / cron) ──────────────────────────────────

@router.post("/benchmarks/recalculate", status_code=202)
def recalculate_benchmarks(db: Session = Depends(get_db)):
    """
    Recomputes MonthlyBenchmark rows for all city × category combinations.
    Schedule this endpoint monthly via a cron job or task queue.
    Returns: { month_year, combos_processed, rows_upserted }
    """
    return svc.recalculate_benchmarks(db)
