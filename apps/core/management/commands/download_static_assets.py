"""Download static assets from live site or Wayback Machine."""

from __future__ import annotations

import re
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

LIVE_BASE = "https://bluelagoonholidays.net"
WAYBACK = "https://web.archive.org/web/2020id_/https://bluelagoonholidays.net"

CSS_FILES = [
    "font-awesome.css",
    "bootstrap.min.css",
    "animate.min.css",
    "style.css",
    "menu.css",
    "responsive.css",
    "magnific-popup.css",
    "settings.css",
    "extralayers.css",
    "slider-pro.min.css",
]

JS_FILES = [
    "jquery-1.js",
    "common_scripts_min.js",
    "functions.js",
    "validate.js",
    "jquery_002.js",
    "jquery.js",
    "revolution_func.js",
    "mapmarker.jquery.js",
    "mapmarker_func.jquery.js",
    "jquery.sliderPro.min.js",
    "mosaic.1.0.1.js",
]

JS_CDN = {
    "jquery.sliderPro.min.js": "https://cdn.jsdelivr.net/npm/slider-pro@1.6.0/dist/js/jquery.sliderPro.min.js",
    "html5shiv.min.js": "https://cdnjs.cloudflare.com/ajax/libs/html5shiv/3.7.3/html5shiv.min.js",
    "respond.min.js": "https://cdnjs.cloudflare.com/ajax/libs/respond.js/1.4.2/respond.min.js",
}

FONT_CDN = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.5.0/fonts"


class Command(BaseCommand):
    help = "Download CSS, JS, images, and fonts into static/ from the live legacy site"

    def handle(self, *args, **options):
        static = Path(settings.STATICFILES_DIRS[0])
        (static / "css").mkdir(parents=True, exist_ok=True)
        (static / "js").mkdir(parents=True, exist_ok=True)
        (static / "img").mkdir(parents=True, exist_ok=True)
        (static / "fonts").mkdir(parents=True, exist_ok=True)

        for name in CSS_FILES:
            self._fetch(f"{LIVE_BASE}/css/{name}", static / "css" / name)

        for name in JS_FILES:
            dest = static / "js" / name
            if not self._fetch(f"{LIVE_BASE}/js/{name}", dest):
                self._fetch(f"{WAYBACK}/js/{name}", dest)

        for name, url in JS_CDN.items():
            if not (static / "js" / name).exists():
                self._fetch(url, static / "js" / name)

        for font in ("fontawesome-webfont.woff2", "fontawesome-webfont.woff", "fontawesome-webfont.ttf"):
            self._fetch(f"{FONT_CDN}/{font}", static / "fonts" / font)

        self._fetch(f"{LIVE_BASE}/css/images/blank.gif", static / "css" / "images" / "blank.gif")

        self.stdout.write(self.style.SUCCESS("Asset download complete. Restart runserver and hard-refresh."))

    def _fetch(self, url: str, dest: Path) -> bool:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and len(resp.content) > 100:
                dest.write_bytes(resp.content)
                self.stdout.write(f"  OK {dest.name}")
                return True
        except requests.RequestException as exc:
            self.stdout.write(self.style.WARNING(f"  FAIL {dest.name}: {exc}"))
        return False
