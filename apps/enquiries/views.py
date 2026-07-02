"""Enquiry form views."""

from __future__ import annotations

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods
from django_ratelimit.decorators import ratelimit

from enquiries.forms import ContactForm
from enquiries.package_enquiry import build_package_enquiry_initial
from enquiries.services import save_contact_from_request
from packages.models import Package


def _resolve_package(request) -> Package | None:
    slug = ""
    if request.method == "POST":
        slug = (request.POST.get("package_slug") or "").strip()
    else:
        slug = (request.GET.get("package") or "").strip()
    if not slug:
        return None
    return Package.objects.filter(slug=slug, status=Package.Status.PUBLISHED).select_related(
        "category"
    ).first()


def _contact_form_initial(package) -> dict:
    return build_package_enquiry_initial(package)


@ratelimit(key="ip", rate="5/m", method="POST", block=True)
@require_http_methods(["GET", "POST"])
def contact(request):
    enquiry_package = _resolve_package(request)

    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            result = save_contact_from_request(form, request)
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
                    "Your enquiry was saved. Email delivery failed — our team will follow up from the admin inbox.",
                )
            return redirect("enquiries:contact")
        messages.error(request, "Please correct the errors below.")
        enquiry_package = (
            Package.objects.filter(
                slug=form.data.get("package_slug", "").strip(),
                status=Package.Status.PUBLISHED,
            )
            .select_related("category")
            .first()
            or enquiry_package
        )
    else:
        form = ContactForm(initial=_contact_form_initial(enquiry_package))

    return render(
        request,
        "website/contact.html",
        {
            "form": form,
            "enquiry_package": enquiry_package,
            "page_title": "Contact",
        },
    )
