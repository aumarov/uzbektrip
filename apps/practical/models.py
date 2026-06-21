from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS
from apps.core.sections import SectionToggleMixin


class PracticalIndexPage(SectionToggleMixin, Page):
    section_flag = "show_practical"
    intro = RichTextField(blank=True)
    icon = models.CharField(max_length=10, default="ℹ️")

    content_panels = Page.content_panels + [
        FieldPanel("icon"),
        FieldPanel("intro"),
    ]
    subpage_types = ["practical.PracticalPage"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["pages"] = PracticalPage.objects.live().public().child_of(self).order_by("title")
        return ctx


class PracticalPage(SectionToggleMixin, SEOMixin, Page):
    section_flag = "show_practical"
    icon = models.CharField(max_length=10, default="📋")
    short_desc = models.CharField(max_length=120, blank=True)

    body = StreamField(STANDARD_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("icon"),
        FieldPanel("short_desc"),
        FieldPanel("body"),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["practical.PracticalIndexPage"]
