"""Import legacy HTML content into database."""

from __future__ import annotations

from decimal import Decimal

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from core.models import (
    Banner,
    HomeActivity,
    HomeFeatureBox,
    HomePackageHighlight,
    HomePromoBanner,
    HomeSlider,
    HomeSpotlight,
    NavigationItem,
    OfficeBranch,
    SiteSettings,
)
from gallery.models import GalleryImage
from packages.models import (
    Package,
    PackageCategory,
    PackageExclusion,
    PackageInclusion,
    PackagePrice,
)
from website.models import StaticPage


class Command(BaseCommand):
    help = "Seed database with content migrated from legacy Blue Lagoon PHP/HTML site"

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING(
                "import_legacy_data is deprecated after the CMS streamline. "
                "Use Django admin to manage banners, packages, gallery, and contact settings."
            )
        )
        return
        self._site_settings()
        self._navigation()
        self._branches()
        self._categories()
        self._domestic_packages()
        self._international_packages()
        self._static_pages()
        self._home_content()
        self._banners()
        self._gallery_placeholders()
        self.stdout.write(self.style.SUCCESS("Legacy data import complete."))

    def _site_settings(self):
        SiteSettings.load()

    def _navigation(self):
        if NavigationItem.objects.exists():
            return
        home = NavigationItem.objects.create(label="Home", url_name="core:home", display_order=1)
        NavigationItem.objects.create(label="About", url_name="website:about", display_order=2)
        NavigationItem.objects.create(label="Services", url_name="website:services", display_order=3)
        packages = NavigationItem.objects.create(
            label="Packages", url_name="", display_order=4
        )
        NavigationItem.objects.create(
            label="Domestic",
            url_name="packages:domestic_list",
            parent=packages,
            display_order=1,
        )
        NavigationItem.objects.create(
            label="International",
            url_name="packages:international_list",
            parent=packages,
            display_order=2,
        )
        NavigationItem.objects.create(label="Gallery", url_name="gallery:list", display_order=5)
        NavigationItem.objects.create(label="Contact us", url_name="enquiries:contact", display_order=6)
        self.stdout.write(f"  Navigation created (home id={home.pk})")

    def _branches(self):
        if OfficeBranch.objects.exists():
            return
        OfficeBranch.objects.create(
            name="Registered Office",
            address="BLUE LAGOON HOLIDAY CRUISES PVT LTD, AYINI BYPASS LINK ROAD, "
            "VITHAYATHIL BUILDING, MARADU, ERNAKULAM, KERALA 682304",
            phone_primary="+91 9846308744",
            phone_secondary="",
            email="mail@bluelagoonholidays.net",
            display_order=1,
        )
        OfficeBranch.objects.create(
            name="Thiruvankulam Branch",
            address="TEMPLE ROAD, THIRUVANKULAM, COCHIN 682305",
            phone_primary="+91 9846308744",
            email="mail@bluelagoonholidays.net",
            display_order=2,
        )
        OfficeBranch.objects.create(
            name="Koothuparamba Branch",
            address="MUNICIPAL SHOPPING COMPLEX, KOOTHUPARAMP",
            phone_primary="+91 9846308744",
            email="bluelagoonholiday@gmail.com",
            display_order=3,
        )
        OfficeBranch.objects.create(
            name="Kannur Branch",
            address="HIRA CENTER, GOVERNMENT HOSPITAL ROAD, MATTANNUR, KANNUR - 670702",
            phone_primary="+91 9846308744",
            email="bluelagoonholiday@gmail.com",
            display_order=4,
        )

    def _categories(self):
        categories = [
            ("Domestic", PackageCategory.CategoryType.DOMESTIC, "domestic"),
            ("International", PackageCategory.CategoryType.INTERNATIONAL, "international"),
            ("Kerala", PackageCategory.CategoryType.KERALA, "kerala"),
            ("Pilgrim", PackageCategory.CategoryType.PILGRIM, "pilgrim"),
        ]
        for name, ctype, slug in categories:
            PackageCategory.objects.get_or_create(
                slug=slug, defaults={"name": name, "category_type": ctype}
            )

    def _domestic_packages(self):
        domestic = PackageCategory.objects.get(category_type=PackageCategory.CategoryType.DOMESTIC)
        packages = [
            {
                "slug": "athirapilly-waterfalls",
                "title": "Athirapilly Waterfalls",
                "short_description": "Sed pretium, ligula sollicitudin laoreet viverra, tortor libero sodales leo.",
                "duration": "3 Days / 2 Nights",
                "price": Decimal("1500"),
                "compare_price": Decimal("2500"),
                "legacy_image_prefix": "1",
                "display_order": 1,
            },
            {
                "slug": "kuttanad-water-festival",
                "title": "Kuttanad Water Festival",
                "short_description": "Experience the vibrant water festival of Kuttanad backwaters.",
                "duration": "3 Days / 2 Nights",
                "price": Decimal("1500"),
                "compare_price": Decimal("2500"),
                "legacy_image_prefix": "1",
                "display_order": 2,
            },
            {
                "slug": "alleppey-backwaters",
                "title": "Alleppey Backwaters",
                "short_description": "Cruise through the serene backwaters of Alleppey.",
                "duration": "3 Days / 2 Nights",
                "price": Decimal("1500"),
                "compare_price": Decimal("2500"),
                "legacy_image_prefix": "1",
                "display_order": 3,
            },
        ]
        for data in packages:
            pkg, created = Package.objects.get_or_create(
                slug=data["slug"],
                defaults={**data, "category": domestic, "status": Package.Status.PUBLISHED},
            )
            if created:
                self._add_standard_inclusions(pkg)

    def _international_packages(self):
        international = PackageCategory.objects.get(
            category_type=PackageCategory.CategoryType.INTERNATIONAL
        )
        packages = [
            {
                "slug": "golden-triangle",
                "title": "GOLDEN TRIANGLE",
                "short_description": "09 NIGHTS / 10 DAYS (DELHI / JAIPUR / RANTHAMBORE / AGRA / DELHI)",
                "duration": "09 NIGHTS / 10 DAYS",
                "route": "DELHI / JAIPUR / RANTHAMBORE / AGRA / DELHI",
                "price": Decimal("1500"),
                "compare_price": Decimal("2500"),
                "legacy_image_prefix": "",
                "description": (
                    "Rajasthan, a largest state of India in terms of area, is well known for its "
                    "splendid garrisons and palaces, folk and classical dances with multicolored "
                    "attires, camel & elephant rides and sadhus with lengthy disheveled hair."
                ),
                "display_order": 1,
            },
            {
                "slug": "heavenly-abode",
                "title": "HEAVENLY ABODE",
                "short_description": "6 NIGHTS / 7 DAYS (SRINAGAR / PAHALGAM / GULMARG / SRINAGAR / SONMARG / DELHI)",
                "duration": "6 NIGHTS / 7 DAYS",
                "route": "SRINAGAR / PAHALGAM / GULMARG / SRINAGAR / SONMARG / DELHI",
                "price": Decimal("1500"),
                "compare_price": Decimal("2500"),
                "legacy_image_prefix": "1",
                "display_order": 2,
            },
            {
                "slug": "hills-and-backwaters",
                "title": "HILLS AND BACKWATERS",
                "short_description": "3 NIGHTS / 2 DAYS (COCHIN / THEKKADY / ALAPPUZHA / COCHIN)",
                "duration": "3 NIGHTS / 2 DAYS",
                "route": "COCHIN / THEKKADY / ALAPPUZHA / COCHIN",
                "price": Decimal("1500"),
                "compare_price": Decimal("2500"),
                "legacy_image_prefix": "2",
                "display_order": 3,
            },
        ]
        for data in packages:
            pkg, created = Package.objects.get_or_create(
                slug=data["slug"],
                defaults={**data, "category": international, "status": Package.Status.PUBLISHED},
            )
            if created:
                self._add_standard_inclusions(pkg)
                PackagePrice.objects.bulk_create(
                    [
                        PackagePrice(
                            package=pkg,
                            season_label="Low (from 23/03 to 31/05)",
                            price=Decimal("1400"),
                            display_order=1,
                        ),
                        PackagePrice(
                            package=pkg,
                            season_label="Middle (from 23/03 to 31/05)",
                            price=Decimal("1500"),
                            display_order=2,
                        ),
                        PackagePrice(
                            package=pkg,
                            season_label="High (from 23/03 to 31/05)",
                            price=Decimal("1600"),
                            display_order=3,
                        ),
                    ]
                )

    def _add_standard_inclusions(self, pkg):
        inclusions = [
            "Accommodation for nights in Twin/Double room on bed & breakfast basis",
            "Transportation by private Air conditioned vehicle",
            "Local English Speaking Guide during City tour only",
            "Monument entry fee (single visit)",
            "Present applicable taxes",
        ]
        exclusions = [
            "International air fare",
            "Visa / Insurance charges",
            "Camera fee at monument",
            "Items of personal nature viz, tips, porterage, room service, laundry etc.",
        ]
        PackageInclusion.objects.bulk_create(
            [PackageInclusion(package=pkg, text=t, display_order=i) for i, t in enumerate(inclusions, 1)]
        )
        PackageExclusion.objects.bulk_create(
            [PackageExclusion(package=pkg, text=t, display_order=i) for i, t in enumerate(exclusions, 1)]
        )

    def _static_pages(self):
        StaticPage.objects.get_or_create(
            slug="about",
            defaults={
                "title": "About Us",
                "page_type": StaticPage.PageType.ABOUT,
                "subtitle": "Blue Lagoon Holidays",
                "content": "<p>Blue Lagoon Holiday Cruises Pvt Ltd offers curated tour packages across Kerala and beyond.</p>",
                "is_published": True,
            },
        )
        StaticPage.objects.get_or_create(
            slug="services",
            defaults={
                "title": "Services",
                "page_type": StaticPage.PageType.SERVICES,
                "content": "<p>We provide tour planning, hotel bookings, and customized itineraries.</p>",
                "is_published": True,
            },
        )
        StaticPage.objects.get_or_create(
            slug="wayanad",
            defaults={
                "title": "WAYANAD",
                "page_type": StaticPage.PageType.LANDING,
                "subtitle": "Enjoy spectacular Wayanad",
                "banner_css_class": "about-wayanad",
                "content": "<p>Wayanad is located at the Western Ghats of Kerala. It is a green paradise nestled in the mountain region.</p>",
                "is_published": True,
            },
        )
        StaticPage.objects.get_or_create(
            slug="pilgrim-packages",
            defaults={
                "title": "Pilgrim Packages",
                "page_type": StaticPage.PageType.LANDING,
                "content": "<p>The chanting of hallowed prayers can be experienced on a pilgrimage tour to India.</p>",
                "is_published": True,
            },
        )
        StaticPage.objects.get_or_create(
            slug="international-packages",
            defaults={
                "title": "International Packages",
                "page_type": StaticPage.PageType.LANDING,
                "content": "<p>Explore our curated international tour packages.</p>",
                "is_published": True,
            },
        )

    def _home_content(self):
        if HomeFeatureBox.objects.exists():
            return
        HomeFeatureBox.objects.bulk_create(
            [
                HomeFeatureBox(
                    title="Cozy and Charming Destinations",
                    description="Kerala is one of the most charming and captivating states of India.",
                    display_order=1,
                ),
                HomeFeatureBox(
                    title="Relax in a beautiful contest",
                    description="Kerala is a colorful land of fairs and festivals.",
                    display_order=2,
                ),
                HomeFeatureBox(
                    title="Enjoy Tour activities",
                    description="Beaches, backwaters, houseboats, traditional villages, and verdant hill stations.",
                    display_order=3,
                ),
            ]
        )
        HomePackageHighlight.objects.bulk_create(
            [
                HomePackageHighlight(
                    title="Kerala Packages",
                    description="Kerala is one of the most charming and captivating states of India.",
                    link_url="/pages/wayanad/",
                    display_order=1,
                ),
                HomePackageHighlight(
                    title="Lakshadweep Packages",
                    description="One of world's most spectacular tropical island systems.",
                    link_url="http://lakshadweepcruises.com/",
                    is_external=True,
                    display_order=2,
                ),
                HomePackageHighlight(
                    title="International Packages",
                    description="Explore international destinations with Blue Lagoon Holidays.",
                    link_url="/pages/international-packages/",
                    display_order=3,
                ),
                HomePackageHighlight(
                    title="Piligrim Packages",
                    description="Spiritual trips across India's holy centers.",
                    link_url="/pages/pilgrim-packages/",
                    display_order=4,
                ),
            ]
        )
        HomeActivity.objects.bulk_create(
            [
                HomeActivity(title="Take a ride on Elephants", description="Elephant safari trips through difficult terrains.", display_order=1),
                HomeActivity(title="Discover typical Food", description="Kerala food is hot and spicy with fresh spices.", display_order=2),
                HomeActivity(title="Learn to cook delicious food", description="Every district has mouth-watering delicacies.", display_order=3),
                HomeActivity(title="Ayurvedic Treatments", description="Ayurvedic treatment peculiar to Kerala tradition.", display_order=4),
            ]
        )
        HomePromoBanner.objects.get_or_create(
            headline="This week only for all rides!",
            highlight_text="-30% OFF",
        )
        HomeSpotlight.objects.get_or_create(
            title="Enjoy spectacular Wayanad",
            defaults={
                "description": "Wayanad is located at the Western Ghats of Kerala.",
                "link_url": "/pages/wayanad/",
                "css_class": "about-wayanad",
            },
        )
        HomeSlider.objects.get_or_create(
            title="Blue Lagoon Holidays",
            defaults={
                "subtitle": "Destinations / Tour activities / Pleasure",
                "link_url": "/pages/wayanad/",
                "link_text": "View More",
            },
        )

    def _banners(self):
        if Banner.objects.exists():
            return
        image_path = settings.BASE_DIR / "static" / "img" / "slide-1.jpg"
        if not image_path.exists():
            self.stdout.write(self.style.WARNING("slide-1.jpg not found; skip default banner seed."))
            return
        with image_path.open("rb") as image_file:
            Banner.objects.create(
                title="Default Home Hero",
                subtitle="Your Journey Awaits",
                heading="Explore the <em>world</em>.<br>Create unforgettable memories.",
                description=(
                    "From breathtaking islands and vibrant cities to peaceful mountain escapes, "
                    "discover handcrafted travel experiences designed with comfort, elegance, "
                    "and unforgettable memories in mind."
                ),
                desktop_image=File(image_file, name="slide-1.jpg"),
                text_alignment="left",
                text_color="white",
                overlay_opacity=Decimal("0"),
                primary_button_text="Explore Packages",
                primary_button_url="/packages/",
                primary_button_style="primary",
                secondary_button_text="View Gallery",
                secondary_button_url="/gallery/",
                secondary_button_style="glass",
                animation="kenburns",
                order=1,
                is_active=True,
            )
        self.stdout.write("Created default homepage banner.")

    def _gallery_placeholders(self):
        if GalleryImage.objects.exists():
            return
        for i in range(1, 21):
            GalleryImage.objects.create(
                title=f"Photo {i}",
                legacy_filename=f"pic_{i}.jpg",
                display_order=i,
                alt_text=f"Blue Lagoon Holidays gallery photo {i}",
            )
