"""SEO template tags and JSON-LD helpers."""

from __future__ import annotations

import json

from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.inclusion_tag("includes/seo_meta.html", takes_context=True)
def seo_meta(context, obj=None, title=None, description=None, image=None):
    """Render SEO meta tags, OpenGraph, and Twitter cards."""
    page_title = title or (obj.get_meta_title() if obj and hasattr(obj, "get_meta_title") else "")
    page_description = description or (
        obj.get_meta_description() if obj and hasattr(obj, "get_meta_description") else ""
    )
    canonical = ""
    if obj and hasattr(obj, "canonical_url") and obj.canonical_url:
        canonical = obj.canonical_url
    elif "request" in context:
        canonical = context["request"].build_absolute_uri()

    og_image = image
    if not og_image and obj and hasattr(obj, "og_image") and obj.og_image:
        og_image = obj.og_image.url
    elif not og_image and obj and hasattr(obj, "banner_image") and obj.banner_image:
        og_image = obj.banner_image.url

    return {
        "page_title": page_title or settings.SITE_NAME,
        "page_description": page_description,
        "canonical_url": canonical,
        "og_image": og_image,
        "site_name": settings.SITE_NAME,
    }


@register.simple_tag
def schema_org_json(data: dict) -> str:
    """Output Schema.org JSON-LD script tag."""
    return mark_safe(
        f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'
    )
