"""Attach static images to gallery records that have no uploaded file."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from gallery.models import GalleryImage


def _seed_sources() -> list[Path]:
    """Prefer medium-sized legacy photos, then home marketing images."""
    static_img = Path(settings.BASE_DIR) / "static" / "img"
    sources: list[Path] = []

    sources.extend(sorted(static_img.glob("*_medium.jpg")))
    sources.extend(sorted(static_img.glob("slide-*.jpg")))

    home = static_img / "home"
    if home.is_dir():
        sources.extend(sorted(home.glob("*.jpg")))
        sources.extend(sorted(home.glob("*.png")))

    wayanad = static_img / "wayanad"
    if wayanad.is_dir():
        sources.extend(sorted(wayanad.glob("*.jpg")))

    # Deduplicate while preserving order
    seen: set[Path] = set()
    unique: list[Path] = []
    for path in sources:
        if path not in seen and path.is_file():
            seen.add(path)
            unique.append(path)
    return unique


class Command(BaseCommand):
    help = "Populate gallery photos from bundled static images when files are missing."

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Replace images on all active gallery records, not only empty ones.",
        )

    def handle(self, *args, **options):
        sources = _seed_sources()
        if not sources:
            self.stderr.write(self.style.ERROR("No source images found under static/img/."))
            return

        if options["force"]:
            records = list(GalleryImage.objects.filter(is_active=True).order_by("display_order"))
        else:
            records = list(
                GalleryImage.objects.filter(is_active=True, image="").order_by("display_order")
            )

        if not records:
            self.stdout.write("No gallery records need images.")
            return

        updated = 0
        for index, record in enumerate(records):
            src = sources[index % len(sources)]
            with src.open("rb") as handle:
                record.image.save(src.name, File(handle), save=True)
            updated += 1
            self.stdout.write(f"  {record.title} <- {src.relative_to(settings.BASE_DIR)}")

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} gallery photo(s)."))
