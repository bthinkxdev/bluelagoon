"""Tests for package search filtering."""

from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings

from packages.models import Package, PackageCategory
from packages.search import (
    DURATION_SHORT,
    PackageSearch,
    SORT_PRICE_ASC,
    SORT_PRICE_DESC,
    _parse_travellers,
)


class PackageSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.domestic = PackageCategory.objects.create(
            name="Domestic",
            slug="domestic",
            category_type=PackageCategory.CategoryType.DOMESTIC,
        )
        cls.international = PackageCategory.objects.create(
            name="International",
            slug="international",
            category_type=PackageCategory.CategoryType.INTERNATIONAL,
        )
        Package.objects.create(
            title="Alleppey Backwaters",
            slug="alleppey-backwaters",
            category=cls.domestic,
            short_description="Cruise through serene backwaters from Cochin.",
            route="COCHIN / ALAPPUZHA / COCHIN",
            duration="3 Days / 2 Nights",
            price=Decimal("1500"),
            status=Package.Status.PUBLISHED,
        )
        Package.objects.create(
            title="Golden Triangle",
            slug="golden-triangle",
            category=cls.international,
            short_description="Delhi Jaipur Agra tour",
            route="DELHI / JAIPUR / AGRA / DELHI",
            duration="09 NIGHTS / 10 DAYS",
            price=Decimal("25000"),
            status=Package.Status.PUBLISHED,
        )
        Package.objects.create(
            title="Munnar Escape",
            slug="munnar-escape",
            category=cls.domestic,
            short_description="Hill station getaway in Munnar",
            route="COCHIN / MUNNAR / COCHIN",
            duration="2 Days / 1 Night",
            price=Decimal("8000"),
            status=Package.Status.PUBLISHED,
        )

    def test_filter_by_destination_to(self):
        search = PackageSearch(
            category_type=PackageCategory.CategoryType.DOMESTIC,
            to_place="Alleppey",
        )
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().slug, "alleppey-backwaters")

    def test_filter_by_from_route(self):
        search = PackageSearch(
            category_type=PackageCategory.CategoryType.DOMESTIC,
            from_place="Cochin",
        )
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        self.assertEqual(qs.count(), 2)

    def test_relevance_prefers_title_match(self):
        search = PackageSearch(
            category_type="all",
            to_place="Munnar",
        )
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        self.assertEqual(qs.first().slug, "munnar-escape")

    def test_filter_by_trip_length(self):
        search = PackageSearch(
            category_type=PackageCategory.CategoryType.INTERNATIONAL,
            depart=date(2026, 7, 1),
            return_date=date(2026, 7, 10),
        )
        self.assertEqual(search.trip_days, 10)
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().slug, "golden-triangle")

    def test_duration_bucket_short(self):
        search = PackageSearch(category_type="all", duration_bucket=DURATION_SHORT)
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        slugs = set(qs.values_list("slug", flat=True))
        self.assertIn("alleppey-backwaters", slugs)
        self.assertIn("munnar-escape", slugs)
        self.assertNotIn("golden-triangle", slugs)

    def test_sort_price_asc(self):
        search = PackageSearch(category_type="all", sort=SORT_PRICE_ASC)
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        prices = list(qs.values_list("price", flat=True))
        self.assertEqual(prices, sorted(prices))

    def test_sort_price_desc(self):
        search = PackageSearch(category_type="all", sort=SORT_PRICE_DESC)
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        prices = list(qs.values_list("price", flat=True))
        self.assertEqual(prices, sorted(prices, reverse=True))

    def test_parse_travellers_string(self):
        adults, children = _parse_travellers("", "", "2 Adults, 1 Child")
        self.assertEqual(adults, 2)
        self.assertEqual(children, 1)

    def test_duration_days_populated_on_save(self):
        package = Package.objects.get(slug="golden-triangle")
        self.assertEqual(package.duration_days, 10)

    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }
    )
    def test_domestic_list_view_with_search(self):
        response = self.client.get(
            "/packages/domestic/",
            {"to": "Alleppey", "from": "Cochin", "adults": "2", "children": "1"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Alleppey Backwaters")
        self.assertContains(response, "Search results")

    @override_settings(
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        }
    )
    def test_list_view_sort_and_duration_controls(self):
        response = self.client.get("/packages/", {"sort": "price_asc", "duration": "short"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "wl-package-filters")
        self.assertContains(response, "Price: Low to High")

    @override_settings(
        EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
        STORAGES={
            "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
            "staticfiles": {
                "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
            },
        },
    )
    def test_empty_search_shows_custom_enquiry_form(self):
        response = self.client.get("/packages/", {"to": "Zzyxnonexistent999"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "wl-search-enquiry")
        self.assertContains(response, "We can arrange your trip exactly the way you want")
        self.assertContains(response, "pre-designed packages may not align")
        self.assertContains(response, "Arrival date:")
        self.assertContains(response, "enquiry_source")
