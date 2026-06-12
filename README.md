# Skout — AI-Native Career Manager for Creators

Skout is an **AI-native manager** for local creators. Creators connect their
Instagram, get a true engagement-rate read, and let the Career Manager agent
quote fair rates, evaluate brand briefs, and keep their voice consistent.
On the other side, **local business onboarding** feeds Skout's owned creator
index — the data backbone that powers our own discovery API instead of
scraping or paying for third-party data.

> Originally a two-sided discovery marketplace; pivoted to the AI-manager
> model with the brand side retained as the data and revenue backbone.
> Toronto-first rollout.

## What's in the box

### Creator side — Career Manager
- **Rate Calculator** — deterministic formula + local market data joins to quote fair rates per deliverable.
- **Brief Evaluator** — paste a brand brief; gets red-flag analysis and a suggested counter-rate.
- **Voice / Tone profile** — LLM-built profile of the creator's content voice, persisted on the profile.
- **Career chat** — conversational agent with per-creator conversation history.
- **Instagram OAuth** — creators connect their professional account; Skout reads profile + insights to compute real engagement rates.

### Business side — data backbone
- **Local business onboarding** — businesses register and describe what they need.
- **Brand Agent (chat)** — tool-loop agent (7 tools) with persistent brand-fact memory; chains discovery → filtering → outreach in one conversation.
- **Discovery / Filtering / Outreach agents** — semantic search over the owned creator index (Pinecone), structured re-ranking, and personalized outreach drafts.
- **Map view** — creators plotted by neighbourhood (Leaflet).

## Architecture

```
┌────────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Next.js 14 (web/) │────▶│  FastAPI Backend │────▶│  SQLite/Postgres│
│  React + Tailwind  │     │  + agent tool    │     │  (relational)   │
└────────────────────┘     │    loop          │     └─────────────────┘
                           │  + MCP Server    │     ┌─────────────────┐
                           └──────┬───────────┘────▶│    Pinecone     │
                                  │                 │   (vectors)     │
                                  ▼                 └─────────────────┘
                           ┌─────────────────┐      ┌─────────────────┐
                           │ Groq (dev, free)│      │ Instagram Graph │
                           │ Claude (prod)   │      │ API (OAuth)     │
                           └─────────────────┘      └─────────────────┘
```

The legacy Streamlit UI lives in `frontend/` and still runs, but the
**Next.js app in `web/` is the primary frontend** — the Streamlit pages are
kept for reference during the migration and will be removed.

See [docs/AGENTS.md](docs/AGENTS.md) for the full agent reference and
[docs/PRICING.md](docs/PRICING.md) for both pricing surfaces.

## Quickstart

### 1. Backend
```bash
python -m venv .venv
.venv\Scripts\activate              # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env                # fill PINECONE_API_KEY, GROQ_API_KEY, INSTAGRAM_* etc.
uvicorn backend.main:app --reload --port 8000
```

### 2. Web frontend
```bash
cd web
npm install
npm run dev                         # http://localhost:3000
```

### 3. (Optional) Seed demo creators
```bash
python scripts/seed_demo_creators.py
```

Open:
- Web app → http://localhost:3000
- API docs → http://localhost:8000/docs

## Folder Layout

```
Skout/
├── backend/
│   ├── main.py                 FastAPI entry
│   ├── core/                   config, db, security
│   ├── models/                 SQLAlchemy ORM (creators, brand facts, oauth state…)
│   ├── schemas/                Pydantic DTOs
│   ├── api/                    REST routers (auth, instagram, creator-agent, agent chat…)
│   ├── agents/                 Tool loop + tools, discovery/filter/outreach
│   ├── services/               Rate calculator, brief evaluator, tone, brand facts,
│   │                           Instagram OAuth + maintenance, LLM, embeddings, Pinecone
│   └── mcp_server/             MCP tools
├── web/                        Next.js 14 app (primary frontend)
│   ├── app/creator/            Dashboard, Career Manager, onboarding, profile
│   ├── app/business/           Dashboard, discover, filter, map, AI agent
│   ├── components/             Career, business, map, layout components
│   └── lib/api.ts              Typed API client
├── frontend/                   Legacy Streamlit UI (being phased out)
├── data/                       Seed JSONs
├── scripts/                    Seeding + dev utilities
├── docs/                       AGENTS.md, PRICING.md, APP_REVIEW.md, ARCHITECTURE.md
└── tests/
```

## Tech Stack
| Layer | Choice | Why |
|-------|--------|-----|
| API | FastAPI + Pydantic v2 | Async, auto-docs, fast |
| UI | **Next.js 14 + React 18 + Tailwind** | Production frontend (replaced Streamlit MVP) |
| Maps | Leaflet / react-leaflet | Neighbourhood-level creator map |
| Relational DB | SQLite → Postgres (Render) | Zero-config dev, prod-ready |
| Vector DB | Pinecone | Managed, serverless |
| Embeddings | sentence-transformers (free) | 384-d, local |
| LLM (dev) | Groq — llama-3.3-70b (free tier) | Fast + free tool-loop agent |
| LLM (prod) | Claude Sonnet 4.6 | Flip `LLM_PROVIDER=anthropic` |
| Creator data | Instagram Graph API (OAuth) | Consented, first-party metrics |
| Tool protocol | MCP | Expose Skout to Claude Desktop etc. |
| Deploy | Render (`render.yaml`) + Vercel (`web/vercel.json`) | API + web |

## Pricing

Two surfaces (see [docs/PRICING.md](docs/PRICING.md)):
1. **Platform tiers** — what brands pay Skout (Free / Pro $49 / Agency $199).
2. **Creator rates** — what the Rate Calculator helps creators quote to brands.

## Roadmap

- Meta App Review → Advanced Access for Instagram permissions ([docs/APP_REVIEW.md](docs/APP_REVIEW.md))
- Data-deletion callback + live privacy/terms pages
- Retire the Streamlit frontend once web/ reaches parity
- Engagement-rate & fake-follower heuristic scorer
- Public discovery API for agencies (usage-based billing)

## License
Proprietary – © Skout
