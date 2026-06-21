import os
from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
)

environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-replace-in-production")

ALLOWED_HOSTS = env("ALLOWED_HOSTS")

INSTALLED_APPS = [
    # Wagtail
    "wagtail.contrib.forms",
    "wagtail.contrib.redirects",
    "wagtail.contrib.settings",
    "wagtail.contrib.search_promotions",
    "wagtail.contrib.sitemaps",
    "wagtail.contrib.routable_page",
    "wagtail.contrib.table_block",
    # Localize — must come before wagtail.locales
    "wagtail_localize",
    "wagtail_localize.locales",
    # Wagtail core
    "wagtail.snippets",
    "wagtail.documents",
    "wagtail.images",
    "wagtail.search",
    "wagtail.sites",
    "wagtail.admin",
    "wagtail",
    # Third party
    "modelcluster",
    "taggit",
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
    # Project apps
    "apps.core",
    "apps.home",
    "apps.cities",
    "apps.sights",
    "apps.restaurants",
    "apps.hotels",
    "apps.visa",
    "apps.news",
    "apps.blog",
    "apps.practical",
    "apps.routes",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "wagtail.contrib.redirects.middleware.RedirectMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "apps.core.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# Internationalization
LANGUAGE_CODE = "en"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_L10N = True
USE_TZ = True

# wagtail==5.2.8's published package ships wagtailcore migrations only up to
# 0089 even though its models.py already defines Embed/UserProfile — every
# app with a Page subclass needs a migration that creates them. Rather than
# relying on `makemigrations` silently writing that missing file into
# site-packages (non-portable, invisible to git, and the source of a real
# deploy failure once), we vendor the full wagtailcore migration history here
# so it's identical and version-controlled across every environment.
MIGRATION_MODULES = {
    "wagtailcore": "apps.core.wagtailcore_migrations",
}

WAGTAIL_I18N_ENABLED = True

WAGTAIL_CONTENT_LANGUAGES = LANGUAGES = [
    ("en", "English"),
    ("ru", "Русский"),
    ("uz", "O'zbek"),
    ("zh", "中文"),
    ("de", "Deutsch"),
    ("fr", "Français"),
    ("ar", "العربية"),
    ("ko", "한국어"),
    ("ja", "日本語"),
    ("tr", "Türkçe"),
]

LOCALE_PATHS = [BASE_DIR / "locale"]

# Static files
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media files
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Default primary key
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Wagtail
WAGTAIL_SITE_NAME = "UzbekTrip"
WAGTAILADMIN_BASE_URL = "http://localhost:8000"
WAGTAILIMAGES_IMAGE_MODEL = "wagtailimages.Image"
WAGTAIL_ENABLE_UPDATE_CHECK = False
# Every {% image %} tag site-wide requests format-webp — these cap the
# rendition file size without a visible quality hit at these dimensions.
WAGTAILIMAGES_WEBP_QUALITY = 80
WAGTAILIMAGES_JPEG_QUALITY = 82

# Search
WAGTAILSEARCH_BACKENDS = {
    "default": {
        "BACKEND": "wagtail.search.backends.database",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]
