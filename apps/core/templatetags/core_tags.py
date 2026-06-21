import json
from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()


def _dumps(value):
    encoded = json.dumps(value, default=str, ensure_ascii=False)
    return encoded.replace("</", "<\\/")


@register.filter(name="jsonld")
def jsonld(value):
    """
    Safely serialize a Python dict (from a page's get_schema_ld()) into a
    JSON-LD string for embedding inside <script type="application/ld+json">.
    Escapes '</' so the payload can never break out of the script tag.
    """
    if not value:
        return ""
    return mark_safe(_dumps(value))


@register.filter(name="itemlist_jsonld")
def itemlist_jsonld(items):
    """
    Builds a generic schema.org ItemList from any iterable of objects that
    have .title/.full_url (i.e. any Wagtail Page queryset) — drop into an
    index page's {% block schema_ld %} to describe its listing for crawlers
    and answer engines, with zero extra queries.
    """
    items = list(items)
    if not items:
        return ""
    data = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": i + 1,
                "url": item.full_url,
                "name": item.title,
            }
            for i, item in enumerate(items)
        ],
    }
    return format_html('<script type="application/ld+json">{}</script>', mark_safe(_dumps(data)))


@register.simple_tag(takes_context=True, name="breadcrumb_jsonld")
def breadcrumb_jsonld(context, page):
    """
    Generic BreadcrumbList schema for any page at any depth — replaces the
    ad-hoc hardcoded copies that used to live in individual page templates.
    Skips the Wagtail tree root and the site's HomePage is rendered as "Home".
    """
    request = context.get("request")
    if request is None or page is None:
        return ""

    ancestors = list(page.get_ancestors(inclusive=True).live().public().specific())
    # Drop the tree root (depth 1) — it's Wagtail's invisible root, not a real page.
    crumbs = [p for p in ancestors if p.depth > 1]
    if not crumbs:
        return ""

    base = f"{request.scheme}://{request.get_host()}"
    items = []
    for i, crumb in enumerate(crumbs):
        name = "Home" if crumb.depth == 2 else crumb.title
        items.append({
            "@type": "ListItem",
            "position": i + 1,
            "name": name,
            "item": f"{base}{crumb.url}" if crumb.url else f"{base}{crumb.full_url}",
        })

    data = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }
    return format_html('<script type="application/ld+json">{}</script>', mark_safe(_dumps(data)))
