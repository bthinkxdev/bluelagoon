"""Shared helpers for package enquiry forms."""

from __future__ import annotations

from typing import TYPE_CHECKING

from packages.models import Package
from packages.search import travel_type_label

if TYPE_CHECKING:
    from packages.search import PackageSearch


def build_package_enquiry_initial(package: Package | None) -> dict:
    """Prefill the contact/enquiry message with structured travel requirements."""
    if not package:
        return {}
    return {
        "package_slug": package.slug,
        "message": (
            f"I would like to visit {package.title}. Kindly find my travel requirements below\n\n"
            "Arrival date:\n"
            "Departure date:\n"
            "Number of nights:\n"
            "Number of adults:\n"
            "Number of child: (Age: )"
        ),
    }


def build_search_enquiry_initial(search: PackageSearch) -> dict:
    """Prefill enquiry message from an empty destination search."""
    lines = [
        (
            "We couldn't find a ready-made package for your selected destination. "
            "Please share your travel requirements, and our travel consultant will "
            "prepare a customized itinerary for you."
        ),
        "",
        "Kindly find my travel requirements below:",
        "",
    ]
    if search.travel_type and search.travel_type != "all":
        lines.append(f"Travel type: {travel_type_label(search.travel_type)}")
    if search.destination:
        lines.append(f"Destination: {search.destination}")
    else:
        lines.append("Destination:")
    if search.travel_date:
        lines.append(f"Travel date: {search.travel_date.strftime('%d %b %Y')}")
    else:
        lines.append("Travel date:")
    lines.append(f"Number of adults: {search.adults}")
    if search.children:
        lines.append(f"Number of children: {search.children}")
    else:
        lines.append("Number of children: 0")
    return {"message": "\n".join(lines)}
