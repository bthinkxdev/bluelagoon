"""Template tags for DB-managed page hero banners."""

from django import template

from core.page_heroes import HeroImageUrls, get_page_hero_url, get_page_hero_urls

register = template.Library()


@register.simple_tag
def page_hero_url(page_key: str) -> str:
    """Return desktop hero background URL for a PageHero.page_key value."""
    return get_page_hero_url(page_key)


@register.simple_tag
def page_hero_urls(page_key: str) -> HeroImageUrls:
    """Return desktop + mobile hero URLs for a PageHero.page_key value."""
    return get_page_hero_urls(page_key)
