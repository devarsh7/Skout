"""
Smoke tests — verify that core modules import and basic schema validation works.
No external services (Pinecone/Ollama) are required to run these.
"""
from __future__ import annotations

from backend.schemas.agent import FilterRequest, Filters
from backend.schemas.creator import CreatorOnboard


def test_creator_schema_requires_handle():
    payload = {
        "full_name": "Test User",
        "email": "test@example.com",
        "country": "US",
        "niches": ["fitness"],
    }
    dto = CreatorOnboard(**payload)
    assert dto.has_at_least_one_handle() is False
    assert dto.total_followers() == 0


def test_creator_schema_accepts_handle():
    dto = CreatorOnboard(
        full_name="Jane Doe",
        email="jane@example.com",
        country="us",
        niches=["Beauty"],
        instagram_handle="jane",
        instagram_followers=10000,
    )
    assert dto.country == "US"
    assert dto.niches == ["beauty"]
    assert dto.has_at_least_one_handle() is True
    assert dto.total_followers() == 10000


def test_filter_request_defaults():
    f = Filters(niches=["tech"], countries=["US"])
    req = FilterRequest(filters=f, top_k=10)
    assert req.filters.min_total_followers == 1000
    assert req.top_k == 10


def test_llm_factory_imports():
    # We don't actually invoke the LLM (no Ollama in CI) — just ensure imports work.
    from backend.services import llm_service  # noqa: F401
