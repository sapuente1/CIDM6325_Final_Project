from django.contrib import admin
from django.test import TestCase

from apps.airports.models import Airport


class AirportAdminTests(TestCase):
    def test_airport_registered_in_admin(self) -> None:
        self.assertIn(Airport, admin.site._registry)

