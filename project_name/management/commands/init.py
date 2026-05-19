"""
Bootstrap the Wagtail page tree and default site for a fresh MongoDB install.

Wagtail's data migrations (root page, default site) live in wagtail's own
migration package and are not replicated when MIGRATION_MODULES redirects to
empty stub packages, so this command creates them programmatically.

When bakerydemo is installed on a MongoDB backend, index pages are seeded
directly (SQL backends can call load_initial_data instead).

Usage:
    python manage.py init
"""

import importlib

from django.apps import apps
from django.core.management.base import BaseCommand


def _get_home_page_class():
    """Return (HomePage class, kwargs) for the appropriate home page model."""
    if apps.is_installed("bakerydemo.base"):
        module = importlib.import_module("bakerydemo.base.models")
        return module.HomePage, {
            "title": "Home",
            "slug": "home",
            "hero_text": "Welcome to the Wagtail Bakery",
            "hero_cta": "Browse our breads",
        }
    module = importlib.import_module("home.models")
    return module.HomePage, {"title": "Home", "slug": "home"}


class Command(BaseCommand):
    help = "Create the Wagtail root page, home page, and default site."

    def handle(self, **options):
        try:
            from django.contrib.contenttypes.models import ContentType
            from wagtail.models import Locale, Page, Site
        except ImportError:
            self.stdout.write("Wagtail is not installed — nothing to do.")
            return

        from django.conf import settings

        lang = (getattr(settings, "LANGUAGE_CODE", "en") or "en").split("-")[0][:2]
        locale, _ = Locale.objects.get_or_create(language_code=lang)

        root_page = Page.objects.filter(depth=1).first()
        if root_page is None:
            page_ct, _ = ContentType.objects.get_or_create(
                app_label="wagtailcore", model="page"
            )
            root_page = Page.add_root(
                title="Root",
                slug="root",
                content_type=page_ct,
                locale=locale,
                url_path="/",
                live=True,
            )
            self.stdout.write("Created Wagtail root page")

        actual_children = Page.objects.filter(
            depth=root_page.depth + 1, path__startswith=root_page.path
        ).count()
        if root_page.numchild != actual_children:
            root_page.numchild = actual_children
            root_page.save(update_fields=["numchild"])

        home_cls, home_kwargs = _get_home_page_class()
        if home_cls.objects.exists():
            home = home_cls.objects.first()
            self.stdout.write(f"Using existing home page: '{home.title}'")
        else:
            home = home_cls(locale=locale, **home_kwargs)
            root_page.add_child(instance=home)
            self.stdout.write(f"Created home page '{home.title}'")

        site = Site.objects.filter(is_default_site=True).first()
        if site:
            site.root_page = home
            site.site_name = home.title
            site.save()
            self.stdout.write(f"Updated default site ({site.hostname}:{site.port})")
        else:
            Site.objects.create(
                hostname="localhost",
                port=8000,
                root_page=home,
                site_name=home.title,
                is_default_site=True,
            )
            self.stdout.write("Created default site at localhost:8000")

        if apps.is_installed("bakerydemo.base"):
            engine = settings.DATABASES.get("default", {}).get("ENGINE", "")
            if "mongodb" in engine:
                self._seed_bakerydemo(home)
            else:
                from django.core.management import call_command

                self.stdout.write("Loading bakerydemo fixture data...")
                call_command("load_initial_data")

        self.stdout.write(self.style.SUCCESS("Done"))

    def _seed_bakerydemo(self, home):
        from bakerydemo.base.models import FooterText, Person, StandardPage
        from bakerydemo.blog.models import (
            BlogIndexPage,
            BlogPage,
            BlogPersonRelationship,
        )
        from bakerydemo.breads.models import (
            BreadIngredient,
            BreadPage,
            BreadsIndexPage,
            BreadType,
            Country,
        )
        from bakerydemo.locations.models import LocationPage, LocationsIndexPage
        from bakerydemo.people.models import PeopleIndexPage
        from bakerydemo.recipes.models import (
            RecipeIndexPage,
            RecipePage,
            RecipePersonRelationship,
        )

        locale = home.locale

        def get_or_create_child(parent, page_cls, title, slug, **kwargs):
            existing = page_cls.objects.filter(slug=slug).first()
            if existing:
                self.stdout.write(f"  exists: {title}")
                return existing
            page = page_cls(title=title, slug=slug, **kwargs)
            parent.add_child(instance=page)
            self.stdout.write(f"  created: {title}")
            return page

        breads = get_or_create_child(home, BreadsIndexPage, "Breads", "breads")
        blog = get_or_create_child(home, BlogIndexPage, "Blog", "blog")
        locations = get_or_create_child(
            home, LocationsIndexPage, "Locations", "locations"
        )
        get_or_create_child(home, PeopleIndexPage, "People", "people")
        recipes = get_or_create_child(home, RecipeIndexPage, "Recipes", "recipes")

        get_or_create_child(
            home,
            StandardPage,
            "About",
            "about",
            introduction="A short history of the bakery.",
        )
        get_or_create_child(
            home,
            StandardPage,
            "Contact",
            "contact",
            introduction="Get in touch with the bakery team.",
        )

        if not FooterText.objects.exists():
            FooterText.objects.create(
                locale=locale,
                body="<p>&copy; The Wagtail Bakery</p>",
            )
            self.stdout.write("  created: FooterText")

        countries = {}
        for title in ("United States", "France", "Italy"):
            obj, created = Country.objects.get_or_create(title=title)
            countries[title] = obj
            if created:
                self.stdout.write(f"  created: Country '{title}'")

        bread_types = {}
        for title in ("Sourdough", "Sandwich", "Flatbread"):
            obj, created = BreadType.objects.get_or_create(title=title)
            bread_types[title] = obj
            if created:
                self.stdout.write(f"  created: BreadType '{title}'")

        ingredients = {}
        for name in ("Flour", "Yeast", "Salt", "Water", "Olive oil"):
            obj, created = BreadIngredient.objects.get_or_create(name=name)
            ingredients[name] = obj
            if created:
                self.stdout.write(f"  created: BreadIngredient '{name}'")

        persons = []
        for first, last, job in (
            ("Madison", "Belrose", "Head Baker"),
            ("Cameron", "Wilson", "Pastry Chef"),
            ("Robert", "Russell", "Sous Chef"),
        ):
            obj, created = Person.objects.get_or_create(
                first_name=first,
                last_name=last,
                defaults={"job_title": job},
            )
            persons.append(obj)
            if created:
                self.stdout.write(f"  created: Person '{first} {last}'")

        for title, slug, country, btype in (
            ("Baguette", "baguette", countries["France"], bread_types["Sandwich"]),
            ("Ciabatta", "ciabatta", countries["Italy"], bread_types["Sandwich"]),
            ("Pita", "pita", countries["Italy"], bread_types["Flatbread"]),
        ):
            if breads.get_children().filter(slug=slug).exists():
                self.stdout.write(f"  exists: BreadPage '{title}'")
                continue
            page = BreadPage(
                title=title,
                slug=slug,
                introduction=f"{title} from {country.title}.",
                origin=country,
                bread_type=btype,
            )
            breads.add_child(instance=page)
            page.ingredients.add(
                ingredients["Flour"], ingredients["Water"], ingredients["Salt"]
            )
            page.save()
            self.stdout.write(f"  created: BreadPage '{title}'")

        for title, slug, author in (
            ("Bread baking 101", "bread-baking-101", persons[0]),
            ("Our local sourcing story", "local-sourcing", persons[1]),
        ):
            if blog.get_children().filter(slug=slug).exists():
                self.stdout.write(f"  exists: BlogPage '{title}'")
                continue
            page = BlogPage(
                title=title,
                slug=slug,
                introduction=f"{title} — a short post.",
            )
            page.blog_person_relationship.add(BlogPersonRelationship(person=author))
            blog.add_child(instance=page)
            self.stdout.write(f"  created: BlogPage '{title}'")

        for title, slug, address, lat_long in (
            (
                "Downtown Bakery",
                "downtown",
                "123 Main St\nMetropolis",
                "40.7128, -74.0060",
            ),
            (
                "Riverside Bakery",
                "riverside",
                "55 Riverside Dr\nMetropolis",
                "40.7150, -74.0090",
            ),
        ):
            if locations.get_children().filter(slug=slug).exists():
                self.stdout.write(f"  exists: LocationPage '{title}'")
                continue
            page = LocationPage(
                title=title,
                slug=slug,
                introduction=f"Welcome to {title}.",
                address=address,
                lat_long=lat_long,
            )
            locations.add_child(instance=page)
            self.stdout.write(f"  created: LocationPage '{title}'")

        for title, slug, author in (
            ("Classic Sourdough", "classic-sourdough", persons[2]),
            ("Quick Flatbread", "quick-flatbread", persons[0]),
        ):
            if recipes.get_children().filter(slug=slug).exists():
                self.stdout.write(f"  exists: RecipePage '{title}'")
                continue
            page = RecipePage(
                title=title,
                slug=slug,
                subtitle="A bakery favorite.",
                introduction=f"{title} — a quick walkthrough.",
                recipe_headline="<p>Time-tested recipe.</p>",
            )
            page.recipe_person_relationship.add(
                RecipePersonRelationship(person=author)
            )
            recipes.add_child(instance=page)
            self.stdout.write(f"  created: RecipePage '{title}'")

        home.refresh_from_db()
        changed = False
        if home.featured_section_1 is None:
            home.featured_section_1 = breads
            home.featured_section_1_title = "Breads"
            changed = True
        if home.featured_section_2 is None:
            home.featured_section_2 = blog
            home.featured_section_2_title = "Blog"
            changed = True
        if changed:
            home.save()
            self.stdout.write("Updated homepage featured sections")
