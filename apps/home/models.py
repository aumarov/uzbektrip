from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS


class HomePage(SEOMixin, Page):
    # Hero
    hero_eyebrow = models.CharField(max_length=120, default="The Silk Road Reborn")
    hero_title = models.CharField(max_length=200, default="Discover Uzbekistan")
    hero_subtitle = models.TextField(
        blank=True,
        default=(
            "7,000 years of civilization. Turquoise domes that pierce the desert sky. "
            "A hospitality that will rearrange your understanding of welcome."
        ),
    )
    hero_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_cta_primary_text = models.CharField(max_length=60, default="Explore Cities")
    hero_cta_secondary_text = models.CharField(max_length=60, default="Plan Your Route")

    # Stats bar
    stat1_number = models.CharField(max_length=20, default="+73%")
    stat1_label = models.CharField(max_length=80, default="Tourist growth vs 2019")
    stat2_number = models.CharField(max_length=20, default="100")
    stat2_label = models.CharField(max_length=80, default="Visa-free countries")
    stat3_number = models.CharField(max_length=20, default="7,000")
    stat3_label = models.CharField(max_length=80, default="Years of history")
    stat4_number = models.CharField(max_length=20, default="4")
    stat4_label = models.CharField(max_length=80, default="UNESCO World Heritage Sites")

    # Visa banner
    visa_title = models.CharField(max_length=200, default="Visa-Free for 100+ Countries")
    visa_body = models.TextField(
        blank=True,
        default=(
            "Uzbekistan has opened its doors to the world. Check if your country qualifies "
            "for visa-free entry, or learn how to apply for an e-Visa in minutes."
        ),
    )

    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "cities.CityIndexPage",
        "sights.SightsIndexPage",
        "restaurants.RestaurantIndexPage",
        "hotels.HotelIndexPage",
        "visa.VisaIndexPage",
        "news.NewsIndexPage",
        "blog.BlogIndexPage",
        "practical.PracticalIndexPage",
        "routes.RoutesIndexPage",
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_eyebrow"),
                FieldPanel("hero_title"),
                FieldPanel("hero_subtitle"),
                FieldPanel("hero_image"),
                FieldPanel("hero_cta_primary_text"),
                FieldPanel("hero_cta_secondary_text"),
            ],
            heading="Hero",
        ),
        MultiFieldPanel(
            [
                FieldPanel("stat1_number"),
                FieldPanel("stat1_label"),
                FieldPanel("stat2_number"),
                FieldPanel("stat2_label"),
                FieldPanel("stat3_number"),
                FieldPanel("stat3_label"),
                FieldPanel("stat4_number"),
                FieldPanel("stat4_label"),
            ],
            heading="Hero Stats",
        ),
        MultiFieldPanel(
            [
                FieldPanel("visa_title"),
                FieldPanel("visa_body"),
            ],
            heading="Visa Banner",
        ),
    ]

    promote_panels = SEOMixin.seo_panels

    def get_context(self, request):
        from apps.cities.models import CityPage
        from apps.sights.models import SightPage
        from apps.news.models import NewsArticle
        from apps.routes.models import RoutePage

        ctx = super().get_context(request)
        ctx["featured_cities"] = (
            CityPage.objects.live().public().order_by("featured_order", "title")[:5]
        )
        ctx["featured_sights"] = (
            SightPage.objects.live().public()
            .select_related("primary_city", "cover_image")
            .order_by("-is_featured", "title")[:3]
        )
        ctx["featured_articles"] = (
            NewsArticle.objects.live().public()
            .select_related("primary_city", "cover_image")
            .order_by("-published_date", "-first_published_at")[:3]
        )
        ctx["popular_posts"] = (
            NewsArticle.objects.live().public()
            .select_related("cover_image")
            .order_by("-view_count", "-published_date")[:4]
        )
        ctx["featured_routes"] = (
            RoutePage.objects.live().public().order_by("featured_order", "title")[:4]
        )
        return ctx


class LandingPage(SEOMixin, Page):
    """
    Blank-canvas page: editors build the entire layout using StreamField blocks.
    Navigation and footer can each be toggled off per-page for fully custom designs.
    Suitable for: promotional campaigns, event pages, city spotlights, tour packages.
    """

    # Optional custom top bar overriding the default dark nav
    custom_header_html = models.TextField(
        blank=True,
        help_text=(
            "Optional: paste custom HTML for a page-specific header. "
            "Leave blank to use the site nav (unless Hide Nav is ticked)."
        ),
    )

    body = StreamField(STANDARD_BLOCKS, use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("custom_header_html")],
            heading="Custom Header (optional)",
        ),
        FieldPanel("body"),
    ]

    promote_panels = SEOMixin.seo_panels

    # Can live anywhere under the site root
    parent_page_types = [
        "home.HomePage",
        "cities.CityIndexPage",
        "cities.CityPage",
        "wagtailcore.Page",
    ]
