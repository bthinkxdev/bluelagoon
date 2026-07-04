"""Tests for destination-based package search."""

from datetime import date
from decimal import Decimal

from django.test import TestCase, override_settings

from packages.models import Destination, Package, TravelType
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
        cls.alleppey = Destination.objects.create(
            name="Alleppey",
            travel_type=TravelType.DOMESTIC,
            country="India",
            is_active=True,
        )
        cls.munnar = Destination.objects.create(
            name="Munnar",
            travel_type=TravelType.DOMESTIC,
            country="India",
            is_active=True,
        )
        cls.delhi = Destination.objects.create(
            name="Delhi",
            travel_type=TravelType.INTERNATIONAL,
            country="India",
            is_active=True,
        )
        Package.objects.create(
            title="Alleppey Backwaters",
            slug="alleppey-backwaters",
            travel_type=TravelType.DOMESTIC,
            destination=cls.alleppey,
            short_description="Cruise through serene backwaters from Cochin.",
            route="COCHIN / ALAPPUZHA / COCHIN",
            duration="3 Days / 2 Nights",
            price=Decimal("1500"),
            status=Package.Status.PUBLISHED,
        )
        Package.objects.create(
            title="Golden Triangle",
            slug="golden-triangle",
            travel_type=TravelType.INTERNATIONAL,
            destination=cls.delhi,
            short_description="Delhi Jaipur Agra tour",
            route="DELHI / JAIPUR / AGRA / DELHI",
            duration="09 NIGHTS / 10 DAYS",
            price=Decimal("25000"),
            status=Package.Status.PUBLISHED,
        )
        Package.objects.create(
            title="Munnar Escape",
            slug="munnar-escape",
            travel_type=TravelType.DOMESTIC,
            destination=cls.munnar,
            short_description="Hill station getaway in Munnar",
            route="COCHIN / MUNNAR / COCHIN",
            duration="2 Days / 1 Night",
            price=Decimal("8000"),
            status=Package.Status.PUBLISHED,
        )

    def test_filter_by_destination(self):
        search = PackageSearch(
            travel_type=TravelType.DOMESTIC,
            destination="Alleppey",
        )
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().slug, "alleppey-backwaters")

    def test_filter_by_travel_type(self):
        search = PackageSearch(travel_type=TravelType.DOMESTIC)
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        slugs = set(qs.values_list("slug", flat=True))
        self.assertEqual(slugs, {"alleppey-backwaters", "munnar-escape"})

    def test_relevance_prefers_destination_match(self):
        search = PackageSearch(travel_type="all", destination="Munnar")
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        self.assertEqual(qs.first().slug, "munnar-escape")

    def test_travel_date_does_not_filter_packages(self):
        search = PackageSearch(
            travel_type=TravelType.INTERNATIONAL,
            travel_date=date(2026, 7, 1),
        )
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().slug, "golden-triangle")

    def test_duration_bucket_short(self):
        search = PackageSearch(travel_type="all", duration_bucket=DURATION_SHORT)
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        slugs = set(qs.values_list("slug", flat=True))
        self.assertIn("alleppey-backwaters", slugs)
        self.assertIn("munnar-escape", slugs)
        self.assertNotIn("golden-triangle", slugs)

    def test_sort_price_asc(self):
        search = PackageSearch(travel_type="all", sort=SORT_PRICE_ASC)
        qs = search.apply(Package.objects.filter(status=Package.Status.PUBLISHED))
        prices = list(qs.values_list("price", flat=True))
        self.assertEqual(prices, sorted(prices))

    def test_sort_price_desc(self):
        search = PackageSearch(travel_type="all", sort=SORT_PRICE_DESC)
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

    def test_legacy_to_param_still_works(self):
        from django.test import RequestFactory

        request = RequestFactory().get("/packages/", {"to": "Munnar", "category": "domestic"})
        search = PackageSearch.from_request(request, "domestic")
        self.assertEqual(search.destination, "Munnar")

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
            {"destination": "Alleppey", "adults": "2", "children": "1"},
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
        response = self.client.get(
            "/packages/",
            {
                "destination": "Zzyxnonexistent999",
                "category": "international",
                "depart": "2026-07-05",
                "adults": "2",
                "children": "1",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "wl-search-enquiry")
        self.assertContains(response, "Enter your details")
        self.assertContains(response, "We will reach out to you soon.")
        self.assertNotContains(response, "Search results")
        self.assertContains(response, "Destination: Zzyxnonexistent999")
        self.assertContains(response, "Travel type: International")
        self.assertContains(response, "Travel date: 05 Jul 2026")
        self.assertContains(response, "enquiry_source")

    def test_destination_autocomplete_api(self):
        response = self.client.get(
            "/api/destinations/",
            {"travel_type": "domestic", "search": "mu"},
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        names = [item["name"] for item in data]
        self.assertIn("Munnar", names)
        self.assertNotIn("Delhi", names)

    def test_destination_autocomplete_accepts_free_text_search_without_forcing_match(self):
        response = self.client.get(
            "/api/destinations/",
            {"travel_type": "international", "search": "ladakh"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])
