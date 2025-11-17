from __future__ import annotations

from typing import Any

from django.db.models import QuerySet
from django.views.generic import TemplateView

from ..airports.models import Airport
from ..base.models import City


class SearchView(TemplateView):
    """Render search results for airports and cities based on `q`.

    Non-goals in this slice: pagination and highlighting (handled in later briefs).
    """

    template_name: str = "search/results.html"

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        raw_q = self.request.GET.get("q", "")
        q = (raw_q or "").strip()

        context["query"] = q
        context["had_query"] = bool(q)

        if not q:
            # Avoid DB work on empty queries
            context["airport_results"] = Airport.objects.none()
            context["city_results"] = City.objects.none()
            context["results_count"] = 0
            return context

        # Basic icontains search using existing queryset helpers; limit until pagination lands
        airports: QuerySet[Airport] = (
            Airport.objects.search(q)
            .select_related("country", "city")
            .only(
                "name",
                "iata_code",
                "ident",
                "municipality",
                "iso_country",
                "country__name",
                "city__name",
            )
        )
        cities: QuerySet[City] = (
            City.objects.search(q)
            .select_related("country")
            .only(
                "name",
                "slug",
                "country__iso_code",
                "country__name",
            )
        )

        # Temporary cap to keep page manageable pre-pagination
        airport_list = list(airports[:20])
        city_list = list(cities[:20])

        context["airport_results"] = airport_list
        context["city_results"] = city_list
        context["results_count"] = len(airport_list) + len(city_list)
        return context
