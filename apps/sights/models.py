from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS
from apps.core.sections import SectionToggleMixin


class SightsIndexPage(SectionToggleMixin, Page):
    section_flag = "show_sights"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["sights.SightPage"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        city_slug = request.GET.get("city", "")
        category = request.GET.get("category", "")

        qs = (
            SightPage.objects.live()
            .public()
            .child_of(self)
            .select_related("primary_city", "cover_image")
            .order_by("-is_featured", "title")
        )
        if city_slug:
            qs = qs.filter(
                models.Q(primary_city__slug=city_slug) | models.Q(related_cities__slug=city_slug)
            ).distinct()
        if category:
            qs = qs.filter(category=category)

        ctx["sights"] = qs
        ctx["categories"] = SightPage.CATEGORY_CHOICES
        ctx["selected_city"] = city_slug
        ctx["selected_category"] = category

        from apps.cities.models import CityPage
        ctx["all_cities"] = CityPage.objects.live().public().order_by("title")
        return ctx


class SightPage(SectionToggleMixin, SEOMixin, Page):
    section_flag = "show_sights"

    CATEGORY_CHOICES = [
        ("monument", "Monument & Architecture"),
        ("museum", "Museum"),
        ("religious", "Religious Site"),
        ("market", "Bazaar & Market"),
        ("nature", "Nature & Parks"),
        ("viewpoint", "Viewpoint"),
    ]
    CATEGORY_ICONS = {
        "monument": "🏛️", "museum": "🖼️", "religious": "🕌",
        "market": "🛍️", "nature": "🌳", "viewpoint": "👁️",
    }

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="monument")
    tagline = models.CharField(max_length=255, blank=True)
    excerpt = models.TextField(max_length=300, blank=True)

    primary_city = models.ForeignKey(
        "cities.CityPage", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="sights",
    )
    related_cities = models.ManyToManyField(
        "cities.CityPage", blank=True, related_name="related_sights",
    )

    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Upload at least 2400×1000px, wide landscape. Auto-cropped and served as WebP.",
    )

    ticket_price = models.CharField(max_length=100, blank=True, help_text='e.g. "Free" or "50,000 UZS"')
    opening_hours = models.CharField(max_length=200, blank=True, help_text='e.g. "9:00–18:00 daily"')
    best_time_to_visit = models.CharField(max_length=200, blank=True, help_text='e.g. "Early morning, golden hour"')
    is_unesco = models.BooleanField(default=False, verbose_name="UNESCO World Heritage Site")
    is_featured = models.BooleanField(default=False)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    body = StreamField(STANDARD_BLOCKS, use_json_field=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.SearchField("tagline"),
        index.FilterField("category"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("tagline"),
                FieldPanel("excerpt"),
                FieldPanel("cover_image"),
                FieldPanel("primary_city"),
                FieldPanel("related_cities"),
                FieldPanel("is_unesco"),
                FieldPanel("is_featured"),
            ],
            heading="Sight Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("ticket_price"),
                FieldPanel("opening_hours"),
                FieldPanel("best_time_to_visit"),
            ],
            heading="Visiting Info",
        ),
        FieldPanel("body"),
        MultiFieldPanel([FieldPanel("latitude"), FieldPanel("longitude")], heading="Location"),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["sights.SightsIndexPage"]

    def get_category_icon(self):
        return self.CATEGORY_ICONS.get(self.category, "📍")

    def get_schema_ld(self):
        from urllib.parse import urlsplit

        data = {
            "@context": "https://schema.org",
            "@type": "TouristAttraction",
            "name": self.title,
            "description": self.search_description or self.excerpt,
            "url": self.full_url,
        }
        if self.latitude and self.longitude:
            data["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": str(self.latitude),
                "longitude": str(self.longitude),
            }
        img = self.og_image or self.cover_image
        if img:
            base = urlsplit(self.full_url)
            data["image"] = f"{base.scheme}://{base.netloc}{img.file.url}"
        return data
