from __future__ import annotations

from typing import Any

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import FormView, TemplateView

from ..airports.models import Airport
from .costs import calculate_fuel_cost
from .forms import CostCalculatorForm, DistanceCalculatorForm, FlyOrDriveForm
from .geo import calculate_distance_between_points, geodesic_distance, km_to_miles


class IndexView(TemplateView):
    """Minimal index landing page for the Calculators app."""

    template_name: str = "calculators/index.html"


@method_decorator(cache_page(600), name="dispatch")  # 10 minutes
class DistanceCalculatorView(FormView):
    template_name = "calculators/distance_calculator.html"
    form_class = DistanceCalculatorForm

    def form_valid(self, form: DistanceCalculatorForm) -> HttpResponse:  # type: ignore[override]
        lat1, lon1 = form.origin_coords
        lat2, lon2 = form.destination_coords
        unit = form.cleaned_data["unit"].lower()
        route_factor = float(form.cleaned_data["route_factor"])  # already validated

        flight, driving = calculate_distance_between_points(
            lat1, lon1, lat2, lon2, unit=unit, include_driving_estimate=True, route_factor=route_factor
        )

        # Driving time estimate (hours) using AVG_SPEED_KMH; if miles, convert speed
        avg_speed_kmh = float(getattr(settings, "AVG_SPEED_KMH", 80.0))
        driving_km = driving if unit == "km" else driving * 1.60934
        hours = driving_km / avg_speed_kmh if driving_km > 0 else 0.0

        context: dict[str, Any] = {
            "form": form,
            "unit": unit,
            "flight_distance": flight,
            "driving_distance": driving,
            "driving_time_hours": hours,
        }

        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "calculators/partials/distance_result.html", context)
        return render(self.request, self.template_name, context)

    def form_invalid(self, form: DistanceCalculatorForm) -> HttpResponse:  # type: ignore[override]
        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "calculators/partials/distance_result.html", {"form": form}, status=400)
        return super().form_invalid(form)


@method_decorator(cache_page(600), name="dispatch")  # 10 minutes
class CostCalculatorView(FormView):
    template_name = "calculators/cost_calculator.html"
    form_class = CostCalculatorForm

    def form_valid(self, form: CostCalculatorForm) -> HttpResponse:  # type: ignore[override]
        lat1, lon1 = form.origin_coords
        lat2, lon2 = form.destination_coords
        unit = form.cleaned_data["unit"].lower()
        route_factor = float(form.cleaned_data["route_factor"])  # already validated

        flight, driving = calculate_distance_between_points(
            lat1, lon1, lat2, lon2, unit=unit, include_driving_estimate=True, route_factor=route_factor
        )

        # Cost is computed on kilometers; convert if user selected miles
        driving_km = driving if unit == "km" else driving * 1.60934
        fuel_economy = float(form.cleaned_data["fuel_economy_l_per_100km"])  # L/100km
        fuel_price = float(form.cleaned_data["fuel_price_per_liter"])  # currency per liter
        total_cost = calculate_fuel_cost(driving_km, fuel_economy_l_per_100km=fuel_economy, fuel_price_per_liter=fuel_price)

        # Driving time estimate
        avg_speed_kmh = float(getattr(settings, "AVG_SPEED_KMH", 80.0))
        hours = driving_km / avg_speed_kmh if driving_km > 0 else 0.0

        context: dict[str, Any] = {
            "form": form,
            "unit": unit,
            "flight_distance": flight,
            "driving_distance": driving,
            "driving_time_hours": hours,
            "fuel_cost": total_cost,
        }

        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "calculators/partials/cost_result.html", context)
        return render(self.request, self.template_name, context)

    def form_invalid(self, form: CostCalculatorForm) -> HttpResponse:  # type: ignore[override]
        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "calculators/partials/cost_result.html", {"form": form}, status=400)
        return super().form_invalid(form)


class DistancePartialView(DistanceCalculatorView):
    def form_invalid(self, form: DistanceCalculatorForm) -> HttpResponse:  # type: ignore[override]
        # For partial endpoint, on invalid input render full page with errors (tests expect this)
        return render(self.request, "calculators/distance_calculator.html", {"form": form}, status=400)


class CostPartialView(CostCalculatorView):
    def form_invalid(self, form: CostCalculatorForm) -> HttpResponse:  # type: ignore[override]
        # For partial endpoint, on invalid input render full page with errors (tests expect this)
        return render(self.request, "calculators/cost_calculator.html", {"form": form}, status=400)


class FlyOrDriveView(FormView):
    template_name = "calculators/fly_or_drive.html"
    form_class = FlyOrDriveForm

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context.setdefault("flight", None)
        context.setdefault("driving", None)
        return context

    def form_valid(self, form: FlyOrDriveForm) -> HttpResponse:  # type: ignore[override]
        unit = form.cleaned_data.get("unit", "km")
        route_factor = float(form.cleaned_data.get("route_factor") or getattr(settings, "ROUTE_FACTOR", 1.2))
        avg_speed = float(form.cleaned_data.get("avg_speed_kmh") or getattr(settings, "AVG_SPEED_KMH", 80.0))
        fuel_economy = float(form.cleaned_data.get("fuel_economy_l_per_100km") or getattr(settings, "FUEL_ECONOMY_L_PER_100KM", 7.5))
        fuel_price = float(form.cleaned_data.get("fuel_price_per_liter") or getattr(settings, "FUEL_PRICE_PER_LITER", 1.50))
        fare_per_km = float(form.cleaned_data.get("fare_per_km") or 0.15)
        passengers = int(form.cleaned_data.get("passengers") or 1)
        trip_type = form.cleaned_data.get("trip_type", "one-way")
        trip_multiplier = 2 if trip_type == "round-trip" else 1

        lat1, lon1 = form.origin_coords
        lat2, lon2 = form.destination_coords

        # Flight distance based on nearest airports; fall back to geodesic between coords.
        origin_airport = None
        dest_airport = None
        origin_nearest = Airport.objects.nearest(lat1, lon1, limit=1)
        dest_nearest = Airport.objects.nearest(lat2, lon2, limit=1)
        if origin_nearest:
            origin_airport = origin_nearest[0]
        if dest_nearest:
            dest_airport = dest_nearest[0]

        if origin_airport and dest_airport:
            flight_distance_km = geodesic_distance(
                origin_airport.latitude_deg,
                origin_airport.longitude_deg,
                dest_airport.latitude_deg,
                dest_airport.longitude_deg,
            )
        else:
            flight_distance_km = geodesic_distance(lat1, lon1, lat2, lon2)

        flight_distance = km_to_miles(flight_distance_km) if unit == "miles" else flight_distance_km
        flight_time_hours = (flight_distance_km / 800.0) + 1.5  # 800 km/h cruise + buffer
        flight_cost = flight_distance_km * fare_per_km * passengers * trip_multiplier

        flight_data = {
            "distance": round(flight_distance, 2),
            "distance_unit": unit,
            "time_hours": round(flight_time_hours * trip_multiplier, 2),
            "cost": round(flight_cost, 2),
            "airports": {"origin": origin_airport, "destination": dest_airport},
        }

        # Driving side using straight-line + route factor
        straight_line, driving_distance = calculate_distance_between_points(
            lat1,
            lon1,
            lat2,
            lon2,
            unit=unit,
            include_driving_estimate=True,
            route_factor=route_factor,
        )
        driving_time_hours = (driving_distance / avg_speed) if driving_distance > 0 else 0.0
        driving_cost = calculate_fuel_cost(
            driving_distance if unit == "km" else driving_distance * 1.60934,
            fuel_economy_l_per_100km=fuel_economy,
            fuel_price_per_liter=fuel_price,
        )
        driving_data = {
            "straight_line": round(straight_line * trip_multiplier, 2),
            "distance": round(driving_distance * trip_multiplier, 2),
            "distance_unit": unit,
            "time_hours": round(driving_time_hours * trip_multiplier, 2),
            "cost": round(driving_cost * trip_multiplier, 2),
            "route_factor": route_factor,
            "avg_speed_kmh": avg_speed,
            "fuel_economy": fuel_economy,
            "fuel_price": fuel_price,
        }

        # Recommendation based on cost first, then time
        if driving_data["cost"] < flight_data["cost"]:
            recommendation = "Drive"
            rationale = f"Driving is cheaper by {round(flight_data['cost'] - driving_data['cost'], 2)}"
        else:
            recommendation = "Fly"
            rationale = f"Flying is cheaper by {round(driving_data['cost'] - flight_data['cost'], 2)}"

        if driving_data["time_hours"] > 0 and flight_data["time_hours"] > 0:
            time_diff = round(abs(driving_data["time_hours"] - flight_data["time_hours"]), 1)
            if driving_data["time_hours"] > flight_data["time_hours"]:
                rationale += f"; flying saves about {time_diff} hours"
            else:
                rationale += f"; driving saves about {time_diff} hours"

        context: dict[str, Any] = {
            "form": form,
            "flight": flight_data,
            "driving": driving_data,
            "recommendation": recommendation,
            "rationale": rationale,
            "trip_type": trip_type,
            "passengers": passengers,
        }

        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "calculators/partials/fly_or_drive_result.html", context)
        return render(self.request, self.template_name, context)

    def form_invalid(self, form: FlyOrDriveForm) -> HttpResponse:  # type: ignore[override]
        if self.request.headers.get("HX-Request") == "true":
            return render(self.request, "calculators/partials/fly_or_drive_result.html", {"form": form}, status=400)
        return super().form_invalid(form)
