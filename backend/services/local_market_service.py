"""Local Market Intelligence — service layer.

Provides:
  • Local Creator Leaderboard     (top N creators per city × category × month)
  • Industry Benchmark            (avg engagement / followers for a city × category)
  • Creator vs Benchmark          (how a specific creator compares to local peers)
  • Neighbourhood counts          (creators per sub-area in a city)
  • Trending Formats              (Reel / Carousel / Static / Story by engagement)
  • Benchmark recalculation       (populates monthly_benchmarks table)
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.models.benchmark import MonthlyBenchmark
from backend.models.creator import Creator
from backend.models.neighbourhood import Neighbourhood
from backend.models.post import Post
from backend.services.location_confidence import calculate_confidence


# ── helpers ────────────────────────────────────────────────────────────────────

def _current_month() -> str:
    return datetime.utcnow().strftime("%Y-%m")


def _creators_in_city(db: Session, city: str) -> list[Creator]:
    """All creators whose city matches (case-insensitive)."""
    return (
        db.query(Creator)
        .filter(func.lower(Creator.city) == city.lower())
        .all()
    )


def _creators_in_city_and_category(db: Session, city: str, category: str) -> list[Creator]:
    all_in_city = _creators_in_city(db, city)
    cat = category.lower()
    return [c for c in all_in_city if cat in [n.lower() for n in (c.niches or [])]]


# ── 1. Leaderboard ─────────────────────────────────────────────────────────────

def get_leaderboard(
    db: Session,
    city: str,
    category: str,
    month_year: Optional[str] = None,
    limit: int = 10,
) -> list[dict]:
    """
    Top `limit` creators in city × category ranked by avg_engagement_rate.
    month_year is accepted but currently used for labelling only — per-month
    engagement data requires the posts table to be populated.
    """
    if not month_year:
        month_year = _current_month()

    creators = _creators_in_city_and_category(db, city, category)
    creators.sort(key=lambda c: c.avg_engagement_rate or 0, reverse=True)

    result = []
    for rank, c in enumerate(creators[:limit], 1):
        pub = c.to_public_dict()
        conf = calculate_confidence(pub)
        result.append({
            "rank":                rank,
            "creator_id":          c.id,
            "display_name":        c.display_name or c.full_name,
            "instagram_handle":    c.instagram_handle,
            "tiktok_handle":       c.tiktok_handle,
            "total_followers":     c.total_followers,
            "avg_engagement_rate": c.avg_engagement_rate,
            "city":                c.city,
            "country":             c.country,
            "neighbourhood":       c.neighbourhood,
            "niches":              c.niches or [],
            "open_to_collabs":     c.open_to_collabs,
            "month_year":          month_year,
            "location_confidence": conf["level"],
            "location_sources":    conf["sources"],
        })
    return result


# ── 2. Industry Benchmark ──────────────────────────────────────────────────────

def get_benchmark(
    db: Session,
    city: str,
    category: str,
    month_year: Optional[str] = None,
) -> dict:
    """
    Live-calculated benchmark for city × category.
    Also checks for a stored MonthlyBenchmark first (faster).
    """
    if not month_year:
        month_year = _current_month()

    # Try cached first
    stored = (
        db.query(MonthlyBenchmark)
        .filter(
            func.lower(MonthlyBenchmark.city) == city.lower(),
            func.lower(MonthlyBenchmark.category) == category.lower(),
            MonthlyBenchmark.month_year == month_year,
        )
        .first()
    )
    if stored:
        return stored.to_dict()

    # Live calculation from creators
    creators = _creators_in_city_and_category(db, city, category)
    n = len(creators)
    if n == 0:
        return {
            "city": city, "category": category, "month_year": month_year,
            "creator_count": 0,
            "avg_engagement_rate": 0.0,
            "avg_followers": 0.0,
            "avg_posts_per_week": None,
            "cached": False,
        }

    avg_eng = sum(c.avg_engagement_rate or 0 for c in creators) / n
    avg_fol = sum(c.total_followers or 0 for c in creators) / n

    return {
        "city":                 city,
        "category":             category,
        "month_year":           month_year,
        "creator_count":        n,
        "avg_engagement_rate":  round(avg_eng, 4),
        "avg_followers":        round(avg_fol, 0),
        "avg_posts_per_week":   None,   # requires posts table data
        "cached":               False,
    }


# ── 3. Creator vs Benchmark ────────────────────────────────────────────────────

def get_creator_vs_benchmark(
    db: Session,
    creator_id: str,
    city: str,
    category: str,
) -> dict:
    """
    Returns benchmark + creator stats + ratio string.
    e.g. "6.2% engagement is 2.4x the Toronto Food average of 2.6%"
    """
    creator = db.query(Creator).filter(Creator.id == creator_id).first()
    if not creator:
        return {"error": "Creator not found"}

    benchmark = get_benchmark(db, city, category)
    avg_eng   = benchmark.get("avg_engagement_rate", 0)
    c_eng     = creator.avg_engagement_rate or 0

    if avg_eng > 0:
        ratio = round(c_eng / avg_eng, 1)
        direction = "above" if c_eng >= avg_eng else "below"
        message = (
            f"This creator's {c_eng:.1%} engagement is {ratio}x the "
            f"{city} {category.title()} average of {avg_eng:.1%}"
        )
    else:
        ratio = None
        direction = None
        message = f"No benchmark data for {city} × {category}"

    return {
        "creator_id":          creator_id,
        "creator_name":        creator.display_name or creator.full_name,
        "creator_engagement":  c_eng,
        "creator_followers":   creator.total_followers,
        "benchmark":           benchmark,
        "ratio":               ratio,
        "direction":           direction,
        "message":             message,
    }


# ── 4. Neighbourhoods ──────────────────────────────────────────────────────────

def get_neighbourhoods(db: Session, city: str) -> list[dict]:
    """
    All neighbourhoods for a city with creator count per neighbourhood.
    """
    hoods = (
        db.query(Neighbourhood)
        .filter(func.lower(Neighbourhood.city) == city.lower())
        .order_by(Neighbourhood.name)
        .all()
    )
    result = []
    for h in hoods:
        count = (
            db.query(Creator)
            .filter(func.lower(Creator.neighbourhood) == h.name.lower())
            .count()
        )
        d = h.to_dict()
        d["creator_count"] = count
        result.append(d)
    return result


def get_creators_in_neighbourhood(
    db: Session,
    neighbourhood: str,
    city: Optional[str] = None,
) -> list[dict]:
    """Creators that self-reported this neighbourhood."""
    q = db.query(Creator).filter(
        func.lower(Creator.neighbourhood) == neighbourhood.lower()
    )
    if city:
        q = q.filter(func.lower(Creator.city) == city.lower())
    creators = q.order_by(Creator.avg_engagement_rate.desc()).all()
    return [c.to_public_dict() for c in creators]


def get_available_cities(db: Session) -> list[dict]:
    """Cities that have at least one creator, sorted by creator count."""
    rows = (
        db.query(Creator.city, Creator.country, func.count(Creator.id).label("count"))
        .filter(Creator.city.isnot(None))
        .group_by(Creator.city, Creator.country)
        .order_by(func.count(Creator.id).desc())
        .all()
    )
    return [{"city": r.city, "country": r.country, "creator_count": r.count} for r in rows]


# ── 5. Trending Formats ────────────────────────────────────────────────────────

def get_trending_formats(db: Session, city: str, category: str) -> dict:
    """
    Engagement by content format (Reel / Carousel / Static / Story) for the
    last 30 days in city × category.  Requires posts table data.
    """
    from datetime import timedelta
    cutoff = datetime.utcnow() - timedelta(days=30)

    # Get creator IDs for city × category
    creators = _creators_in_city_and_category(db, city, category)
    creator_ids = [c.id for c in creators]

    if not creator_ids:
        return {
            "city": city, "category": category, "data_available": False,
            "reason": f"No creators indexed for {city} × {category}",
            "formats": [],
        }

    posts = (
        db.query(Post)
        .filter(
            Post.creator_id.in_(creator_ids),
            Post.format.isnot(None),
            Post.posted_at >= cutoff,
        )
        .all()
    )

    if len(posts) < 5:
        return {
            "city": city, "category": category, "data_available": False,
            "reason": f"Not enough post data yet ({len(posts)} posts, minimum 5 required)",
            "formats": [],
            "posts_tracked": len(posts),
            "creators_in_area": len(creator_ids),
        }

    # Aggregate by format
    by_format: dict[str, list[float]] = defaultdict(list)
    for p in posts:
        by_format[p.format].append(p.engagement_rate)

    formats = sorted(
        [
            {
                "format":          fmt,
                "avg_engagement":  round(sum(rates) / len(rates), 4),
                "post_count":      len(rates),
            }
            for fmt, rates in by_format.items()
        ],
        key=lambda x: x["avg_engagement"],
        reverse=True,
    )

    result: dict = {
        "city": city, "category": category,
        "data_available": True,
        "formats": formats,
        "posts_tracked": len(posts),
    }

    if len(formats) >= 2:
        top    = formats[0]
        second = formats[1]
        ratio  = top["avg_engagement"] / max(second["avg_engagement"], 0.0001)
        result["top_format"]       = top["format"]
        result["second_format"]    = second["format"]
        result["top_vs_second"]    = round(ratio, 1)
        result["headline"]         = (
            f'{top["format"]}s are getting {ratio:.1f}x more engagement '
            f'than {second["format"]}s for {city} {category.title()} creators this month'
        )

    return result


# ── 6. Benchmark recalculation (cron target) ───────────────────────────────────

def recalculate_benchmarks(db: Session) -> dict:
    """
    Recompute MonthlyBenchmark rows for all city × category combos with creators.
    Called by POST /local/benchmarks/recalculate — schedule monthly.
    """
    month_year = _current_month()
    combos: set[tuple[str, str]] = set()

    for c in db.query(Creator).filter(Creator.city.isnot(None)).all():
        for niche in c.niches or []:
            combos.add((c.city.lower(), niche.lower()))

    upserted = 0
    for city_lower, category_lower in combos:
        creators = _creators_in_city_and_category(db, city_lower, category_lower)
        n = len(creators)
        if n == 0:
            continue

        avg_eng = sum(c.avg_engagement_rate or 0 for c in creators) / n
        avg_fol = sum(c.total_followers or 0 for c in creators) / n

        # Format-level averages from posts (may be empty)
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=30)
        ids = [c.id for c in creators]
        posts = (
            db.query(Post)
            .filter(Post.creator_id.in_(ids), Post.format.isnot(None), Post.posted_at >= cutoff)
            .all()
        ) if ids else []

        by_fmt: dict[str, list[float]] = defaultdict(list)
        for p in posts:
            by_fmt[p.format].append(p.engagement_rate)

        def _avg(key: str):
            return round(sum(by_fmt[key]) / len(by_fmt[key]), 4) if by_fmt.get(key) else None

        reel_avg   = _avg("Reel")
        car_avg    = _avg("Carousel")
        stat_avg   = _avg("Static")
        story_avg  = _avg("Story")

        # Top format
        fmt_avgs = {k: v for k, v in {
            "Reel": reel_avg, "Carousel": car_avg,
            "Static": stat_avg, "Story": story_avg,
        }.items() if v is not None}
        top_fmt  = max(fmt_avgs, key=lambda k: fmt_avgs[k]) if fmt_avgs else None
        top_mult = None
        if top_fmt and len(fmt_avgs) >= 2:
            sorted_vals = sorted(fmt_avgs.values(), reverse=True)
            top_mult = round(sorted_vals[0] / max(sorted_vals[1], 0.0001), 1)

        # Upsert
        existing = (
            db.query(MonthlyBenchmark)
            .filter(
                func.lower(MonthlyBenchmark.city) == city_lower,
                func.lower(MonthlyBenchmark.category) == category_lower,
                MonthlyBenchmark.month_year == month_year,
            )
            .first()
        )
        if existing:
            row = existing
        else:
            row = MonthlyBenchmark(city=city_lower, category=category_lower, month_year=month_year)
            db.add(row)

        row.avg_engagement_rate      = round(avg_eng, 4)
        row.avg_followers            = round(avg_fol, 0)
        row.creator_count            = n
        row.avg_reel_engagement      = reel_avg
        row.avg_carousel_engagement  = car_avg
        row.avg_static_engagement    = stat_avg
        row.avg_story_engagement     = story_avg
        row.top_format               = top_fmt
        row.top_format_multiplier    = top_mult
        row.calculated_at            = datetime.utcnow()
        upserted += 1

    db.commit()
    return {"month_year": month_year, "combos_processed": len(combos), "rows_upserted": upserted}
