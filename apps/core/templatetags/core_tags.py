import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="jsonld")
def jsonld(value):
    """
    Safely serialize a Python dict (from a page's get_schema_ld()) into a
    JSON-LD string for embedding inside <script type="application/ld+json">.
    Escapes '</' so the payload can never break out of the script tag.
    """
    if not value:
        return ""
    encoded = json.dumps(value, default=str, ensure_ascii=False)
    encoded = encoded.replace("</", "<\\/")
    return mark_safe(encoded)
