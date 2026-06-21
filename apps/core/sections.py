"""
Site-section on/off switching.

Each toggleable category (Cities, Sights, Eat, Stay, Routes, Visa, Practical,
News, Blog) has a boolean in SectionSettings (Wagtail admin: Settings →
Sections & Ads). Index and detail pages for that category inherit
SectionToggleMixin and declare `section_flag`, so the whole category can be
hidden from navigation AND made inaccessible by URL with one checkbox —
no need to unpublish every page individually.
"""
from django.http import Http404


class SectionToggleMixin:
    """
    Mix into any Page model. Set `section_flag` to the SectionSettings
    field name that controls this page's visibility, e.g.:

        class SightPage(SectionToggleMixin, SEOMixin, Page):
            section_flag = "show_sights"
    """

    section_flag = None

    def serve(self, request, *args, **kwargs):
        if self.section_flag and not self._section_is_enabled():
            raise Http404("This section is currently disabled.")
        return super().serve(request, *args, **kwargs)

    def _section_is_enabled(self):
        from apps.core.models import SectionSettings

        settings = SectionSettings.load(request_or_site=None)
        return getattr(settings, self.section_flag, True)
