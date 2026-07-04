"""Package listing and detail views."""

from __future__ import annotations

from django.contrib import messages
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import urlencode
from django_ratelimit.decorators import ratelimit

from enquiries.forms import ContactForm
from enquiries.package_enquiry import build_package_enquiry_initial, build_search_enquiry_initial
from enquiries.services import save_contact_from_request
from django.http import JsonResponse
from django.views.decorators.http import require_GET

from packages.models import (
    Destination,
    Package,
    PackageCategory,
    PackageExclusion,
    PackageImage,
    PackageInclusion,
    Testimonial,
)
from packages.search import PackageSearch, TRAVEL_TYPES, category_label as get_category_label


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
        .select_related("category", "destination")
        .prefetch_related(
            Prefetch("images", queryset=PackageImage.objects.order_by("display_order"))
        )
        .order_by("display_order", "title")
    )
    if category_type:
        qs = qs.filter(category__category_type=category_type)
    return qs


@require_GET
def destination_autocomplete(request):
    """JSON suggestions for destination search autocomplete."""
    travel_type = (request.GET.get("travel_type") or "").strip()
    search = (request.GET.get("search") or "").strip()

    qs = Destination.objects.filter(is_active=True)
    if travel_type in TRAVEL_TYPES:
        qs = qs.filter(travel_type=travel_type)
    if search:
        qs = qs.filter(name__icontains=search)

    results = list(
        qs.order_by("display_order", "name").values("id", "name")[:12]
    )
    return JsonResponse(results, safe=False)


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


def _package_list_context(
    request,
    category_filter: str = "",
    *,
    enquiry_form: ContactForm | None = None,
) -> dict:
    search = PackageSearch.from_request(request, category_filter or "all")
    packages = search.apply(_published_packages(category_filter or None))
    show_search_enquiry = search.has_filters and not packages

    if enquiry_form is None and show_search_enquiry:
        enquiry_form = ContactForm(initial=build_search_enquiry_initial(search))

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
        "enquiry_form": enquiry_form,
        "show_search_enquiry": show_search_enquiry,
        **search.to_context(),
    }


def _enquiry_feedback_messages(request, result) -> None:
    if result.notification_sent and result.confirmation_sent:
        messages.success(
            request,
            "Thank you! Your enquiry was sent and a confirmation email is on its way.",
        )
    elif result.notification_sent:
        messages.success(
            request,
            "Thank you! We received your enquiry and will contact you soon.",
        )
    else:
        messages.warning(
            request,
            "Your enquiry was saved. Email delivery failed — our team will follow up shortly.",
        )


def _list_redirect_url(request, search: PackageSearch) -> str:
    params = search.query_dict()
    url = request.path
    if params:
        url = f"{url}?{urlencode(params)}"
    return f"{url}#wl-search-enquiry"


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
def _render_package_list(request, category_filter: str = ""):
    search = PackageSearch.from_request(request, category_filter or "all")
    enquiry_form = None

    if request.method == "POST" and request.POST.get("enquiry_source") == "package_search":
        enquiry_form = ContactForm(request.POST)
        if enquiry_form.is_valid():
            result = save_contact_from_request(enquiry_form, request)
            _enquiry_feedback_messages(request, result)
            return redirect(_list_redirect_url(request, search))
        messages.error(request, "Please correct the errors below.")

    return render(
        request,
        "packages/package_list.html",
        _package_list_context(request, category_filter, enquiry_form=enquiry_form),
    )


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


def domestic_list(request):
    return _render_package_list(request, PackageCategory.CategoryType.DOMESTIC)


def international_list(request):
    return _render_package_list(request, PackageCategory.CategoryType.INTERNATIONAL)


def pilgrim_list(request):
    return _render_package_list(request, PackageCategory.CategoryType.PILGRIM)


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
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

    enquiry_form = None
    if request.method == "POST":
        enquiry_form = ContactForm(request.POST)
        if enquiry_form.is_valid():
            result = save_contact_from_request(enquiry_form, request)
            if result.notification_sent and result.confirmation_sent:
                messages.success(
                    request,
                    "Thank you! Your enquiry was sent and a confirmation email is on its way.",
                )
            elif result.notification_sent:
                messages.success(
                    request,
                    "Thank you! We received your enquiry and will contact you soon.",
                )
            else:
                messages.warning(
                    request,
                    "Your enquiry was saved. Email delivery failed — our team will follow up shortly.",
                )
            return redirect(f"{request.path}#wl-package-enquiry")
        messages.error(request, "Please correct the errors below.")

    if enquiry_form is None:
        enquiry_form = ContactForm(initial=build_package_enquiry_initial(package))

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
            "enquiry_form": enquiry_form,
        },
    )


def domestic_detail(request, slug):
    return package_detail(request, slug, PackageCategory.CategoryType.DOMESTIC)


def international_detail(request, slug):
    return package_detail(request, slug, PackageCategory.CategoryType.INTERNATIONAL)


def pilgrim_detail(request, slug):
    return package_detail(request, slug, PackageCategory.CategoryType.PILGRIM)
