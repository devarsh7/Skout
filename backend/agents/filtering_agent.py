"""
Filtering Agent
===============
Takes structured filter criteria (+ optional NL query) and returns creators
that satisfy ALL filters. Uses Pinecone's metadata filter when possible, then
applies a SQL post-filter for anything Pinecone can't express.

Implemented as a **LangGraph** so you can plug in more nodes later
(e.g. fake-follower check, pricing-band check, diversity rebalancer).
"""
from __future__ import annotations

from typing import Any, TypedDict

from loguru import logger
from sqlalchemy.orm import Session

from backend.models.creator import Creator
from backend.schemas.agent import AgentHit, AgentResponse, FilterRequest, Filters
from backend.services.creator_service import get_many
from backend.services.vector_store import get_vector_store


# ---- LangGraph state --------------------------------------------------------
class FilterState(TypedDict, total=False):
    req: FilterRequest
    db: Session
    hits: list[dict[str, Any]]
    creators: list[Creator]
    final: list[dict[str, Any]]
    explanation: str


# ---- Pinecone filter builder -----------------------------------------------
def build_pinecone_filter(f: Filters) -> dict | None:
    """Translate our Filters schema into a Pinecone metadata filter."""
    clauses: dict[str, Any] = {}

    if f.countries:
        clauses["country"] = {"$in": [c.upper() for c in f.countries]}
    if f.niches:
        clauses["niches"] = {"$in": [n.lower() for n in f.niches]}
    if f.languages:
        clauses["languages"] = {"$in": [lang.lower() for lang in f.languages]}
    if f.platforms:
        clauses["platforms"] = {"$in": [p.lower() for p in f.platforms]}
    if f.audience_countries:
        clauses["audience_countries"] = {"$in": [c.upper() for c in f.audience_countries]}

    follower_clause: dict[str, Any] = {}
    if f.min_total_followers:
        follower_clause["$gte"] = f.min_total_followers
    if f.max_total_followers:
        follower_clause["$lte"] = f.max_total_followers
    if follower_clause:
        clauses["total_followers"] = follower_clause

    if f.min_engagement_rate:
        clauses["avg_engagement_rate"] = {"$gte": f.min_engagement_rate}
    if f.verified_only:
        clauses["is_verified"] = True
    if f.open_to_collabs_only:
        clauses["open_to_collabs"] = True

    return clauses or None


# ---- Graph nodes -----------------------------------------------------------
def _node_vector_search(state: FilterState) -> FilterState:
    req = state["req"]
    vs = get_vector_store()
    if vs is None:
        state["hits"] = []
        return state
    query = req.query or _filters_to_pseudoquery(req.filters)
    pf = build_pinecone_filter(req.filters)
    logger.debug(f"Pinecone filter: {pf}")
    hits = vs.query(text=query, top_k=req.top_k, pinecone_filter=pf)
    state["hits"] = hits
    return state


def _node_hydrate(state: FilterState) -> FilterState:
    hits = state.get("hits") or []
    ids = [h["id"] for h in hits]
    creators = get_many(state["db"], ids)
    state["creators"] = creators
    return state


def _node_apply_residual_filters(state: FilterState) -> FilterState:
    """Post-filters for anything we couldn't express to Pinecone."""
    f = state["req"].filters
    creators = state.get("creators") or []
    hit_by_id = {h["id"]: h for h in state.get("hits") or []}

    out = []
    for c in creators:
        # City isn't in Pinecone filter — check here (case-insensitive).
        if f.cities and (c.city or "").lower() not in {x.lower() for x in f.cities}:
            continue
        h = hit_by_id.get(c.id, {})
        out.append(
            {
                "id": c.id,
                "score": float(h.get("score", 0.0)),
                "creator": c.to_public_dict(),
            }
        )

    # Keep original relevance order from Pinecone
    out.sort(key=lambda x: x["score"], reverse=True)
    state["final"] = out
    state["explanation"] = (
        f"{len(out)} creators matched "
        f"(platforms={f.platforms or 'any'}, niches={f.niches or 'any'}, "
        f"country={f.countries or 'any'}, followers≥{f.min_total_followers})."
    )
    return state


def _filters_to_pseudoquery(f: Filters) -> str:
    """Synthesize a readable query string so Pinecone still does *some* semantic work."""
    bits = []
    if f.niches:
        bits.append("Niches: " + ", ".join(f.niches))
    if f.countries:
        bits.append("Countries: " + ", ".join(f.countries))
    if f.cities:
        bits.append("Cities: " + ", ".join(f.cities))
    if f.languages:
        bits.append("Languages: " + ", ".join(f.languages))
    if f.platforms:
        bits.append("Platforms: " + ", ".join(f.platforms))
    return " | ".join(bits) or "creator"


# ---- Public class ----------------------------------------------------------
class FilteringAgent:
    """LangGraph-powered filter pipeline with SQL fallback."""

    def __init__(self) -> None:
        self._vs = get_vector_store()
        if self._vs is not None:
            from langgraph.graph import END, StateGraph

            g = StateGraph(FilterState)
            g.add_node("vector_search", _node_vector_search)
            g.add_node("hydrate", _node_hydrate)
            g.add_node("residual_filters", _node_apply_residual_filters)
            g.set_entry_point("vector_search")
            g.add_edge("vector_search", "hydrate")
            g.add_edge("hydrate", "residual_filters")
            g.add_edge("residual_filters", END)
            self._graph = g.compile()
        else:
            self._graph = None

    def run(self, db: Session, req: FilterRequest) -> AgentResponse:
        if self._graph is None:
            return self._sql_filter(db, req)

        final_state: FilterState = self._graph.invoke({"req": req, "db": db})
        items = final_state.get("final", [])
        return AgentResponse(
            agent="filtering",
            total=len(items),
            results=[
                AgentHit(score=item["score"], creator=item["creator"]) for item in items
            ],
            explanation=final_state.get("explanation"),
        )

    def _sql_filter(self, db: Session, req: FilterRequest) -> AgentResponse:
        """Pure SQL filtering when Pinecone is not configured."""
        f = req.filters
        q = db.query(Creator)

        if f.countries:
            q = q.filter(Creator.country.in_([c.upper() for c in f.countries]))
        if f.min_total_followers:
            q = q.filter(Creator.total_followers >= f.min_total_followers)
        if f.max_total_followers:
            q = q.filter(Creator.total_followers <= f.max_total_followers)
        if f.min_engagement_rate:
            q = q.filter(Creator.avg_engagement_rate >= f.min_engagement_rate)
        if f.verified_only:
            q = q.filter(Creator.is_verified == True)   # noqa: E712
        if f.open_to_collabs_only:
            q = q.filter(Creator.open_to_collabs == True)  # noqa: E712

        candidates = q.order_by(Creator.total_followers.desc()).limit(req.top_k * 4).all()

        # Python-side JSON field filtering (SQLite has limited JSON support)
        results = []
        for c in candidates:
            if f.platforms:
                present = []
                if c.instagram_handle: present.append("instagram")
                if c.tiktok_handle:    present.append("tiktok")
                if c.youtube_channel:  present.append("youtube")
                if c.facebook_page:    present.append("facebook")
                if c.twitter_handle:   present.append("twitter")
                if not any(p in present for p in f.platforms):
                    continue
            if f.niches and not any(n in (c.niches or []) for n in f.niches):
                continue
            if f.languages and not any(lang in (c.languages or []) for lang in f.languages):
                continue
            if f.cities and (c.city or "").lower() not in {x.lower() for x in f.cities}:
                continue
            if f.audience_countries and not any(
                ac in (c.audience_countries or []) for ac in f.audience_countries
            ):
                continue
            results.append(c)
            if len(results) >= req.top_k:
                break

        hits = [AgentHit(score=1.0, creator=c.to_public_dict()) for c in results]
        f_summary = (
            f"platforms={f.platforms or 'any'}, niches={f.niches or 'any'}, "
            f"country={f.countries or 'any'}, followers≥{f.min_total_followers}"
        )
        return AgentResponse(
            agent="filtering",
            total=len(hits),
            results=hits,
            explanation=(
                f"{len(hits)} creators matched ({f_summary}). "
                "Using SQL filters — Pinecone not configured."
            ),
        )
