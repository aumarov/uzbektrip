from django.apps import AppConfig
from django.db import transaction


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"

    def ready(self):
        from django.db.models.signals import post_save
        from wagtail.models import Locale

        post_save.connect(_bootstrap_locale_sync, sender=Locale)


def _bootstrap_locale_sync(sender, instance, created, **kwargs):
    """
    When a new Locale is created (Settings -> Locales -> Add Locale), mirror
    the entire default-locale page tree into it as alias pages, so editors
    land on a ready-to-translate tree instead of an empty one.

    Deferred to transaction.on_commit: wagtail-localize's own admin view
    saves the Locale and any editor-chosen "synchronise from" component in
    the same atomic block. Running only after that commits lets us check
    whether the editor already configured a sync source — if so we leave
    it alone instead of racing it and hitting the OneToOneField constraint
    on LocaleSynchronization.locale.
    """
    if not created:
        return

    transaction.on_commit(lambda: _ensure_locale_sync(instance))


def _ensure_locale_sync(new_locale):
    from wagtail.models import Locale
    from wagtail_localize.models import LocaleSynchronization

    if LocaleSynchronization.objects.filter(locale=new_locale).exists():
        return  # editor already picked a sync source via the admin form

    default_locale = Locale.get_default()
    if default_locale.pk == new_locale.pk:
        return

    # Saving this triggers wagtail-localize's own post_save signal, which
    # calls .sync_trees() for us (synchronous by default — no task queue
    # configured in this project).
    LocaleSynchronization.objects.create(locale=new_locale, sync_from=default_locale)
