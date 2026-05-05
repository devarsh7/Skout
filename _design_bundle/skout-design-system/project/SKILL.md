# Skout Design System

A design system for Skout — an AI-powered platform that helps SMBs and creators find each other through semantic search and multi-agent workflows. Trust-and-hope brand voice, blue-forward palette, owl mark.

## When to use this skill

Invoke this skill whenever you're designing something for Skout — marketing pages, onboarding flows, creator discovery UI, outreach tooling, campaign dashboards, slides, or internal product surfaces. Use it as the source of truth for colors, type, spacing, components, and voice.

## How to use it

**1. Import the tokens.** Every HTML artifact you produce for Skout must start with:

```html
<link rel="stylesheet" href="colors_and_type.css">
```

(adjust the path as needed). This pulls in Poppins + Open Sans from Google Fonts and declares every CSS variable — colors, type scale, spacing, radii, shadows.

**2. Compose with the web kit.** For React/JSX prototypes, load `ui_kits/web/kit.css` and import the JSX components from `ui_kits/web/`:

- `Primitives.jsx` — `Button`, `IconButton`, `Eyebrow`, `Pill`, `StatusDot`, `Avatar`, `Card`
- `Chrome.jsx` — `Navbar`, `Footer`
- `Fields.jsx` — `TextField`, `Select`, `Textarea`, `RangeField`, `CheckboxRow`
- `CreatorCard.jsx` — the shared creator result card (avatar, handle, niche, match score, reveal CTA)
- `Sections.jsx` — Hero, How-It-Works, Mission, Feature sections
- `App.jsx` — the composed marketing + app walkthrough

Open `ui_kits/web/index.html` to see every component in context.

**3. Respect the voice.** See `README.md` § CONTENT FUNDAMENTALS. Short version: trust-and-hope, plain-English, never hype-y. Emphasise owned-data, opt-in, control. Creators are the protagonists — brands discover them, not the other way around.

## Key rules

- **Primary color: `var(--blue-600)` (#2563EB).** Use it for CTAs, links, and the logo dot. Don't invent new blues.
- **Type: Poppins (display) + Open Sans (body).** Do not swap to Inter, Roboto, or system fonts.
- **Iconography: Lucide.** Include via `<script src="https://unpkg.com/lucide@latest"></script>` and call `lucide.createIcons()` after render. Do not use emoji for production buttons/nav.
- **One intentional unicode glyph:** `✦` as the eyebrow prefix. Everything else is Lucide.
- **Cards:** 16–20px radius, `var(--shadow-card)`, white background, 1px `var(--border)` stroke.
- **Buttons:** 8px radius, 600 weight, never uppercase. Primary = filled blue; secondary = outline; ghost = transparent.
- **Spacing rhythm:** 4 / 8 / 12 / 16 / 24 / 32 / 48 / 64 / 96 px — use the `--sp-*` variables.
- **No gradients as CTAs.** Skout uses flat blue. Gradients only appear in the hero background wash.

## What's in this folder

```
/
├── README.md                ← full system writeup (read this first)
├── SKILL.md                 ← this file
├── colors_and_type.css      ← CSS tokens (import this first)
├── assets/
│   ├── logo-skout-owl.svg
│   ├── logo-skout-wordmark.svg
│   └── favicon.svg
├── preview/                 ← design-system tab cards
└── ui_kits/
    └── web/                 ← JSX components + index.html showcase
```

## Common tasks

- **New marketing page** → start from `ui_kits/web/index.html`, keep the Navbar + Footer, compose sections with `SectionHeader` + `Card` + `Button`.
- **Creator search result** → use `<CreatorCard />` unchanged. It carries the canonical layout.
- **Onboarding form** → use `Fields.jsx` primitives; group in `Card`; keep single-column on mobile.
- **Slide deck** → no deck template exists yet. Use the `deck_stage.js` starter component, import `colors_and_type.css`, and treat slides as composed `Card`/`SectionHeader` layouts.

## Things NOT in this system

- No dark mode. Everything is light, blue-forward.
- No mobile-app UI kit (Skout is web-first today).
- No illustration library — use real creator photography placeholders when imagery is needed.
- No video/motion system — keep entry animations subtle (fade + 18px rise, ~600ms).

See `README.md` for full context, content-voice guidance, color/type scales, and component details.
