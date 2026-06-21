"""
Shared StreamField block library.
Import STANDARD_BLOCKS into any page model's StreamField.
"""
from wagtail.blocks import (
    CharBlock, TextBlock, RichTextBlock, StructBlock, ListBlock,
    URLBlock, ChoiceBlock, PageChooserBlock,
    RawHTMLBlock as WagtailRawHTMLBlock,
)
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.contrib.table_block.blocks import TableBlock as WagtailTableBlock


# ── RICH TEXT ───────────────────────────────────────────────────────

class BodyRichTextBlock(RichTextBlock):
    class Meta:
        label = "Rich Text"
        icon = "doc-full"
        template = "blocks/richtext_block.html"


# ── IMAGE ───────────────────────────────────────────────────────────

class ImageBlock(StructBlock):
    image = ImageChooserBlock()
    caption = CharBlock(required=False)
    attribution = CharBlock(required=False)
    alignment = ChoiceBlock(
        choices=[
            ("full", "Full width"),
            ("center", "Centered"),
            ("left", "Float left"),
            ("right", "Float right"),
        ],
        default="full",
    )

    class Meta:
        icon = "image"
        label = "Image"
        template = "blocks/image_block.html"


# ── GALLERY ─────────────────────────────────────────────────────────

class GalleryBlock(StructBlock):
    images = ListBlock(
        StructBlock([
            ("image", ImageChooserBlock()),
            ("caption", CharBlock(required=False)),
        ]),
        label="Photos",
    )
    columns = ChoiceBlock(
        choices=[("2", "2 cols"), ("3", "3 cols"), ("4", "4 cols")],
        default="3",
    )

    class Meta:
        icon = "image"
        label = "Photo Gallery"
        template = "blocks/gallery_block.html"


# ── QUOTE ────────────────────────────────────────────────────────────

class QuoteBlock(StructBlock):
    quote = TextBlock()
    attribution = CharBlock(required=False)
    attribution_role = CharBlock(required=False, label="Role / source")

    class Meta:
        icon = "openquote"
        label = "Pull Quote"
        template = "blocks/quote_block.html"


# ── ALERT / NOTICE ───────────────────────────────────────────────────

class AlertBlock(StructBlock):
    style = ChoiceBlock(
        choices=[
            ("info", "ℹ️  Info"),
            ("tip", "💡  Tip"),
            ("warning", "⚠️  Warning"),
            ("success", "✅  Good to know"),
        ],
        default="info",
    )
    heading = CharBlock(required=False)
    text = RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        icon = "warning"
        label = "Alert / Notice"
        template = "blocks/alert_block.html"


# ── CALL TO ACTION ───────────────────────────────────────────────────

class CTABlock(StructBlock):
    text = CharBlock(label="Button text")
    page = PageChooserBlock(required=False, label="Internal page")
    url = URLBlock(required=False, label="External URL (overrides page)")
    style = ChoiceBlock(
        choices=[("primary", "Primary — gold"), ("outline", "Outline")],
        default="primary",
    )

    class Meta:
        icon = "link"
        label = "Button / CTA"
        template = "blocks/cta_block.html"


# ── CARD ─────────────────────────────────────────────────────────────

class CardBlock(StructBlock):
    image = ImageChooserBlock(required=False)
    title = CharBlock()
    text = RichTextBlock(required=False, features=["bold", "italic", "link", "ol", "ul"])
    cta = CTABlock(required=False, label="Button (optional)")

    class Meta:
        icon = "doc-full"
        label = "Card"
        template = "blocks/card_block.html"


class CardsBlock(StructBlock):
    columns = ChoiceBlock(
        choices=[("2", "2 columns"), ("3", "3 columns"), ("4", "4 columns")],
        default="3",
        label="Grid columns",
    )
    cards = ListBlock(CardBlock())

    class Meta:
        icon = "grip"
        label = "Cards Grid"
        template = "blocks/cards_block.html"


# ── ACCORDION / FAQ ──────────────────────────────────────────────────

class AccordionItemBlock(StructBlock):
    title = CharBlock(label="Question / heading")
    content = RichTextBlock(features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        icon = "collapse-down"
        label = "Item"


class AccordionBlock(StructBlock):
    heading = CharBlock(required=False, label="Section heading (optional)")
    items = ListBlock(AccordionItemBlock())

    class Meta:
        icon = "collapse-down"
        label = "Accordion / FAQ"
        template = "blocks/accordion_block.html"


# ── STATISTICS ───────────────────────────────────────────────────────

class StatItemBlock(StructBlock):
    number = CharBlock(help_text='e.g. "+73%", "7,000", "4"')
    label = CharBlock()

    class Meta:
        icon = "order"


class StatsBlock(StructBlock):
    heading = CharBlock(required=False)
    stats = ListBlock(StatItemBlock())

    class Meta:
        icon = "list-ul"
        label = "Statistics / Numbers"
        template = "blocks/stats_block.html"


# ── TIMELINE / ITINERARY ─────────────────────────────────────────────

class TimelineItemBlock(StructBlock):
    marker = CharBlock(label="Day / Date", help_text='e.g. "Day 1" or "Apr 15"')
    title = CharBlock()
    description = RichTextBlock(features=["bold", "italic", "link"])
    image = ImageChooserBlock(required=False)

    class Meta:
        icon = "time"
        label = "Day / Step"


class TimelineBlock(StructBlock):
    heading = CharBlock(required=False)
    items = ListBlock(TimelineItemBlock())

    class Meta:
        icon = "time"
        label = "Timeline / Itinerary"
        template = "blocks/timeline_block.html"


# ── VIDEO EMBED ──────────────────────────────────────────────────────

class VideoEmbedBlock(StructBlock):
    video = EmbedBlock(help_text="Paste a YouTube or Vimeo URL")
    caption = CharBlock(required=False)

    class Meta:
        icon = "media"
        label = "Video Embed"
        template = "blocks/video_embed_block.html"


# ── DOCUMENT DOWNLOAD ────────────────────────────────────────────────

class DocumentBlock(StructBlock):
    document = DocumentChooserBlock()
    title = CharBlock(required=False, help_text="Override document title (optional)")
    description = CharBlock(required=False)

    class Meta:
        icon = "doc-full-inverse"
        label = "Document Download"
        template = "blocks/document_block.html"


# ── TWO COLUMNS ──────────────────────────────────────────────────────

class TwoColumnBlock(StructBlock):
    ratio = ChoiceBlock(
        choices=[
            ("half", "50 / 50"),
            ("wider-left", "60 / 40"),
            ("wider-right", "40 / 60"),
        ],
        default="half",
        label="Column ratio",
    )
    left = RichTextBlock(label="Left column")
    right = RichTextBlock(label="Right column")

    class Meta:
        icon = "grip"
        label = "Two Columns"
        template = "blocks/two_column_block.html"


# ── TABLE ────────────────────────────────────────────────────────────

TABLE_OPTIONS = {
    "renderer": "html",
}


class TableBlock(WagtailTableBlock):
    """Data table with optional header row."""
    class Meta:
        icon = "table"
        label = "Table"
        template = "blocks/table_block.html"


# ── RAW HTML ─────────────────────────────────────────────────────────

class RawHTMLBlock(WagtailRawHTMLBlock):
    class Meta:
        icon = "code"
        label = "Raw HTML"


# ── STANDARD BLOCK PALETTE ───────────────────────────────────────────
# Use this list in any StreamField:
#   body = StreamField(STANDARD_BLOCKS, use_json_field=True)

STANDARD_BLOCKS = [
    ("rich_text",    BodyRichTextBlock()),
    ("image",        ImageBlock()),
    ("gallery",      GalleryBlock()),
    ("quote",        QuoteBlock()),
    ("alert",        AlertBlock()),
    ("cta",          CTABlock()),
    ("cards",        CardsBlock()),
    ("accordion",    AccordionBlock()),
    ("stats",        StatsBlock()),
    ("timeline",     TimelineBlock()),
    ("video",        VideoEmbedBlock()),
    ("document",     DocumentBlock()),
    ("table",        TableBlock()),
    ("two_columns",  TwoColumnBlock()),
    ("html",         RawHTMLBlock()),
]
