"""Static website pages and services."""

from __future__ import annotations

from django.db import models

from ckeditor.fields import RichTextField

from core.mixins import SEOMixin, SluggedModel, TimeStampedModel


class StaticPage(TimeStampedModel, SluggedModel, SEOMixin):
    """CMS-managed static pages (About, Services, category landings)."""

    class PageType(models.TextChoices):
        ABOUT = "about", "About"
        SERVICES = "services", "Services"
        LANDING = "landing", "Landing Page"
        CUSTOM = "custom", "Custom"

    title = models.CharField(max_length=200)
    page_type = models.CharField(max_length=20, choices=PageType.choices, default=PageType.CUSTOM)
    subtitle = models.CharField(max_length=255, blank=True)
    content = RichTextField(blank=True)
    banner_css_class = models.CharField(max_length=80, blank=True)
    hero_image = models.ImageField(
        upload_to="pages/",
        blank=True,
        null=True,
        help_text="Deprecated — use Admin → Core → Page heroes for banner images.",
    )
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["title"]

    def _slug_source(self) -> str:
        return self.title

    def __str__(self) -> str:
        return self.title


class Service(TimeStampedModel, SluggedModel):
    """Individual service offering."""

    title = models.CharField(max_length=200)
    short_description = models.TextField(blank=True)
    description = RichTextField(blank=True)
    icon_class = models.CharField(max_length=80, blank=True)
    image = models.ImageField(upload_to="services/", blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "title"]

    def _slug_source(self) -> str:
        return self.title

    def __str__(self) -> str:
        return self.title
