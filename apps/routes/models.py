from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS
from apps.core.sections import SectionToggleMixin


class RoutesIndexPage(SectionToggleMixin, Page):
    section_flag = "show_routes"
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["routes.RoutePage"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["routes"] = RoutePage.objects.live().public().child_of(self).order_by("featured_order", "title")
        return ctx


class RoutePage(SectionToggleMixin, SEOMixin, Page):
    section_flag = "show_routes"
    duration = models.CharField(max_length=50)
    cities_covered = models.CharField(max_length=300, blank=True)
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    featured_order = models.PositiveSmallIntegerField(default=99)
    difficulty = models.CharField(
        max_length=20,
        choices=[("easy", "Easy"), ("moderate", "Moderate"), ("challenging", "Challenging")],
        default="easy",
    )
    best_season = models.CharField(max_length=100, blank=True)
    excerpt = models.TextField(max_length=300, blank=True)

    body = StreamField(STANDARD_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("duration"),
            FieldPanel("cities_covered"),
            FieldPanel("cover_image"),
            FieldPanel("difficulty"),
            FieldPanel("best_season"),
            FieldPanel("excerpt"),
            FieldPanel("featured_order"),
        ], heading="Route Info"),
        FieldPanel("body"),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["routes.RoutesIndexPage"]
