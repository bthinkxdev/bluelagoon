"""Django admin — packages, destinations, and categories."""

from django.contrib import admin

from packages.models import (
    Destination,
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


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "travel_type",
        "country",
        "state",
        "is_active",
        "display_order",
        "updated_at",
    )
    list_filter = ("travel_type", "is_active", "country")
    search_fields = ("name", "country", "state", "description")
    list_editable = ("is_active", "display_order")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("display_order", "name")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "name",
                    "slug",
                    "travel_type",
                    "country",
                    "state",
                    "is_active",
                    "display_order",
                )
            },
        ),
        (
            "Content",
            {"fields": ("description", "image")},
        ),
    )


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
    list_display = (
        "title",
        "destination",
        "category",
        "duration",
        "price",
        "status",
        "display_order",
    )
    list_filter = ("category", "destination__travel_type", "status", "category__category_type")
    search_fields = ("title", "short_description", "route", "destination__name")
    prepopulated_fields = {"slug": ("title",)}
    list_editable = ("display_order", "status")
    autocomplete_fields = ("destination",)
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
                    "destination",
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
                    "Destination drives package search. Category is kept for package detail URLs. "
                    "Duration is the label shown on the site (e.g. 3 Days / 2 Nights). "
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
