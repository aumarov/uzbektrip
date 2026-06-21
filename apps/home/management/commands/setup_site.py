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

        # Remove the default welcome page if it exists
        old_home = Page.objects.filter(depth=2).first()
        if old_home and old_home.__class__.__name__ != "HomePage":
            self.stdout.write(f"Removing old home page: {old_home.title}")
            old_home.delete()
            # Re-fetch root so treebeard path state is fresh
            root = Page.objects.filter(depth=1).first()

        # Create HomePage if it doesn't exist
        if not HomePage.objects.exists():
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

        # Create or update the site record
        site = Site.objects.first()
        if site:
            site.root_page = home
            site.hostname = "localhost"
            site.port = 8000
            site.site_name = "UzbekTrip"
            site.is_default_site = True
            site.save()
            self.stdout.write(self.style.SUCCESS("✓ Updated Wagtail site record"))
        else:
            Site.objects.create(
                hostname="localhost",
                port=8000,
                site_name="UzbekTrip",
                root_page=home,
                is_default_site=True,
            )
            self.stdout.write(self.style.SUCCESS("✓ Created Wagtail site record"))

        self.stdout.write(self.style.SUCCESS("\nSetup complete!"))
        self.stdout.write("  Admin: http://localhost:8000/cms/")
        self.stdout.write("  Site:  http://localhost:8000/")
