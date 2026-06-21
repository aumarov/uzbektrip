from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.models import Page


class SEOMixin(models.Model):
    # ── Social / SEO ──────────────────────────────────────────────
    og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Social share image — 1200×630 px (Facebook, LinkedIn, Telegram)",
    )
    twitter_card_type = models.CharField(
        max_length=30,
        choices=[
            ("summary", "Summary (small image)"),
            ("summary_large_image", "Summary with Large Image (recommended)"),
        ],
        default="summary_large_image",
    )
    noindex = models.BooleanField(
        default=False,
        help_text="Prevent search engines from indexing this page",
    )
    meta_keywords = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated. Most search engines ignore this now, but some verticals/aggregators still read it.",
    )

    # ── Layout / design ───────────────────────────────────────────
    hide_nav = models.BooleanField(
        default=False,
        help_text="Hide the top navigation bar (useful for landing pages)",
    )
    hide_footer = models.BooleanField(
        default=False,
        help_text="Hide the site footer",
    )

    seo_panels = Page.promote_panels + [
        MultiFieldPanel(
            [
                FieldPanel("og_image"),
                FieldPanel("twitter_card_type"),
                FieldPanel("noindex"),
                FieldPanel("meta_keywords"),
            ],
            heading="Social / SEO",
        ),
        MultiFieldPanel(
            [
                FieldPanel("hide_nav"),
                FieldPanel("hide_footer"),
            ],
            heading="Page Layout",
        ),
    ]

    class Meta:
        abstract = True
