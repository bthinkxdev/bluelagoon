"""Package listing and detail views."""

from __future__ import annotations

from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.cache import cache_page

from packages.models import Package, PackageCategory, PackageExclusion, PackageImage, PackageInclusion, Testimonial
from packages.search import PackageSearch, category_label as get_category_label


PACKAGE_LIST_CATEGORIES = (
    PackageCategory.CategoryType.DOMESTIC,
    PackageCategory.CategoryType.INTERNATIONAL,
    PackageCategory.CategoryType.PILGRIM,
)


def resolve_list_category(request) -> str:
    """Category filter from ?category= or legacy ?tab=."""
    for key in ("category", "tab"):
        value = (request.GET.get(key) or "").strip()
        if value in PACKAGE_LIST_CATEGORIES:
            return value
    return ""


def _published_packages(category_type: str | None = None):
    qs = (
        Package.objects.filter(
            status=Package.Status.PUBLISHED,
            category__category_type__in=PACKAGE_LIST_CATEGORIES,
        )
        .select_related("category")
        .prefetch_related(
            Prefetch("images", queryset=PackageImage.objects.order_by("display_order"))
        )
        .order_by("display_order", "title")
    )
    if category_type:
        qs = qs.filter(category__category_type=category_type)
    return qs


def _package_detail_queryset():
    return Package.objects.select_related("category").prefetch_related(
        Prefetch("images", queryset=PackageImage.objects.order_by("display_order")),
        Prefetch("inclusions", queryset=PackageInclusion.objects.order_by("display_order")),
        Prefetch("exclusions", queryset=PackageExclusion.objects.order_by("display_order")),
        Prefetch(
            "testimonials",
            queryset=Testimonial.objects.filter(is_active=True).order_by("display_order"),
        ),
    )


def _category_tab_urls(search: PackageSearch) -> dict[str, str]:
    """URLs for All / Domestic / International / Pilgrim tabs (preserves search filters)."""
    params = search.query_dict()
    params.pop("category", None)
    params.pop("tab", None)
    list_url = reverse("packages:list")
    urls = {"all": f"{list_url}?{urlencode(params)}" if params else list_url}
    for cat in PACKAGE_LIST_CATEGORIES:
        cat_params = {**params, "category": cat}
        urls[cat] = f"{list_url}?{urlencode(cat_params)}"
    return urls


def _package_list_context(request, category_filter: str = "") -> dict:
    search = PackageSearch.from_request(request, category_filter or "all")
    packages = search.apply(_published_packages(category_filter or None))

    if category_filter:
        titles = {
            PackageCategory.CategoryType.DOMESTIC: "Domestic Tour Packages",
            PackageCategory.CategoryType.INTERNATIONAL: "International Tour Packages",
            PackageCategory.CategoryType.PILGRIM: "Pilgrim Tour Packages",
        }
        breadcrumbs = {
            PackageCategory.CategoryType.DOMESTIC: "Domestic Packages",
            PackageCategory.CategoryType.INTERNATIONAL: "International Packages",
            PackageCategory.CategoryType.PILGRIM: "Pilgrim Packages",
        }
        page_title = titles.get(category_filter, "Tour Packages")
        breadcrumb = [("Packages", reverse("packages:list")), (breadcrumbs[category_filter], None)]
        category_label_text = get_category_label(category_filter)
    else:
        page_title = "Tour Packages"
        breadcrumb = [("Packages", None)]
        category_label_text = "Tour"

    return {
        "packages": packages,
        "page_title": page_title,
        "breadcrumb": breadcrumb,
        "list_url_name": "packages:list",
        "category_type": category_filter,
        "category_label": category_label_text,
        "show_category_labels": not category_filter,
        "category_tab_urls": _category_tab_urls(search),
        **search.to_context(),
    }


def _render_package_list(request, category_filter: str = ""):
    return render(
        request,
        "packages/package_list.html",
        _package_list_context(request, category_filter),
    )


@cache_page(60 * 5)
def package_list(request):
    return _render_package_list(request, resolve_list_category(request))


def package_list_partial(request):
    """AJAX fragment for category filtering without full page reload."""
    category_filter = resolve_list_category(request)
    return render(
        request,
        "packages/includes/package_list_results.html",
        _package_list_context(request, category_filter),
    )


@cache_page(60 * 5)
def domestic_list(request):
    return _render_package_list(request, PackageCategory.CategoryType.DOMESTIC)


@cache_page(60 * 5)
def international_list(request):
    return _render_package_list(request, PackageCategory.CategoryType.INTERNATIONAL)


@cache_page(60 * 5)
def pilgrim_list(request):
    return _render_package_list(request, PackageCategory.CategoryType.PILGRIM)


def package_detail(request, slug, category_type: str):
    package = get_object_or_404(
        _package_detail_queryset(),
        slug=slug,
        category__category_type=category_type,
        status=Package.Status.PUBLISHED,
    )
    list_names = {
        PackageCategory.CategoryType.DOMESTIC: ("Domestic Packages", "packages:list"),
        PackageCategory.CategoryType.INTERNATIONAL: ("International Packages", "packages:list"),
        PackageCategory.CategoryType.PILGRIM: ("Pilgrim Packages", "packages:list"),
    }
    list_label, list_url = list_names.get(category_type, ("Packages", "packages:list"))
    list_href = reverse(list_url)
    if category_type in PACKAGE_LIST_CATEGORIES:
        list_href = f"{list_href}?category={category_type}"

    subtitle = package.duration or ""
    if package.route:
        subtitle = f"{subtitle} — {package.route}" if subtitle else package.route

    return render(
        request,
        "packages/package_detail.html",
        {
            "package": package,
            "page_title": package.title,
            "hero_subtitle": subtitle,
            "breadcrumb_crumbs": [
                (list_label, list_href),
                (package.title, None),
            ],
            "search": PackageSearch.from_request(request, category_type),
        },
    )


def domestic_detail(request, slug):
    return package_detail(request, slug, PackageCategory.CategoryType.DOMESTIC)


def international_detail(request, slug):
    return package_detail(request, slug, PackageCategory.CategoryType.INTERNATIONAL)


def pilgrim_detail(request, slug):
    return package_detail(request, slug, PackageCategory.CategoryType.PILGRIM)
