"""Django admin — packages and categories."""

from django.contrib import admin

from packages.models import (
    Package,
    PackageCategory,
    PackageExclusion,
    PackageImage,
    PackageInclusion,
    Testimonial,
)


class PackageImageInline(admin.TabularInline):
    model = PackageImage
    extra = 3
    fields = ("display_order", "image", "alt_text")
    ordering = ("display_order",)
    verbose_name = "Photo"
    verbose_name_plural = "Package photos"


class PackageInclusionInline(admin.TabularInline):
    model = PackageInclusion
    extra = 3
    fields = ("display_order", "text")
    ordering = ("display_order",)


class PackageExclusionInline(admin.TabularInline):
    model = PackageExclusion
    extra = 3
    fields = ("display_order", "text")
    ordering = ("display_order",)


class TestimonialInline(admin.TabularInline):
    model = Testimonial
    extra = 1
    fields = ("display_order", "name", "rating", "quote", "photo", "is_active")
    ordering = ("display_order",)


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "package", "rating", "display_order", "is_active")
    list_filter = ("is_active", "package__category")
    search_fields = ("name", "quote", "package__title")
    list_editable = ("display_order", "is_active")
    autocomplete_fields = ("package",)
    ordering = ("display_order", "-created_at")


@admin.register(PackageCategory)
class PackageCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "category_type", "is_active")
    list_filter = ("category_type", "is_active")
    list_editable = ("is_active",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "duration", "price", "status", "display_order")
    list_filter = ("category", "status", "category__category_type")
    search_fields = ("title", "short_description", "route")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("display_order", "status")
    inlines = [
        PackageImageInline,
        PackageInclusionInline,
        PackageExclusionInline,
        TestimonialInline,
    ]
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "title",
                    "slug",
                    "category",
                    "status",
                    "is_featured",
                    "display_order",
                )
            },
        ),
        (
            "Details",
            {
                "fields": (
                    "short_description",
                    "description",
                    "duration",
                    "route",
                    "hero_banner",
                    "hero_banner_mobile",
                    "price",
                    "price_note",
                ),
                "description": (
                    "Duration is the label shown on the site (e.g. 3 Days / 2 Nights). "
                    "Sorting and duration filters use it automatically. "
                    "Hero banners: desktop 1920×400 px, mobile 390×400 px (780×800 @2x). "
                    "Gallery photos stay 1920×1080."
                ),
            },
        ),
        (
            "Photos & lists",
            {
                "fields": (),
                "description": (
                    "Add photos, inclusions, exclusions, and testimonials below. "
                    "Testimonials appear on the home page and on this package's detail page."
                ),
            },
        ),
    )
