"""Gallery models — flat photo list with titles."""

from __future__ import annotations

from django.db import models

from core.mixins import TimeStampedModel


class GalleryImage(TimeStampedModel):
    """Site gallery photo."""

    title = models.CharField(max_length=200)
    image = models.ImageField(upload_to="gallery/")
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order", "-created_at"]
        verbose_name = "Gallery photo"
        verbose_name_plural = "Gallery photos"

    def __str__(self) -> str:
        return self.title
