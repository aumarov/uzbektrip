# Launch Plan & Section Toggles

## Phase 1 (live now)
Cities, Sights, Routes, Visa & Entry, Practical, News, Blog/Tips.

## Phase 3 (when ready to monetize)
Eat (Restaurants) and Stay (Hotels) — built and deployed, but switched **off** by
default so they don't go live with thin or unverified content. Restaurant and
Hotel pages already carry the monetization fields (`booking_url`, `is_partner`)
needed for affiliate/booking-commission revenue — see `editorial-standards.md` §7
for the disclosure rules that apply once they're switched on.

## How to switch a category on or off

In the Wagtail admin: **Settings → Sections**. Untick a box and the category
disappears from the nav and footer, and every page in it returns a 404 —
no need to unpublish pages one by one.

| Category | Admin field | Default |
|---|---|---|
| Cities | `show_cities` | On |
| Sights | `show_sights` | On |
| Eat (Restaurants) | `show_eat` | **Off** |
| Stay (Hotels) | `show_stay` | **Off** |
| Routes | `show_routes` | On |
| Visa & Entry | `show_visa` | On |
| Practical | `show_practical` | On |
| News | `show_news` | On |
| Blog / Tips | `show_blog` | On |

## How to turn on an ad placement

**Settings → Ad Placements** — five slots matching the original blueprint
(leaderboard, mid-page, article-inline, sidebar, footer). Paste your ad
network's embed code into a slot, tick **Enabled**, save. Leaving a slot off
(or on with empty code) renders nothing — no empty placeholder boxes ship to
production.

## Before flipping Eat or Stay on

1. Populate at least a handful of real Restaurant/Hotel pages per launched city
2. Confirm every partner listing has `is_partner` ticked where a commission applies (§7 of editorial standards)
3. Spot-check the disclosure badge renders correctly on a sample page
4. Then: Settings → Sections → tick `show_eat` / `show_stay` → Save
