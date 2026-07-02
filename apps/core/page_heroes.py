"""Resolve inner-page hero banner URLs from the database."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from django.templatetags.static import static

from core.models import (
    PAGE_HERO_HEIGHT,
    PAGE_HERO_MOBILE_BREAKPOINT,
    PAGE_HERO_MOBILE_HEIGHT,
    PAGE_HERO_MOBILE_WIDTH,
    PAGE_HERO_WIDTH,
    PageHero,
)

# Live site paths — each page_key maps to exactly one URL (list vs landing are separate).
PAGE_LIVE_PATHS: dict[str, str] = {
    PageHero.PageKey.SERVICES: "/services/",
    PageHero.PageKey.GALLERY: "/gallery/",
    PageHero.PageKey.PACKAGES_ALL: "/packages/",
    PageHero.PageKey.PACKAGES_DOMESTIC: "/packages/?category=domestic",
    PageHero.PageKey.PACKAGES_INTERNATIONAL: "/packages/?category=international",
    PageHero.PageKey.PACKAGES_PILGRIM: "/packages/?category=pilgrim",
    PageHero.PageKey.ABOUT: "/about/",
    PageHero.PageKey.CONTACT: "/contact/",
    PageHero.PageKey.LANDING_WAYANAD: "/pages/wayanad/",
    PageHero.PageKey.LANDING_INTERNATIONAL: "/pages/international-packages/",
    PageHero.PageKey.LANDING_PILGRIM: "/pages/pilgrim-packages/",
}

STATIC_FALLBACKS: dict[str, str] = {
    PageHero.PageKey.SERVICES: "img/slide-1.jpg",
    PageHero.PageKey.GALLERY: "img/slide-1.jpg",
    PageHero.PageKey.PACKAGES_ALL: "img/slide_hero.jpg",
    PageHero.PageKey.PACKAGES_DOMESTIC: "img/about-wayanad.jpg",
    PageHero.PageKey.PACKAGES_INTERNATIONAL: "img/int_03.jpg",
    PageHero.PageKey.PACKAGES_PILGRIM: "img/header_bg.jpg",
    PageHero.PageKey.ABOUT: "img/slide_hero.jpg",
    PageHero.PageKey.CONTACT: "img/int_03.jpg",
    PageHero.PageKey.LANDING_WAYANAD: "img/about-wayanad.jpg",
    PageHero.PageKey.LANDING_INTERNATIONAL: "img/int_03.jpg",
    PageHero.PageKey.LANDING_PILGRIM: "img/header_bg.jpg",
}

DEFAULT_FALLBACK = "img/slide-1.jpg"

HERO_DESKTOP_UPLOAD_HELP = (
    f"Desktop — upload exactly {PAGE_HERO_WIDTH}×{PAGE_HERO_HEIGHT} px. "
    "Package list pages and destination landing pages are separate rows."
)

HERO_MOBILE_UPLOAD_HELP = (
    f"Mobile — upload exactly {PAGE_HERO_MOBILE_WIDTH}×{PAGE_HERO_MOBILE_HEIGHT} px. "
    f"Shown on screens up to {PAGE_HERO_MOBILE_BREAKPOINT}px wide. "
    "Falls back to the desktop image if empty."
)

# Backwards compatibility for admin import.
HERO_UPLOAD_HELP = HERO_DESKTOP_UPLOAD_HELP


@dataclass(frozen=True)
class HeroImageUrls:
    desktop: str
    mobile: str


def page_hero_live_path(page_key: str) -> str:
    return PAGE_LIVE_PATHS.get(page_key, "")


def clear_page_hero_cache() -> None:
    get_page_hero_urls.cache_clear()


def _static_fallback(page_key: str) -> str:
    return static(STATIC_FALLBACKS.get(page_key, DEFAULT_FALLBACK))


@lru_cache(maxsize=64)
def get_page_hero_urls(page_key: str) -> HeroImageUrls:
    """Desktop + mobile hero URLs for a PageHero.page_key value."""
    valid_keys = {choice.value for choice in PageHero.PageKey}
    if page_key not in valid_keys:
        fallback = static(DEFAULT_FALLBACK)
        return HeroImageUrls(desktop=fallback, mobile=fallback)

    hero = (
        PageHero.objects.filter(page_key=page_key, is_active=True)
        .only("image", "mobile_image")
        .first()
    )
    if not hero:
        fallback = _static_fallback(page_key)
        return HeroImageUrls(desktop=fallback, mobile=fallback)

    desktop = hero.image.url if hero.image else _static_fallback(page_key)
    mobile = hero.mobile_image.url if hero.mobile_image else desktop
    return HeroImageUrls(desktop=desktop, mobile=mobile)


def get_page_hero_url(page_key: str) -> str:
    """Desktop hero URL (backwards compatible)."""
    return get_page_hero_urls(page_key).desktop
