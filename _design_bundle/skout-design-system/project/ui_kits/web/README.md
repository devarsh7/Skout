# Skout Web — UI Kit

Pixel-faithful recreation of the Skout Streamlit web app, ported to JSX components so they can be composed into any mock.

## What's in here

| File | Role |
| --- | --- |
| `index.html` | Click-through prototype: Home → Discover → Filter → Outreach → Campaigns → Creator Onboarding |
| `Navbar.jsx` | Sticky, blurred navbar with logo + links + CTA |
| `Footer.jsx` | Brand block + page links + bottom row |
| `Hero.jsx` | Hero band with fade-up animated h1 (word-by-word reveal) + CTAs + status |
| `SectionHeader.jsx` | Eyebrow + title + lead triplet used across every page |
| `FeatureCard.jsx` | Icon + title + description card (used in "How it works" + mission) |
| `Button.jsx` | Primary / outline / ghost / icon-only |
| `Badge.jsx` | Eyebrow pill + niche chip + status dot |
| `Input.jsx` | Text input, textarea, chip multiselect, select |
| `CreatorCard.jsx` | Discovery/Filter result — 3-column layout with match score |
| `PageHeader.jsx` | The banded header used on all sub-pages |
| `MissionQuote.jsx` | Blue-faint mission block |
| `OutreachForm.jsx` | Compact AI-outreach drafting surface |
| `CampaignsTable.jsx` | Creator directory table |

## Using a component

```jsx
<Button variant="primary" icon="search">Discover Creators</Button>
<CreatorCard creator={{...}} score={0.91} reason="..." />
<Hero
  eyebrow="✦ AI-Powered Creator Discovery"
  title={['Find the right creators.', 'In plain English.']}
  accentLine={1}  // which line renders in blue
/>
```

## Source fidelity

Every spacing value, shadow, border radius, and color comes from `frontend/utils/styles.py` with two intentional deviations:

1. **Fonts swapped Inter → Poppins/Open Sans** per brand direction.
2. **Emoji CTAs → Lucide icons** where higher fidelity matters. Emoji still accepted on page-title headers per Streamlit routing constraint.

Everything else is 1:1 with the live code.
