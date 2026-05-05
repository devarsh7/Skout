"""
Centralized application settings, loaded from `.env` via pydantic-settings.
Access via the `settings` singleton at the bottom of the file.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    app_name: str = "Skout"
    app_env: Literal["development", "production"] = "development"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    frontend_port: int = 8501
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60

    # --- Database ---
    database_url: str = "sqlite:///./skout.db"

    # --- Pinecone (active vector DB) ---
    pinecone_api_key: str = ""
    pinecone_index_name: str = "skout-creators"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"
    pinecone_dimension: int = 384

    # --- LLM ---
    llm_provider: Literal["ollama", "anthropic", "openai"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    # Paid (commented via env by default; still loaded if present) ---------
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-6"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    # --- Agent Chat (free tier) ---
    # Free key at console.groq.com — add GROQ_API_KEY to .env
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # --- Embeddings ---
    embedding_provider: Literal["local", "openai"] = "local"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    openai_embedding_model: str = "text-embedding-3-small"

    # --- SMTP (OTP emails) ---
    smtp_host:     str = ""
    smtp_port:     int = 587
    smtp_user:     str = ""
    smtp_password: str = ""
    smtp_from:     str = ""

    # --- Instagram Graph API ---
    instagram_app_id: str = ""
    instagram_app_secret: str = ""
    instagram_redirect_uri: str = "http://localhost:8000/instagram/callback"

    # --- MCP ---
    mcp_server_host: str = "127.0.0.1"
    mcp_server_port: int = 9000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Cached settings factory — avoids re-parsing .env on every import."""
    return Settings()


settings = get_settings()
