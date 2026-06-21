from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS


class CityIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["cities.CityPage"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["cities"] = CityPage.objects.live().public().child_of(self).order_by("title")
        return ctx


class CityPage(SEOMixin, Page):
    tagline = models.CharField(max_length=255, blank=True)
    description = RichTextField()
    hero_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    featured_order = models.PositiveSmallIntegerField(default=99)
    is_featured = models.BooleanField(default=False)
    badge = models.CharField(max_length=50, blank=True)
    latitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Auto-filled by the location search above — or enter manually (e.g. 39.654000)",
    )
    longitude = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        help_text="Auto-filled by the location search above — or enter manually (e.g. 66.975400)",
    )

    body = StreamField(STANDARD_BLOCKS, use_json_field=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("description"),
        index.SearchField("tagline"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("tagline"),
            FieldPanel("hero_image"),
            FieldPanel("description"),
            FieldPanel("badge"),
            FieldPanel("is_featured"),
            FieldPanel("featured_order"),
        ], heading="City Info"),
        FieldPanel("body"),
        MultiFieldPanel([FieldPanel("latitude"), FieldPanel("longitude")], heading="Location"),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["cities.CityIndexPage"]

    def get_context(self, request):
        from django.db.models import Q
        from apps.news.models import NewsArticle

        ctx = super().get_context(request)
        ctx["city_news"] = (
            NewsArticle.objects.live().public()
            .filter(Q(primary_city=self) | Q(related_cities=self))
            .distinct()
            .select_related("cover_image")
            .order_by("-published_date")[:4]
        )
        return ctx

    def get_schema_ld(self):
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
        return data
