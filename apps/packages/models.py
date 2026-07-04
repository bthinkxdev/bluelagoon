"""Tour package models — streamlined for CMS."""

from __future__ import annotations

from django.db import models

from ckeditor.fields import RichTextField

from core.mixins import SluggedModel, TimeStampedModel


class TravelType(models.TextChoices):
    """Domestic / International / Pilgrimage — used on packages and destinations."""

    DOMESTIC = "domestic", "Domestic"
    INTERNATIONAL = "international", "International"
    PILGRIM = "pilgrim", "Pilgrimage"


class Destination(TimeStampedModel, SluggedModel):
    """Searchable travel destination within a travel type."""

    name = models.CharField(max_length=160, db_index=True)
    travel_type = models.CharField(
        max_length=20,
        choices=TravelType.choices,
        db_index=True,
    )
    country = models.CharField(max_length=120, blank=True, default="")
    state = models.CharField(max_length=120, blank=True, default="")
    description = models.TextField(blank=True, default="")
    image = models.ImageField(upload_to="destinations/", blank=True, null=True)
    is_active = models.BooleanField(default=True, db_index=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "name"]
        indexes = [
            models.Index(fields=["travel_type", "is_active", "name"]),
        ]
        verbose_name = "Destination"
        verbose_name_plural = "Destinations"

    def _slug_source(self) -> str:
        return self.name

    def __str__(self) -> str:
        return f"{self.name} ({self.get_travel_type_display()})"


class Package(TimeStampedModel, SluggedModel):
    """Tour package."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=200)
    travel_type = models.CharField(
        max_length=20,
        choices=TravelType.choices,
        default=TravelType.DOMESTIC,
        db_index=True,
        help_text="Domestic, International, or Pilgrimage — used for URLs, tabs, and badges.",
    )
    destination = models.ForeignKey(
        "Destination",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="packages",
        help_text="Primary destination used for search and filtering.",
    )
    short_description = models.CharField(
        max_length=500, blank=True, help_text="Short summary for listings."
    )
    description = RichTextField(blank=True, help_text="Full package description.")
    duration = models.CharField(
        max_length=120,
        blank=True,
        help_text="Display text, e.g. 09 NIGHTS / 10 DAYS (used for filters/sort).",
    )
    duration_days = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        editable=False,
        help_text="Auto-calculated from duration — not shown in admin.",
    )
    route = models.CharField(
        max_length=500, blank=True, help_text="e.g. DELHI / JAIPUR / AGRA"
    )
    hero_banner = models.ImageField(
        upload_to="packages/hero/desktop/",
        blank=True,
        null=True,
        help_text="Desktop hero — upload exactly 1920×400 px.",
    )
    hero_banner_mobile = models.ImageField(
        upload_to="packages/hero/mobile/",
        blank=True,
        null=True,
        help_text="Mobile hero — upload exactly 390×400 px (or 780×800 px @2x). Falls back to desktop hero if empty.",
    )
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_note = models.CharField(max_length=120, blank=True, default="*Pax/Per Day")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PUBLISHED)
    is_featured = models.BooleanField(default=False)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order", "title"]

    def _slug_source(self) -> str:
        return self.title

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        from packages.search import extract_duration_days

        if self.destination_id:
            destination = self.destination
            if destination and destination.travel_type in TravelType.values:
                self.travel_type = destination.travel_type
        self.duration_days = extract_duration_days(self.duration or "")
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        from django.urls import reverse

        routes = {
            TravelType.DOMESTIC: "packages:domestic_detail",
            TravelType.INTERNATIONAL: "packages:international_detail",
            TravelType.PILGRIM: "packages:pilgrim_detail",
        }
        route = routes.get(self.travel_type, "packages:domestic_detail")
        return reverse(route, kwargs={"slug": self.slug})


class PackageImage(TimeStampedModel):
    """Photos for a package (detail gallery + listing thumbnail)."""

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="packages/gallery/")
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Package photo"
        verbose_name_plural = "Package photos"

    def __str__(self) -> str:
        return f"{self.package.title} — photo {self.display_order}"


class PackageInclusion(TimeStampedModel):
    """What's included in the package."""

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="inclusions")
    text = models.CharField(max_length=255)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Inclusion"
        verbose_name_plural = "Inclusions"

    def __str__(self) -> str:
        return self.text[:60]


class PackageExclusion(TimeStampedModel):
    """What's not included in the package."""

    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="exclusions")
    text = models.CharField(max_length=255)
    display_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["display_order"]
        verbose_name = "Exclusion"
        verbose_name_plural = "Exclusions"

    def __str__(self) -> str:
        return self.text[:60]


class Testimonial(TimeStampedModel):
    """Guest review shown on home and package detail pages."""

    package = models.ForeignKey(
        Package,
        on_delete=models.CASCADE,
        related_name="testimonials",
    )
    name = models.CharField(max_length=120)
    quote = models.TextField(help_text="Testimonial text.")
    rating = models.PositiveSmallIntegerField(
        default=5,
        help_text="Star rating from 1 to 5.",
    )
    photo = models.ImageField(upload_to="testimonials/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self) -> str:
        return f"{self.name} — {self.package.title}"

    @property
    def rating_clamped(self) -> int:
        return max(1, min(5, self.rating or 5))
