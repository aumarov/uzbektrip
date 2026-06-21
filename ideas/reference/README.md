# Reference Materials

These are the original brief documents provided at project kickoff and again when requesting the brand book — kept here for traceability, since `brand-book.md` and `editorial-standards.md` were written against them.

- `uzbekguide-homepage.html` — the original homepage design mockup (placeholder brand "UzbekGuide", before the project was renamed to UzbekTrip). The current production templates (`templates/home/home_page.html`, `static/css/main.css`) are the implemented, evolved version of this mockup.
- `uzbekistan-tourism-website-guide.md` — the original full development blueprint (architecture, SEO plan, content strategy, launch phases). Several of its recommendations (wagtail-localize, the 5 ad-slot layout, the SEOMixin pattern, the phased launch plan) are implemented as designed; a few (Dokploy/Docker deployment, wagtail-seo package, Meilisearch, Celery) were superseded by decisions made during actual implementation — check the live codebase, not this document, for current architecture.
