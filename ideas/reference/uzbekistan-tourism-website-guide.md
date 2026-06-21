# UzbekGuide — Tourism Website: Full Development Blueprint

## 1. Vision & Competitive Positioning

After reviewing TengriGuide (your reference), VisitUzbekistan.travel, Lonely Planet, and Trip.com, the best tourism portals share:

- **City-first navigation** — travelers think in destinations, not categories
- **Visual-led hierarchy** — stunning photography drives dwell time
- **Practical depth** — visa, SIM, transport, currency in one place
- **Multi-language** — at minimum EN + RU + UZ, expandable at any time via admin
- **Mobile-first** — 62% of travel searches are mobile
- **Fast content delivery** — lazy images, WebP, CDN

**Your unique angle**: Uzbekistan is one of the **7 fastest-growing tourism destinations globally (2025, UN Tourism)** with 73% growth vs 2019. A modern, well-optimized portal fills a real gap — most existing Uzbekistan tourism sites are dated.

---

## 2. Site Architecture

```
UzbekGuide/
├── Home (/)
│   ├── Hero: "Discover Uzbekistan — The Silk Road Reborn"
│   ├── Featured cities grid
│   ├── Top experiences carousel
│   ├── Latest articles/tips
│   ├── Ad slot #1 (leaderboard, above fold)
│   └── Ad slot #2 (sidebar / mid-page banner)
│
├── Cities (/cities/)
│   ├── Tashkent (/cities/tashkent/)
│   ├── Samarkand (/cities/samarkand/)
│   ├── Bukhara (/cities/bukhara/)
│   ├── Khiva (/cities/khiva/)
│   ├── Nukus (/cities/nukus/)
│   ├── Fergana (/cities/fergana/)
│   └── Shakhrisabz (/cities/shakhrisabz/)
│
├── Each City Page (e.g. /cities/samarkand/)
│   ├── Hero + intro
│   ├── Sights & Attractions
│   ├── Restaurants & Cafés
│   ├── Hotels & Guesthouses
│   ├── Shopping & Souvenirs
│   ├── Activities & Entertainment
│   ├── Day Routes / Itineraries
│   ├── Getting There & Around
│   ├── Local Events & Festivals
│   └── Ad slots #3 and #4
│
├── Visa & Entry (/visa/)
│   ├── Visa-free countries list
│   ├── e-Visa application guide
│   ├── Border crossing info
│   └── FAQ (schema.org FAQPage)
│
├── Practical Info (/practical/)
│   ├── SIM & eSIM guide
│   ├── Currency & payment (UZS)
│   ├── Transport (trains, taxis, Yandex Go)
│   ├── Health & safety
│   ├── Weather & best time to visit
│   └── Cultural etiquette
│
├── Routes & Itineraries (/routes/)
├── Blog & Tips (/blog/)
└── Advertise (/advertise/) [internal]
```

### Advertisement Placement (5 slots)

| Slot | Location | Size | Type |
|------|----------|------|------|
| #1 | Homepage top leaderboard | 970×90 | Sticky banner |
| #2 | Homepage mid-page | 728×90 | Display |
| #3 | City page mid-content | 728×90 | Inline banner |
| #4 | City/blog page sidebar | 300×250 | Display |
| #5 | Blog/article page inline | 300×250 | Native-style |

---

## 3. Django + Wagtail Architecture

### Project Structure

```
uzbekguide/
├── config/
│   ├── settings/
│   │   ├── base.py
│   │   ├── production.py   # Dokploy env
│   │   └── local.py
│   ├── urls.py
│   └── wsgi.py
│
├── apps/
│   ├── home/               # Homepage
│   ├── cities/             # City pages
│   ├── destinations/       # Attractions, hotels, restaurants
│   ├── practical/          # Visa, SIM, transport
│   ├── routes/             # Itineraries
│   ├── blog/               # Articles & tips
│   ├── ads/                # Ad slot management
│   └── core/               # Shared models, SEO mixin
│
├── templates/
│   ├── base.html           # All SEO meta lives here
│   ├── home/
│   ├── cities/
│   └── ...
│
├── static/
│   ├── css/
│   ├── js/
│   └── img/
│
└── media/                  # Served via Cloudflare R2 / S3
```

### Key Wagtail Page Models

```python
# apps/cities/models.py

from wagtail.models import Page, Locale
from wagtail.fields import StreamField, RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.routable_page.models import RoutablePageMixin
from wagtail.search import index
from django.db import models


class CityIndexPage(Page):
    """Lists all cities — one per locale, created by Wagtail Localize"""
    intro = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+'
    )
    content_panels = Page.content_panels + [
        FieldPanel('intro'),
        FieldPanel('hero_image'),
    ]
    subpage_types = ['cities.CityPage']


class CityPage(RoutablePageMixin, Page):
    """Individual city guide page — fully translatable"""

    # Core fields
    tagline = models.CharField(max_length=255, blank=True)
    description = RichTextField()
    hero_image = models.ForeignKey(
        'wagtailimages.Image', null=True,
        on_delete=models.SET_NULL, related_name='+'
    )

    # SEO fields (separate from Wagtail's built-in promote_panels)
    og_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text="Social share image — 1200×630px recommended"
    )
    twitter_card_type = models.CharField(
        max_length=20,
        choices=[
            ('summary', 'Summary (small image)'),
            ('summary_large_image', 'Summary with Large Image'),
        ],
        default='summary_large_image'
    )

    # Geographic data for schema.org TouristDestination
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    # Structured content sections via StreamField
    body = StreamField([
        ('sights',      SightsBlock()),
        ('restaurants', RestaurantBlock()),
        ('hotels',      HotelBlock()),
        ('shopping',    ShoppingBlock()),
        ('transport',   TransportBlock()),
        ('events',      EventsBlock()),
        ('ad_slot',     AdSlotBlock()),
        ('rich_text',   RichTextBlock()),
        ('gallery',     GalleryBlock()),
        ('map',         MapBlock()),
        ('faq',         FAQBlock()),          # Generates FAQPage schema
    ], use_json_field=True)

    search_fields = Page.search_fields + [
        index.SearchField('description'),
        index.SearchField('tagline'),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('tagline'),
            FieldPanel('hero_image'),
            FieldPanel('description'),
        ], heading="City Info"),
        FieldPanel('body'),
        MultiFieldPanel([
            FieldPanel('latitude'),
            FieldPanel('longitude'),
        ], heading="Map / Location"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('og_image'),
            FieldPanel('twitter_card_type'),
        ], heading="Social Media / SEO"),
    ]

    parent_page_types = ['cities.CityIndexPage']
    subpage_types = ['destinations.DestinationPage']

    def get_schema_ld(self):
        """Returns schema.org JSON-LD dict for this city"""
        data = {
            "@context": "https://schema.org",
            "@type": "TouristDestination",
            "name": self.title,
            "description": self.search_description or self.tagline,
            "url": self.full_url,
        }
        if self.latitude and self.longitude:
            data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(self.latitude),
                "longitude": str(self.longitude),
            }
        if self.og_image:
            data["image"] = self.og_image.get_rendition('fill-1200x630').url
        return data
```

---

## 4. Admin-Managed Locale System

This is a core architectural decision. The goal is: **editors add new languages through the Wagtail admin without any code deployment.**

### 4.1 Installation

```bash
pip install wagtail-localize
```

```python
# settings/base.py

INSTALLED_APPS = [
    # Wagtail core
    'wagtail.contrib.search_promotions',
    'wagtail.contrib.settings',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.sitemaps',

    # Localization — ORDER MATTERS
    'wagtail_localize',
    'wagtail_localize.locales',   # replaces wagtail.locales

    'wagtail.snippets',
    'wagtail.documents',
    'wagtail.images',
    'wagtail.search',
    'wagtail.admin',
    'wagtail',

    # Django i18n
    'django.contrib.contenttypes',
    ...
]

# Enable Wagtail's internationalisation feature
WAGTAIL_I18N_ENABLED = True

# Define the INITIAL set of languages.
# New locales are added by editors in the admin — no settings change needed.
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ('en', 'English'),
    ('ru', 'Русский'),
    ('uz', "O'zbek"),
]

# Default language
LANGUAGE_CODE = 'en'

# Django's URL i18n middleware (handles /ru/... /uz/... prefixes)
MIDDLEWARE = [
    'django.middleware.locale.LocaleMiddleware',
    ...
]
```

```python
# config/urls.py
from django.conf.urls.i18n import i18n_patterns
from wagtail.contrib.sitemaps.views import sitemap

urlpatterns = [
    path('sitemap.xml', sitemap),          # Non-localised
    path('robots.txt', robots_txt_view),
]

urlpatterns += i18n_patterns(
    path('', include(wagtail_urls)),        # /en/ /ru/ /uz/ etc.
    prefix_default_language=False,          # /  == English (no /en/ prefix)
)
```

### 4.2 How an Editor Adds a New Language (Zero Code)

1. Go to **Settings → Locales → Add locale** in the Wagtail admin
2. Select the language code (e.g. `zh` for Chinese, `de` for German)
3. Click **Sync translated pages** — Wagtail Localize creates translated copies of all existing pages as drafts
4. Use the built-in **translation editor** or submit to machine translation (DeepL)
5. Publish — the new locale is live at `/zh/cities/samarkand/` etc.

No `settings.py` edit, no deployment, no developer needed.

### 4.3 Machine Translation (Optional but Recommended)

```python
# settings/base.py

WAGTAILLOCALIZE_MACHINE_TRANSLATOR = {
    "CLASS": "wagtail_localize.machine_translators.deepl.DeepLTranslator",
    "OPTIONS": {
        "AUTH_KEY": env("DEEPL_API_KEY"),
    },
}

# Alternatively, Google Cloud Translation:
# "CLASS": "wagtail_localize.machine_translators.google.GoogleCloudTranslator",
# "OPTIONS": {"PROJECT_ID": env("GOOGLE_CLOUD_PROJECT_ID")}
```

With this in place, an editor can click **"Machine translate"** on any page and get an instant draft translation in any language DeepL supports, ready to review and publish.

### 4.4 LANGUAGES setting vs Wagtail Locales

There is one subtle point: Django's `LANGUAGES` setting controls which language codes are *valid* in URL patterns. If an editor adds a locale that isn't in `LANGUAGES`, the URL prefix (`/zh/`) won't resolve.

**Best practice: keep LANGUAGES broad** with all plausible future languages, and use Wagtail Locales to control which ones are *actually active*:

```python
# settings/base.py — permissive list covering future expansion
LANGUAGES = [
    ('en',  'English'),
    ('ru',  'Русский'),
    ('uz',  "O'zbek"),
    ('zh',  '中文'),
    ('de',  'Deutsch'),
    ('fr',  'Français'),
    ('ar',  'العربية'),
    ('ko',  '한국어'),
    ('ja',  '日本語'),
    ('tr',  'Türkçe'),
    ('fa',  'فارسی'),
]

# Wagtail only activates the ones an editor creates in Settings → Locales.
# This list is just the maximum possible set.
WAGTAIL_CONTENT_LANGUAGES = LANGUAGES
```

---

## 5. Complete SEO Meta Implementation

### 5.1 The Full `<head>` — base.html

This covers every modern SEO and social requirement in one place:

```html
{# templates/base.html #}
{% load wagtailcore_tags wagtailimages_tags i18n %}

<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE }}"
      {% if LANGUAGE_BIDI %}dir="rtl"{% endif %}>
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">

  {# ── CORE SEO ────────────────────────────────────────────── #}
  <title>{% block title %}{{ page.seo_title|default:page.title }} — UzbekGuide{% endblock %}</title>
  <meta name="description"
        content="{% block meta_desc %}{{ page.search_description }}{% endblock %}">
  <meta name="robots"
        content="{% block robots %}index, follow{% endblock %}">

  {# Canonical — always the default-locale URL to avoid duplicate content #}
  <link rel="canonical" href="{{ page.full_url }}">

  {# ── HREFLANG (auto-generated from Wagtail Localize) ────── #}
  {% for translation in page.get_translations.live %}
    <link rel="alternate"
          hreflang="{{ translation.locale.language_code }}"
          href="{{ translation.full_url }}">
  {% endfor %}
  {# x-default points to English version #}
  <link rel="alternate" hreflang="x-default" href="{{ page.full_url }}">

  {# ── OPEN GRAPH (Facebook, LinkedIn, WhatsApp, Telegram) ── #}
  <meta property="og:site_name"    content="UzbekGuide">
  <meta property="og:locale"       content="{{ LANGUAGE_CODE|replace:'-','_' }}">
  <meta property="og:type"         content="{% block og_type %}website{% endblock %}">
  <meta property="og:title"        content="{% block og_title %}{{ page.seo_title|default:page.title }}{% endblock %}">
  <meta property="og:description"  content="{% block og_desc %}{{ page.search_description }}{% endblock %}">
  <meta property="og:url"          content="{{ page.full_url }}">
  {% block og_image %}
    {% if page.og_image %}
      {% image page.og_image fill-1200x630 format-webp as og_img %}
      <meta property="og:image"         content="{{ request.scheme }}://{{ request.get_host }}{{ og_img.url }}">
      <meta property="og:image:width"   content="1200">
      <meta property="og:image:height"  content="630">
      <meta property="og:image:alt"     content="{{ page.title }}">
      <meta property="og:image:type"    content="image/webp">
    {% endif %}
  {% endblock %}

  {# Article-specific OG (for blog pages) #}
  {% block og_article %}{% endblock %}

  {# ── TWITTER / X CARDS ───────────────────────────────────── #}
  {# summary_large_image is correct for most pages; set per-page via admin #}
  <meta name="twitter:card"        content="{% block tw_card %}{{ page.twitter_card_type|default:'summary_large_image' }}{% endblock %}">
  <meta name="twitter:site"        content="@uzbekguide">
  <meta name="twitter:creator"     content="@uzbekguide">
  <meta name="twitter:title"       content="{% block tw_title %}{{ page.seo_title|default:page.title }}{% endblock %}">
  <meta name="twitter:description" content="{% block tw_desc %}{{ page.search_description }}{% endblock %}">
  {% block tw_image %}
    {% if page.og_image %}
      {% image page.og_image fill-1200x630 format-webp as tw_img %}
      <meta name="twitter:image"     content="{{ request.scheme }}://{{ request.get_host }}{{ tw_img.url }}">
      <meta name="twitter:image:alt" content="{{ page.title }}">
    {% endif %}
  {% endblock %}

  {# ── SCHEMA.ORG JSON-LD ──────────────────────────────────── #}
  {# Website-level (every page) #}
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "UzbekGuide",
    "url": "{{ request.scheme }}://{{ request.get_host }}",
    "inLanguage": "{{ LANGUAGE_CODE }}",
    "potentialAction": {
      "@type": "SearchAction",
      "target": {
        "@type": "EntryPoint",
        "urlTemplate": "{{ request.scheme }}://{{ request.get_host }}/search?q={search_term_string}"
      },
      "query-input": "required name=search_term_string"
    }
  }
  </script>

  {# Breadcrumb (every page except homepage) #}
  {% if breadcrumbs %}
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "BreadcrumbList",
    "itemListElement": [
      {% for crumb in breadcrumbs %}
      {
        "@type": "ListItem",
        "position": {{ forloop.counter }},
        "name": "{{ crumb.title }}",
        "item": "{{ crumb.url }}"
      }{% if not forloop.last %},{% endif %}
      {% endfor %}
    ]
  }
  </script>
  {% endif %}

  {# Page-type specific schema (overridden in child templates) #}
  {% block schema_ld %}{% endblock %}

  {# ── PERFORMANCE ─────────────────────────────────────────── #}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="dns-prefetch" href="//cdn.uzbekguide.uz">
  <link rel="preload" as="image"
        href="{% block hero_img_preload %}{% endblock %}">

  {# Favicon set #}
  <link rel="icon" type="image/svg+xml" href="/static/img/favicon.svg">
  <link rel="icon" type="image/png" sizes="32x32" href="/static/img/favicon-32.png">
  <link rel="apple-touch-icon" href="/static/img/apple-touch-icon.png">
  <link rel="manifest" href="/static/manifest.webmanifest">
  <meta name="theme-color" content="#1A3A6B">

  {# ── CSS ──────────────────────────────────────────────────── #}
  {% block extra_css %}{% endblock %}
</head>
```

### 5.2 City Page Template — Schema Override

```html
{# templates/cities/city_page.html #}
{% extends "base.html" %}
{% load wagtailimages_tags %}

{% block og_type %}place{% endblock %}

{% block schema_ld %}
<script type="application/ld+json">
{{ page.get_schema_ld|json_script:"" }}
</script>
{% endblock %}

{% block hero_img_preload %}
  {% if page.hero_image %}
    {% image page.hero_image fill-1440x600 format-webp as hero %}{{ hero.url }}
  {% endif %}
{% endblock %}
```

### 5.3 Blog / Article Page — Extra Meta

```python
# apps/blog/models.py
from wagtail.models import Page
from django.db import models

class BlogPost(Page):
    author_name  = models.CharField(max_length=200)
    author_twitter = models.CharField(max_length=50, blank=True,
        help_text="@handle without the @")
    published_date = models.DateField()
    updated_date   = models.DateField(null=True, blank=True)
    reading_time   = models.PositiveIntegerField(default=5,
        help_text="Estimated minutes")
    ...
```

```html
{# templates/blog/blog_post.html #}
{% extends "base.html" %}

{% block og_type %}article{% endblock %}

{% block og_article %}
  <meta property="article:published_time" content="{{ page.published_date|date:'c' }}">
  {% if page.updated_date %}
  <meta property="article:modified_time"  content="{{ page.updated_date|date:'c' }}">
  {% endif %}
  <meta property="article:author"         content="{{ page.author_name }}">
  <meta property="article:section"        content="Travel">
  <meta property="article:tag"            content="Uzbekistan">
{% endblock %}

{% block tw_card %}summary_large_image{% endblock %}
{% block tw_title %}{{ page.title }}{% endblock %}
{% if page.author_twitter %}
  {# Override twitter:creator for articles with a named author #}
  {% block tw_creator %}<meta name="twitter:creator" content="@{{ page.author_twitter }}">{% endblock %}
{% endif %}

{% block schema_ld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "headline": "{{ page.title }}",
  "description": "{{ page.search_description }}",
  "datePublished": "{{ page.published_date|date:'c' }}",
  "dateModified": "{{ page.updated_date|default:page.published_date|date:'c' }}",
  "author": {
    "@type": "Person",
    "name": "{{ page.author_name }}"
  },
  "publisher": {
    "@type": "Organization",
    "name": "UzbekGuide",
    "logo": {
      "@type": "ImageObject",
      "url": "{{ request.scheme }}://{{ request.get_host }}/static/img/logo.png"
    }
  },
  "image": "{% if page.og_image %}{% image page.og_image fill-1200x630 format-webp as ai %}{{ request.scheme }}://{{ request.get_host }}{{ ai.url }}{% endif %}",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ page.full_url }}"
  },
  "timeRequired": "PT{{ page.reading_time }}M",
  "inLanguage": "{{ LANGUAGE_CODE }}"
}
</script>
{% endblock %}
```

### 5.4 Visa & Practical Pages — FAQ Schema

```html
{# If the page has an FAQ StreamField block, this fires automatically #}
{% block schema_ld %}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {% for faq in page.faq_items %}
    {
      "@type": "Question",
      "name": "{{ faq.question }}",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "{{ faq.answer|striptags }}"
      }
    }{% if not forloop.last %},{% endif %}
    {% endfor %}
  ]
}
</script>
{% endblock %}
```

### 5.5 Complete SEO Mixin (Reusable Across All Page Types)

```python
# apps/core/seo.py

from wagtail.admin.panels import FieldPanel, MultiFieldPanel, ObjectList, TabbedInterface
from django.db import models


class SEOMixin(models.Model):
    """
    Add to any Page model to get the full SEO panel.
    Usage:
        class CityPage(SEOMixin, Page):
            promote_panels = SEOMixin.seo_panels
    """

    og_image = models.ForeignKey(
        'wagtailimages.Image', null=True, blank=True,
        on_delete=models.SET_NULL, related_name='+',
        help_text="Social share image — 1200 × 630 px. Shown on Facebook, LinkedIn, WhatsApp, Telegram."
    )
    twitter_card_type = models.CharField(
        max_length=30,
        choices=[
            ('summary',             'Summary (small square image)'),
            ('summary_large_image', 'Summary with Large Image (recommended)'),
        ],
        default='summary_large_image',
        help_text="Controls how the link appears when shared on X (Twitter)."
    )
    noindex = models.BooleanField(
        default=False,
        help_text="Tick to prevent search engines from indexing this page (e.g. thank-you pages)."
    )
    canonical_url = models.URLField(
        blank=True,
        help_text="Override canonical URL — leave blank to use the page's own URL."
    )

    seo_panels = Page.promote_panels + [
        MultiFieldPanel([
            FieldPanel('og_image'),
            FieldPanel('twitter_card_type'),
        ], heading="Social Media Sharing"),
        MultiFieldPanel([
            FieldPanel('noindex'),
            FieldPanel('canonical_url'),
        ], heading="Advanced SEO"),
    ]

    class Meta:
        abstract = True
```

### 5.6 Wagtail SEO Package (Recommended Alternative)

Instead of the custom mixin you can also use **`wagtail-seo`** (by Kalob Taulien), which adds all of the above through a polished admin UI out of the box:

```bash
pip install wagtail-seo
```

```python
INSTALLED_APPS += ['wagtailseo']

# In your page models:
from wagtailseo.models import SeoMixin

class CityPage(SeoMixin, RoutablePageMixin, Page):
    seo_image_sources = ['og_image', 'hero_image']  # fallback chain
    seo_description_sources = ['search_description', 'tagline', 'description']
    ...
```

`wagtail-seo` automatically generates all OG, Twitter Card, and schema.org tags from a single unified admin panel, with fallback chains so no page ever has a missing meta tag.

---

## 6. Core Web Vitals Optimization

Target thresholds (2026):
- **LCP** < 2.5 s
- **INP** < 200 ms
- **CLS** < 0.1

### Images (biggest LCP impact)

```html
{# Hero image: eager, preloaded, sized explicitly to prevent CLS #}
{% image page.hero_image fill-1440x600 format-webp as hero %}
<img src="{{ hero.url }}"
     width="1440" height="600"
     alt="{{ page.title }} — hero"
     loading="eager"
     fetchpriority="high"
     decoding="sync">

{# All other images: lazy #}
{% image item.image fill-600x400 format-webp as thumb %}
<img src="{{ thumb.url }}"
     width="600" height="400"
     alt="{{ item.title }}"
     loading="lazy"
     decoding="async">
```

### Caching

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env("REDIS_URL"),
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
        "TIMEOUT": 3600,  # 1 hour default
    }
}

# Per-view cache decorators
from django.views.decorators.cache import cache_page

@cache_page(60 * 60)    # City pages: 1 hour
@cache_page(60 * 5)     # Blog index: 5 minutes
```

### Static Assets

```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE = ['whitenoise.middleware.WhiteNoiseMiddleware', ...]
```

### Database — Avoid N+1

```python
cities = CityPage.objects.live().select_related(
    'hero_image', 'locale'
).prefetch_related(
    'translations'
).order_by('title')
```

---

## 7. Multilingual — How It All Works Together

```
Editor creates locale "zh" in admin
         ↓
Wagtail Localize creates draft copies of all pages in Chinese
         ↓
Editor reviews / machine-translates via DeepL
         ↓
Pages published at /zh/cities/samarkand/ etc.
         ↓
base.html auto-generates hreflang tags for all live translations
         ↓
Google indexes each language version independently
```

### Language Switcher in Frontend

```html
{# nav partial — shows only active/live locales #}
{% for locale in page.get_translations.live %}
  <a href="{{ locale.full_url }}"
     hreflang="{{ locale.locale.language_code }}"
     {% if locale.locale == page.locale %}aria-current="true"{% endif %}>
    {{ locale.locale.get_display_name }}
  </a>
{% endfor %}
```

This switcher is fully dynamic — no hardcoding. When a new locale is published, it automatically appears in the nav.

---

## 8. Dokploy Deployment

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    command: gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
    env_file: .env
    depends_on: [db, redis]

  db:
    image: postgres:16-alpine
    volumes: [postgres_data:/var/lib/postgresql/data]
    environment:
      POSTGRES_DB: uzbekguide
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes

  nginx:
    image: nginx:alpine
    ports: ["80:80", "443:443"]
    volumes:
      - ./nginx/uzbekguide.conf:/etc/nginx/conf.d/default.conf
      - static_volume:/app/staticfiles
    depends_on: [web]

volumes:
  postgres_data:
  static_volume:
```

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    libjpeg-dev libpng-dev libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
```

### requirements.txt

```
Django==5.1.*
wagtail==6.3.*
wagtail-localize==1.9.*
wagtail-seo==2.*            # Full SEO panel with OG + Twitter + schema
gunicorn==22.*
psycopg2-binary==2.9.*
django-redis==5.4.*
whitenoise==6.7.*
django-storages[boto3]==1.14.*
Pillow==10.*
django-environ==0.11.*
celery==5.*
```

### Nginx Config

```nginx
server {
    listen 80;
    server_name uzbekguide.uz www.uzbekguide.uz;

    gzip on;
    gzip_types text/plain text/css application/json application/javascript image/svg+xml;
    gzip_min_length 1024;

    location /static/ {
        alias /app/staticfiles/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        # Recommended: serve via Cloudflare R2 instead
        alias /app/media/;
        expires 30d;
    }

    location / {
        proxy_pass http://web:8000;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

---

## 9. Content Strategy

### Cities (priority order by tourist traffic)

1. **Samarkand** — Registan, Shah-i-Zinda, Gur-e-Amir, Ulugbek Observatory
2. **Bukhara** — Kalon Minaret, Ark Citadel, Lyab-i-Hauz, Chor Minor
3. **Tashkent** — Khast Imam, Chorsu Bazaar, Metro art stations
4. **Khiva** — Ichon-Qala (UNESCO), Juma Mosque, Kalta Minor
5. **Shakhrisabz** — Ak-Saray Palace

### Highest-Intent Search Queries (write these first)

- "Uzbekistan visa free countries 2025"
- "Uzbekistan e-visa guide"
- "Ucell vs Beeline SIM card Uzbekistan"
- "Tashkent airport to city center"
- "Best time to visit Uzbekistan"
- "Currency exchange Uzbekistan UZS"
- "Afrosiyob train Tashkent Samarkand"

### Unique Content Pillars

- Silk Road historical context for each monument
- Photography tips & golden hour times per location
- Local food guides with Uzbek/Russian dish names
- Festival calendar (Navruz, Bukhara Biennale, Sharq Taronalari)
- Per-city budget breakdown templates

---

## 10. Recommended Packages & Tools

| Purpose | Package / Tool |
|---------|----------------|
| CMS | wagtail 6.x |
| i18n & admin-managed locales | wagtail-localize 1.9+ |
| Full SEO meta (OG, Twitter, schema) | wagtail-seo 2.x |
| Machine translation | DeepL API via wagtail-localize |
| Search | Meilisearch + meilisearch-python |
| Maps | Leaflet.js (no API cost) |
| Image CDN | Cloudflare R2 + Images |
| Caching | Redis via django-redis |
| Task queue | Celery + Redis |
| Analytics | Plausible + GA4 |
| Monitoring | Sentry |
| Forms | django-crispy-forms |
| Content Security Policy | django-csp |

---

## 11. SEO Checklist Before Launch

### Technical
- [ ] HTTPS enforced everywhere
- [ ] robots.txt: disallow `/admin/`, `/django-admin/`, include sitemap URL
- [ ] XML sitemap at `/sitemap.xml`, submitted to Google Search Console
- [ ] Locale-specific sitemaps (auto-generated by wagtail-localize)
- [ ] 301 redirects for any URL changes
- [ ] Canonical URLs on all pages
- [ ] Breadcrumb nav implemented (HTML + schema.org)

### Meta Tags
- [ ] Unique `<title>` (50–60 chars) on every page
- [ ] Unique `<meta description>` (150–160 chars) on every page
- [ ] `<meta name="robots">` — never `noindex` on live content pages
- [ ] Hreflang tags auto-generated from active Wagtail locales
- [ ] `x-default` hreflang pointing to English version

### Open Graph
- [ ] `og:title`, `og:description`, `og:url`, `og:image` on all pages
- [ ] OG image is 1200×630 px, served via HTTPS
- [ ] `og:type` = `article` on blog posts, `place` on city pages
- [ ] `article:published_time` and `article:modified_time` on blog posts

### Twitter / X Cards
- [ ] `twitter:card` = `summary_large_image` on all content pages
- [ ] `twitter:site` set to @uzbekguide handle
- [ ] `twitter:image` matches OG image (same URL)
- [ ] Test with X Card Validator: https://cards-dev.twitter.com/validator

### Schema.org
- [ ] `WebSite` + `SearchAction` on every page
- [ ] `TouristDestination` on all city pages
- [ ] `TouristAttraction` on all sight/destination pages
- [ ] `LocalBusiness` on hotels, restaurants
- [ ] `Article` on all blog posts
- [ ] `FAQPage` on visa/practical pages
- [ ] `BreadcrumbList` on all non-homepage pages
- [ ] Validate with: https://validator.schema.org

### Images & Performance
- [ ] All images served as WebP
- [ ] Hero images: `loading="eager" fetchpriority="high"`
- [ ] All below-fold images: `loading="lazy" decoding="async"`
- [ ] Explicit `width` and `height` on every `<img>` (prevents CLS)
- [ ] Core Web Vitals green on PageSpeed Insights (mobile)
- [ ] LCP < 2.5s, INP < 200ms, CLS < 0.1

### Content
- [ ] All images have descriptive `alt` attributes
- [ ] Internal linking between city pages and their destinations
- [ ] No orphan pages (every page reachable from nav or sitemap)
- [ ] Google Analytics 4 + Search Console connected

---

## 12. Development Phases

### Phase 1 — Foundation (Month 1–2)
- Django + Wagtail + wagtail-localize + wagtail-seo setup
- Dokploy pipeline, Docker, Nginx, Redis
- Homepage + 3 city pages (Samarkand, Bukhara, Tashkent)
- Visa & practical info pages
- Full SEO base.html with all meta tags
- English only — but locale system ready to extend

### Phase 2 — Content (Month 2–3)
- All 7 city pages with destinations
- 20+ destination sub-pages
- Blog with 10 starter articles
- Russian translation via admin (no code change)

### Phase 3 — Monetization & Growth (Month 3–4)
- Ad slot system live
- Uzbek + Chinese via admin locales + DeepL
- Meilisearch integration
- Newsletter system

### Phase 4 — Performance & SEO (Ongoing)
- Core Web Vitals optimization sprints
- Content expansion (50+ articles)
- Link building with travel bloggers
- Festival & events calendar (live content)
