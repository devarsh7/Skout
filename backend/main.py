"""
Skout — FastAPI entrypoint.

Run locally:
    uvicorn backend.main:app --reload --port 8000
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from backend.api import agents as agents_router
from backend.api import agent_chat as agent_chat_router
from backend.api import auth as auth_router
from backend.api import creators as creators_router
from backend.api import creator_agent as creator_agent_router
from backend.api import instagram as instagram_router
from backend.api import local as local_router
from backend.core.config import settings
from backend.core.database import get_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.app_name} ({settings.app_env}) …")
    init_db()
    logger.info("Database tables ready.")
    # Seed neighbourhoods if empty
    from backend.models.neighbourhood import seed_neighbourhoods
    db = next(get_db())
    try:
        n = seed_neighbourhoods(db)
        if n:
            logger.info(f"Seeded {n} neighbourhoods.")
    finally:
        db.close()
    yield
    logger.info("Shutting down.")


app = FastAPI(
    title="Skout API",
    description="Influencer discovery & filtering platform.",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS (Streamlit runs on a different port)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth_router.router)
app.include_router(creators_router.router)
app.include_router(agents_router.router)
app.include_router(agent_chat_router.router)
app.include_router(creator_agent_router.router)
app.include_router(instagram_router.router)
app.include_router(local_router.router)


@app.get("/", tags=["meta"])
def root():
    return {
        "name": settings.app_name,
        "version": "0.1.0",
        "env": settings.app_env,
        "llm_provider": settings.llm_provider,
        "vector_db": "pinecone",
    }


@app.get("/health", tags=["meta"])
def health():
    return {"status": "ok"}
