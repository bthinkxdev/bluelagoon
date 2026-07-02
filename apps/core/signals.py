"""Cache invalidation for page hero lookups."""

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from core.models import PageHero
from core.page_heroes import clear_page_hero_cache


@receiver(post_save, sender=PageHero)
@receiver(post_delete, sender=PageHero)
def invalidate_page_hero_cache(**kwargs) -> None:
    clear_page_hero_cache()
