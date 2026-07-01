"""Utilities to import legacy HTML into Django templates."""

from __future__ import annotations

import re
from pathlib import Path

# Legacy filename -> Django URL template fragment
URL_MAP: dict[str, str] = {
    "index.html": "{% url 'core:home' %}",
    "index.php": "{% url 'core:home' %}",
    "about.html": "{% url 'website:about' %}",
    "services.html": "{% url 'website:services' %}",
    "gallery.html": "{% url 'gallery:list' %}",
    "contact.html": "{% url 'enquiries:contact' %}",
    "contact.php": "{% url 'enquiries:contact' %}",
    "destinations.html": "{% url 'packages:domestic_list' %}",
    "international_destinations.html": "{% url 'packages:international_list' %}",
    "more-wayanad.html": "{% url 'website:landing' 'wayanad' %}",
    "more-piligrim.html": "{% url 'website:landing' 'pilgrim-packages' %}",
    "more_international.html": "{% url 'website:landing' 'international-packages' %}",
    "more-details.html": "{% url 'packages:domestic_detail' 'athirapilly-waterfalls' %}",
    "more-details-html": "{% url 'packages:domestic_detail' 'athirapilly-waterfalls' %}",
    "international_itinerary.php": "{% url 'packages:international_detail' 'golden-triangle' %}",
    "international_itinerary.php?id=1": "{% url 'packages:international_detail' 'golden-triangle' %}",
    "international_itinerary.php?id=2": "{% url 'packages:international_detail' 'heavenly-abode' %}",
    "international_itinerary.php?id=3": "{% url 'packages:international_detail' 'hills-and-backwaters' %}",
}

LEGACY_FILES: dict[str, str] = {
    "index.html": "core/home_content.html",
    "about.html": "website/about_content.html",
    "services.html": "website/services_content.html",
    "gallery.html": "gallery/gallery_content.html",
    "contact.html": "website/contact_content.html",
    "destinations.html": "packages/domestic_list_content.html",
    "international_destinations.html": "packages/international_list_content.html",
    "more-details.html": "packages/domestic_detail_content.html",
    "international_itinerary.php": "packages/international_detail_content.html",
    "more-wayanad.html": "website/landing_wayanad_content.html",
    "more-piligrim.html": "website/landing_pilgrim_content.html",
    "more_international.html": "website/landing_international_content.html",
}

STATIC_ATTRS = (
    "src",
    "href",
    "data-src",
    "data-small",
    "data-medium",
    "data-large",
    "data-retina",
    "data-lazyload",
)


def strip_php(html: str) -> str:
    """Remove PHP blocks from legacy files."""
    html = re.sub(r"<\?php.*?\?>", "", html, flags=re.DOTALL)
    return html


def extract_main_content(html: str) -> str:
    """Extract HTML between header and footer."""
    html = strip_php(html)
    match = re.search(r"</header>\s*(.*?)\s*<footer", html, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    match = re.search(r"<!-- End Header -->\s*(.*?)\s*<footer", html, flags=re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return ""


def staticify(content: str) -> str:
    """Convert asset paths (img/css/js/fonts) to Django static tags."""

    def repl_static(match: re.Match) -> str:
        attr = match.group(1)
        quote = match.group(2)
        path = match.group(3)
        if path.startswith(("http://", "https://", "{%", "javascript:", "tel:", "mailto:")):
            return match.group(0)
        asset_prefixes = ("img/", "css/", "js/", "fonts/", "../src/css/images/")
        if not any(path.startswith(p) for p in asset_prefixes):
            return match.group(0)
        if path.startswith("../src/css/images/"):
            path = "css/images/" + path.split("/")[-1]
        return f"{attr}={quote}{{% static '{path}' %}}{quote}"

    pattern = rf'({"|".join(STATIC_ATTRS)})=(["\'])([^"\']+)\2'
    return re.sub(pattern, repl_static, content)


def linkify(content: str) -> str:
    """Replace legacy .html/.php links with Django URLs."""
    content = content.replace('href="#"', 'href="{% url \'core:home\' %}"')
    content = content.replace("href='#'", "href=\"{% url 'core:home' %}\"")
    for legacy, django_url in sorted(URL_MAP.items(), key=lambda x: -len(x[0])):
        content = content.replace(f'href="{legacy}"', f'href="{django_url}"')
        content = content.replace(f"href='{legacy}'", f"href='{django_url}'")
    return content


def convert_legacy_html(html: str) -> str:
    """Full pipeline: extract, linkify, staticify."""
    content = extract_main_content(html)
    content = linkify(content)
    content = staticify(content)
    return content


def write_legacy_template(templates_dir: Path, relative_path: str, body: str) -> Path:
    """Write a legacy content partial with load static at top."""
    dest = templates_dir / relative_path
    dest.parent.mkdir(parents=True, exist_ok=True)
    header = "{% load static %}\n"
    dest.write_text(header + body + "\n", encoding="utf-8")
    return dest


def process_legacy_directory(legacy_dir: Path, templates_dir: Path) -> list[str]:
    """Process all mapped legacy files. Returns list of written template paths."""
    written: list[str] = []
    for legacy_name, template_rel in LEGACY_FILES.items():
        source = legacy_dir / legacy_name
        if not source.exists():
            continue
        html = source.read_text(encoding="utf-8", errors="ignore")
        body = convert_legacy_html(html)
        dest = write_legacy_template(templates_dir, template_rel, body)
        written.append(str(dest.relative_to(templates_dir)))
    return written
