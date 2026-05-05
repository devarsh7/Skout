"""Neighbourhood ORM — sub-city areas for hyperlocal creator filtering.

Pre-seeded for major cities. Creators self-select their neighbourhood on
profile setup. SMBs filter by neighbourhood with creator count badges.
"""
from __future__ import annotations

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from backend.core.database import Base


class Neighbourhood(Base):
    __tablename__ = "neighbourhoods"
    __table_args__ = (
        UniqueConstraint("city", "name", name="uq_neighbourhood_city_name"),
    )

    id:      Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city:    Mapped[str] = mapped_column(String(120), index=True, nullable=False)
    country: Mapped[str] = mapped_column(String(2),  nullable=False)
    name:    Mapped[str] = mapped_column(String(120), index=True, nullable=False)

    def to_dict(self) -> dict:
        return {"id": self.id, "city": self.city, "country": self.country, "name": self.name}


# ── Seed data ──────────────────────────────────────────────────────────────────
NEIGHBOURHOOD_SEEDS: list[tuple[str, str, str]] = [
    # (city, country, name)
    ("Toronto",       "CA", "Kensington Market"),
    ("Toronto",       "CA", "Yorkville"),
    ("Toronto",       "CA", "The Annex"),
    ("Toronto",       "CA", "Queen West"),
    ("Toronto",       "CA", "Distillery District"),
    ("Toronto",       "CA", "Leslieville"),
    ("Toronto",       "CA", "Little Italy"),
    ("Toronto",       "CA", "Roncesvalles"),
    ("Toronto",       "CA", "Beaches"),
    ("Toronto",       "CA", "King West"),

    ("New York",      "US", "SoHo"),
    ("New York",      "US", "Williamsburg"),
    ("New York",      "US", "East Village"),
    ("New York",      "US", "Upper West Side"),
    ("New York",      "US", "DUMBO"),
    ("New York",      "US", "Astoria"),
    ("New York",      "US", "Park Slope"),
    ("New York",      "US", "Harlem"),
    ("New York",      "US", "Lower East Side"),
    ("New York",      "US", "Tribeca"),

    ("Los Angeles",   "US", "Venice Beach"),
    ("Los Angeles",   "US", "Silver Lake"),
    ("Los Angeles",   "US", "West Hollywood"),
    ("Los Angeles",   "US", "Echo Park"),
    ("Los Angeles",   "US", "Santa Monica"),
    ("Los Angeles",   "US", "Koreatown"),
    ("Los Angeles",   "US", "Studio City"),
    ("Los Angeles",   "US", "Culver City"),

    ("London",        "GB", "Shoreditch"),
    ("London",        "GB", "Notting Hill"),
    ("London",        "GB", "Camden"),
    ("London",        "GB", "Brixton"),
    ("London",        "GB", "Mayfair"),
    ("London",        "GB", "Hackney"),
    ("London",        "GB", "Canary Wharf"),
    ("London",        "GB", "Peckham"),
    ("London",        "GB", "Dalston"),

    ("Mumbai",        "IN", "Bandra"),
    ("Mumbai",        "IN", "Colaba"),
    ("Mumbai",        "IN", "Juhu"),
    ("Mumbai",        "IN", "Andheri"),
    ("Mumbai",        "IN", "Lower Parel"),
    ("Mumbai",        "IN", "Worli"),
    ("Mumbai",        "IN", "Powai"),

    ("Sydney",        "AU", "Newtown"),
    ("Sydney",        "AU", "Surry Hills"),
    ("Sydney",        "AU", "Bondi"),
    ("Sydney",        "AU", "Pyrmont"),
    ("Sydney",        "AU", "Glebe"),

    ("Berlin",        "DE", "Mitte"),
    ("Berlin",        "DE", "Prenzlauer Berg"),
    ("Berlin",        "DE", "Kreuzberg"),
    ("Berlin",        "DE", "Neukölln"),
    ("Berlin",        "DE", "Friedrichshain"),

    ("Singapore",     "SG", "Orchard"),
    ("Singapore",     "SG", "Tiong Bahru"),
    ("Singapore",     "SG", "Chinatown"),
    ("Singapore",     "SG", "Bugis"),
    ("Singapore",     "SG", "Dempsey Hill"),
]


def seed_neighbourhoods(db) -> int:
    """Insert seed data if the table is empty. Returns number inserted."""
    if db.query(Neighbourhood).count() > 0:
        return 0
    for city, country, name in NEIGHBOURHOOD_SEEDS:
        db.add(Neighbourhood(city=city, country=country, name=name))
    db.commit()
    return len(NEIGHBOURHOOD_SEEDS)
