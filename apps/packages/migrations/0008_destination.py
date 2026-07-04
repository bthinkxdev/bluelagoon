"""Add Destination model, link packages, and seed from existing package data."""

from __future__ import annotations

import re

from django.db import migrations, models
import django.db.models.deletion
from django.utils.text import slugify


TRAVEL_TYPES = {"domestic", "international", "pilgrim"}

_SUFFIX_RE = re.compile(
    r"\b(packages?|tours?|trip|escape|getaway|holiday|holidays|cruise|cruises)\b",
    re.I,
)


def _destination_name(title: str, route: str) -> str:
    title = (title or "").strip()
    route = (route or "").strip()
    if route:
        parts = [part.strip(" /") for part in re.split(r"[/•|,]+", route) if part.strip(" /")]
        # Prefer a middle stop when the route is A / B / A style.
        if len(parts) >= 3 and parts[0].lower() == parts[-1].lower():
            return parts[1].title()
        if parts:
            # Skip common departure hubs when a later stop exists.
            hubs = {"cochin", "kochi", "delhi", "mumbai", "bangalore", "bengaluru"}
            for part in parts:
                if part.lower() not in hubs:
                    return part.title()
            return parts[0].title()
    cleaned = _SUFFIX_RE.sub("", title).strip(" -–—")
    return cleaned or title or "Destination"


def _unique_slug(Destination, base: str) -> str:
    slug = slugify(base)[:200] or "destination"
    candidate = slug
    counter = 1
    while Destination.objects.filter(slug=candidate).exists():
        candidate = f"{slug}-{counter}"
        counter += 1
    return candidate


def populate_destinations(apps, schema_editor):
    Package = apps.get_model("packages", "Package")
    Destination = apps.get_model("packages", "Destination")

    cache: dict[tuple[str, str], object] = {}

    for package in Package.objects.select_related("category").iterator():
        category_type = getattr(package.category, "category_type", "") or ""
        travel_type = category_type if category_type in TRAVEL_TYPES else "domestic"
        name = _destination_name(package.title, package.route)
        key = (name.casefold(), travel_type)

        destination = cache.get(key)
        if destination is None:
            destination = Destination.objects.filter(
                name__iexact=name,
                travel_type=travel_type,
            ).first()
            if destination is None:
                destination = Destination.objects.create(
                    name=name,
                    slug=_unique_slug(Destination, name),
                    travel_type=travel_type,
                    country="India" if travel_type in {"domestic", "pilgrim"} else "",
                    is_active=True,
                    display_order=0,
                )
            cache[key] = destination

        package.destination_id = destination.pk
        package.save(update_fields=["destination"])


class Migration(migrations.Migration):
    dependencies = [
        ("packages", "0007_page_hero_mobile"),
    ]

    operations = [
        migrations.CreateModel(
            name="Destination",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("name", models.CharField(db_index=True, max_length=160)),
                (
                    "travel_type",
                    models.CharField(
                        choices=[
                            ("domestic", "Domestic"),
                            ("international", "International"),
                            ("pilgrim", "Pilgrimage"),
                        ],
                        db_index=True,
                        max_length=20,
                    ),
                ),
                ("country", models.CharField(blank=True, default="", max_length=120)),
                ("state", models.CharField(blank=True, default="", max_length=120)),
                ("description", models.TextField(blank=True, default="")),
                ("image", models.ImageField(blank=True, null=True, upload_to="destinations/")),
                ("is_active", models.BooleanField(db_index=True, default=True)),
                ("display_order", models.PositiveIntegerField(default=0)),
            ],
            options={
                "verbose_name": "Destination",
                "verbose_name_plural": "Destinations",
                "ordering": ["display_order", "name"],
            },
        ),
        migrations.AddIndex(
            model_name="destination",
            index=models.Index(
                fields=["travel_type", "is_active", "name"],
                name="packages_de_travel__7f0c8a_idx",
            ),
        ),
        migrations.AddField(
            model_name="package",
            name="destination",
            field=models.ForeignKey(
                blank=True,
                help_text="Primary destination used for search and filtering.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="packages",
                to="packages.destination",
            ),
        ),
        migrations.RunPython(populate_destinations, migrations.RunPython.noop),
    ]
