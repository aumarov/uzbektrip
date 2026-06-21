from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.urls import path, include
from django.views.generic import RedirectView
from wagtail import urls as wagtail_urls
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.documents import urls as wagtaildocs_urls
from wagtail.contrib.sitemaps.views import sitemap

from apps.core.views import robots_txt, llms_txt

urlpatterns = [
    # Root → always redirect to English homepage
    path("", RedirectView.as_view(url="/en/", permanent=False)),
    path("sitemap.xml", sitemap),
    path("robots.txt", robots_txt),
    path("llms.txt", llms_txt),
    path("cms/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
]

# All language versions get an explicit prefix: /en/, /ru/, /uz/, etc.
urlpatterns += i18n_patterns(
    path("", include(wagtail_urls)),
    prefix_default_language=True,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
