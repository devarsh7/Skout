# Skout Design System

> A platform that helps SMBs and creators find each other.
> Influencers onboard themselves; brands discover them in plain English;
> a multi-agent AI layer handles matching, filtering, and outreach drafting.

**Brand voice:** *trust & hope.* A clean, bright, blue-forward aesthetic with an owl as the wisdom/insight mark.

---

## Product context

Skout is the home of owned, opt-in creator data. The core value prop is:

1. **Creators onboard themselves** → Skout builds an owned dataset (no scraping, no third-party APIs).
2. **Brands search in plain English** → a Discovery Agent returns semantically-ranked creators.
3. **Filter pipeline** refines by platform, followers, engagement, location, language.
4. **Outreach Agent** drafts personalized first-touch messages.
5. **Campaigns** view tracks onboarded creators and outreach status.

### Surfaces represented in the current codebase

| Surface | File | Role |
| --- | --- | --- |
| Marketing home | `frontend/streamlit_app.py` | Hero + "How it works" + Mission + CTAs |
| Creator onboarding | `frontend/pages/1_🎤_Creator_Onboarding.py` | Multi-section self-serve form |
| Discover Influencers | `frontend/pages/2_🔍_Discover_Influencers.py` | NL search → creator cards |
| Filter & Refine | `frontend/pages/3_🎯_Filter_and_Refine.py` | Structured filter panel → creator cards |
| AI Outreach | `frontend/pages/4_✉️_AI_Outreach.py` | Draft-a-message workflow |
| Campaigns | `frontend/pages/5_📊_Campaigns.py` | Directory + contact reveal |
| Creator result card | `frontend/components/creator_card.py` | Shared result component |
| Shared styles | `frontend/utils/styles.py` | Navbar, footer, CSS vars (primary source) |

### Sources reviewed

- **Codebase:** `frontend/` (read-only, mounted). The `utils/styles.py` file is the ground truth for colors, spacing rhythm, shadows, card shapes, button shapes, form styles, and navbar/footer patterns. Everything in this design system was lifted from there or harmonised with it.
- **No Figma provided.**
- **No slide templates provided.**

---

## CONTENT FUNDAMENTALS

Skout's copy sounds like **a knowledgeable friend who built the tool they wished existed**. Never salesy, never breathless — confident that the product does what it says.

### Voice — trust & hope

- **Reassuring, not hype-y.** Emphasise owned data, opt-in, control. "Creators control what brands see about them." "No scraping, no ToS violations, no surprise API bills."
- **Plain-English, not jargon-first.** Even when the tech is sophisticated (LangGraph, Pinecone, multi-agent), the user-facing copy says *"Ask in plain English. The Discovery Agent handles the rest."*
- **Optimistic utility.** Hope comes from framing: *"puts creators in the driver's seat"*, *"find the right creators"*, *"get discovered by brands that actually fit."*

### Tone & grammar

- **Second person.** Talks *to* the user: "you", "your brief", "your creators". Brand voice uses "we" sparingly.
- **Sentence case.** Headings are sentence case with occasional accent-word capitalization via color, not caps. (`Find the right creators. In plain English.`)
- **Short sentences. Specific numbers.** "In under two minutes." "10k–100k followers." "5 seconds."
- **Em dashes and colons for rhythm.** "Two sides. One seamless workflow." "Built on trust. Powered by AI."
- **Eyebrow labels ALL CAPS + tracked.** "HOW IT WORKS", "OUR MISSION", "GET STARTED". These are the only uppercase text in the system.

### Buttons and CTAs

Buttons lead with an emoji glyph + action verb:
- `🎤 Join as Creator`  ·  `🔍 Discover Creators`  ·  `🚀 Run Discovery Agent`
- `✨ Draft message`  ·  `🎯 Run Filtering Agent`  ·  `📇 View contact`

Primary button uses sentence case + first-person creator framing when relevant ("✨ Create my creator profile").

### Examples

| Good | Why |
| --- | --- |
| *"Find the right creators. In plain English."* | Promise + differentiator, 7 words |
| *"Ask in plain English. The Discovery Agent handles the rest."* | Tells user what to do and what it does |
| *"Creators onboard themselves — brands search in natural language."* | Two sides explained in one line |
| *"Built on trust. Powered by AI."* | Rhythm, balance, the mission in 6 words |

### Emoji & glyphs

- **Used deliberately** as iconography substitutes on CTAs, eyebrow prefixes, and step cards (🎤 🔍 🎯 ✉️ 📊 🔒 🧠 ✨ 🚀 ✦ 🛰️).
- Never decorative. Each emoji stands in for an icon and should be replaced with a proper SVG icon (Lucide `mic`, `search`, `target`, etc.) when higher fidelity is needed. See `ICONOGRAPHY` below.
- The satellite (🛰️) is the current stand-in for the brand mark; the target end state is the **owl** mark described in the Iconography section.

### Things to avoid

- Em-dash soup or too-clever metaphors. Skout is direct.
- Exclamation points (except *"Profile created!"* after success states).
- Buzzwords without substance. If you say "AI", the next sentence explains which agent, what it does.
- Purple/pink startup gradients across large surfaces. The one violet-blue gradient is reserved for the 3-word `Powered by AI` text accent.

---

## VISUAL FOUNDATIONS

### Color

- **Primary family: Skout Blue.** A full 50→900 blue scale driven by `--blue-600 (#2563EB)` as the CTA / accent color.
- **Ink family: slate.** `--navy #0F172A` for headings, `--body #334155` for paragraphs, `--muted #64748B` for secondary, `--subtle #94A3B8` for tertiary/labels.
- **Surface family:** pure white `#FFFFFF`, alt background `#F8FAFD`, soft blue page gradient from `#EEF4FF → #FFFFFF`.
- **Borders:** always `#E2E8F0` (neutral) or `rgba(37,99,235,0.14)` (brand-tinted). Never heavy black.
- **Semantic:** success `#16A34A`, warning `#F59E0B`, danger `#DC2626`, info = blue-600.
- **Restraint.** Accent purple (`#7C3AED`) appears *only* inside the `Powered by AI` text gradient. Nowhere else.

### Typography

- **Headings: Poppins** (400/500/600/700/800/900). Geometric, friendly, approachable — matches the creator-forward voice.
- **Body: Open Sans** (400/500/600/700). Industry standard for UI — trustworthy, readable at small sizes.
- **Mono: system UI-mono stack** for IDs and code chips.
- Headings use tight letter-spacing (`-0.03em` / `-0.035em` for display). Body is comfortable at `line-height 1.7-1.8`.
- Fluid type on display + h1; everything else fixed.

> **Substitution note:** the live `frontend/utils/styles.py` currently loads Inter for everything. Per brand direction (Poppins/Open Sans), the design system tokens use Poppins + Open Sans. If you want the production code updated, flag it and we'll PR `styles.py`.

### Spacing & layout

- **4px base scale.** Tokens 1–24 (4px → 96px). Major section rhythm uses `--section-y: 5.5rem` (88px).
- **Gutters are fluid:** `clamp(1.5rem, 8vw, 7rem)` for content, `clamp(1.5rem, 6vw, 5rem)` for the navbar.
- **Full-bleed sections** alternate `--bg-page` (white) and `--bg-alt` (`#F8FAFD`), separated by 1-px `--border` divider lines. The hero alone uses a blue radial + linear gradient.
- **Max content width** is handled implicitly by gutters; there's no fixed container — the page breathes on wide screens.

### Backgrounds

- **Hero only:** radial ellipse `#DBEAFE` at 50% -10% over a vertical gradient `#EEF4FF → #F5F9FF → #FFFFFF`. Light, airy, blue-tinted.
- **Mission block:** flat `--blue-50` with a 1px `--blue-100` border.
- **Everywhere else:** flat white or flat `--bg-alt`. No patterns, no noise textures, no hand-drawn illustrations. Skout is a clean modern product, not a craft brand.
- **Imagery treatment** (when added) should be bright, high-key, daylight-warm but cool-biased — sky blues, window light, clean studio backgrounds. Never moody/grainy/B&W.

### Animation & motion

- **Scroll-staged entry.** Hero elements fade-up with 0s / 0.1s / 0.2s delays (`@keyframes fadeInUp`). Cards fade-up with 0.5s duration. Badges just fade in.
- **The brief calls for per-heading word-by-word reveal** — this is implemented in the UI kit hero as a `WordReveal` component (staggered 60ms per word). Use only on the hero h1 and major section opener; not everywhere.
- **Timing:** `160ms` for micro-interactions, `220ms` standard, `500ms` card entrance, `700ms` hero. Easing is `cubic-bezier(0.16, 1, 0.3, 1)` for natural motion.
- **No bounces, no elastic.** Skout feels calm and competent, not playful.
- **Status dot** pulses (`blink 2s ease infinite`) only for live backend indicators.

### Hover states

- **Buttons:** translate `-1px` (nav CTA) or `-2px` (hero buttons), shadow intensifies from `--shadow-blue` → a larger 0.28-opacity blue shadow. Background shifts primary → `--blue-700`.
- **Outline buttons:** background fills to `--blue-50`, border darkens to `rgba(37,99,235,0.35)`.
- **Cards:** border shifts `--border` → `--blue-100`, shadow grows `--shadow-sm` → `--shadow-md`, translate `-3px`.
- **Nav links:** background fills to `--bg-alt`, color darkens muted → navy.

### Press states

Not explicitly styled in the codebase. Default approach: drop translate back to `0`, reduce shadow slightly (same-color but smaller). Never shrink beyond `scale(0.98)`.

### Borders

- Default `1px solid var(--border)` (`#E2E8F0`).
- Inputs use `1.5px` for tactile heft.
- Brand-tinted: `1px solid rgba(37,99,235,0.14)` on outline buttons, `1px solid var(--blue-100)` on blue-faint containers.
- **No border-only left-accent cards.** No colored-left-border info boxes. (AI-slop alert.)

### Shadows / elevation

A two-track system:

| Token | Use |
| --- | --- |
| `--shadow-xs` | Inputs at rest |
| `--shadow-sm` | Cards at rest, forms |
| `--shadow-md` | Cards hover |
| `--shadow-lg` | Floating surfaces (menus, modals) |
| `--shadow-blue` | Primary button rest |
| `--shadow-blue-lg` | Primary button hover |
| `--ring-blue` | Focus ring (`0 0 0 3px rgba(37,99,235,0.15)`) |

No inner shadows. No glow effects. Shadows are always slate-black with low alpha, never colored except the intentional blue CTA shadow.

### Corner radii

- **Pills / badges / eyebrow chips:** `999px` (full pill).
- **Buttons:** `8-9px` (`--radius-sm` / `--radius-md`).
- **Inputs:** `8px`.
- **Cards:** `14-16px` (`--radius-lg` / `--radius-xl`).
- **Mission / hero blocks:** `20px` (`--radius-2xl`).
- Nothing perfectly circular except avatars and status dots.

### Transparency & blur

- **Navbar only** uses blur: `background: rgba(255,255,255,0.92)` + `backdrop-filter: blur(16px)`. This is the *signature effect* — do not apply blur elsewhere.
- No frosted-glass cards, no translucent overlays on images.

### Protection gradients vs capsules

When text sits on top of a hero gradient, Skout relies on the **light background** to carry contrast rather than a darkening scrim. Capsules (`badge`, `pill`) are used to call out status and eyebrow labels — not as protection for overlaid text.

### Layout rules

- **Sticky navbar** (`position: sticky; top: 0; z-index: 1000`) with 62px height.
- **Fixed elements:** none other than the navbar. No floating CTAs, no sticky chat bubbles.
- **Section pattern:** eyebrow label → section title → sub-copy (max 560px) → content grid. Consistent across every page.

### Cards

- `border: 1px solid var(--border)` — `border-radius: 16px` — `padding: 2rem` — `box-shadow: --shadow-sm`.
- Hover lifts them 3px with a blue-tinted border and `--shadow-md`.
- Card content order: icon/glyph → title → description. Never reversed.

### Success tells (how to know it's "Skout")

1. Blue-tinted light hero with fade-up animation on the h1.
2. `Eyebrow Label` above every section title (blue, caps, tracked).
3. White + `--bg-alt` section alternation divided by 1px lines.
4. Emoji-led CTAs with blue-shadow lift.
5. Cards with 16px radius, subtle shadow, blue hover border.
6. The only gradient text is a 3-word "Powered by AI" accent in the mission line.

---

## ICONOGRAPHY

The current codebase uses **emoji as iconography** (🎤 🔍 🎯 ✉️ 📊 🔒 🧠 ✨ 🚀 ✦ 🛰️). This is pragmatic for a Streamlit prototype but **not a long-term pattern.**

### Target system: Lucide (stroke icons)

- **Library:** [Lucide](https://lucide.dev) — linked via CDN in UI kits. 24×24, 1.75px stroke, `stroke-linecap: round`, `stroke-linejoin: round`.
- **Color:** `currentColor` so icons inherit the enclosing text color. Default is `--navy` inside content and `--muted` on nav / metadata.
- **Sizes:** 16 (inline), 20 (buttons), 24 (card headers), 32 (feature tiles), 48+ (hero ornaments).
- **Weight consistency:** always the 1.75px stroke. Never mix filled and stroked versions in the same view.

### Emoji → Lucide mapping

| Emoji | Lucide | Where it appears |
| --- | --- | --- |
| 🎤 | `mic` | Creator onboarding |
| 🔍 | `search` | Discovery |
| 🎯 | `target` | Filter & Refine |
| ✉️ | `mail` | AI Outreach |
| 📊 | `bar-chart-3` | Campaigns |
| 🔒 | `lock` | Owned data mission card |
| 🧠 | `brain` | Multi-agent AI mission card |
| ✨ | `sparkles` | "Create my profile", "Draft message" |
| 🚀 | `rocket` | "Run Discovery Agent" |
| ✦  | `sparkles` (outline) | Eyebrow mark |
| 📇 | `contact` | View contact |
| 🛰️ | `satellite` | *(placeholder)* logo mark — **will be replaced by the owl** |

### The owl (brand mark)

Skout's brand symbol is an **owl** — wisdom and insight. A placeholder `assets/logo-skout-owl.svg` and full wordmark `assets/logo-skout-wordmark.svg` are included. These are simple geometric placeholders in Skout Blue; **before production we need the real owl mark from a brand designer.** Flag and request.

### SVG vs PNG

- All iconography is SVG (inline or via Lucide script). No PNG icons in the system.
- Product imagery (hero photos, creator avatars) will be PNG/JPG when added — but none are present in the codebase today.

### Emoji usage going forward

Emoji remain acceptable for:
- Page titles in Streamlit route filenames (platform requirement).
- Balloons animation on success (`st.balloons()`).
- Inline chips in user-generated content.

They are **not acceptable** for production component buttons or nav items. Replace with Lucide.

### Unicode as icons

`✦` (four-pointed star, eyebrow prefix) is the one intentional unicode glyph. Everything else is emoji or Lucide.

---

## Index — what's in this folder

```
/
├── README.md                    ← you are here
├── SKILL.md                     ← agent-invocable skill manifest
├── colors_and_type.css          ← CSS tokens: colors, type, spacing, radii, shadows
├── fonts/                       ← Poppins + Open Sans (Google Fonts; loaded via @import)
├── assets/
│   ├── logo-skout-owl.svg       ← placeholder owl mark
│   ├── logo-skout-wordmark.svg  ← full lockup
│   └── favicon.svg
├── preview/                     ← design-system tab cards (auto-registered)
├── ui_kits/
│   └── web/
│       ├── index.html           ← click-through prototype of the Skout marketing + app
│       ├── README.md            ← kit usage + component list
│       └── *.jsx                ← Navbar, Hero, Card, CreatorCard, PageHeader, Footer …
└── slides/                      ← (none — no deck template was provided)
```

### Key files for agents

1. **`colors_and_type.css`** — import this in every HTML artifact for Skout. It pulls Poppins/Open Sans from Google Fonts and declares every CSS variable.
2. **`ui_kits/web/`** — the JSX components to compose into mocks.
3. **`SKILL.md`** — entry point when this folder is used as a Claude Skill.
