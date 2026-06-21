# UzbekTrip — Editorial Standards

*Version 1.0 — June 2026*

Purpose: every piece of content — a city page, a sight, a news article, eventually a restaurant or hotel listing — should meet the same bar regardless of who wrote it. This document is that bar.

---

## 1. Content Types & Required Structure

### City pages (`CityPage`)
- **Tagline** (1 sentence, evocative, no clichés — see §5)
- **Description** (2–4 paragraphs): what the city is, why it matters historically, what a traveler should expect to feel/see
- **Body blocks**: at minimum one Image block and one Rich Text section beyond the description; Timeline block recommended for "suggested day plan"
- Every city page must link to at least 2 Sight pages and, once available, relevant Routes

### Sight pages (`SightPage`)
- **Tagline**: what makes this specific sight worth the detour
- **Excerpt** (300 char max): used in cards and meta description — must work standalone, not just a truncated first sentence
- **Practical fields are mandatory if known**: ticket price, opening hours, best time to visit. Write "Free" or "Check locally" rather than leaving blank — blank reads as unresearched.
- **UNESCO flag**: only tick if the specific site (not just the city) holds UNESCO designation — verify against the official UNESCO list, don't assume by association.

### News articles (`NewsArticle`)
- **Published date must be the actual publish date**, not the date you started drafting
- **Category must match content** — "Tourism News" for policy/industry changes, "Openings" only for genuinely new venues/attractions, not renovations
- **Primary city is required if the news is location-specific** — this drives the city page's "Latest News" feed; leaving it blank orphans the article from relevant traffic
- **Source attribution required** for any factual claim sourced from a press release, government announcement, or third-party report — use the `source_name`/`source_url` fields, don't bury it in body text

### Blog / Tips (`BlogPost`)
- Practical, evergreen content (SIM cards, transport, food guides) — not time-sensitive (that's News)
- Reading time must be a real estimate (≈200 words/minute), not a placeholder

### Restaurant / Hotel pages (when launched — see §7)
- Same rigor as Sight pages for practical fields (address, hours, price range)
- **Monetization disclosure is non-negotiable** — see §7

---

## 2. Fact-Checking & Accuracy

- **Prices, hours, and visa rules change.** Any page with a price, opening hour, or entry requirement needs a recorded "last verified" understanding — until we add a formal field for this, note the verification date in the Wagtail admin's internal notes, and re-check anything older than 6 months before it ships in a newsletter or gets promoted on the homepage.
- **Primary sources first.** Government tourism boards, UNESCO's own site, official venue websites — before travel blogs or aggregators.
- **Never invent specifics.** If you don't know the exact opening year of a madrasa, write "built in the 15th century" rather than fabricating "1417" to sound precise.
- **Visa and entry information is the highest-stakes content on the site** — a wrong answer here can strand a traveler at a border. Visa page changes require a second person to review before publishing, no exceptions.

---

## 3. Search & Real Sources

When researching with web search or AI assistance:
- Treat AI-generated drafts as a **first pass requiring verification**, not a publishable final. An AI can confidently state a wrong ticket price or a closed venue.
- Cross-check any specific number (price, distance, date, percentage) against at least one named, citable source before publishing.
- If a claim can't be verified, soften the language ("typically costs around") rather than stating a false precise figure.

---

## 4. Images

- **Every image needs real alt text** describing what's actually in the frame for accessibility and SEO — not "image1.jpg" or a repeat of the page title.
- **Attribution**: if an image isn't ours (commissioned/owned), the photographer/source must be credited — use the Image block's caption field.
- **No watermarked stock photos.** No AI-generated images presented as a real, specific, named location — readers are using these photos to recognize the place when they arrive.
- **Cover images are mandatory** for City, Sight, News, Blog, Restaurant, and Hotel pages — pages without one render visibly worse and lose the Open Graph social-share image.

---

## 5. Voice, Tone & Banned Phrases

Full brand voice guidance is in `brand-book.md` §6. Editorially, avoid:

- **Clichés**: "hidden gem," "off the beaten path," "a feast for the senses," "steeped in history," "breathtaking," "must-see" (says nothing — show *why*)
- **Exoticizing language**: "mysterious East," "exotic," "untouched," "like stepping back in time" — these flatten a living country into a backdrop. Uzbekistan has wifi, traffic, and TikTok; write about it as a real place, not a movie set.
- **Empty superlatives without support**: "the most beautiful X in the world" needs a reason attached, or cut it
- **Second-person command overload**: vary "you must visit" with more confident, declarative writing

---

## 6. AI-Assisted Content Policy

- AI tools (including this one) may be used for drafting, structuring, and research assistance.
- **All factual claims must be human-verified before publishing** — see §3.
- AI-generated images are not used as if they were real photographs of real places. If illustrative graphics are ever needed, label them clearly as illustrations.
- A human editor is the named author of record (`author_name` field) and is accountable for the page's accuracy, even when AI assisted the draft.

---

## 7. Monetization & Affiliate Disclosure (Eat & Stay — Phase 3)

Restaurant and Hotel pages carry monetization fields (`booking_url`, `is_partner`) specifically so commercial relationships are structurally separated from editorial judgment:

- **`is_partner` must be ticked any time `booking_url` is an affiliate or paid link.** The template automatically shows a "Partner listing — we may earn a commission" disclosure badge when this is set — never disable or hide this badge.
- **Editorial inclusion is never for sale.** A restaurant or hotel becomes a partner *after* it qualifies editorially (real visit/research, genuine recommendation) — paying for placement does not get a listing onto the site, and does not get it favorable copy it hasn't earned.
- **Disclosure language is required in-content**, not just the badge — see the "This is a paid partner link" note already wired into the templates.
- This mirrors FTC-style disclosure norms and should be treated as a legal requirement, not a style preference, once Eat/Stay go live.

---

## 8. Localization (EN / RU / UZ)

- The brand name "UzbekTrip" is never translated.
- Translations should be reviewed by a fluent speaker before publishing, not shipped as raw machine translation — wagtail-localize's DeepL integration is a first draft tool, not a final-copy tool.
- Practical information (prices, phone formats, addresses) should be localized in *convention*, not just language — e.g. date formats, currency formatting per locale.

---

## 9. Pre-Publish Checklist

Before moving any page from Draft to Published:

- [ ] Tagline/excerpt reads well standalone (used in cards + meta description)
- [ ] Cover image set, with real alt text
- [ ] All practical fields filled or explicitly marked "Free"/"Check locally" — not blank
- [ ] At least one internal link to a related page (city ↔ sight ↔ route ↔ news)
- [ ] No banned phrases from §5
- [ ] Factual claims verified per §3
- [ ] If Eat/Stay: `is_partner` flag correctly set per §7
- [ ] SEO description present (falls back to excerpt, but a hand-written one outperforms the fallback)
