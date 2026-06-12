# Skout — Agents

This document is the source of truth for every agent in Skout. It covers what each
one does, where it lives, what it depends on, and the operational rules that come
out of recent iterations. It also captures the rationale from the conversation
that produced the latest Brand Agent rewrite and the Toronto-first rollout.

> Reading order if you're new: skim _Quick map_ → _Brand Agent_ → _Career Manager
> agents_ → _Cross-cutting concerns_. Skip the rest unless you're modifying it.

---

## Quick map

| Agent | Side | Entry | Brain | Tools | State |
| --- | --- | --- | --- | --- | --- |
| Discovery Agent | Brand | `POST /agents/discovery` | Pinecone semantic search + LLM rerank | none | none |
| Filtering Agent | Brand | `POST /agents/filter` | LangGraph node pipeline | none | request-scoped |
| Outreach Agent | Brand | `POST /agents/outreach` | LLM | none | none |
| **Brand Agent (chat)** | Brand | `POST /agent/chat` | Groq llama-3.3-70b tool loop | 7 tools | Brand-fact memory + conversation history |
| Career Manager — Rate Calculator | Creator | `POST /creator-agent/calculate-rate` | Deterministic formula + market join | n/a | per-creator |
| Career Manager — Brief Evaluator | Creator | `POST /creator-agent/evaluate-brief` | Regex extract + LLM red-flag + rate join | n/a | per-creator |
| Career Manager — Voice / Tone | Creator | `GET/POST /creator-agent/voice` | LLM summarisation | n/a | persisted on Creator |
| Career Manager — Chat | Creator | `POST /creator-agent/chat` | Groq llama-3.3-70b | n/a | conversation history |

All LLM calls go through Groq's OpenAI-compatible API with
`llama-3.3-70b-versatile` while we're on the free tier. To swap to Claude Sonnet
4.6 in production, flip `LLM_PROVIDER=anthropic` and uncomment the Claude block
in `backend/services/agent_chat_service.py::_call_llm`. The Anthropic SDK is the
only new dependency.

---

## Brand Agent (rewritten with tools)

`backend/agents/tool_loop.py` + `backend/agents/tools.py` +
`backend/services/agent_chat_service.py`

### Why we rewrote it

The previous Brand Agent classified the user's intent with a keyword bag
(`"find" → find_creator`, `"draft" → send_outreach`, …) and then ran a single
templated LLM call with hand-stuffed context. It worked for canned demo prompts
but broke the moment a brand asked for anything compound — _"find micro food
creators in Toronto and draft an outreach"_ would either skip the discovery step
or skip the draft.

The rewrite replaces that with an OpenAI-style tool loop. The LLM picks the
right tools, chains them, and stops on its own. Brand-fact memory is injected
into the system prompt every turn so durable preferences persist across
sessions. Every tool call is captured into a `tool_trace` array that the web UI
renders as animated status chips while the response builds.

### Tools

Defined in `backend/agents/tools.py`. Schemas are emitted in OpenAI
function-calling format because Groq accepts them on llama-3.3-70b.

| Tool | Purpose | Notes |
| --- | --- | --- |
| `discover_creators` | Natural-language search across the creator index | Open-to-collabs filter is always applied; results scored with keyword overlap fallback. |
| `filter_creators` | Stricter refinement on a prior result set | Operates on creator IDs the LLM already saw. Engagement is tolerant of both percent and fraction encodings. |
| `get_creator_profile` | Fetch a single creator before drafting | Use this before `draft_outreach_message`. |
| `draft_outreach_message` | Generate a personalised first-touch DM/email | Pulls SMB profile metadata for company name / target city. |
| `get_campaign_status` | Recent campaigns + outreach counts per status | Scoped to the calling SMB. |
| `get_local_benchmark` | Avg engagement / followers for `city × category` | Use this before quoting a budget. |
| `save_brand_fact` | Persist a durable fact for later turns | Backed by the brand-fact memory store (see below). |

### Loop semantics

`run_tool_loop` runs up to `MAX_ITERATIONS = 5` rounds. Each round:

1. Send the full message history + tool schemas to Groq with
   `tool_choice = "auto"`.
2. If the response has no `tool_calls`, capture `content`, exit.
3. Otherwise, run every tool call, append the assistant tool-call message and
   the tool result message back to the history, and loop.

If we exit the loop without final text, we make one extra non-tool LLM call
asking for a 3-4 sentence summary with one clear next step. That's the safety
net for runaway tool chains.

Per-call result JSON is truncated to 8 KB before being fed back into the LLM —
keeps tokens predictable without dropping the metadata the LLM cares about
(IDs, counts, names).

### System prompt addendum

The base prompt makes the agent talk like _"a helpful friend who knows
marketing,"_ ends every reply with one next step, and forbids marketing jargon.
When the tool loop is enabled (`_TOOL_LOOP_ENABLED = True`) we append a tool-use
addendum that tells the LLM to chain tools aggressively, never invent creators
or numbers, and call `save_brand_fact` whenever the user states a durable
preference.

### Brand-fact memory

`backend/services/brand_facts_service.py` + `backend/models/brand_fact.py`

After every user/assistant pair, we run a cheap LLM extraction call against the
last 2 turns asking for durable, third-person facts about the SMB. Each fact
gets a category (`budget | preference | constraint | context | goal | outcome |
other`) and a 0.0-1.0 confidence. Near-duplicates bump the existing row's
confidence rather than creating new ones. The top 15 facts (by confidence ×
recency) get injected into the next turn's system prompt under
`WHAT YOU REMEMBER ABOUT THIS USER`.

The web UI surfaces this state via `BrandMemoryPanel` on the left of the AI
Agent page. Brands can add a fact manually (category picker is colour-coded
inline) or delete a fact they no longer want the agent to anchor on. Deletes
are optimistic with a silent refresh on failure.

### Tool trace UI

`web/components/business/ToolTrace.tsx` renders the `tool_trace` array as a
stack of small status rows above each assistant message. Each row:

- Has an icon mapped to the tool name (`Search` for discover, `Mail` for
  outreach, etc.).
- Animates in with a staggered `fade-up` (60 ms per step).
- Is clickable when args exist; expanding shows a one-line `key: value`
  summary of what was actually passed.
- Colour-codes success vs error in the result summary.

While the request is in-flight, the chat shows a "thinking" indicator that
cycles through four hints (`Reading your brand memory…`, `Searching the
Toronto creator index…`, …) every 1.8 s so the UX feels alive even when the
backend is grinding through 3-4 tool calls.

### Failure modes

- **Groq is down** → `run_tool_loop` raises; `chat()` catches and falls back to
  a single non-tool LLM call (`_call_llm`). User sees a plain reply.
- **Tool fails** → returns `{"error": "..."}`; the LLM sees that and is told to
  recover or apologise.
- **LLM passes bad arguments** → `execute_tool` catches `TypeError`, surfaces
  the message to the LLM so it can correct in the next round.
- **Final summarise also fails** → user sees a fixed _"I gathered the data but
  couldn't compose a final summary"_ message.

---

## Career Manager (creator side)

These agents live under `/creator-agent/*` and are wired into the new
`web/app/creator/career-manager/page.tsx` tabs.

### Rate Calculator

`backend/services/rate_calculator_service.py` →
`POST /creator-agent/calculate-rate`. Deterministic formula, no LLM in the hot
path.

Inputs (also documented in `web/lib/api.ts::RateCalcInputs`):

- `platform` — `instagram | tiktok | youtube`
- `deliverable` — `reel | carousel | static | story | bundle | video |
  integration | dedicated | short`
- `quantity` — integer
- `usage` — `organic | paid_30d | paid_60d | reuse_brand | full_rights`
- `exclusivity` — `none | 30d | 60d | 90d | 180d`
- `add_story_bundle` — boolean

Multipliers are layered:

1. Per-platform base CPM × the creator's follower count.
2. Engagement multiplier (above-average engagement → premium).
3. City multiplier (Toronto is the calibration anchor; other cities scale
   relative to it).
4. Niche multiplier (beauty / fitness premium vs general lifestyle).
5. Usage multiplier (paid usage and reuse stack).
6. Exclusivity multiplier.

The response includes the full `breakdown` so the UI can show the brand
exactly _why_ the number is what it is. `market_range.low/high` (from
`local_market_service`) lets the UI render a comparison band.

The `quote_text` field is a copy-paste-ready paragraph the creator can DM the
brand. The Brand Agent can also use the same numbers via `get_local_benchmark`.

### Brief Evaluator

`backend/services/brief_evaluator_service.py` →
`POST /creator-agent/evaluate-brief`. Pipeline:

1. **Extract** — regex + small LLM call pull `brand_name`, `deliverables`,
   `offered_usd`, `usage`, `exclusivity`, `timeline`, `platform`, and key
   contractual clauses out of free-text.
2. **Red-flag** — second LLM pass surfaces things like _"no revision cap,"
   _"perpetual rights with no buyout,"_ or _"exclusivity longer than 90 days
   without a premium."_
3. **Rate-join** — feed the extracted shape into the Rate Calculator to compute
   the fair number for this creator.
4. **Verdict** — compare offered vs fair: `fair | below | lowball | no_offer`.
   Build a one-line headline (`"$400 is ~38% below fair — counter at $650"`).
5. **Counter draft** — a short reply the creator can paste, anchored to a
   specific counter number and one clarifying question.

### Voice / tone memory

`backend/services/tone_service.py`. The creator's tone fingerprint is a short
LLM-summarised description of how they actually write — pulled from captions
they paste during onboarding or refreshed on demand from
`POST /creator-agent/voice/refresh`. Stored on `Creator.voice_description`.

`VoiceProfileCard.tsx` surfaces the fingerprint on the creator dashboard so
they can see what the model thinks their voice is, and refresh it.

---

## Cross-cutting concerns

### Toronto-first

Toronto is the primary market. The conversation that produced this rewrite
included swapping demo data from Mumbai to Toronto:

- `data/seed_creators.json` — `@priyastyles` is now a Toronto-based beauty
  creator.
- `backend/models/neighbourhood.py` — Mumbai neighbourhood seeds removed.
  Toronto has 10 seeded neighbourhoods (Kensington Market, Yorkville, The
  Annex, Queen West, Distillery District, Leslieville, Little Italy,
  Roncesvalles, Beaches, King West).
- `web/components/MapView.tsx` — `CITY_COORDS` reordered with Toronto first.
  Old India coords are kept as a labelled legacy block so historical creator
  rows still pin correctly.
- `web/app/business/map/page.tsx::MAPPED_CITIES` — same reorder.
- Streamlit and design-bundle placeholders all reflect Toronto.

The Brand Agent's tool schemas already accept a `city` arg, so adding new
primary markets is a config-only change.

### Conversation history

`backend/models/agent_conversation.py`. One row per turn, scoped by `smb_id`
for the Brand Agent and `creator_id` for the Career Manager. `action_data` is
a JSON blob that drives action buttons (`creator_list`, `brief`, `outreach`)
and now also carries the `tool_trace` for the assistant turn that produced
it. The frontend hydrates the trace back from `action_data` when re-loading
history, so animations replay correctly.

### Proactive notifications

`backend/services/agent_chat_service.py::get_proactive_notifications`. On
session start the Brand Agent surfaces three classes of nudges:

- Outreach messages sent 5+ days ago with no reply.
- Closed campaigns with no logged results.
- New creators that appeared in the SMB's target city since their last login.

These render as a banner above the chat — kept silent if there's nothing.

### Layout / theme

Indigo → violet gradient (`#4F46E5 → #7C3AED → #8B5CF6`), Inter typeface,
`#FAFAFE` background, `#1E1B4B` ink. The animation primitives live in
`web/app/globals.css` (`animate-fade-up`, `animate-fade-in`, `animate-pop`,
`animate-count-glow`, `animate-gradient`, `skeleton-shimmer`). Anything new
should compose those, not introduce a new keyframe.

---

## Roadmap

These are queued but not built. Listed here so reviewers can sanity-check that
the current architecture won't paint us into a corner.

- **Server-sent tool trace streaming** — today the trace ships back atomically
  with the final reply. A small SSE upgrade would let the chips animate in as
  each tool returns, not after the whole loop.
- **Outreach Agent → tool** — the Outreach Agent is still a standalone
  endpoint. Folding it into the Brand Agent tool registry would let the LLM
  draft + send in one chain, with the brand-fact memory already injected.
- **Creator-side tool loop** — Career Manager chat is single-shot today. The
  same tool-loop pattern would let it chain Rate Calculator + Brief Evaluator
  + voice rewrite naturally.
- **Brand-fact reasoning** — `save_brand_fact` is fire-and-forget. Adding a
  small periodic consolidation pass (merge contradicting facts, demote stale
  ones) would keep the memory honest as it grows.
