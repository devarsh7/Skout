"""
Discovery Agent
===============
Takes a **natural-language brief** (e.g. "vegan beauty micro-influencers in
Berlin with engaged Gen-Z audience") and returns ranked creators.

Flow
----
1. LLM parses the brief into an intent + soft hints (LLM optional — degrades
   gracefully if LLM is unavailable).
2. Semantic search against Pinecone using the raw query.
3. Light LLM-based re-ranking on the top-K with a one-sentence "why" per hit.
"""
from __future__ import annotations

import json
from typing import Any

from loguru import logger
from sqlalchemy.orm import Session

from sqlalchemy.orm import Session as _Session

from backend.models.creator import Creator
from backend.schemas.agent import AgentHit, AgentResponse, DiscoveryRequest
from backend.services.creator_service import get_many
from backend.services.llm_service import get_llm
from backend.services.vector_store import get_vector_store


_PARSE_PROMPT = """You are Skout's creator-discovery copilot.
Parse the following brand brief into a concise 1-2 sentence search summary
that will be used for semantic search across creator profiles. Keep it terse
and keyword-rich, no preamble.

Brief: {query}
Summary:"""


_RERANK_PROMPT = """You are ranking influencer profiles for a brand brief.

Brief: {query}

Candidates (JSON):
{candidates}

For each candidate, output a JSON array with objects {{"id": "<id>", "score": 0-1, "reason": "<one sentence>"}}.
Only return the JSON array. No prose. No code fences."""


class DiscoveryAgent:
    def __init__(self) -> None:
        self.vs = get_vector_store()

    # -- Public API ---------------------------------------------------------
    def run(self, db: Session, req: DiscoveryRequest) -> AgentResponse:
        if self.vs is None:
            return self._sql_fallback(db, req)

        search_text = self._summarize(req.query)
        logger.debug(f"Discovery search text: {search_text}")

        hits = self.vs.query(text=search_text, top_k=req.top_k)
        if not hits:
            return AgentResponse(
                agent="discovery",
                total=0,
                results=[],
                explanation="No matching creators found. Try broadening your brief.",
            )

        creators = get_many(db, [h["id"] for h in hits])
        id_to_creator = {c.id: c for c in creators}

        enriched = []
        for h in hits:
            c = id_to_creator.get(h["id"])
            if not c:
                continue
            enriched.append({
                "id": h["id"],
                "vector_score": h["score"],
                "creator": c.to_public_dict(),
            })

        reranked = self._rerank(req.query, enriched) or enriched

        return AgentResponse(
            agent="discovery",
            total=len(reranked),
            results=[
                AgentHit(
                    score=item.get("score", item["vector_score"]),
                    reason=item.get("reason"),
                    creator=item["creator"],
                )
                for item in reranked
            ],
            explanation=f"Discovered {len(reranked)} creators via semantic search.",
        )

    def _sql_fallback(self, db: Session, req: DiscoveryRequest) -> AgentResponse:
        """Return creators from SQL ordered by followers when Pinecone is unavailable."""
        rows = (
            db.query(Creator)
            .filter(Creator.open_to_collabs == True)  # noqa: E712
            .order_by(Creator.total_followers.desc())
            .limit(req.top_k)
            .all()
        )
        results = [
            AgentHit(score=1.0, creator=c.to_public_dict()) for c in rows
        ]
        return AgentResponse(
            agent="discovery",
            total=len(results),
            results=results,
            explanation=(
                "Semantic search unavailable (Pinecone not configured). "
                f"Showing {len(results)} creators sorted by follower count."
            ),
        )

    # -- Internals ----------------------------------------------------------
    def _summarize(self, query: str) -> str:
        try:
            llm = get_llm(temperature=0.0)
            out = llm.invoke(_PARSE_PROMPT.format(query=query))
            text = getattr(out, "content", str(out)).strip()
            return text or query
        except Exception as e:  # noqa: BLE001
            logger.warning(f"LLM summarization failed, using raw query: {e}")
            return query

    def _rerank(
        self, query: str, enriched: list[dict[str, Any]]
    ) -> list[dict[str, Any]] | None:
        try:
            llm = get_llm(temperature=0.0)
            # Keep the payload small for local LLMs
            compact = [
                {
                    "id": e["id"],
                    "display_name": e["creator"].get("display_name"),
                    "bio": (e["creator"].get("bio") or "")[:300],
                    "niches": e["creator"].get("niches", []),
                    "country": e["creator"].get("country"),
                    "total_followers": e["creator"].get("total_followers"),
                }
                for e in enriched
            ]
            resp = llm.invoke(
                _RERANK_PROMPT.format(
                    query=query, candidates=json.dumps(compact, ensure_ascii=False)
                )
            )
            text = getattr(resp, "content", str(resp)).strip()
            # Clean common LLM artifacts
            if text.startswith("```"):
                text = text.strip("`").split("\n", 1)[-1]
                if text.endswith("```"):
                    text = text[:-3]
            parsed = json.loads(text)
            if not isinstance(parsed, list):
                return None

            score_map = {p["id"]: p for p in parsed if "id" in p}
            for e in enriched:
                p = score_map.get(e["id"])
                if p:
                    e["score"] = float(p.get("score", e["vector_score"]))
                    e["reason"] = p.get("reason")
            enriched.sort(key=lambda x: x.get("score", 0), reverse=True)
            return enriched
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Rerank skipped: {e}")
            return None
