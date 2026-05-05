"""Location Confidence Score — 4-source triangulation.

Source 1 (self-reported)       → creator has city + country set
Source 2 (audience data)       → audience_location_data contains creator's city
Source 3 (location tags)       → at least one post has location tag (location_tags_confirmed)
Source 4 (caption/hashtag NLP) → NLP processing confirmed the location (nlp_location_confirmed)

Agreement rules:
  ≥ 3 sources agree → HIGH   ✅
  2 sources agree   → MEDIUM 🟡
  ≤ 1 source        → LOW    🟠
"""
from __future__ import annotations

_LEVEL_COLOR = {
    "HIGH":   ("#059669", "#ECFDF5", "#A7F3D0", "✅"),
    "MEDIUM": ("#D97706", "#FFFBEB", "#FDE68A", "🟡"),
    "LOW":    ("#EA580C", "#FFF7ED", "#FED7AA", "🟠"),
}


def calculate_confidence(creator: dict) -> dict:
    """
    Accepts a plain dict (from Creator.to_public_dict() or ORM .to_public_dict()).
    Returns::
        {
            "level":   "HIGH" | "MEDIUM" | "LOW",
            "score":   int (0-4),
            "sources": {
                "self_reported":  bool,
                "audience_data":  bool,
                "location_tags":  bool,
                "nlp":            bool,
            },
        }
    """
    city    = (creator.get("city") or "").strip().lower()
    country = (creator.get("country") or "").strip()

    # Source 1: self-reported — has both city AND country
    s1 = bool(city and country)

    # Source 2: audience data confirms city
    ald = creator.get("audience_location_data") or {}
    s2 = False
    if city and ald:
        for loc_city in ald:
            if loc_city.lower() == city:
                s2 = True
                break

    # Source 3: post location tags (field set by post ingestion pipeline)
    s3 = bool(creator.get("location_tags_confirmed", False))

    # Source 4: caption/hashtag NLP confirmation
    s4 = bool(creator.get("nlp_location_confirmed", False))

    score  = sum([s1, s2, s3, s4])
    level  = "HIGH" if score >= 3 else "MEDIUM" if score >= 2 else "LOW"

    return {
        "level": level,
        "score": score,
        "sources": {
            "self_reported": s1,
            "audience_data": s2,
            "location_tags": s3,
            "nlp":           s4,
        },
    }


def confidence_badge_html(level: str) -> str:
    """Returns an inline HTML badge for the confidence level."""
    color, bg, border, icon = _LEVEL_COLOR.get(level, _LEVEL_COLOR["LOW"])
    return (
        f'<span style="display:inline-flex;align-items:center;gap:4px;'
        f'background:{bg};border:1.5px solid {border};border-radius:999px;'
        f'padding:2px 9px;font-size:11px;font-weight:700;color:{color}">'
        f'{icon} {level}</span>'
    )


def update_creator_confidence(db, creator_orm) -> None:
    """Recalculate and persist location_confidence + location_sources on an ORM object."""
    result = calculate_confidence(creator_orm.to_public_dict())
    creator_orm.location_confidence = result["level"]
    creator_orm.location_sources    = result["sources"]
