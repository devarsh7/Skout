"""
Pinecone wrapper — the single source of truth for creator vectors.

ACTIVE: Pinecone (from day one, per project requirements).
Backup (commented): ChromaDB for offline dev if Pinecone is down.

Metadata stored in Pinecone is intentionally MINIMAL & non-PII:
- country, city (for filtered searches)
- niches (for filtered searches)
- total_followers (for range filters)
- avg_engagement_rate
- platforms
PII (email/phone) stays in the relational DB — we JOIN by id.
"""
from __future__ import annotations

from typing import Any

from loguru import logger

from backend.core.config import settings
from backend.services.embeddings import get_embedder

# Catch import errors at module load time so get_vector_store() can reliably return None.
try:
    from pinecone import Pinecone as _Pinecone, ServerlessSpec as _ServerlessSpec
    _PINECONE_AVAILABLE = True
except Exception as _pinecone_import_err:
    logger.warning(f"Pinecone package unavailable ({_pinecone_import_err!r}) — SQL fallback active.")
    _PINECONE_AVAILABLE = False

_vs_instance: "PineconeStore | None | bool" = False  # False = not yet initialised


def get_vector_store() -> "PineconeStore | None":
    """Returns None (instead of raising) when Pinecone is not configured or unavailable."""
    global _vs_instance
    if _vs_instance is not False:          # already resolved (None or real store)
        return _vs_instance                # type: ignore[return-value]
    if not _PINECONE_AVAILABLE or not settings.pinecone_api_key:
        logger.warning("Pinecone unavailable or PINECONE_API_KEY not set — SQL fallback active.")
        _vs_instance = None
        return None
    try:
        _vs_instance = PineconeStore()
    except Exception as exc:
        logger.error(f"Pinecone init failed ({exc!r}) — SQL fallback active.")
        _vs_instance = None
    return _vs_instance                    # type: ignore[return-value]


class PineconeStore:
    """Lightweight facade over the Pinecone v5 SDK."""

    def __init__(self) -> None:
        Pinecone = _Pinecone
        ServerlessSpec = _ServerlessSpec

        if not settings.pinecone_api_key:
            raise RuntimeError(
                "PINECONE_API_KEY is empty. Set it in .env before running the backend."
            )

        self._pc = Pinecone(api_key=settings.pinecone_api_key)
        existing = [ix.name for ix in self._pc.list_indexes()]

        if settings.pinecone_index_name not in existing:
            logger.info(f"Creating Pinecone index '{settings.pinecone_index_name}'…")
            self._pc.create_index(
                name=settings.pinecone_index_name,
                dimension=settings.pinecone_dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud=settings.pinecone_cloud,
                    region=settings.pinecone_region,
                ),
            )
        self._index = self._pc.Index(settings.pinecone_index_name)
        self._embedder = get_embedder()

    # ---------- Upsert ----------
    def upsert_creator(self, creator_id: str, text: str, metadata: dict) -> None:
        vec = self._embedder.embed_one(text)
        self._index.upsert(vectors=[(creator_id, vec, metadata)])

    def upsert_many(self, items: list[tuple[str, str, dict]]) -> int:
        """items = [(id, text, metadata)]"""
        if not items:
            return 0
        texts = [t for _, t, _ in items]
        vecs = self._embedder.embed(texts)
        payload = [(i, v, m) for (i, _, m), v in zip(items, vecs)]
        # Pinecone recommends batching at 100
        for batch in _chunks(payload, 100):
            self._index.upsert(vectors=batch)
        return len(payload)

    # ---------- Query ----------
    def query(
        self,
        text: str,
        top_k: int = 20,
        pinecone_filter: dict | None = None,
    ) -> list[dict[str, Any]]:
        vec = self._embedder.embed_one(text)
        resp = self._index.query(
            vector=vec,
            top_k=top_k,
            include_metadata=True,
            filter=pinecone_filter or None,
        )
        hits = []
        for match in resp.get("matches", []):
            hits.append(
                {
                    "id": match["id"],
                    "score": float(match["score"]),
                    "metadata": match.get("metadata", {}),
                }
            )
        return hits

    def delete(self, creator_id: str) -> None:
        self._index.delete(ids=[creator_id])


def _chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


# =============================================================================
# ChromaDB fallback (commented — free, local, no API key).
# Uncomment `chromadb` in requirements.txt and flip the factory above to use it.
# =============================================================================
# class ChromaStore:
#     def __init__(self):
#         import chromadb
#         self._client = chromadb.PersistentClient(path="./.chroma")
#         self._col = self._client.get_or_create_collection(
#             name=settings.pinecone_index_name,
#             metadata={"hnsw:space": "cosine"},
#         )
#         self._embedder = get_embedder()
#     ...
