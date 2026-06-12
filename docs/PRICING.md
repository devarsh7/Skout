# Skout — Pricing

Two pricing surfaces live in this product, and they often get conflated. This
document covers both.

1. **Skout's pricing to its customers** — what brands pay Skout to use the
   platform. Three tiers, stubbed in `backend/api/billing.py`.
2. **The pricing the platform helps creators quote to brands** — what the Rate
   Calculator outputs. This is the more interesting surface and the one the
   Career Manager rewrite is built around.

---

## 1. Platform tiers (what brands pay Skout)

Pricing is in USD, billed monthly, with annual at -15%. All tiers include the
core discovery + filtering + map UI and the Brand Agent chat.

### Free — $0

Designed so an SMB owner can answer _"would this work for my one campaign?"_
without committing money.

- 10 natural-language searches per month
- 5 AI-drafted outreach messages per month
- Read-only access to the Toronto creator index
- Single seat, no API access

### Pro — $49 / month

The line where the agent starts being more useful than a freelancer.

- 500 searches per month
- Unlimited outreach drafts
- Saved searches + saved creator lists
- Campaign tracker with outreach pipeline (Kanban)
- Brand-fact memory enabled (the Brand Agent remembers your budget,
  preferences, constraints between sessions)
- Local benchmark tool (`get_local_benchmark`) wired into the agent
- Email support

### Agency — $199 / month

For people running campaigns for other people.

- Everything in Pro
- Up to 5 seats
- API access (rate-limited, usage-based overage)
- CSV export of any creator list or campaign
- Priority support
- White-label option (add-on)

### Implementation notes

- Stripe is stubbed in `backend/api/billing.py` and commented pending prod
  rollout. Webhook handlers route to `User.subscription_status`.
- Tier limits are enforced in `backend/core/limits.py` (search quota counts
  against the calendar month).
- Free → Pro upgrade should be a one-click in the dashboard, not a sales call.
  Pro → Agency goes through the sales modal because we want to capture seat
  count and use-case.
- Pricing is anchored in USD because Canadian SMB buyers price-shop in USD for
  SaaS already; we surface CAD-equivalent at checkout but don't bill in CAD.

---

## 2. Creator quotes (what the Rate Calculator outputs)

This is the methodology the Career Manager's Rate Calculator uses. It's also
what the Brand Agent quotes when it calls `get_local_benchmark`.

### Inputs

The creator (or the brand asking on their behalf) supplies:

- Platform — Instagram, TikTok, or YouTube.
- Deliverable — reel, carousel, static, story, bundle, video, integration,
  dedicated, short.
- Quantity — usually 1, sometimes a bundle (2 reels + 4 stories, etc.).
- Usage — `organic`, `paid_30d`, `paid_60d`, `reuse_brand`, `full_rights`.
- Exclusivity window — none, 30, 60, 90, or 180 days.
- Optional `add_story_bundle` flag — adds the standard 2-story support package.

We also pull the creator's followers and engagement from the SQL row, plus the
city × niche benchmark from `local_market_service`.

### Formula

```
base       = platform_cpm[platform] × followers / 1000
adjusted   = base
             × engagement_multiplier(creator.engagement_rate, niche_baseline)
             × city_multiplier[creator.city]
             × niche_multiplier[creator.primary_niche]
per_unit   = adjusted × deliverable_weight[deliverable]
subtotal   = per_unit × quantity
             × usage_multiplier[usage]
             × exclusivity_multiplier[exclusivity]
quote_usd  = round_to_50(subtotal)
```

Every multiplier is exposed in `breakdown` on the response, so the UI
(`web/components/career/RateCalculator.tsx`) can render a "why this number"
breakdown rather than a black box.

### Platform CPMs (calibration anchors)

These are the base CPMs used as starting points. They're not Skout's opinion
of fair pay — they're the median observed in our index for the platform.
Multipliers do the actual work.

| Platform | Base CPM (USD) |
| --- | --- |
| Instagram | $18 |
| TikTok | $14 |
| YouTube | $25 |

### City multipliers

Toronto is the calibration anchor at 1.00. Other cities scale relative to
Toronto rates.

| City | Multiplier | Notes |
| --- | --- | --- |
| Toronto | 1.00 | Anchor |
| Vancouver | 0.95 | Slightly thinner brand-spend market |
| Montreal | 0.90 | French-market creators trade off reach for niche fit |
| New York | 1.45 | Premium market, high competition |
| Los Angeles | 1.30 | Talent-heavy, brand budgets follow |
| London | 1.20 | GBP-anchored, USD-converted |
| Sydney | 0.90 | Smaller addressable brand pool |
| Berlin | 0.85 | Strong creators, conservative spend |
| Singapore | 1.05 | Premium APAC hub |
| Tokyo | 1.00 | Niche-dependent; defaults to anchor |
| _Other_ | 0.85 | Fallback when no calibration row exists |

These are stored as a config dict in `rate_calculator_service.py`. Override
them in `core/config.py` for A/B tests.

### Niche multipliers

| Niche | Multiplier |
| --- | --- |
| beauty | 1.15 |
| fitness | 1.10 |
| food | 1.05 |
| fashion | 1.10 |
| tech | 1.20 |
| business | 1.25 |
| travel | 0.95 |
| lifestyle | 1.00 |
| pets | 0.95 |
| sustainability | 1.00 |
| _other_ | 0.95 |

Tech and business carry a premium because the audience converts at higher
dollar values — brands accept that and pay for it.

### Usage multipliers

| Usage | Multiplier |
| --- | --- |
| organic | 1.00 |
| paid_30d | 1.40 |
| paid_60d | 1.65 |
| reuse_brand | 1.50 |
| full_rights | 2.20 |

These stack on top of exclusivity. A brand that wants both `paid_60d` _and_
`90d exclusivity` pays both multipliers. The agent will say so out loud.

### Exclusivity multipliers

| Window | Multiplier |
| --- | --- |
| none | 1.00 |
| 30d | 1.10 |
| 60d | 1.20 |
| 90d | 1.35 |
| 180d | 1.65 |

### Engagement adjustment

Engagement multiplier is continuous, not bucketed:

```
multiplier = clamp(0.75, 1.50,  1 + 0.6 × (engagement − niche_baseline) / niche_baseline)
```

A creator at 2x their niche baseline lands at ~1.45×. A creator at half the
baseline lands at 0.85×. The clamp prevents either extreme from breaking the
quote.

### Story bundle add-on

If `add_story_bundle = true`, we add a flat `0.18 × per_unit` to the subtotal
before multipliers. This is the calibrated cost of "two supporting stories
the same day as the reel" — almost always worth it for brands and creators
both, so we surface it as a single checkbox.

### Rounding

Quotes are rounded to the nearest $50. Brands and creators both find round
numbers easier to negotiate against, and the multiplier stack is precise
enough that the implied accuracy of $1378.42 is misleading.

### Worked example

A Toronto beauty creator (@priyastyles, 124K followers, 4.82% engagement) is
quoting 1 Instagram reel + 2 supporting stories for a paid_30d usage with no
exclusivity.

```
base                = 18 × 124000 / 1000           = 2232.00
engagement_mult     = 1 + 0.6 × (4.82 − 4.00) / 4.00 = 1.123
city_mult (Toronto) = 1.00
niche_mult (beauty) = 1.15
per_unit_after_mults = 2232.00 × 1.123 × 1.00 × 1.15 = 2882.92
reel_weight         = 0.40
per_unit_reel       = 2882.92 × 0.40                = 1153.17
story_bundle add-on = 0.18 × per_unit_reel          = 207.57
subtotal            = (1153.17 + 207.57) × 1        = 1360.74
usage (paid_30d)    = × 1.40                        = 1905.04
exclusivity (none)  = × 1.00                        = 1905.04
rounded             = $1900
```

The response also returns `market_range: { low: 1500, high: 2300 }` from the
benchmark service so the UI can render the comparison band.

---

## 3. Brief Evaluator verdict thresholds

The Brief Evaluator joins extracted offer numbers against the Rate Calculator
output. The verdict is decided by the `ratio = offered / fair`:

| Ratio | Verdict | Headline tone |
| --- | --- | --- |
| `≥ 0.95` | `fair` | _"$X is in the fair range — accept or negotiate scope."_ |
| `0.75 ≤ ratio < 0.95` | `below` | _"$X is ~Y% under fair — counter at $Z."_ |
| `< 0.75` | `lowball` | _"$X is significantly under fair — counter or pass."_ |
| `null` (no offer) | `no_offer` | _"No price stated — ask for one before discussing scope."_ |

`counter_draft` is anchored to the rounded fair number. It also includes one
clarifying question (usage, timeline, or rights) so the reply moves the deal
forward rather than just naming a number.

---

## 4. Notes on this document

This document was generated as part of the Brand Agent rewrite + Toronto-first
rollout. The conversation that produced it explicitly asked for `docs/AGENTS.md`
and `docs/PRICING.md` as the wrap-up artefact, so this file is one half of that
deliverable. The other half is `docs/AGENTS.md`.

The numbers in this document are calibration anchors, not promises. When the
calibration data changes (because we have more creators, or a new market goes
live), update the multiplier tables here in the same PR that updates
`rate_calculator_service.py` — keeping the two in sync is the only way the
quotes stay defensible.
