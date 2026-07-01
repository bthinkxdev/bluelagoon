"""Report url(...) references in CSS that point to missing files."""

from __future__ import annotations

import re
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "List missing files referenced from CSS under static/."

    def handle(self, *args, **options):
        static = Path(settings.BASE_DIR) / "static"
        css_dir = static / "css"
        url_re = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""")

        missing: dict[str, set[str]] = {}
        total = 0

        for css in sorted(css_dir.rglob("*.css")):
            text = css.read_text(encoding="utf-8", errors="ignore")
            for match in url_re.finditer(text):
                ref = match.group(1).split("?")[0].split("#")[0]
                if ref.startswith(("data:", "http://", "https://", "//")):
                    continue
                target = (css.parent / ref).resolve()
                if not target.is_file():
                    key = str(css.relative_to(static)).replace("\\", "/")
                    missing.setdefault(key, set()).add(ref)
                    total += 1

        if not missing:
            self.stdout.write(self.style.SUCCESS("No missing CSS url() references found."))
            return

        for css, refs in sorted(missing.items()):
            self.stdout.write(f"=== {css} ===")
            for ref in sorted(refs):
                self.stdout.write(f"  {ref}")
        self.stdout.write(self.style.WARNING(f"Total missing references: {total}"))
