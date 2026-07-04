"""Tour package search — destination-based filtering within travel types."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date
from typing import Any

from django.db.models import Case, F, IntegerField, Q, QuerySet, Value, When
from django.utils.dateparse import parse_date

from packages.models import Package, TravelType

SORT_DEFAULT = "default"
SORT_PRICE_ASC = "price_asc"
SORT_PRICE_DESC = "price_desc"
SORT_DURATION_ASC = "duration_asc"
SORT_DURATION_DESC = "duration_desc"

SORT_CHOICES: dict[str, str] = {
    SORT_DEFAULT: "Recommended",
    SORT_PRICE_ASC: "Price: Low to High",
    SORT_PRICE_DESC: "Price: High to Low",
    SORT_DURATION_ASC: "Duration: Shortest",
    SORT_DURATION_DESC: "Duration: Longest",
}

DURATION_ANY = ""
DURATION_SHORT = "short"
DURATION_MEDIUM = "medium"
DURATION_LONG = "long"

DURATION_CHOICES: dict[str, str] = {
    DURATION_ANY: "Any duration",
    DURATION_SHORT: "1–3 days",
    DURATION_MEDIUM: "4–7 days",
    DURATION_LONG: "8+ days",
}

_DURATION_BUCKETS: dict[str, tuple[int, int]] = {
    DURATION_SHORT: (1, 3),
    DURATION_MEDIUM: (4, 7),
    DURATION_LONG: (8, 999),
}

TRAVEL_TYPES = frozenset(TravelType.values)


@dataclass
class PackageSearch:
    """Search criteria from GET parameters."""

    travel_type: str
    destination: str = ""
    travel_date: date | None = None
    adults: int = 1
    children: int = 0
    tab: str = ""
    sort: str = SORT_DEFAULT
    duration_bucket: str = ""

    # Legacy aliases kept for older links / templates.
    @property
    def category_type(self) -> str:
        return self.travel_type

    @property
    def to_place(self) -> str:
        return self.destination

    @property
    def from_place(self) -> str:
        return ""

    @property
    def depart(self) -> date | None:
        return self.travel_date

    @property
    def return_date(self) -> date | None:
        return None

    @property
    def has_text_search(self) -> bool:
        return bool(self.destination)

    @property
    def has_filters(self) -> bool:
        return bool(
            self.destination
            or self.travel_date
            or self.adults != 1
            or self.children > 0
            or self.duration_bucket
        )

    @property
    def travellers_label(self) -> str:
        parts: list[str] = []
        if self.adults > 0:
            parts.append(f"{self.adults} Adult{'s' if self.adults != 1 else ''}")
        if self.children > 0:
            parts.append(f"{self.children} Child{'ren' if self.children != 1 else ''}")
        return ", ".join(parts) if parts else "1 Adult"

    @property
    def trip_days(self) -> int | None:
        return None

    @classmethod
    def from_request(cls, request, travel_type: str = "all") -> PackageSearch:
        get = request.GET
        adults, children = _parse_travellers(
            get.get("adults", ""),
            get.get("children", ""),
            get.get("travellers", ""),
        )
        sort = (get.get("sort") or SORT_DEFAULT).strip()
        if sort not in SORT_CHOICES:
            sort = SORT_DEFAULT
        duration_bucket = (get.get("duration") or "").strip()
        if duration_bucket not in DURATION_CHOICES:
            duration_bucket = DURATION_ANY

        destination = (get.get("destination") or get.get("to") or "").strip()
        travel_date = parse_date(get.get("depart", "") or "") or parse_date(
            get.get("travel_date", "") or ""
        )

        resolved_type = (travel_type or "all").strip()
        if resolved_type not in TRAVEL_TYPES and resolved_type != "all":
            resolved_type = "all"

        return cls(
            travel_type=resolved_type,
            destination=destination,
            travel_date=travel_date,
            adults=adults,
            children=children,
            tab=(get.get("tab") or "").strip(),
            sort=sort,
            duration_bucket=duration_bucket,
        )

    def apply(self, queryset: QuerySet[Package]) -> QuerySet[Package]:
        qs = queryset

        if self.travel_type in TRAVEL_TYPES:
            qs = qs.filter(travel_type=self.travel_type)

        if self.destination:
            term = self.destination
            match_q = (
                Q(destination__name__iexact=term)
                | Q(destination__name__icontains=term)
                | Q(destination__slug__icontains=term.replace(" ", "-").lower())
                | Q(title__icontains=term)
                | Q(route__icontains=term)
                | Q(short_description__icontains=term)
                | Q(description__icontains=term)
            )
            qs = qs.filter(match_q).distinct()
            qs = _annotate_relevance(qs, [term])

        if self.duration_bucket:
            qs = _filter_by_duration_bucket(qs, self.duration_bucket)

        return self.apply_sort(qs)

    def apply_sort(self, queryset: QuerySet[Package]) -> QuerySet[Package]:
        if self.sort == SORT_PRICE_ASC:
            return queryset.order_by(F("price").asc(nulls_last=True), "display_order", "title")
        if self.sort == SORT_PRICE_DESC:
            return queryset.order_by(F("price").desc(nulls_last=True), "display_order", "title")
        if self.sort == SORT_DURATION_ASC:
            return queryset.order_by(
                F("duration_days").asc(nulls_last=True), "display_order", "title"
            )
        if self.sort == SORT_DURATION_DESC:
            return queryset.order_by(
                F("duration_days").desc(nulls_last=True), "display_order", "title"
            )
        if self.has_text_search and self.sort == SORT_DEFAULT:
            return queryset.order_by("-relevance_score", "display_order", "title")
        return queryset.order_by("display_order", "title")

    def to_context(self) -> dict[str, Any]:
        return {
            "search": self,
            "search_active": self.has_filters,
            "search_query": self.summary(),
            "search_params": self.query_dict(),
            "sort_choices": SORT_CHOICES,
            "duration_choices": DURATION_CHOICES,
        }

    def query_dict(self) -> dict[str, str]:
        """Preserve active filters for links and refine forms."""
        params: dict[str, str] = {}
        if self.destination:
            params["destination"] = self.destination
        if self.travel_date:
            params["depart"] = self.travel_date.isoformat()
        if self.adults != 1:
            params["adults"] = str(self.adults)
        if self.children:
            params["children"] = str(self.children)
        if self.tab:
            params["tab"] = self.tab
        if self.travel_type and self.travel_type != "all":
            params["category"] = self.travel_type
        if self.sort and self.sort != SORT_DEFAULT:
            params["sort"] = self.sort
        if self.duration_bucket:
            params["duration"] = self.duration_bucket
        params["travellers"] = self.travellers_label
        return params

    def summary(self) -> str:
        parts: list[str] = []
        if self.travel_type in TRAVEL_TYPES:
            parts.append(travel_type_label(self.travel_type).lower())
        if self.destination:
            parts.append(self.destination)
        if self.travel_date:
            parts.append(f"travel date {self.travel_date.strftime('%d %b %Y')}")
        if self.duration_bucket:
            parts.append(DURATION_CHOICES.get(self.duration_bucket, self.duration_bucket))
        if self.adults != 1 or self.children:
            parts.append(self.travellers_label.lower())
        return ", ".join(parts)


def extract_duration_days(duration: str) -> int | None:
    """Parse day count from strings like '09 NIGHTS / 10 DAYS'."""
    return _extract_duration_days(duration)


def _term_relevance_case(term: str, *, weight: int = 1) -> Case:
    """Score a single search term with field-weighted relevance."""
    return Case(
        When(destination__name__iexact=term, then=Value(120 * weight)),
        When(destination__name__istartswith=term, then=Value(100 * weight)),
        When(destination__name__icontains=term, then=Value(90 * weight)),
        When(title__iexact=term, then=Value(85 * weight)),
        When(title__istartswith=term, then=Value(75 * weight)),
        When(title__icontains=term, then=Value(65 * weight)),
        When(route__icontains=term, then=Value(50 * weight)),
        When(short_description__icontains=term, then=Value(40 * weight)),
        When(description__icontains=term, then=Value(25 * weight)),
        default=Value(0),
        output_field=IntegerField(),
    )


def _annotate_relevance(queryset: QuerySet[Package], terms: list[str]) -> QuerySet[Package]:
    if not terms:
        return queryset

    score = Value(0, output_field=IntegerField())
    for term in terms:
        score = score + _term_relevance_case(term)
    return queryset.annotate(relevance_score=score).filter(relevance_score__gt=0)


def _parse_travellers(
    adults_raw: str, children_raw: str, travellers_raw: str
) -> tuple[int, int]:
    adults = _clamp_int(adults_raw, default=1, minimum=1, maximum=9)
    children = _clamp_int(children_raw, default=0, minimum=0, maximum=9)

    if adults_raw or children_raw:
        return adults, children

    if not travellers_raw:
        return 1, 0

    adults_match = re.search(r"(\d+)\s*adults?", travellers_raw, re.I)
    children_match = re.search(r"(\d+)\s*child(?:ren)?", travellers_raw, re.I)
    if adults_match:
        adults = _clamp_int(adults_match.group(1), default=1, minimum=1, maximum=9)
    if children_match:
        children = _clamp_int(children_match.group(1), default=0, minimum=0, maximum=9)
    return adults, children


def _clamp_int(value: str, *, default: int, minimum: int, maximum: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(minimum, min(maximum, number))


def _extract_duration_days(duration: str) -> int | None:
    if not duration:
        return None
    day_match = re.search(r"(\d+)\s*days?", duration, re.I)
    if day_match:
        return int(day_match.group(1))
    night_match = re.search(r"(\d+)\s*nights?", duration, re.I)
    if night_match:
        return int(night_match.group(1)) + 1
    return None


def _filter_by_duration_bucket(queryset: QuerySet[Package], bucket: str) -> QuerySet[Package]:
    bounds = _DURATION_BUCKETS.get(bucket)
    if not bounds:
        return queryset
    min_days, max_days = bounds
    return queryset.filter(duration_days__gte=min_days, duration_days__lte=max_days)


def travel_type_label(travel_type: str) -> str:
    labels = {
        TravelType.DOMESTIC: "Domestic",
        TravelType.INTERNATIONAL: "International",
        TravelType.PILGRIM: "Pilgrimage",
    }
    return labels.get(travel_type, "Tour")


# Backward-compatible alias used by older imports.
category_label = travel_type_label
