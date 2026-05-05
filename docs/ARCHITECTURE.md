# Skout Architecture

## Request flow

### Creator onboarding
```
Streamlit form → POST /creators → CreatorService
                                    ├── write to SQLite/Postgres
                                    └── upsert vector to Pinecone
```

### Discovery (NL search)
```
Brand prompt → POST /agents/discovery → DiscoveryAgent
                                          ├── LLM: summarize brief
                                          ├── Pinecone: top-K vector search
                                          ├── SQL: hydrate full creator records
                                          └── LLM: rerank with reasons
```

### Filtering (structured)
```
Filter form → POST /agents/filter → FilteringAgent (LangGraph)
                                       ├── vector_search (Pinecone + metadata filter)
                                       ├── hydrate (SQL)
                                       └── residual_filters (city, etc.)
```

### Outreach
```
Creator ID + brief → POST /agents/outreach → OutreachAgent
                                               ├── SQL: load creator
                                               └── LLM: draft JSON {subject, body}
```

## Why Pinecone + SQL (not pure vector)
- Vector DB handles semantic + basic metadata filters fast.
- SQL is the source of truth for PII and mutable state (followers, rates, status).
- Stale vectors are cheap to rebuild (`POST /creators/reindex`).

## Why LangGraph (not plain LangChain)
- Filtering pipeline has branching candidates (residual filters, scoring, future reranking nodes).
- Gives us checkpointing & observability when we add more nodes (fake-follower scorer, pricing-band reranker, diversity rebalancer).

## Why MCP
- Lets Skout be a first-class tool inside Claude Desktop / Cursor.
- Zero extra backend code — same agents, stdio transport.
- Useful for sales demos ("here's our product inside Claude itself").

## Scaling notes
- Swap SQLite → Postgres by changing `DATABASE_URL`.
- FastAPI is already async-friendly; make agent calls async when you need higher concurrency.
- Pinecone is serverless — scales automatically.
- Embeddings run in-process; move to a dedicated `embeddings-worker` pod if QPS grows.
- Add Redis + `fastapi-limiter` for per-tier rate limiting.
