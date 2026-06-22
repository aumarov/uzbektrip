from django.conf import settings
from wagtail.models import Locale

from apps.core.models import SectionSettings, AdSettings, SEOSettings, AnalyticsSettings


def site_settings(request):
    """Makes `sections` and `ads` available in every template without
    needing {% load wagtailsettings_tags %} + {% get_settings %} everywhere."""
    locales = list(Locale.objects.all())
    locales.sort(key=lambda loc: (loc.language_code != settings.LANGUAGE_CODE, loc.language_code))
    return {
        "sections": SectionSettings.load(request_or_site=request),
        "ads": AdSettings.load(request_or_site=request),
        "active_locales": locales,
        "seo_settings": SEOSettings.load(request_or_site=request),
        "analytics": AnalyticsSettings.load(request_or_site=request),
    }
