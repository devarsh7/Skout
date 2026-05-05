"""
Schemas for the Discovery & Filtering agents.
"""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class DiscoveryRequest(BaseModel):
    """Natural-language creator discovery."""

    query: str = Field(..., description="e.g. 'vegan beauty micro-influencers in Berlin'")
    top_k: int = Field(20, ge=1, le=100)


class Filters(BaseModel):
    """Structured filters for the Filtering Agent."""

    platforms: list[str] = Field(default_factory=list)        # ["instagram", "tiktok"]
    niches: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)
    countries: list[str] = Field(default_factory=list)        # ISO-2
    cities: list[str] = Field(default_factory=list)
    min_total_followers: int = 1000
    max_total_followers: Optional[int] = None
    min_engagement_rate: float = 0.0
    audience_countries: list[str] = Field(default_factory=list)
    audience_age_range: Optional[str] = None
    verified_only: bool = False
    open_to_collabs_only: bool = True


class FilterRequest(BaseModel):
    query: Optional[str] = Field(None, description="Optional NL query; leave blank for pure filter search")
    filters: Filters
    top_k: int = Field(20, ge=1, le=100)


class AgentHit(BaseModel):
    """One returned creator with a relevance score."""

    score: float
    reason: Optional[str] = None
    creator: dict


class AgentResponse(BaseModel):
    agent: str                           # "discovery" | "filtering"
    total: int
    results: list[AgentHit]
    explanation: Optional[str] = None


class OutreachRequest(BaseModel):
    creator_id: str
    brand_name: str
    campaign_brief: str
    tone: str = Field("friendly-professional", description="friendly-professional | casual | formal")
    channel: str = Field("email", description="email | instagram_dm | tiktok_dm")


class OutreachDraft(BaseModel):
    subject: str
    body: str
