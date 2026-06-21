from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, HelpPanel
from wagtail.search import index

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS
from apps.core.sections import SectionToggleMixin


class HotelIndexPage(SectionToggleMixin, Page):
    section_flag = "show_stay"

    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["hotels.HotelPage"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        city_slug = request.GET.get("city", "")

        qs = (
            HotelPage.objects.live()
            .public()
            .child_of(self)
            .select_related("primary_city", "cover_image")
            .order_by("-is_featured", "-star_rating", "title")
        )
        if city_slug:
            qs = qs.filter(primary_city__slug=city_slug)

        ctx["hotels"] = qs
        ctx["selected_city"] = city_slug

        from apps.cities.models import CityPage
        ctx["all_cities"] = CityPage.objects.live().public().order_by("title")
        return ctx


class HotelPage(SectionToggleMixin, SEOMixin, Page):
    section_flag = "show_stay"

    PRICE_CHOICES = [
        ("budget", "$ — Budget"),
        ("mid", "$$ — Mid-range"),
        ("luxury", "$$$ — Luxury"),
    ]

    star_rating = models.PositiveSmallIntegerField(
        default=3, choices=[(i, f"{i} star{'s' if i != 1 else ''}") for i in range(1, 6)]
    )
    price_range = models.CharField(max_length=20, choices=PRICE_CHOICES, default="mid")
    excerpt = models.TextField(max_length=300, blank=True)

    primary_city = models.ForeignKey(
        "cities.CityPage", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="hotels",
    )
    address = models.CharField(max_length=255, blank=True)
    website = models.URLField(blank=True)
    amenities = models.CharField(
        max_length=500, blank=True,
        help_text="Comma-separated, e.g. Free Wi-Fi, Pool, Breakfast included, Parking",
    )

    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Upload at least 2400×1000px, wide landscape. Auto-cropped and served as WebP.",
    )
    is_featured = models.BooleanField(default=False)

    # ── Monetization (Phase 3) ──────────────────────────────────────
    booking_url = models.URLField(
        blank=True,
        help_text="Affiliate booking link (e.g. Booking.com partner link). Leave blank until ready.",
    )
    is_partner = models.BooleanField(
        default=False,
        verbose_name="Paid partner listing",
        help_text="Ticking this shows an affiliate disclosure badge, per editorial standards.",
    )

    body = StreamField(STANDARD_BLOCKS, use_json_field=True, blank=True)

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.FilterField("star_rating"),
        index.FilterField("price_range"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("star_rating"),
                FieldPanel("price_range"),
                FieldPanel("excerpt"),
                FieldPanel("cover_image"),
                FieldPanel("primary_city"),
                FieldPanel("is_featured"),
            ],
            heading="Hotel Info",
        ),
        MultiFieldPanel(
            [FieldPanel("address"), FieldPanel("website"), FieldPanel("amenities")],
            heading="Details",
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
    parent_page_types = ["hotels.HotelIndexPage"]

    def get_amenities_list(self):
        return [a.strip() for a in self.amenities.split(",") if a.strip()]

    def get_schema_ld(self):
        from urllib.parse import urlsplit

        data = {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": self.title,
            "description": self.search_description or self.excerpt,
            "url": self.full_url,
            "starRating": {"@type": "Rating", "ratingValue": self.star_rating},
            "priceRange": self.get_price_range_display(),
        }
        if self.address:
            data["address"] = self.address
        img = self.og_image or self.cover_image
        if img:
            base = urlsplit(self.full_url)
            data["image"] = f"{base.scheme}://{base.netloc}{img.file.url}"
        return data
