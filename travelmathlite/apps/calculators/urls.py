from django.urls import path

from .views import (
    CostCalculatorView,
    DistanceCalculatorView,
    IndexView,
    cost_result_partial,
    distance_result_partial,
)

app_name = "calculators"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("distance/", DistanceCalculatorView.as_view(), name="distance"),
    path("cost/", CostCalculatorView.as_view(), name="cost"),
    # HTMX partial endpoints
    path("partials/distance/", distance_result_partial, name="distance-partial"),
    path("partials/cost/", cost_result_partial, name="cost-partial"),
]
