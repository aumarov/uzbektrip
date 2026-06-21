from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, HelpPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting


@register_setting(icon="list-ul")
class SectionSettings(BaseGenericSetting):
    """
    Master on/off switch per site category. Unticking a box hides the
    category from navigation AND returns 404 for every page in that
    category — no need to unpublish pages one by one when, say, Eat and
    Stay aren't ready to launch yet.
    """

    show_cities = models.BooleanField(default=True, verbose_name="Cities")
    show_sights = models.BooleanField(default=True, verbose_name="Sights")
    show_eat = models.BooleanField(
        default=False,
        verbose_name="Eat (Restaurants)",
        help_text="Off by default — turn on once restaurant content is ready to monetize.",
    )
    show_stay = models.BooleanField(
        default=False,
        verbose_name="Stay (Hotels)",
        help_text="Off by default — turn on once hotel content is ready to monetize.",
    )
    show_routes = models.BooleanField(default=True, verbose_name="Routes")
    show_visa = models.BooleanField(default=True, verbose_name="Visa & Entry")
    show_practical = models.BooleanField(default=True, verbose_name="Practical")
    show_news = models.BooleanField(default=True, verbose_name="News")
    show_blog = models.BooleanField(default=True, verbose_name="Blog / Tips")

    panels = [
        HelpPanel(
            content=(
                "Turn a category off to hide it from the navigation and footer, and "
                "make every page in that category return a 404. Use this for sections "
                "you aren't ready to launch yet (e.g. Eat and Stay until you have "
                "monetized restaurant/hotel content)."
            )
        ),
        MultiFieldPanel(
            [
                FieldPanel("show_cities"),
                FieldPanel("show_sights"),
                FieldPanel("show_eat"),
                FieldPanel("show_stay"),
                FieldPanel("show_routes"),
                FieldPanel("show_visa"),
                FieldPanel("show_practical"),
                FieldPanel("show_news"),
                FieldPanel("show_blog"),
            ],
            heading="Categories",
        ),
    ]

    class Meta:
        verbose_name = "Sections"


@register_setting(icon="pick")
class AdSettings(BaseGenericSetting):
    """
    Five ad placements matching the original site blueprint. Each has its
    own on/off switch and a raw HTML/JS code box — paste your ad network's
    embed code (AdSense, direct-sold tag, etc.) and flip it on. Leaving a
    slot off (or on with empty code) renders nothing — no empty placeholder
    boxes on the live site.
    """

    leaderboard_enabled = models.BooleanField(default=False, verbose_name="Enabled")
    leaderboard_code = models.TextField(
        blank=True,
        verbose_name="Ad code",
        help_text="970×90 — homepage, above the fold.",
    )

    midpage_enabled = models.BooleanField(default=False, verbose_name="Enabled")
    midpage_code = models.TextField(
        blank=True,
        verbose_name="Ad code",
        help_text="728×90 — homepage, mid-page banner.",
    )

    article_inline_enabled = models.BooleanField(default=False, verbose_name="Enabled")
    article_inline_code = models.TextField(
        blank=True,
        verbose_name="Ad code",
        help_text="728×90 — inline within city pages, blog posts, and news articles.",
    )

    sidebar_enabled = models.BooleanField(default=False, verbose_name="Enabled")
    sidebar_code = models.TextField(
        blank=True,
        verbose_name="Ad code",
        help_text="300×250 — homepage and article sidebars.",
    )

    footer_enabled = models.BooleanField(default=False, verbose_name="Enabled")
    footer_code = models.TextField(
        blank=True,
        verbose_name="Ad code",
        help_text="Full-width — above the footer on every page.",
    )

    panels = [
        HelpPanel(
            content=(
                "Paste your ad network's embed code (script tags and all) into a slot, "
                "then tick Enabled. Code entered here renders as-is — only paste code "
                "from sources you trust."
            )
        ),
        MultiFieldPanel(
            [FieldPanel("leaderboard_enabled"), FieldPanel("leaderboard_code")],
            heading="① Leaderboard — 970×90 (homepage top)",
        ),
        MultiFieldPanel(
            [FieldPanel("midpage_enabled"), FieldPanel("midpage_code")],
            heading="② Mid-page banner — 728×90 (homepage)",
        ),
        MultiFieldPanel(
            [FieldPanel("article_inline_enabled"), FieldPanel("article_inline_code")],
            heading="③ Inline banner — 728×90 (city/blog/news pages)",
        ),
        MultiFieldPanel(
            [FieldPanel("sidebar_enabled"), FieldPanel("sidebar_code")],
            heading="④ Sidebar — 300×250",
        ),
        MultiFieldPanel(
            [FieldPanel("footer_enabled"), FieldPanel("footer_code")],
            heading="⑤ Footer banner — full width",
        ),
    ]

    class Meta:
        verbose_name = "Ad Placements"


@register_setting(icon="globe")
class SEOSettings(BaseGenericSetting):
    """
    Site-wide Organization / publisher data used in the WebSite schema.org
    block, Open Graph tags, and Twitter Cards on every page — editable here
    instead of hardcoded in templates.
    """

    organization_name = models.CharField(max_length=120, default="UzbekTrip")
    organization_logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Used as the Organization logo in schema.org markup. Falls back to the static site logo if left blank.",
    )
    default_og_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
        help_text="Fallback social share image (1200×630px) for any page that doesn't set its own.",
    )
    twitter_handle = models.CharField(
        max_length=50, blank=True, default="@uzbektrip",
        help_text='Include the @ — used as the twitter:site meta tag.',
    )
    same_as_links = models.TextField(
        blank=True,
        verbose_name="Social profile URLs",
        help_text="One URL per line (Facebook, Instagram, YouTube, etc.) — used as the Organization's sameAs schema.org property.",
    )

    panels = [
        FieldPanel("organization_name"),
        FieldPanel("organization_logo"),
        FieldPanel("default_og_image"),
        FieldPanel("twitter_handle"),
        FieldPanel("same_as_links"),
    ]

    class Meta:
        verbose_name = "SEO"

    def get_same_as_list(self):
        return [url.strip() for url in self.same_as_links.splitlines() if url.strip()]
