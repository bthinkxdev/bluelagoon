# Generated manually

from django.core.files.base import ContentFile
from django.db import migrations


def import_static_page_hero_images(apps, schema_editor):
    """Copy legacy StaticPage.hero_image uploads into matching PageHero rows."""
    StaticPage = apps.get_model("website", "StaticPage")
    PageHero = apps.get_model("core", "PageHero")

    imports = [
        ({"page_type": "about"}, "about"),
        ({"page_type": "services"}, "services"),
        ({"slug": "wayanad"}, "landing_wayanad"),
        ({"slug": "pilgrim-packages"}, "landing_pilgrim"),
        ({"slug": "international-packages"}, "landing_international"),
    ]

    for lookup, page_key in imports:
        static_page = StaticPage.objects.filter(**lookup).first()
        hero = PageHero.objects.filter(page_key=page_key).first()
        if not static_page or not hero or not static_page.hero_image:
            continue
        if hero.image:
            continue
        try:
            static_page.hero_image.open("rb")
            content = static_page.hero_image.read()
            static_page.hero_image.close()
        except (FileNotFoundError, OSError):
            continue
        filename = static_page.hero_image.name.rsplit("/", 1)[-1]
        hero.image.save(filename, ContentFile(content), save=True)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_page_hero"),
        ("website", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(import_static_page_hero_images, migrations.RunPython.noop),
    ]
