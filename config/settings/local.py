from .base import *  # noqa

DEBUG = True

SECRET_KEY = "local-dev-secret-key-not-for-production"

ALLOWED_HOSTS = ["*"]

# SQLite for quick local dev — override with DATABASE_URL for postgres
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# Use in-memory cache locally
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}

# Email to console
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable password validation in dev
AUTH_PASSWORD_VALIDATORS = []

# Show all queries in debug toolbar (optional — install django-debug-toolbar to use)
INTERNAL_IPS = ["127.0.0.1"]

# Simpler static files in dev
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
