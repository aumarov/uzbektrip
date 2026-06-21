from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, HelpPanel
from wagtail.blocks import StructBlock, CharBlock, RichTextBlock, ListBlock

from apps.core.seo import SEOMixin
from apps.core.blocks import STANDARD_BLOCKS
from apps.core.sections import SectionToggleMixin


class FAQItemBlock(StructBlock):
    question = CharBlock()
    answer = RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        icon = "help"
        label = "FAQ Item"


class VisaIndexPage(SectionToggleMixin, SEOMixin, Page):
    """
    Singleton Visa & Entry page: visa-free country summary, e-Visa steps,
    and a structured FAQ that also drives FAQPage schema.org markup.
    """

    section_flag = "show_visa"
    max_count = 1

    intro = RichTextField(blank=True)
    visa_free_note = RichTextField(
        blank=True,
        help_text="Summary blurb above the visa-free countries content, e.g. '100+ countries...'",
    )
    visa_free_countries = models.TextField(
        blank=True,
        help_text="Comma-separated list of visa-free countries, shown as a flag/tag grid.",
    )

    faq_items = StreamField(
        [("item", FAQItemBlock())],
        use_json_field=True,
        blank=True,
        help_text="Drives both the on-page accordion and FAQPage schema.org markup.",
    )

    body = StreamField(
        STANDARD_BLOCKS,
        use_json_field=True,
        blank=True,
        help_text="Use the Timeline block for e-Visa application steps, Table for border crossing info, etc.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        MultiFieldPanel(
            [FieldPanel("visa_free_note"), FieldPanel("visa_free_countries")],
            heading="Visa-Free Countries",
        ),
        FieldPanel("body"),
        MultiFieldPanel(
            [
                HelpPanel(content="These questions also generate FAQPage schema.org markup for Google."),
                FieldPanel("faq_items"),
            ],
            heading="FAQ",
        ),
    ]

    promote_panels = SEOMixin.seo_panels
    parent_page_types = ["home.HomePage"]
    subpage_types = []

    def get_visa_free_list(self):
        return [c.strip() for c in self.visa_free_countries.split(",") if c.strip()]

    def get_schema_ld(self):
        from django.utils.html import strip_tags

        if not self.faq_items:
            return None
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": item.value["question"],
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": strip_tags(str(item.value["answer"])),
                    },
                }
                for item in self.faq_items
            ],
        }
