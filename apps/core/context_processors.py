"""Site-wide template context."""

from __future__ import annotations

from django.conf import settings

from core.models import NavigationItem, SiteSettings


def site_context(request):
    """Inject site settings and navigation into every template."""
    settings_obj = SiteSettings.load()
    nav_items = (
        NavigationItem.objects.filter(parent__isnull=True, is_active=True)
        .prefetch_related("children")
    )
    return {
        "site_settings": settings_obj,
        "site_name": settings.SITE_NAME,
        "site_url": settings.SITE_URL,
        "navigation_items": nav_items,
    }
