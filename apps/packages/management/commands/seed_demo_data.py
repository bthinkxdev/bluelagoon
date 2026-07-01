"""Seed package categories, sample packages, and testimonials for demo/production."""

from __future__ import annotations

from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from packages.models import (
    Package,
    PackageCategory,
    PackageExclusion,
    PackageInclusion,
    Testimonial,
)

STANDARD_INCLUSIONS = [
    "Accommodation on twin/double sharing basis",
    "Daily breakfast at the hotel",
    "Private air-conditioned transport with driver",
    "All applicable hotel taxes",
]

STANDARD_EXCLUSIONS = [
    "Airfare and visa charges",
    "Personal expenses and tips",
    "Entry fees to monuments unless specified",
    "Travel insurance",
]

CATEGORIES = [
    ("Domestic", PackageCategory.CategoryType.DOMESTIC, "domestic"),
    ("International", PackageCategory.CategoryType.INTERNATIONAL, "international"),
    ("Pilgrim", PackageCategory.CategoryType.PILGRIM, "pilgrim"),
]

PACKAGES = [
  {
    "slug": "kerala-backwaters-retreat",
    "category_slug": "domestic",
    "title": "Kerala Backwaters Retreat",
    "short_description": "Houseboat cruise, village walks, and coastal Kerala flavours.",
    "description": (
      "<p>Drift through Alleppey and Kumarakom on a traditional houseboat, "
      "visit spice gardens, and unwind in boutique waterfront stays.</p>"
    ),
    "duration": "4 Days / 3 Nights",
    "route": "KOCHI / ALAPPUZHA / KUMARAKOM",
    "price": Decimal("18500"),
    "price_note": "per person",
    "display_order": 1,
    "is_featured": True,
  },
  {
    "slug": "wayanad-wildlife-escape",
    "category_slug": "domestic",
    "title": "Wayanad Wildlife Escape",
    "short_description": "Misty hills, tea estates, and wildlife trails in North Kerala.",
    "description": (
      "<p>Explore Wayanad's forests, waterfalls, and plantations with guided "
      "jeep safaris and comfortable resort stays.</p>"
    ),
    "duration": "3 Days / 2 Nights",
    "route": "KOZHIKODE / WAYANAD / KOZHIKODE",
    "price": Decimal("14200"),
    "display_order": 2,
  },
  {
    "slug": "munnar-hill-station",
    "category_slug": "domestic",
    "title": "Munnar Hill Station",
    "short_description": "Tea valleys, Eravikulam views, and cool mountain air.",
    "description": (
      "<p>A relaxed hill-station break with plantation visits, scenic drives, "
      "and time at a misty resort in Munnar.</p>"
    ),
    "duration": "3 Days / 2 Nights",
    "route": "KOCHI / MUNNAR / KOCHI",
    "price": Decimal("12800"),
    "display_order": 3,
  },
  {
    "slug": "golden-triangle",
    "category_slug": "international",
    "title": "Golden Triangle",
    "short_description": "Delhi, Jaipur, and Agra — India's classic heritage circuit.",
    "description": (
      "<p>Discover the Taj Mahal, Amber Fort, and Old Delhi with private "
      "transport, handpicked hotels, and expert local guides.</p>"
    ),
    "duration": "6 Days / 5 Nights",
    "route": "DELHI / JAIPUR / AGRA / DELHI",
    "price": Decimal("32500"),
    "price_note": "per person",
    "display_order": 1,
    "is_featured": True,
  },
  {
    "slug": "dubai-city-break",
    "category_slug": "international",
    "title": "Dubai City Break",
    "short_description": "Skyline views, desert safari, and curated city experiences.",
    "description": (
      "<p>Stay in a central Dubai hotel with desert safari, marina cruise, "
      "and flexible time for shopping and sightseeing.</p>"
    ),
    "duration": "5 Days / 4 Nights",
    "route": "DUBAI",
    "price": Decimal("45800"),
    "display_order": 2,
  },
  {
    "slug": "singapore-family-fun",
    "category_slug": "international",
    "title": "Singapore Family Fun",
    "short_description": "Gardens, Sentosa, and easy family-friendly city touring.",
    "description": (
      "<p>A compact Singapore itinerary with Sentosa, Gardens by the Bay, "
      "and smooth airport transfers for families.</p>"
    ),
    "duration": "5 Days / 4 Nights",
    "route": "SINGAPORE",
    "price": Decimal("51200"),
    "display_order": 3,
  },
  {
    "slug": "varanasi-spiritual-journey",
    "category_slug": "pilgrim",
    "title": "Varanasi Spiritual Journey",
    "short_description": "Ganga aarti, temple visits, and sacred city walks.",
    "description": (
      "<p>Experience evening Ganga aarti, Sarnath, and guided temple visits "
      "with respectful pacing and comfortable stays.</p>"
    ),
    "duration": "4 Days / 3 Nights",
    "route": "VARANASI / SARNATH",
    "price": Decimal("16800"),
    "display_order": 1,
    "is_featured": True,
  },
  {
    "slug": "tirupati-darshan",
    "category_slug": "pilgrim",
    "title": "Tirupati Darshan",
    "short_description": "Balaji darshan assistance with transfers and hotel support.",
    "description": (
      "<p>Organised Tirupati pilgrimage with darshan coordination, local "
      "transfers, and clean accommodation near the temple town.</p>"
    ),
    "duration": "3 Days / 2 Nights",
    "route": "CHENNAI / TIRUPATI / CHENNAI",
    "price": Decimal("11500"),
    "display_order": 2,
  },
]

TESTIMONIALS = [
  {
    "package_slug": "golden-triangle",
    "name": "Achu Joseph",
    "rating": 5,
    "quote": (
      "Blue Lagoon planned our Golden Triangle trip flawlessly. Hotels were great "
      "and the guide in Jaipur was excellent."
    ),
    "display_order": 1,
  },
  {
    "package_slug": "kerala-backwaters-retreat",
    "name": "Priya Menon",
    "rating": 5,
    "quote": (
      "The houseboat experience was magical. The team was responsive from enquiry "
      "to checkout — highly recommended."
    ),
    "display_order": 2,
  },
  {
    "package_slug": "dubai-city-break",
    "name": "Rahul Nair",
    "rating": 5,
    "quote": (
      "Desert safari and hotel pick-ups were perfectly timed. Great value for a "
      "first international holiday."
    ),
    "display_order": 3,
  },
  {
    "package_slug": "varanasi-spiritual-journey",
    "name": "Mary Thomas",
    "rating": 4,
    "quote": (
      "A deeply moving pilgrimage. Blue Lagoon handled logistics so we could focus "
      "on the spiritual experience."
    ),
    "display_order": 4,
  },
  {
    "package_slug": "wayanad-wildlife-escape",
    "name": "Anil Kumar",
    "rating": 5,
    "quote": (
      "Wayanad was beautiful and the resort they suggested was perfect for our "
      "anniversary weekend."
    ),
    "display_order": 5,
  },
  {
    "package_slug": "tirupati-darshan",
    "name": "Sneha Raj",
    "rating": 5,
    "quote": (
      "Darshan arrangements were smooth and stress-free. Will book again for our "
      "parents' pilgrimage."
    ),
    "display_order": 6,
  },
]


class Command(BaseCommand):
    help = "Create demo package categories, packages, and testimonials (safe to re-run)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--if-empty",
            action="store_true",
            help="Only run when there are no published packages (recommended on production).",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Update existing packages/testimonials that match slugs.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        if options["if_empty"] and Package.objects.filter(status=Package.Status.PUBLISHED).exists():
            self.stdout.write(
                self.style.WARNING("Published packages already exist — skipped (--if-empty).")
            )
            return

        categories = self._seed_categories()
        packages = self._seed_packages(categories, force=options["force"])
        testimonials = self._seed_testimonials(packages, force=options["force"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo data ready: {len(categories)} categories, "
                f"{len(packages)} packages, {testimonials} testimonials."
            )
        )
        self.stdout.write("Upload package photos in Admin -> Packages when ready.")

    def _seed_categories(self) -> dict[str, PackageCategory]:
        created: dict[str, PackageCategory] = {}
        for name, ctype, slug in CATEGORIES:
            obj, was_created = PackageCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "category_type": ctype, "is_active": True},
            )
            if not was_created:
                obj.name = name
                obj.category_type = ctype
                obj.is_active = True
                obj.save()
            created[slug] = obj
            label = "created" if was_created else "exists"
            self.stdout.write(f"  Category [{label}] {obj.name}")
        return created

    def _seed_packages(self, categories: dict[str, PackageCategory], *, force: bool) -> dict[str, Package]:
        packages: dict[str, Package] = {}
        for data in PACKAGES:
            slug = data["slug"]
            category = categories[data["category_slug"]]
            defaults = {
                "title": data["title"],
                "category": category,
                "short_description": data["short_description"],
                "description": data.get("description", ""),
                "duration": data["duration"],
                "route": data.get("route", ""),
                "price": data.get("price"),
                "price_note": data.get("price_note", "per person"),
                "status": Package.Status.PUBLISHED,
                "is_featured": data.get("is_featured", False),
                "display_order": data.get("display_order", 0),
            }
            pkg, was_created = Package.objects.get_or_create(slug=slug, defaults=defaults)
            if not was_created and force:
                for key, value in defaults.items():
                    setattr(pkg, key, value)
                pkg.save()
                pkg.inclusions.all().delete()
                pkg.exclusions.all().delete()
                self._add_lists(pkg)
                self.stdout.write(f"  Package [updated] {pkg.title}")
            elif was_created:
                self._add_lists(pkg)
                self.stdout.write(f"  Package [created] {pkg.title}")
            else:
                self.stdout.write(f"  Package [exists] {pkg.title}")
            packages[slug] = pkg
        return packages

    def _add_lists(self, pkg: Package) -> None:
        PackageInclusion.objects.bulk_create(
            [
                PackageInclusion(package=pkg, text=text, display_order=index)
                for index, text in enumerate(STANDARD_INCLUSIONS, start=1)
            ]
        )
        PackageExclusion.objects.bulk_create(
            [
                PackageExclusion(package=pkg, text=text, display_order=index)
                for index, text in enumerate(STANDARD_EXCLUSIONS, start=1)
            ]
        )

    def _seed_testimonials(self, packages: dict[str, Package], *, force: bool) -> int:
        count = 0
        for data in TESTIMONIALS:
            package = packages.get(data["package_slug"])
            if not package:
                self.stdout.write(
                    self.style.WARNING(f"  Skip testimonial — package missing: {data['package_slug']}")
                )
                continue
            lookup = {
                "package": package,
                "name": data["name"],
            }
            defaults = {
                "quote": data["quote"],
                "rating": data["rating"],
                "display_order": data["display_order"],
                "is_active": True,
            }
            obj, was_created = Testimonial.objects.get_or_create(defaults=defaults, **lookup)
            if not was_created and force:
                for key, value in defaults.items():
                    setattr(obj, key, value)
                obj.save()
                self.stdout.write(f"  Testimonial [updated] {obj.name}")
            else:
                label = "created" if was_created else "exists"
                self.stdout.write(f"  Testimonial [{label}] {obj.name}")
            count += 1
        return count
