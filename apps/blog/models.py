from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.search import index
from taggit.models import TaggedItemBase
from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS
from apps.core.sections import SectionToggleMixin


class BlogPostTag(TaggedItemBase):
    content_object = ParentalKey(
        "blog.BlogPost", related_name="tagged_items", on_delete=models.CASCADE
    )


class BlogIndexPage(SectionToggleMixin, Page):
    section_flag = "show_blog"
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [FieldPanel("intro")]
    subpage_types = ["blog.BlogPost"]
    parent_page_types = ["home.HomePage"]

    def get_context(self, request):
        ctx = super().get_context(request)
        tag = request.GET.get("tag")
        posts = BlogPost.objects.live().public().child_of(self).order_by("-first_published_at")
        if tag:
            posts = posts.filter(tags__name=tag)
        ctx["posts"] = posts
        return ctx


class BlogPost(SectionToggleMixin, SEOMixin, Page):
    section_flag = "show_blog"
    CATEGORY_CHOICES = [
        ("food", "Food & Drink"),
        ("practical", "Practical Info"),
        ("sights", "Sights & Attractions"),
        ("culture", "Culture & History"),
        ("transport", "Transport"),
        ("accommodation", "Hotels & Guesthouses"),
    ]

    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES, default="practical")
    author_name = models.CharField(max_length=200, default="UzbekTrip Editorial")
    author_twitter = models.CharField(max_length=50, blank=True)
    cover_image = models.ForeignKey(
        "wagtailimages.Image", null=True, blank=True,
        on_delete=models.SET_NULL, related_name="+",
    )
    excerpt = models.TextField(max_length=300, blank=True)
    reading_time = models.PositiveSmallIntegerField(default=5)
    view_count = models.PositiveIntegerField(default=0, editable=False)
    tags = ClusterTaggableManager(through=BlogPostTag, blank=True)

    body = StreamField(STANDARD_BLOCKS, use_json_field=True)

    search_fields = Page.search_fields + [
        index.SearchField("excerpt"),
        index.SearchField("body"),
    ]

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel("category"),
            FieldPanel("cover_image"),
            FieldPanel("excerpt"),
            FieldPanel("reading_time"),
            FieldPanel("author_name"),
            FieldPanel("author_twitter"),
            FieldPanel("tags"),
        ], heading="Post Info"),
        FieldPanel("body"),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["blog.BlogIndexPage"]

    def get_category_display_icon(self):
        icons = {
            "food": "🍽️", "practical": "📱", "sights": "🏛️",
            "culture": "🎭", "transport": "🚂", "accommodation": "🏨",
        }
        return icons.get(self.category, "📄")
