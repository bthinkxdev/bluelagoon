"""Shared model utilities and mixins."""

from __future__ import annotations

from django.db import models
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    """Abstract base with created/updated timestamps."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SEOMixin(models.Model):
    """Reusable SEO fields for pages and packages."""

    meta_title = models.CharField(max_length=200, blank=True)
    meta_description = models.TextField(blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    canonical_url = models.URLField(blank=True)
    og_image = models.ImageField(upload_to="seo/", blank=True, null=True)

    class Meta:
        abstract = True

    def get_meta_title(self) -> str:
        return self.meta_title or getattr(self, "title", "")

    def get_meta_description(self) -> str:
        return self.meta_description or ""


class SluggedModel(models.Model):
    """Auto-generate unique slugs from title/name."""

    slug = models.SlugField(max_length=220, unique=True, blank=True)

    class Meta:
        abstract = True

    def _slug_source(self) -> str:
        return getattr(self, "title", None) or getattr(self, "name", "")

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self._slug_source())[:200] or "item"
            slug = base
            counter = 1
            model = self.__class__
            while model.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
