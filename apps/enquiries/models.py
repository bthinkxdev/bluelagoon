"""Enquiry and contact form models."""

from __future__ import annotations

from django.db import models

from core.mixins import TimeStampedModel


class ContactEnquiry(TimeStampedModel):
    """General contact form submission."""

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    message = models.TextField()
    package = models.ForeignKey(
        "packages.Package",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="contact_enquiries",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)
    confirmation_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Contact enquiries"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name} — {self.email}"

    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class PackageEnquiry(TimeStampedModel):
    """Package-specific enquiry."""

    package = models.ForeignKey(
        "packages.Package", on_delete=models.SET_NULL, null=True, blank=True, related_name="enquiries"
    )
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    travel_date = models.DateField(null=True, blank=True)
    guests = models.PositiveIntegerField(default=1)
    message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Package enquiries"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} — {self.package or 'General'}"


class NewsletterSubscription(TimeStampedModel):
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email
