"""Gallery views."""

from __future__ import annotations

from django.core.paginator import Paginator
from django.shortcuts import render

from gallery.models import GalleryImage


def gallery_list(request):
    images = (
        GalleryImage.objects.filter(is_active=True)
        .exclude(image="")
        .order_by("display_order", "-created_at")
    )
    paginator = Paginator(images, 20)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "gallery/gallery.html",
        {
            "page_obj": page_obj,
            "images": page_obj,
            "page_title": "Gallery",
        },
    )
