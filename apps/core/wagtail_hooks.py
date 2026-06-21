from wagtail import hooks
from django.utils.html import format_html
from django.templatetags.static import static


@hooks.register("insert_editor_js")
def geocode_editor_js():
    return format_html(
        '<script src="{}"></script>',
        static("admin/js/geocode_lookup.js"),
    )


@hooks.register("insert_editor_css")
def geocode_editor_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("admin/css/geocode_lookup.css"),
    )
