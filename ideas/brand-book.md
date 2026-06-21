# UzbekTrip — Brand Book

*Version 1.0 — June 2026*

---

## 1. Brand Positioning

**What we are:** The most complete, independently-written travel guide to Uzbekistan — built for the moment Uzbekistan became one of the fastest-growing tourism destinations on earth (+73% growth vs. 2019, UN Tourism 2025).

**The gap we fill:** Existing Uzbekistan tourism sites are dated, government-run, or thin SEO content farms. UzbekTrip is the first portal built with the production quality, photography, and structured depth that travelers already expect from guides to Japan, Italy, or Morocco.

**One-line positioning:** *"Uzbekistan, the way travelers actually need it — by city, not by category."*

**Audience:** International independent travelers (FIT — Free Independent Travelers) in the research and booking phase, aged 25–55, planning a first or second trip to Central Asia. Secondary audience: travel agents and tour operators sourcing structured city/route content.

**Competitive set:** Lonely Planet country pages, Trip.com destination guides, VisitUzbekistan.travel (the official government site — we're more current and more usable), TengriGuide (regional reference point).

**What we are not:** A booking engine, a forum, or a listicle farm. Every page should read like it was written by someone who has actually stood in the Registan at sunrise.

---

## 2. Logo

Located in `ideas/logo/`:

| File | Use |
|---|---|
| `icon-mark.svg` | App icon, favicon, social avatar — dark lapis background |
| `icon-mark-on-cream.svg` | Same icon, light background variant |
| `logo-horizontal-dark.svg` | Primary lockup — site nav, dark UI, video intros |
| `logo-horizontal-light.svg` | Primary lockup — print, partner decks, light UI |

**The mark:** An 8-pointed girih star — the geometric motif found in the tilework of the Registan, Shah-i-Zinda, and Ichon-Qala. It is not a generic globe-and-pin travel-logo cliché; it is specific to the region we cover, and it scales cleanly from a 16px favicon to a banner.

**Construction:** Icon mark + wordmark, separated by 14px minimum clear space (measured as the icon's own radius). Never stretch, rotate, recolor outside the approved palette, or place the wordmark above/below the icon — horizontal lockup only.

**Minimum size:** Icon mark alone: 16px. Horizontal lockup: 120px wide (below this, drop to icon-only).

**Don'ts:**
- Don't recreate the star with rounded corners or fewer/more than 8 points
- Don't place the dark lockup on any background lighter than `--lapis-mid` (#2B5499) — contrast fails
- Don't add a drop shadow, outline, or gradient to the mark
- Don't translate "UzbekTrip" — the brand name stays Latin-script across EN/RU/UZ; only surrounding copy is translated

---

## 3. Color System

These are the production CSS variables (`static/css/main.css`) — the brand book and the codebase share one source of truth.

| Token | Hex | Use |
|---|---|---|
| `--lapis` | `#1A3A6B` | Primary brand color — nav, headers, dark sections. Named for lapis lazuli, historically mined in the region and used to color Silk Road tilework blue. |
| `--lapis-mid` | `#2B5499` | Secondary blue — links, hover states |
| `--gold` | `#C9A84C` | Accent — badges, CTAs, the star mark. Evokes Registan's gilded madrasa interiors. |
| `--gold-light` | `#E8C96D` | Lighter accent — headlines on dark backgrounds, hover states |
| `--turquoise` | `#2AABB8` | Tertiary accent — used sparingly (category tags, dome-blue callouts) |
| `--terracotta` | `#C4612A` | Warm accent — Eat section, food content, warning-adjacent UI |
| `--cream` | `#FAF6EE` | Page background — desert sand / aged paper, never pure white |
| `--ink` | `#1A1510` | Primary text, footer background |
| `--muted` | `#6B6258` | Secondary text, captions, metadata |
| `--border` | `#E8DFD0` | Hairlines, card borders |

**Rule of thumb:** Lapis and cream carry 80% of every page. Gold is a spotlight color — used for one or two focal points per screen (a badge, a CTA, a headline accent), never as a fill for large areas. Terracotta is reserved for Eat/food contexts so the category has its own visual identity once it launches.

---

## 4. Typography

| Role | Font | Where |
|---|---|---|
| Display / headlines | **Cormorant Garamond** (serif, weights 400/600/700, italic) | H1–H3, hero text, pull quotes, logo wordmark |
| Body / UI | **DM Sans** (weights 300/400/500/600) | Paragraphs, nav, buttons, forms, metadata |

**Why this pairing:** Cormorant Garamond has the editorial, slightly classical weight of a travel magazine masthead — it reads as written-by-humans, not generated-by-template. DM Sans is a clean geometric sans that keeps long-form practical content (visa rules, SIM card prices) legible and modern. The contrast between the two is the brand's typographic signature — don't introduce a third typeface.

**Usage rules:**
- Headlines: Cormorant Garamond, weight 700, occasional italic for emphasis within a headline (e.g. *"Discover *Uzbekistan*"*)
- Body copy: DM Sans 400, line-height 1.6–1.8 for readability in long-form city/sight descriptions
- Labels, badges, nav: DM Sans 500/600, uppercase, letter-spacing 0.05–0.12em
- Never set body copy in Cormorant Garamond — it's a display face only, legibility drops at small sizes

---

## 5. Imagery Style

- **Subject:** Architecture and people over abstract landscape. The Registan at golden hour outperforms a generic desert shot every time.
- **Color grading:** Warm, slightly desaturated — avoid oversaturated HDR "Instagram filter" looks. Skies should look like skies, not neon.
- **Composition:** Wide environmental shots for hero/cover images; close, human-scale shots (market stalls, craftspeople, food) for in-article imagery.
- **People:** Always with informed consent context implied — candid, not staged-tourist-in-frame shots. Local people doing local things, not travelers posing.
- **Aspect ratios:** 16:9 for article covers, 4:3 for city cards, 1:1 for gallery thumbnails — matches the grid system already built into the templates.
- **Never use:** Stock photos with visible watermarks, AI-generated images presented as real locations (see Editorial Standards §6), or images that don't match the actual content (a Bukhara photo on a Samarkand page).

---

## 6. Voice & Tone

**We sound like:** A well-traveled friend who's done the research, not a brochure and not a Reddit thread.

- **Confident, not breathless.** "The Registan is the single best reason to visit Samarkand" — not "OMG you HAVE to see this AMAZING place!!"
- **Specific over generic.** "Madrasas built 1417–1660" beats "ancient and historic."
- **Practical without being dry.** Visa rules and SIM card prices get the same care as the poetic intro — readers came here to actually plan a trip.
- **Respectful of the culture we're covering.** We are guests writing about a host country; avoid exoticizing language ("mysterious," "exotic," "untouched") that flattens Uzbekistan into a backdrop.

See `editorial-standards.md` for the full content style guide.

---

## 7. Application Examples

- **Nav bar:** Dark lapis, gold-light wordmark, white nav links — already live in `templates/base.html`
- **Category badges:** Gold-on-cream pill badges, uppercase, letter-spaced — see `.news-cat-badge` in `static/css/main.css`
- **CTAs:** Gold fill for primary actions, outline-white for secondary — `.btn-primary` / `.btn-outline`
- **Section dividers:** Lapis full-width bands (Practical strip, Visa banner) break up long cream-background scroll — don't overuse, max 2–3 per page

---

## 8. File Index

```
ideas/
├── brand-book.md              ← this file
├── editorial-standards.md
└── logo/
    ├── icon-mark.svg
    ├── icon-mark-on-cream.svg
    ├── logo-horizontal-dark.svg
    └── logo-horizontal-light.svg
```

Production-ready raster exports (`logo.png`, `favicon-32.png`, `apple-touch-icon.png`) live in `static/img/` and should be regenerated from these SVGs whenever the mark changes, to keep brand book and shipped assets in sync.
