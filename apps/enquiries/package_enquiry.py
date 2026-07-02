"""Shared helpers for package enquiry forms."""

from __future__ import annotations

from typing import TYPE_CHECKING

from packages.models import Package

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
    """Prefill enquiry message from an empty package search."""
    lines = [
        (
            "I searched for a trip matching my requirements, but none of our current "
            "pre-designed packages fit exactly. Please help me plan a custom itinerary."
        ),
        "",
        "Kindly find my travel requirements below:",
        "",
    ]
    if search.from_place:
        lines.append(f"Departing from: {search.from_place}")
    if search.to_place:
        lines.append(f"Destination: {search.to_place}")
    if search.depart:
        lines.append(f"Arrival date: {search.depart.strftime('%d %b %Y')}")
    elif not search.return_date:
        lines.append("Arrival date:")
    if search.return_date:
        lines.append(f"Departure date: {search.return_date.strftime('%d %b %Y')}")
    elif not search.depart:
        lines.append("Departure date:")
    if search.trip_days:
        nights = max(search.trip_days - 1, 1)
        lines.append(f"Number of nights: {nights}")
    else:
        lines.append("Number of nights:")
    lines.append(f"Number of adults: {search.adults}")
    if search.children:
        lines.append(f"Number of child: {search.children} (Age: )")
    else:
        lines.append("Number of child: (Age: )")
    return {"message": "\n".join(lines)}
