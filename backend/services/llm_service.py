"""
Unified LLM factory.

Swap providers by flipping LLM_PROVIDER in `.env` — no code changes required.

Active by default: **Ollama** (free, local, offline).
Paid options (Claude / OpenAI) are imported lazily to avoid hard dependencies
when you're only running on Ollama.

Usage:
    from backend.services.llm_service import get_llm
    llm = get_llm()
    resp = llm.invoke("Hello")
"""
from __future__ import annotations

from functools import lru_cache
from typing import Any

from loguru import logger

from backend.core.config import settings


@lru_cache(maxsize=1)
def get_llm(temperature: float = 0.2, **kwargs: Any):
    """Return a LangChain chat model configured from settings."""
    provider = settings.llm_provider.lower()

    # ---------- FREE / LOCAL ----------
    if provider == "ollama":
        from langchain_ollama import ChatOllama

        logger.info(f"Using Ollama model '{settings.ollama_model}' @ {settings.ollama_base_url}")
        return ChatOllama(
            model=settings.ollama_model,
            base_url=settings.ollama_base_url,
            temperature=temperature,
            **kwargs,
        )

    # ---------- PAID: Anthropic Claude ----------
    # Uncomment `langchain-anthropic` in requirements.txt and install.
    if provider == "anthropic":
        # from langchain_anthropic import ChatAnthropic
        # logger.info(f"Using Anthropic model '{settings.anthropic_model}'")
        # return ChatAnthropic(
        #     model=settings.anthropic_model,
        #     api_key=settings.anthropic_api_key,
        #     temperature=temperature,
        #     **kwargs,
        # )
        raise RuntimeError(
            "Anthropic provider selected but `langchain-anthropic` is not installed. "
            "Uncomment it in requirements.txt and `pip install -r requirements.txt`."
        )

    # ---------- PAID: OpenAI GPT-4o ----------
    if provider == "openai":
        # from langchain_openai import ChatOpenAI
        # logger.info(f"Using OpenAI model '{settings.openai_model}'")
        # return ChatOpenAI(
        #     model=settings.openai_model,
        #     api_key=settings.openai_api_key,
        #     temperature=temperature,
        #     **kwargs,
        # )
        raise RuntimeError(
            "OpenAI provider selected but `langchain-openai` is not installed. "
            "Uncomment it in requirements.txt and `pip install -r requirements.txt`."
        )

    raise ValueError(f"Unknown LLM_PROVIDER: {provider}")
