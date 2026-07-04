"""Replace PackageCategory with Package.travel_type and drop the categories table."""

from __future__ import annotations

from django.db import migrations, models


TRAVEL_TYPES = {"domestic", "international", "pilgrim"}


def copy_category_to_travel_type(apps, schema_editor):
    Package = apps.get_model("packages", "Package")
    for package in Package.objects.select_related("category", "destination").iterator():
        category_type = getattr(getattr(package, "category", None), "category_type", "") or ""
        travel_type = category_type if category_type in TRAVEL_TYPES else "domestic"
        destination = getattr(package, "destination", None)
        if destination and destination.travel_type in TRAVEL_TYPES:
            travel_type = destination.travel_type
        package.travel_type = travel_type
        package.save(update_fields=["travel_type"])


class Migration(migrations.Migration):
    dependencies = [
        ("packages", "0009_merge_destination_hero_mobile"),
    ]

    operations = [
        migrations.AddField(
            model_name="package",
            name="travel_type",
            field=models.CharField(
                choices=[
                    ("domestic", "Domestic"),
                    ("international", "International"),
                    ("pilgrim", "Pilgrimage"),
                ],
                db_index=True,
                default="domestic",
                help_text="Domestic, International, or Pilgrimage — used for URLs, tabs, and badges.",
                max_length=20,
            ),
        ),
        migrations.RunPython(copy_category_to_travel_type, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="package",
            name="category",
        ),
        migrations.DeleteModel(
            name="PackageCategory",
        ),
    ]
