# Skout — AI Influencer Discovery & Filtering Platform

A two-sided marketplace where **creators self-onboard** (sharing their Instagram, TikTok, YouTube, Facebook handles + contact details) and **brands discover/filter them** through AI agents.

## Why this model wins
- **Owned data moat** — no scraping, no third-party API fees, no ToS risk.
- **Network effects** — more creators ⇒ better discovery ⇒ more brands ⇒ more revenue ⇒ more creators.
- **Compliance-friendly** — explicit creator consent at onboarding.

## Architecture

```
┌───────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Streamlit UI     │────▶│  FastAPI Backend │────▶│  SQLite/Postgres│
│  (Creators+Brands)│     │  + LangGraph     │     │  (relational)   │
└───────────────────┘     │  + LangChain     │     └─────────────────┘
                          │  + MCP Server    │     ┌─────────────────┐
                          └──────┬───────────┘────▶│    Pinecone     │
                                 │                 │   (vectors)     │
                                 ▼                 └─────────────────┘
                          ┌──────────────┐
                          │ Ollama (free)│
                          │ or Claude/GPT│
                          └──────────────┘
```

### Two Agents (LangGraph orchestrated)
1. **Discovery Agent** – natural-language semantic search across the creator index (Pinecone).
2. **Filtering Agent** – applies structured filters (platform, follower range, location, niche, engagement rate, language, verified status) and re-ranks.

### Bonus: **Outreach Agent**
Generates personalized DM/email drafts per creator — a sticky, high-retention feature.

## Quickstart

### 1. Install Ollama (free local LLM)
```bash
# https://ollama.com
ollama pull llama3.1:8b
ollama serve    # runs on :11434
```

### 2. Set up Python env
```bash
python -m venv .venv
source .venv/bin/activate           # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                # then fill PINECONE_API_KEY
```

### 3. Create Pinecone index
Go to [pinecone.io](https://app.pinecone.io), create an index named `skout-creators`, dimension `384`, metric `cosine`.

### 4. (Optional) Seed demo creators
```bash
python scripts/seed_demo_creators.py
```

### 5. Run the stack
```bash
# Terminal 1 – backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2 – frontend
streamlit run frontend/streamlit_app.py

# Terminal 3 – MCP server (optional, for IDE / Claude Desktop integration)
python -m backend.mcp_server.server
```

Open:
- Brand/Creator UI → http://localhost:8501
- API docs → http://localhost:8000/docs

## Folder Layout

```
Skout/
├── backend/
│   ├── main.py                 FastAPI entry
│   ├── core/                   config, db, security
│   ├── models/                 SQLAlchemy ORM
│   ├── schemas/                Pydantic DTOs
│   ├── api/                    REST routers
│   ├── agents/                 Discovery, Filter, Outreach (LangGraph)
│   ├── services/               LLM, Embeddings, Pinecone, Creator service
│   └── mcp_server/             MCP tools
├── frontend/
│   ├── streamlit_app.py        Landing
│   └── pages/                  Creator onboarding + Brand workflows
├── data/                       Seed JSONs
├── scripts/                    Seeding, re-indexing utilities
├── tests/
└── docs/
```

## Tech Stack
| Layer | Choice | Why |
|-------|--------|-----|
| API | FastAPI + Pydantic v2 | Async, auto-docs, fast |
| UI | Streamlit (multipage) | Fastest path to MVP |
| Relational DB | SQLite → Postgres | Zero-config dev, prod-ready |
| Vector DB | **Pinecone** | Managed, serverless, scale |
| Embeddings | sentence-transformers (free) | 384-d, local, quick |
| LLM (dev) | **Ollama** (llama3.1:8b) | Free, offline |
| LLM (prod) | Claude Sonnet 4.6 / GPT-4o | Drop-in via env var |
| Orchestration | LangChain + LangGraph | Stateful agent flows |
| Tool protocol | MCP | Expose Skout to Claude Desktop etc. |

## Revenue Model (scaffolded in v1)

| Tier | Price | Includes |
|------|-------|----------|
| Free | $0 | 10 searches / mo, 5 outreach drafts |
| Pro | $49 / mo | 500 searches, unlimited drafts, saved searches, campaigns |
| Agency | $199 / mo | Multi-seat, API access, CSV export, priority support |

Stripe hooks are stubbed in `backend/api/billing.py` (commented pending prod).

## Roadmap (post-MVP hooks you'll want)

- Creator verification (OAuth w/ Meta/Google/TikTok — bumps data quality & trust)
- Engagement-rate & fake-follower heuristic scorer
- Campaign tracker with outreach pipeline (Kanban)
- ROI dashboard (brand uploads post URL → scrape public metrics)
- Slack/Email alerts on new matching creators
- API for agencies (rate-limited with usage-based billing)
- White-label / multi-tenant mode

## License
Proprietary – © Skout
