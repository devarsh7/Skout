"""
Pydantic DTOs for creator onboarding + retrieval.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class CreatorOnboard(BaseModel):
    """Incoming payload when a creator signs up."""

    full_name: str = Field(..., min_length=2, max_length=120)
    display_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None

    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    youtube_channel: Optional[str] = None
    facebook_page: Optional[str] = None
    twitter_handle: Optional[str] = None
    website: Optional[str] = None

    instagram_followers: int = 0
    tiktok_followers: int = 0
    youtube_subscribers: int = 0

    avg_engagement_rate: float = 0.0
    avg_views: int = 0

    bio: Optional[str] = Field(None, max_length=2000)
    niches: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    city: Optional[str] = None
    audience_countries: list[str] = Field(default_factory=list)
    audience_age_range: Optional[str] = None
    audience_gender_split: dict[str, float] = Field(default_factory=dict)

    min_rate_usd: float = 0.0
    open_to_collabs: bool = True
    preferred_collab_types: list[str] = Field(default_factory=list)

    @field_validator("niches", "languages", mode="before")
    @classmethod
    def _lowercase_list(cls, v):
        if isinstance(v, list):
            return [str(x).lower().strip() for x in v if x]
        return v

    @field_validator("country", mode="before")
    @classmethod
    def _uppercase_country(cls, v):
        return v.upper() if isinstance(v, str) else v

    def total_followers(self) -> int:
        return (
            (self.instagram_followers or 0)
            + (self.tiktok_followers or 0)
            + (self.youtube_subscribers or 0)
        )

    def has_at_least_one_handle(self) -> bool:
        return any(
            [
                self.instagram_handle,
                self.tiktok_handle,
                self.youtube_channel,
                self.facebook_page,
                self.twitter_handle,
            ]
        )


class CreatorUpdate(BaseModel):
    """All fields optional — only provided fields are applied."""

    display_name: Optional[str] = None
    phone: Optional[str] = None

    instagram_handle: Optional[str] = None
    tiktok_handle: Optional[str] = None
    youtube_channel: Optional[str] = None
    facebook_page: Optional[str] = None
    twitter_handle: Optional[str] = None
    website: Optional[str] = None

    instagram_followers: Optional[int] = None
    tiktok_followers: Optional[int] = None
    youtube_subscribers: Optional[int] = None

    avg_engagement_rate: Optional[float] = None
    avg_views: Optional[int] = None

    bio: Optional[str] = Field(None, max_length=2000)
    niches: Optional[list[str]] = None
    languages: Optional[list[str]] = None
    country: Optional[str] = Field(None, min_length=2, max_length=2)
    city: Optional[str] = None
    audience_countries: Optional[list[str]] = None
    audience_age_range: Optional[str] = None

    min_rate_usd: Optional[float] = None
    open_to_collabs: Optional[bool] = None
    preferred_collab_types: Optional[list[str]] = None

    @field_validator("niches", "languages", mode="before")
    @classmethod
    def _lowercase_list(cls, v):
        if isinstance(v, list):
            return [str(x).lower().strip() for x in v if x]
        return v

    @field_validator("country", mode="before")
    @classmethod
    def _uppercase_country(cls, v):
        return v.upper() if isinstance(v, str) else v


class CreatorPublic(BaseModel):
    """Public creator card — safe to show to anyone."""

    id: str
    display_name: str
    bio: Optional[str] = None
    niches: list[str] = []
    languages: list[str] = []
    country: Optional[str] = None
    city: Optional[str] = None
    total_followers: int = 0
    instagram_followers: int = 0
    tiktok_followers: int = 0
    youtube_subscribers: int = 0
    avg_engagement_rate: float = 0.0
    is_verified: bool = False
    handles: dict[str, Optional[str]] = {}


class CreatorContact(CreatorPublic):
    """PII-included variant — gated behind auth + tier checks."""

    email: Optional[EmailStr] = None
    phone: Optional[str] = None
