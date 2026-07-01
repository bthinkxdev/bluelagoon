"""Sitemap configuration."""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from gallery.models import GalleryImage
from packages.models import Package


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "core:home",
            "website:about",
            "website:services",
            "gallery:list",
            "enquiries:contact",
            "packages:list",
        ]

    def location(self, item):
        return reverse(item)


class PackageSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.9

    def items(self):
        return Package.objects.filter(status=Package.Status.PUBLISHED)

    def lastmod(self, obj):
        return obj.updated_at


class GallerySitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.5

    def items(self):
        return GalleryImage.objects.filter(is_active=True)[:50]

    def lastmod(self, obj):
        return obj.updated_at
