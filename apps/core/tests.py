from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from core.models import PageHero
from core.page_heroes import clear_page_hero_cache, get_page_hero_url, get_page_hero_urls


@override_settings(
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
)
class PageHeroTests(TestCase):
    def setUp(self):
        clear_page_hero_cache()
        for page_key, _label in PageHero.PageKey.choices:
            PageHero.objects.get_or_create(page_key=page_key)

    def tearDown(self):
        clear_page_hero_cache()

    def test_fallback_when_no_upload(self):
        url = get_page_hero_url(PageHero.PageKey.SERVICES)
        self.assertIn("/static/", url)
        self.assertIn("slide-1.jpg", url)

    def test_db_image_when_uploaded(self):
        hero = PageHero.objects.get(page_key=PageHero.PageKey.SERVICES)
        hero.image.save(
            "services-hero.jpg",
            SimpleUploadedFile(
                "services-hero.jpg",
                b"fake-image-bytes",
                content_type="image/jpeg",
            ),
            save=True,
        )
        clear_page_hero_cache()
        self.assertIn("services-hero", get_page_hero_url(PageHero.PageKey.SERVICES))

    def test_inactive_hero_uses_fallback(self):
        hero = PageHero.objects.get(page_key=PageHero.PageKey.SERVICES)
        hero.image.save(
            "services-hero.jpg",
            SimpleUploadedFile("services-hero.jpg", b"x", content_type="image/jpeg"),
            save=True,
        )
        hero.is_active = False
        hero.save()
        clear_page_hero_cache()
        self.assertIn("slide-1.jpg", get_page_hero_url(PageHero.PageKey.SERVICES))

    def test_mobile_falls_back_to_desktop(self):
        hero = PageHero.objects.get(page_key=PageHero.PageKey.SERVICES)
        hero.image.save(
            "services-desktop.jpg",
            SimpleUploadedFile("services-desktop.jpg", b"desktop", content_type="image/jpeg"),
            save=True,
        )
        clear_page_hero_cache()
        urls = get_page_hero_urls(PageHero.PageKey.SERVICES)
        self.assertIn("services-desktop", urls.desktop)
        self.assertEqual(urls.desktop, urls.mobile)

    def test_mobile_image_when_uploaded(self):
        hero = PageHero.objects.get(page_key=PageHero.PageKey.SERVICES)
        hero.image.save(
            "services-desktop.jpg",
            SimpleUploadedFile("services-desktop.jpg", b"desktop", content_type="image/jpeg"),
            save=True,
        )
        hero.mobile_image.save(
            "services-mobile.jpg",
            SimpleUploadedFile("services-mobile.jpg", b"mobile", content_type="image/jpeg"),
            save=True,
        )
        clear_page_hero_cache()
        urls = get_page_hero_urls(PageHero.PageKey.SERVICES)
        self.assertIn("services-mobile", urls.mobile)
        self.assertNotEqual(urls.desktop, urls.mobile)

    def test_pilgrim_list_and_landing_use_different_keys(self):
        list_url = get_page_hero_url(PageHero.PageKey.PACKAGES_PILGRIM)
        landing_url = get_page_hero_url(PageHero.PageKey.LANDING_PILGRIM)
        self.assertNotEqual(PageHero.PageKey.PACKAGES_PILGRIM, PageHero.PageKey.LANDING_PILGRIM)
        # Separate DB rows — uploads can differ even when fallbacks match.
        list_hero = PageHero.objects.get(page_key=PageHero.PageKey.PACKAGES_PILGRIM)
        landing_hero = PageHero.objects.get(page_key=PageHero.PageKey.LANDING_PILGRIM)
        self.assertNotEqual(list_hero.pk, landing_hero.pk)
        list_hero.image.save(
            "pilgrim-list.jpg",
            SimpleUploadedFile("pilgrim-list.jpg", b"list", content_type="image/jpeg"),
            save=True,
        )
        clear_page_hero_cache()
        self.assertIn("pilgrim-list", get_page_hero_url(PageHero.PageKey.PACKAGES_PILGRIM))
        self.assertNotIn("pilgrim-list", landing_url)
        self.assertEqual(landing_url, get_page_hero_url(PageHero.PageKey.LANDING_PILGRIM))

    def test_seed_creates_one_row_per_page(self):
        self.assertEqual(PageHero.objects.count(), len(PageHero.PageKey.choices))
