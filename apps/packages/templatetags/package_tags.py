"""Template helpers for package listings."""

from __future__ import annotations

import re
from urllib.parse import quote

from django import template
from django.templatetags.static import static

register = template.Library()


@register.filter
def route_bullets(value: str) -> str:
    """Format DELHI / JAIPUR / AGRA as DELHI • JAIPUR • AGRA."""
    if not value:
        return ""
    parts = [part.strip() for part in re.split(r"\s*/\s*", value) if part.strip()]
    return " • ".join(parts)


@register.filter
def phone_tel(value: str) -> str:
    """Digits for tel: links (keeps leading +)."""
    if not value:
        return ""
    cleaned = re.sub(r"[^\d+]", "", value)
    return cleaned


@register.filter
def whatsapp_href(value: str, message: str = "") -> str:
    """WhatsApp chat URL for wa.me using the site's phone number."""
    if not value:
        return ""
    digits = re.sub(r"\D", "", value)
    if not digits:
        return ""
    url = f"https://wa.me/{digits}"
    if message:
        url = f"{url}?text={quote(message)}"
    return url


@register.filter
def star_rating(value) -> range:
    """Range 1..rating for filled star loops."""
    try:
        count = int(value)
    except (TypeError, ValueError):
        count = 5
    count = max(1, min(5, count))
    return range(1, count + 1)


def _gallery_slide(url: str, alt: str) -> dict[str, str]:
    return {"src": url, "alt": alt}


@register.simple_tag
def package_gallery_images(package) -> list[dict[str, str]]:
    """Uploaded photos for this package only."""
    slides: list[dict[str, str]] = []
    seen: set[str] = set()
    for img in package.images.all():
        if not img.image:
            continue
        url = img.image.url
        if url in seen:
            continue
        seen.add(url)
        slides.append(_gallery_slide(url, img.alt_text or package.title))
    return slides


@register.simple_tag
def package_hero_image(package) -> str:
    """First uploaded package photo, or site placeholder."""
    gallery = package_gallery_images(package)
    if gallery:
        return gallery[0]["src"]
    return static("img/slide-1.jpg")


@register.simple_tag
def package_list_image(package) -> str:
    """Listing thumbnail — first uploaded photo or placeholder."""
    gallery = package_gallery_images(package)
    if gallery:
        return gallery[0]["src"]
    return static("img/slide-1.jpg")


@register.simple_tag
def testimonial_marquee_rows(testimonials):
    """Split testimonials into two rows for the dual-row marquee."""
    items = list(testimonials)
    if not items:
        return {"row_a": [], "row_b": []}
    if len(items) == 1:
        return {"row_a": items, "row_b": items}
    row_a = items[0::2]
    row_b = items[1::2]
    return {"row_a": row_a, "row_b": row_b}


@register.simple_tag
def package_detail_url(package) -> str:
    from django.urls import reverse

    from packages.models import PackageCategory

    routes = {
        PackageCategory.CategoryType.DOMESTIC: "packages:domestic_detail",
        PackageCategory.CategoryType.INTERNATIONAL: "packages:international_detail",
        PackageCategory.CategoryType.PILGRIM: "packages:pilgrim_detail",
    }
    name = routes.get(package.category.category_type, "packages:domestic_detail")
    return reverse(name, kwargs={"slug": package.slug})
