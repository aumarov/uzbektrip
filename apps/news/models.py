from django.db import models
from django.db.models import Q
from django.utils import timezone

from modelcluster.fields import ParentalKey, ParentalManyToManyField
from modelcluster.contrib.taggit import ClusterTaggableManager
from taggit.models import TaggedItemBase

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, FieldRowPanel
from wagtail.search import index

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS


class NewsTag(TaggedItemBase):
    content_object = ParentalKey(
        "news.NewsArticle",
        related_name="tagged_items",
        on_delete=models.CASCADE,
    )


class NewsIndexPage(Page):
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["news.NewsArticle"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        city_slug = request.GET.get("city", "")
        category = request.GET.get("category", "")

        qs = (
            NewsArticle.objects.live()
            .public()
            .child_of(self)
            .select_related("primary_city", "cover_image")
            .prefetch_related("related_cities", "tags")
            .order_by("-published_date", "-first_published_at")
        )

        if city_slug:
            qs = qs.filter(
                Q(primary_city__slug=city_slug) | Q(related_cities__slug=city_slug)
            ).distinct()

        if category:
            qs = qs.filter(category=category)

        ctx["articles"] = qs
        ctx["featured"] = qs.filter(is_featured=True).first()
        ctx["categories"] = NewsArticle.CATEGORY_CHOICES
        ctx["selected_city"] = city_slug
        ctx["selected_category"] = category

        from apps.cities.models import CityPage
        ctx["all_cities"] = CityPage.objects.live().public().order_by("title")
        return ctx


class NewsArticle(SEOMixin, Page):
    CATEGORY_CHOICES = [
        ("tourism", "Tourism News"),
        ("openings", "New Openings"),
        ("events", "Events & Festivals"),
        ("transport", "Transport & Infrastructure"),
        ("culture", "Culture & Heritage"),
        ("practical", "Practical Updates"),
        ("visa", "Visa & Entry"),
    ]

    CATEGORY_ICONS = {
        "tourism": "✈️",
        "openings": "🏨",
        "events": "🎭",
        "transport": "🚂",
        "culture": "🏛️",
        "practical": "📋",
        "visa": "🛂",
    }

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="tourism")

    # ── City linking ──────────────────────────────────────────────
    primary_city = models.ForeignKey(
        "cities.CityPage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="news_articles",
        help_text="Main city this article is about",
    )
    related_cities = ParentalManyToManyField(
        "cities.CityPage",
        blank=True,
        related_name="related_news",
        help_text="Additional cities mentioned in this article",
    )

    # ── Authorship ────────────────────────────────────────────────
    author_name = models.CharField(max_length=200, default="UzbekTrip Editorial")
    author_twitter = models.CharField(
        max_length=50, blank=True, help_text="@handle without the @"
    )

    # ── Dates ─────────────────────────────────────────────────────
    published_date = models.DateField(
        default=timezone.now,
        help_text="Date shown publicly and used in Schema.org / OG meta",
    )
    updated_date = models.DateField(
        null=True,
        blank=True,
        help_text="Leave blank if article has not been updated since first publish",
    )

    # ── Media ─────────────────────────────────────────────────────
    cover_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Hero / card image. Also used as OG image when no separate og_image is set",
    )

    # ── Content ───────────────────────────────────────────────────
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        help_text="Shown in card previews and used as meta description when no SEO description is set",
    )
    reading_time = models.PositiveSmallIntegerField(default=3, help_text="Minutes to read")
    is_featured = models.BooleanField(
        default=False, help_text="Highlight at the top of the listing page"
    )
    view_count = models.PositiveIntegerField(default=0, editable=False)

    # ── Source (press releases) ───────────────────────────────────
    source_name = models.CharField(max_length=200, blank=True)
    source_url = models.URLField(blank=True)

    tags = ClusterTaggableManager(through=NewsTag, blank=True)

    body = StreamField(STANDARD_BLOCKS, use_json_field=True)

    # ── Search ────────────────────────────────────────────────────
    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.SearchField("body"),
        index.FilterField("category"),
        index.FilterField("published_date"),
        index.RelatedFields("primary_city", [index.SearchField("title")]),
    ]

    # ── Admin panels ──────────────────────────────────────────────
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("category"),
                FieldPanel("cover_image"),
                FieldPanel("excerpt"),
                FieldRowPanel(
                    [
                        FieldPanel("published_date"),
                        FieldPanel("updated_date"),
                        FieldPanel("reading_time"),
                    ]
                ),
                FieldPanel("author_name"),
                FieldPanel("author_twitter"),
                FieldPanel("is_featured"),
            ],
            heading="Article Info",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_city"),
                FieldPanel("related_cities"),
                FieldPanel("tags"),
            ],
            heading="City & Tags",
        ),
        MultiFieldPanel(
            [FieldPanel("source_name"), FieldPanel("source_url")],
            heading="Source (optional — for press releases)",
        ),
        FieldPanel("body"),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["news.NewsIndexPage"]

    # ── Helpers ───────────────────────────────────────────────────
    def get_category_icon(self):
        return self.CATEGORY_ICONS.get(self.category, "📰")

    def get_all_cities(self):
        """Primary city first, then related_cities."""
        cities = list(self.related_cities.all())
        if self.primary_city and self.primary_city not in cities:
            cities.insert(0, self.primary_city)
        return cities

    def get_effective_description(self):
        return self.search_description or self.excerpt

    def get_schema_ld(self, request):
        data = {
            "@context": "https://schema.org",
            "@type": "NewsArticle",
            "headline": self.title,
            "description": self.get_effective_description(),
            "datePublished": self.published_date.isoformat(),
            "dateModified": (self.updated_date or self.published_date).isoformat(),
            "author": {
                "@type": "Person",
                "name": self.author_name,
            },
            "publisher": {
                "@type": "Organization",
                "name": "UzbekTrip",
                "logo": {
                    "@type": "ImageObject",
                    "url": f"{request.scheme}://{request.get_host()}/static/img/logo.png",
                },
            },
            "mainEntityOfPage": {
                "@type": "WebPage",
                "@id": self.full_url,
            },
            "url": self.full_url,
            "inLanguage": request.LANGUAGE_CODE,
            "timeRequired": f"PT{self.reading_time}M",
            "articleSection": self.get_category_display(),
        }

        img = self.og_image or self.cover_image
        if img:
            data["image"] = {
                "@type": "ImageObject",
                "url": f"{request.scheme}://{request.get_host()}{img.file.url}",
                "width": img.width,
                "height": img.height,
            }

        keywords = [self.get_category_display()]
        for city in self.get_all_cities():
            keywords.append(city.title)
        keywords += list(self.tags.values_list("name", flat=True))
        if keywords:
            data["keywords"] = ", ".join(keywords)

        return data

    def get_breadcrumbs(self):
        """Returns list of {title, url} dicts for BreadcrumbList schema + HTML."""
        parent = self.get_parent()
        crumbs = [
            {"title": "Home", "url": self.get_site().root_page.full_url},
            {"title": parent.title, "url": parent.full_url},
        ]
        if self.primary_city:
            crumbs.append({
                "title": self.primary_city.title,
                "url": f"{parent.full_url}?city={self.primary_city.slug}",
            })
        crumbs.append({"title": self.title, "url": self.full_url})
        return crumbs

    def get_context(self, request):
        ctx = super().get_context(request)
        ctx["breadcrumbs"] = self.get_breadcrumbs()
        ctx["schema_ld"] = self.get_schema_ld(request)

        # Related articles: same city first, then same category
        related_qs = (
            NewsArticle.objects.live()
            .public()
            .exclude(pk=self.pk)
            .select_related("primary_city", "cover_image")
        )
        if self.primary_city:
            ctx["related_articles"] = (
                related_qs.filter(
                    Q(primary_city=self.primary_city)
                    | Q(related_cities=self.primary_city)
                )
                .distinct()
                .order_by("-published_date")[:3]
            )
        else:
            ctx["related_articles"] = related_qs.filter(
                category=self.category
            ).order_by("-published_date")[:3]

        return ctx

    def serve(self, request, *args, **kwargs):
        """Increment view count on each visit (used for 'popular' ordering)."""
        NewsArticle.objects.filter(pk=self.pk).update(
            view_count=models.F("view_count") + 1
        )
        return super().serve(request, *args, **kwargs)
