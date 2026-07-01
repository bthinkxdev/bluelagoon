"""Website static page views."""

from __future__ import annotations

from django.shortcuts import render
from django.views.decorators.cache import cache_page

from website.models import Service, StaticPage


@cache_page(60 * 5)
def about(request):
    page = StaticPage.objects.filter(page_type=StaticPage.PageType.ABOUT, is_published=True).first()
    return render(request, "website/about.html", {"page": page, "page_title": "About"})


@cache_page(60 * 5)
def services(request):
    page = StaticPage.objects.filter(
        page_type=StaticPage.PageType.SERVICES, is_published=True
    ).first()
    service_list = Service.objects.filter(is_active=True)
    return render(
        request,
        "website/services.html",
        {"page": page, "services": service_list, "page_title": "Services"},
    )


LANDING_TEMPLATES = {
    "wayanad": "website/landing_wayanad.html",
    "pilgrim-packages": "website/landing_pilgrim.html",
    "international-packages": "website/landing_international.html",
}


LANDING_BREADCRUMBS = {
    "wayanad": [("Destinations", None), ("Wayanad", None)],
    "pilgrim-packages": [("Destinations", None), ("Pilgrimage Tours", None)],
    "international-packages": [("Destinations", None), ("International Packages", None)],
}


@cache_page(60 * 5)
def landing_page(request, slug):
    template = LANDING_TEMPLATES.get(slug, "website/landing.html")
    page = StaticPage.objects.filter(slug=slug, is_published=True).first()
    crumbs = LANDING_BREADCRUMBS.get(slug)
    if not crumbs and page:
        crumbs = [(page.title, None)]
    return render(
        request,
        template,
        {
            "page": page,
            "page_title": page.title if page else slug.replace("-", " ").title(),
            "breadcrumb_crumbs": crumbs,
        },
    )
