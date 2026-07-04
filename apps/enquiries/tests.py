"""Tests for contact form and email delivery."""

from __future__ import annotations

from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.models import SiteSettings
from enquiries.models import ContactEnquiry
from packages.models import Package, PackageCategory


@override_settings(
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    },
)
class ContactEnquiryEmailTests(TestCase):
    def setUp(self):
        self.client = Client()
        site = SiteSettings.load()
        site.email = "office@bluelagoon.test"
        site.email_from = "noreply@bluelagoon.test"
        site.email_notification_to = "staff@bluelagoon.test"
        site.smtp_enabled = False
        site.save()

        category = PackageCategory.objects.create(
            name="Domestic",
            slug="domestic",
            category_type=PackageCategory.CategoryType.DOMESTIC,
        )
        self.package = Package.objects.create(
            title="Golden Triangle",
            slug="golden-triangle",
            category=category,
            duration="5 Days / 4 Nights",
            status=Package.Status.PUBLISHED,
        )

    def _valid_payload(self, **overrides):
        data = {
            "first_name": "Achu",
            "last_name": "Joseph",
            "email": "guest@example.com",
            "phone": "+91 9876543210",
            "message": "I would like to book this package for four travellers in December.",
            "captcha_answer": "12",
            "captcha_expected": "12",
        }
        data.update(overrides)
        return data

    def test_contact_form_sends_staff_and_customer_emails(self):
        response = self.client.post(reverse("enquiries:contact"), self._valid_payload())
        self.assertEqual(response.status_code, 302)

        enquiry = ContactEnquiry.objects.get()
        self.assertTrue(enquiry.email_sent)
        self.assertTrue(enquiry.confirmation_sent)
        self.assertEqual(len(mail.outbox), 2)

        staff_mail = next(m for m in mail.outbox if "staff@bluelagoon.test" in m.to)
        customer_mail = next(m for m in mail.outbox if m.to == ["guest@example.com"])
        self.assertEqual(customer_mail.to, ["guest@example.com"])
        self.assertEqual(staff_mail.reply_to, ["guest@example.com"])
        self.assertIn("Achu Joseph", staff_mail.subject)
        self.assertIn("Thank you", customer_mail.subject)

    def test_package_enquiry_prefill_and_notification(self):
        url = reverse("enquiries:contact") + f"?package={self.package.slug}"
        get_response = self.client.get(url)
        self.assertEqual(get_response.status_code, 200)
        self.assertContains(get_response, "Golden Triangle")
        self.assertContains(get_response, self.package.slug)

        payload = self._valid_payload(package_slug=self.package.slug)
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)

        enquiry = ContactEnquiry.objects.get()
        self.assertEqual(enquiry.package_id, self.package.pk)
        staff_mail = next(m for m in mail.outbox if "staff@bluelagoon.test" in m.to)
        self.assertIn("Golden Triangle", staff_mail.subject)
        self.assertIn("Golden Triangle", staff_mail.body)

    def test_contact_form_invalid_shows_errors(self):
        payload = self._valid_payload(message="short")
        response = self.client.post(reverse("enquiries:contact"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "between 10 and 5000")
        self.assertEqual(ContactEnquiry.objects.count(), 0)
        self.assertEqual(len(mail.outbox), 0)

    def test_invalid_package_slug_rejected(self):
        payload = self._valid_payload(package_slug="missing-package")
        response = self.client.post(reverse("enquiries:contact"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactEnquiry.objects.count(), 0)

    def test_package_detail_shows_enquiry_form_with_prefill(self):
        url = reverse("packages:domestic_detail", kwargs={"slug": self.package.slug})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="wl-package-enquiry"')
        self.assertContains(response, "Plan your trip")
        self.assertContains(response, "Arrival date:")
        self.assertContains(response, "Number of adults:")
        self.assertContains(response, self.package.slug)

    def test_package_detail_enquiry_submission(self):
        url = reverse("packages:domestic_detail", kwargs={"slug": self.package.slug})
        payload = self._valid_payload(
            package_slug=self.package.slug,
            message=(
                "I would like to visit Golden Triangle. Kindly find my travel requirements below\n\n"
                "Arrival date: 5th July 2026\n"
                "Departure date: 10th July 2026\n"
                "Number of nights: 5\n"
                "Number of adults: 2\n"
                "Number of child: 1 (Age: 5)"
            ),
        )
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.endswith("#wl-package-enquiry"))

        enquiry = ContactEnquiry.objects.get()
        self.assertEqual(enquiry.package_id, self.package.pk)
        self.assertIn("5th July 2026", enquiry.message)
        staff_mail = next(m for m in mail.outbox if "staff@bluelagoon.test" in m.to)
        self.assertIn("Golden Triangle", staff_mail.subject)

    def test_empty_search_enquiry_submission(self):
        url = "/packages/?destination=Zzyxnonexistent999&category=international"
        payload = {
            "enquiry_source": "package_search",
            "first_name": "Achu",
            "last_name": "Joseph",
            "email": "guest@example.com",
            "phone": "+91 9876543210",
            "message": (
                "I searched for a trip matching my requirements, but none of our current "
                "pre-designed packages fit exactly. Please help me plan a custom itinerary."
            ),
            "captcha_answer": "12",
            "captcha_expected": "12",
        }
        response = self.client.post(url, payload)
        self.assertEqual(response.status_code, 302)
        self.assertIn("#wl-search-enquiry", response.url)
        self.assertEqual(ContactEnquiry.objects.count(), 1)
