"""Django admin — gallery photos."""

from django.contrib import admin
from django.utils.html import format_html

from gallery.models import GalleryImage


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ("title", "image_preview", "display_order", "is_active", "created_at")
    list_editable = ("display_order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)
    ordering = ("display_order", "-created_at")

    @admin.display(description="Preview")
    def image_preview(self, obj: GalleryImage):
        if obj.image:
            return format_html(
                '<img src="{}" alt="" style="height:40px;width:auto;border-radius:6px;">',
                obj.image.url,
            )
        return format_html('<span style="color:#b45309;">No file — upload image</span>')
