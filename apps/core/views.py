"""Core views: home page and error handlers."""

from __future__ import annotations

from django.shortcuts import render

from core.models import Banner
from packages.models import Testimonial


def home(request):
    """Homepage with dynamic hero banners."""
    banners = Banner.objects.active()
    testimonials = (
        Testimonial.objects.filter(is_active=True)
        .select_related("package", "package__destination")
        .order_by("display_order", "-created_at")
    )
    context = {
        "page_title": "Home",
        "banners": banners,
        "testimonials": testimonials,
    }
    first_banner = banners.first()
    if first_banner and first_banner.meta_title:
        context["page_title"] = first_banner.meta_title
    if first_banner:
        context["page_description"] = first_banner.meta_description
    return render(request, "core/home.html", context)


def handler404(request, exception):
    return render(request, "errors/404.html", status=404)


def handler403(request, exception):
    return render(request, "errors/403.html", status=403)


def handler500(request):
    return render(request, "errors/500.html", status=500)
