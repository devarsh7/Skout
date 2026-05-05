"""
Embeddings factory.

Default: **sentence-transformers/all-MiniLM-L6-v2** (free, 384-d, ~80MB).
Matches Pinecone dimension configured in settings.

For production / higher quality, switch EMBEDDING_PROVIDER=openai and uncomment
the relevant block + pip install openai.
"""
from __future__ import annotations

from functools import lru_cache

from loguru import logger

from backend.core.config import settings


@lru_cache(maxsize=1)
def get_embedder():
    """Return an object with `.embed(list[str]) -> list[list[float]]`."""
    provider = settings.embedding_provider.lower()

    if provider == "local":
        return _LocalEmbedder(settings.embedding_model)

    if provider == "openai":
        # from langchain_openai import OpenAIEmbeddings
        # return _OpenAIEmbedder(OpenAIEmbeddings(
        #     model=settings.openai_embedding_model,
        #     api_key=settings.openai_api_key,
        # ))
        raise RuntimeError(
            "OpenAI embeddings selected but `langchain-openai` is not installed. "
            "Uncomment it in requirements.txt and `pip install -r requirements.txt`."
        )

    raise ValueError(f"Unknown EMBEDDING_PROVIDER: {provider}")


class _LocalEmbedder:
    """Wrapper around sentence-transformers for batch embedding."""

    def __init__(self, model_name: str) -> None:
        from sentence_transformers import SentenceTransformer

        logger.info(f"Loading local embedder: {model_name}")
        self._model = SentenceTransformer(model_name)

    def embed(self, texts: list[str]) -> list[list[float]]:
        arr = self._model.encode(
            texts,
            batch_size=32,
            show_progress_bar=False,
            normalize_embeddings=True,
        )
        return arr.tolist()

    def embed_one(self, text: str) -> list[float]:
        return self.embed([text])[0]


# class _OpenAIEmbedder:
#     def __init__(self, backend):
#         self._backend = backend
#     def embed(self, texts):
#         return self._backend.embed_documents(texts)
#     def embed_one(self, text):
#         return self._backend.embed_query(text)
