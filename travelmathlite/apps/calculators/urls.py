from django.urls import path

from .views import (
    CostCalculatorView,
    DistanceCalculatorView,
    IndexView,
)

app_name = "calculators"

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("distance/", DistanceCalculatorView.as_view(), name="distance"),
    path("cost/", CostCalculatorView.as_view(), name="cost"),
]
