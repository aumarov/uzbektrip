"""
Creates the initial Wagtail page tree and site record.
Run once after migrate:
    python manage.py setup_site
"""
from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from wagtail.models import Page, Site, Locale


class Command(BaseCommand):
    help = "Create the initial Wagtail homepage and site structure"

    def handle(self, *args, **options):
        from apps.home.models import HomePage
        from apps.cities.models import CityIndexPage
        from apps.sights.models import SightsIndexPage
        from apps.restaurants.models import RestaurantIndexPage
        from apps.hotels.models import HotelIndexPage
        from apps.visa.models import VisaIndexPage
        from apps.news.models import NewsIndexPage
        from apps.blog.models import BlogIndexPage
        from apps.practical.models import PracticalIndexPage
        from apps.routes.models import RoutesIndexPage

        # Get or create the default locale
        locale, _ = Locale.objects.get_or_create(language_code="en")

        # Wagtail ships with a root page (id=1) and a default "Welcome to Wagtail" page.
        # We'll replace the default welcome page with our HomePage.
        root = Page.objects.filter(depth=1).first()
        if root is None:
            self.stderr.write("No root page found. Run migrations first.")
            return

        # Create HomePage if it doesn't exist. Only touch the default Wagtail
        # "Welcome" page when we're about to create our real one — checking
        # old_home.__class__ here is a no-op (Page.objects always returns the
        # base Page model, never the specific subclass), so doing this
        # unconditionally on every run would delete HomePage and all its
        # children — Cities, Sights, every page in the tree — each time.
        if not HomePage.objects.exists():
            old_home = Page.objects.filter(depth=2).first()
            if old_home:
                self.stdout.write(f"Removing old home page: {old_home.title}")
                old_home.delete()
                root = Page.objects.filter(depth=1).first()

            home = HomePage(
                title="Home",
                slug="home",
                locale=locale,
                hero_eyebrow="The Silk Road Reborn",
                hero_title="Discover\nUzbekistan",
                hero_subtitle=(
                    "7,000 years of civilization. Turquoise domes that pierce the desert sky. "
                    "A hospitality that will rearrange your understanding of welcome."
                ),
            )
            root.add_child(instance=home)
            self.stdout.write(self.style.SUCCESS("✓ Created HomePage"))
        else:
            home = HomePage.objects.first()
            self.stdout.write("  HomePage already exists, skipping.")

        # Create sub-sections
        sections = [
            ("Cities", "cities", CityIndexPage),
            ("Sights", "sights", SightsIndexPage),
            ("Eat", "restaurants", RestaurantIndexPage),
            ("Stay", "hotels", HotelIndexPage),
            ("Visa & Entry", "visa", VisaIndexPage),
            ("News", "news", NewsIndexPage),
            ("Blog", "blog", BlogIndexPage),
            ("Practical Info", "practical", PracticalIndexPage),
            ("Routes", "routes", RoutesIndexPage),
        ]
        for title, slug, PageClass in sections:
            if not PageClass.objects.exists():
                page = PageClass(title=title, slug=slug, locale=locale)
                home.add_child(instance=page)
                self.stdout.write(self.style.SUCCESS(f"✓ Created {title} ({slug})"))
            else:
                self.stdout.write(f"  {title} already exists, skipping.")

        # Create or update the site record. Hostname/port are ONLY set when
        # creating a brand-new Site — never overwritten on an existing one.
        # Wagtail's page-preview feature builds its dummy request's Host
        # header from this record, so clobbering a correctly-configured
        # production hostname back to "localhost:8000" on every command run
        # breaks Preview in production (DisallowedHost -> 400) without
        # affecting live serving, which routes by Django's URLconf instead —
        # this is exactly what happened here, twice.
        import os

        site = Site.objects.first()
        if site:
            site.root_page = home
            site.site_name = "UzbekTrip"
            site.is_default_site = True
            site.save()
            self.stdout.write(self.style.SUCCESS(f"✓ Updated Wagtail site record ({site.hostname}:{site.port})"))
        else:
            hostname = os.environ.get("WAGTAIL_SITE_HOSTNAME", "localhost")
            port = int(os.environ.get("WAGTAIL_SITE_PORT", "8000"))
            Site.objects.create(
                hostname=hostname,
                port=port,
                site_name="UzbekTrip",
                root_page=home,
                is_default_site=True,
            )
            self.stdout.write(self.style.SUCCESS(f"✓ Created Wagtail site record ({hostname}:{port})"))

        self.stdout.write(self.style.SUCCESS("\nSetup complete!"))
        self.stdout.write("  Admin: http://localhost:8000/cms/")
        self.stdout.write("  Site:  http://localhost:8000/")
