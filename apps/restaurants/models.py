from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, HelpPanel
from wagtail.search import index

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS
from apps.core.sections import SectionToggleMixin


class RestaurantIndexPage(SectionToggleMixin, Page):
    section_flag = "show_eat"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["restaurants.RestaurantPage"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        city_slug = request.GET.get("city", "")
        cuisine = request.GET.get("cuisine", "")

        qs = (
            RestaurantPage.objects.live()
            .public()
            .child_of(self)
            .select_related("primary_city", "cover_image")
            .order_by("-is_featured", "title")
        )
        if city_slug:
            qs = qs.filter(primary_city__slug=city_slug)
        if cuisine:
            qs = qs.filter(cuisine=cuisine)

        ctx["restaurants"] = qs
        ctx["cuisines"] = RestaurantPage.CUISINE_CHOICES
        ctx["selected_city"] = city_slug
        ctx["selected_cuisine"] = cuisine

        from apps.cities.models import CityPage
        ctx["all_cities"] = CityPage.objects.live().public().order_by("title")
        return ctx


class RestaurantPage(SectionToggleMixin, SEOMixin, Page):
    section_flag = "show_eat"

    CUISINE_CHOICES = [
        ("uzbek", "Uzbek / National"),
        ("asian", "Asian"),
        ("european", "European"),
        ("italian", "Italian"),
        ("cafe", "Café & Bakery"),
        ("fast_food", "Fast Food"),
    ]
    PRICE_CHOICES = [
        ("budget", "$ — Budget"),
        ("mid", "$$ — Mid-range"),
        ("upscale", "$$$ — Upscale"),
    ]

    cuisine = models.CharField(max_length=30, choices=CUISINE_CHOICES, default="uzbek")
    price_range = models.CharField(max_length=20, choices=PRICE_CHOICES, default="mid")
    excerpt = models.TextField(max_length=300, blank=True)

    primary_city = models.ForeignKey(
        "cities.CityPage", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="restaurants",
    )
    address = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    opening_hours = models.CharField(max_length=200, blank=True)

    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    is_featured = models.BooleanField(default=False)

    # ── Monetization (Phase 3) ──────────────────────────────────────
    booking_url = models.URLField(
        blank=True,
        help_text="Affiliate / reservation link. Leave blank until a partnership is in place.",
    )
    is_partner = models.BooleanField(
        default=False,
        verbose_name="Paid partner listing",
        help_text="Ticking this shows an affiliate disclosure badge, per editorial standards.",
    )

    body = StreamField(STANDARD_BLOCKS, use_json_field=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.FilterField("cuisine"),
        index.FilterField("price_range"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("cuisine"),
                FieldPanel("price_range"),
                FieldPanel("excerpt"),
                FieldPanel("cover_image"),
                FieldPanel("primary_city"),
                FieldPanel("is_featured"),
            ],
            heading="Restaurant Info",
        ),
        MultiFieldPanel(
            [FieldPanel("address"), FieldPanel("phone"), FieldPanel("website"), FieldPanel("opening_hours")],
            heading="Contact & Hours",
        ),
        MultiFieldPanel(
            [
                HelpPanel(content="Leave blank until you have a real partnership / affiliate link."),
                FieldPanel("booking_url"),
                FieldPanel("is_partner"),
            ],
            heading="Monetization",
        ),
        FieldPanel("body"),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["restaurants.RestaurantIndexPage"]

    def get_schema_ld(self):
        from urllib.parse import urlsplit

        data = {
            "@context": "https://schema.org",
            "@type": "Restaurant",
            "name": self.title,
            "description": self.search_description or self.excerpt,
            "url": self.full_url,
            "servesCuisine": self.get_cuisine_display(),
            "priceRange": self.get_price_range_display(),
        }
        if self.address:
            data["address"] = self.address
        if self.phone:
            data["telephone"] = self.phone
        img = self.og_image or self.cover_image
        if img:
            base = urlsplit(self.full_url)
            data["image"] = f"{base.scheme}://{base.netloc}{img.file.url}"
        return data
