from apps.core.models import SectionSettings, AdSettings


def site_settings(request):
    """Makes `sections` and `ads` available in every template without
    needing {% load wagtailsettings_tags %} + {% get_settings %} everywhere."""
    return {
        "sections": SectionSettings.load(request_or_site=request),
        "ads": AdSettings.load(request_or_site=request),
    }
