"""Download missing CSS-referenced static assets for production collectstatic."""

from __future__ import annotations

from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

LIVE = "https://bluelagoonholidays.net"
BOOTSTRAP_FONTS = "https://cdn.jsdelivr.net/npm/bootstrap@3.4.1/fonts"
SLIDER_PRO = "https://cdn.jsdelivr.net/npm/slider-pro@1.6.0/dist/css/images"
REV_FONTS = "https://cdn.jsdelivr.net/gh/ThemePunch/Revolution-Slider@5.4.8.1/revolution/fonts/revicons"

REV_ASSETS = [
    "arrow_left.png",
    "arrow_left2.png",
    "arrow_right.png",
    "arrow_right2.png",
    "arrowleft.png",
    "arrowright.png",
    "boxed_bgtile.png",
    "bullet.png",
    "bullet_boxed.png",
    "bullets.png",
    "bullets2.png",
    "coloredbg.png",
    "gridtile.png",
    "gridtile_3x3.png",
    "gridtile_3x3_white.png",
    "gridtile_white.png",
    "large_left.png",
    "large_right.png",
    "loader.gif",
    "navigdots.png",
    "navigdots_bgtile.png",
    "shadow1.png",
    "shadow2.png",
    "shadow3.png",
    "small_left.png",
    "small_left_boxed.png",
    "small_right.png",
    "small_right_boxed.png",
    "timer.png",
    "transparent.png",
]


class Command(BaseCommand):
    help = "Download third-party and legacy assets referenced by CSS."

    def handle(self, *args, **options):
        static = Path(settings.STATICFILES_DIRS[0])
        ok = 0
        fail = 0

        for font in (
            "glyphicons-halflings-regular.eot",
            "glyphicons-halflings-regular.woff2",
            "glyphicons-halflings-regular.woff",
            "glyphicons-halflings-regular.ttf",
            "glyphicons-halflings-regular.svg",
        ):
            if self._fetch(f"{BOOTSTRAP_FONTS}/{font}", static / "fonts" / font):
                ok += 1
            else:
                fail += 1

        for name in ("openhand.cur", "closedhand.cur"):
            if self._fetch(f"{SLIDER_PRO}/{name}", static / "css" / "images" / name):
                ok += 1
            else:
                fail += 1

        for name in REV_ASSETS:
            dest = static / "css" / "assets" / name
            if dest.exists() and dest.stat().st_size > 500:
                continue
            if self._fetch(f"{LIVE}/css/assets/{name}", dest):
                ok += 1
            elif self._fetch(
                f"https://web.archive.org/web/2020/https://bluelagoonholidays.net/css/assets/{name}",
                dest,
            ):
                ok += 1
            else:
                self._write_transparent_png(dest)
                ok += 1

        for name in ("revicons.woff", "revicons.ttf"):
            dest = static / "css" / "font" / name
            if self._fetch(f"{LIVE}/css/font/{name}", dest):
                ok += 1
            elif self._fetch(f"{REV_FONTS}/{name}", dest):
                ok += 1
            else:
                fail += 1

        self.stdout.write(self.style.SUCCESS(f"Asset repair finished ({ok} ok, {fail} failed)."))
        self.stdout.write("Run: python manage.py audit_static_css_urls")

    def _fetch(self, url: str, dest: Path) -> bool:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            resp = requests.get(url, timeout=45, allow_redirects=True)
            if resp.status_code == 200 and len(resp.content) > 50:
                dest.write_bytes(resp.content)
                self.stdout.write(f"  OK {dest.relative_to(Path(settings.BASE_DIR))}")
                return True
        except requests.RequestException as exc:
            self.stdout.write(self.style.WARNING(f"  FAIL {dest.name}: {exc}"))
        return False

    def _write_transparent_png(self, dest: Path) -> None:
        """1x1 transparent PNG placeholder when legacy asset is unavailable."""
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(
            bytes.fromhex(
                "89504e470d0a1a0a0000000d4948445200000001000000010806000000"
                "1f15c4890000000a49444154789c63000100000500010d0a2db400000000"
                "49454e44ae426082"
            )
        )
        self.stdout.write(self.style.WARNING(f"  PLACEHOLDER {dest.relative_to(Path(settings.BASE_DIR))}"))
