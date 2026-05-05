"""SKOUT Match Score — 5-dimension creator × SMB compatibility scoring.

Works with plain dicts (API payloads) so it runs in both the Streamlit
frontend and the FastAPI backend without any ORM dependency.
"""
from __future__ import annotations

_WEIGHTS = {
    "location":     0.30,
    "niche":        0.25,
    "demographics": 0.20,
    "engagement":   0.15,
    "availability": 0.10,
}

# Industry → relevant content niches (for SMBs that haven't set target_categories)
_INDUSTRY_NICHES: dict[str, list[str]] = {
    "Beauty & Personal Care":   ["beauty", "lifestyle", "fashion"],
    "Fashion & Apparel":        ["fashion", "lifestyle", "art"],
    "Food & Beverage":          ["food", "lifestyle"],
    "Technology & Software":    ["tech", "gaming", "education"],
    "Travel & Hospitality":     ["travel", "lifestyle", "food"],
    "Health & Wellness":        ["fitness", "lifestyle", "food"],
    "Finance & Fintech":        ["finance", "business", "education"],
    "Gaming & Entertainment":   ["gaming", "tech", "music"],
    "Education":                ["education", "books", "business"],
    "Other":                    [],
}


def calculate_match_score(smb_meta: dict, creator: dict) -> dict:
    """
    Parameters
    ----------
    smb_meta : dict
        Business user's profile_meta (from User.profile_meta).
        Keys used: target_city, city, country, target_categories, industry,
                   target_gender, target_age_range.
    creator : dict
        Creator dict from the API (to_public_dict output or full creator record).
        Keys used: country, city, audience_location_data, niches,
                   content_categories, audience_gender_split, audience_age_range,
                   avg_engagement_rate, authenticity_score,
                   availability_status, open_to_collabs.

    Returns
    -------
    dict with keys:
        total (float 0-100)
        breakdown (dict of dimension → {score, weight, label, detail})
    """

    # ── 1. Location Match (30%) ──────────────────────────────────────────────
    smb_city    = (smb_meta.get("target_city") or smb_meta.get("city") or "").lower().strip()
    smb_country = (smb_meta.get("country") or "").upper()
    c_city      = (creator.get("city") or "").lower().strip()
    c_country   = (creator.get("country") or "").upper()

    location_score = 0.0
    location_detail = "No location data"

    # Source A: audience_location_data gives city-level % (most precise)
    ald: dict = creator.get("audience_location_data") or {}
    if smb_city and ald:
        for city, pct in ald.items():
            if city.lower() == smb_city:
                location_score  = min(float(pct), 100.0)
                location_detail = f"{pct:.0f}% audience in {smb_city.title()}"
                break

    # Source B: creator.city field — direct city name match
    if location_score == 0 and smb_city and c_city:
        if c_city == smb_city:
            location_score  = 85.0
            location_detail = f"Creator is based in {smb_city.title()}"
        elif smb_country and c_country and c_country == smb_country:
            location_score  = 35.0
            location_detail = f"Same country, different city ({c_country})"
        elif c_country:
            location_score  = 10.0
            location_detail = f"Different region ({c_country})"
    elif location_score == 0:
        # No target city set — fall back to country
        if smb_country and c_country and c_country == smb_country:
            location_score  = 50.0
            location_detail = f"Same country ({c_country})"
        elif c_country:
            location_score  = 15.0
            location_detail = f"Different region ({c_country})"

    # ── 2. Niche Match (25%) ─────────────────────────────────────────────────
    smb_cats: list[str] = [c.lower() for c in (smb_meta.get("target_categories") or [])]
    if not smb_cats:
        industry = smb_meta.get("industry", "")
        smb_cats = _INDUSTRY_NICHES.get(industry, [])

    content_cats: dict = creator.get("content_categories") or {}
    creator_niches: list[str] = [n.lower() for n in (creator.get("niches") or [])]

    niche_score  = 0.0
    niche_detail = "No category data"

    if smb_cats:
        if content_cats:
            # Precise: sum % of creator's content in matching categories
            for cat in smb_cats:
                niche_score += float(content_cats.get(cat, 0))
            niche_score  = min(niche_score, 100.0)
            matches      = [c for c in smb_cats if content_cats.get(c, 0) > 0]
            niche_detail = f"{len(matches)}/{len(smb_cats)} categories matched"
        elif creator_niches:
            matched = [n for n in creator_niches if n in smb_cats]
            if matched:
                # How much of target is covered (primary signal)
                target_coverage = len(matched) / max(len(smb_cats), 1)
                # How focused the creator is on target niches (secondary signal)
                creator_focus   = len(matched) / max(len(creator_niches), 1)
                # Blend: 65% target coverage + 35% creator focus
                niche_score  = min((target_coverage * 0.65 + creator_focus * 0.35) * 100, 100.0)
                niche_detail = f"{len(matched)} of {len(creator_niches)} creator niches match"
            else:
                niche_score  = 0.0
                niche_detail = "No matching niches"
    elif creator_niches:
        niche_score  = 45.0
        niche_detail = "No target set — partial credit"

    # ── 3. Audience Demographics (20%) ──────────────────────────────────────
    target_gender = (smb_meta.get("target_gender") or "all").lower()
    target_ages: list[str] = smb_meta.get("target_age_range") or []
    gender_split: dict = creator.get("audience_gender_split") or {}

    # Gender score
    if target_gender in ("female", "f", "women"):
        g_val = gender_split.get("f") or gender_split.get("female")
        gender_score = float(g_val) * 100 if g_val is not None else 50.0
    elif target_gender in ("male", "m", "men"):
        g_val = gender_split.get("m") or gender_split.get("male")
        gender_score = float(g_val) * 100 if g_val is not None else 50.0
    else:
        gender_score = 80.0  # no preference

    # Age score
    creator_age = creator.get("audience_age_range") or ""
    if target_ages and creator_age:
        age_score = 100.0 if creator_age in target_ages else 30.0
    else:
        age_score = 75.0  # no data — neutral

    demographics_score  = (gender_score + age_score) / 2
    demographics_detail = f"Gender {gender_score:.0f}% · Age {age_score:.0f}%"

    # ── 4. Engagement Quality (15%) ──────────────────────────────────────────
    authenticity = creator.get("authenticity_score")
    if authenticity is not None:
        engagement_score  = float(authenticity)
        engagement_detail = f"Authenticity score: {authenticity:.0f}"
    else:
        eng = float(creator.get("avg_engagement_rate") or 0)
        if   eng >= 0.08: engagement_score = 95
        elif eng >= 0.05: engagement_score = 80
        elif eng >= 0.03: engagement_score = 62
        elif eng >= 0.01: engagement_score = 42
        else:             engagement_score = 22
        engagement_detail = f"Engagement rate: {eng:.1%}"

    # ── 5. Availability (10%) ────────────────────────────────────────────────
    status = creator.get("availability_status")
    if status == "available":
        availability_score, availability_detail = 100.0, "Available for collabs"
    elif status == "busy":
        availability_score, availability_detail = 0.0, "Currently busy"
    elif status == "inactive":
        availability_score, availability_detail = 20.0, "Inactive"
    elif creator.get("open_to_collabs", True):
        availability_score, availability_detail = 90.0, "Open to collabs"
    else:
        availability_score, availability_detail = 15.0, "Not accepting collabs"

    # ── Weighted total ───────────────────────────────────────────────────────
    total = (
        location_score     * _WEIGHTS["location"]     +
        niche_score        * _WEIGHTS["niche"]        +
        demographics_score * _WEIGHTS["demographics"] +
        engagement_score   * _WEIGHTS["engagement"]   +
        availability_score * _WEIGHTS["availability"]
    )

    return {
        "total": round(total, 1),
        "breakdown": {
            "location":     {"score": round(location_score, 1),     "weight": 30, "label": "Location Match",     "detail": location_detail},
            "niche":        {"score": round(niche_score, 1),        "weight": 25, "label": "Niche Fit",          "detail": niche_detail},
            "demographics": {"score": round(demographics_score, 1), "weight": 20, "label": "Demographics",       "detail": demographics_detail},
            "engagement":   {"score": round(engagement_score, 1),   "weight": 15, "label": "Engagement Quality", "detail": engagement_detail},
            "availability": {"score": round(availability_score, 1), "weight": 10, "label": "Availability",       "detail": availability_detail},
        },
    }


def score_color(total: float) -> tuple[str, str, str]:
    """Returns (text_color, bg_color, ring_color) based on score."""
    if total >= 70:
        return "#059669", "#ECFDF5", "#A7F3D0"
    if total >= 40:
        return "#D97706", "#FFFBEB", "#FDE68A"
    return "#DC2626", "#FEF2F2", "#FECACA"


def score_label(total: float) -> str:
    if total >= 70: return "Strong"
    if total >= 40: return "Moderate"
    return "Weak"
