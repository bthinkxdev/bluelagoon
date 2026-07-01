"""Sync full page content from legacy HTML/PHP files into Django templates."""

from __future__ import annotations

from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from core.legacy_html import LEGACY_FILES, process_legacy_directory


class Command(BaseCommand):
    help = "Import full HTML body content from legacy files into Django template partials"

    def add_arguments(self, parser):
        parser.add_argument(
            "--legacy-dir",
            type=str,
            default=None,
            help="Path to folder containing legacy HTML/PHP files (default: parent of bluelagoon/)",
        )

    def handle(self, *args, **options):
        base = Path(settings.BASE_DIR)
        legacy_dir = Path(options["legacy_dir"]) if options["legacy_dir"] else base.parent
        templates_dir = base / "templates"

        if not legacy_dir.exists():
            self.stderr.write(self.style.ERROR(f"Legacy directory not found: {legacy_dir}"))
            return

        self.stdout.write(f"Reading legacy files from: {legacy_dir}")
        written = process_legacy_directory(legacy_dir, templates_dir)

        for path in written:
            self.stdout.write(f"  Wrote templates/{path}")

        missing = [name for name in LEGACY_FILES if not (legacy_dir / name).exists()]
        if missing:
            self.stdout.write(self.style.WARNING(f"Missing legacy files: {', '.join(missing)}"))

        self.stdout.write(self.style.SUCCESS(f"Synced {len(written)} legacy page templates."))
