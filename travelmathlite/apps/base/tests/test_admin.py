from django.contrib import admin
from django.test import TestCase

from apps.base.models import City, Country


class BaseAdminTests(TestCase):
    def test_country_and_city_registered(self) -> None:
        self.assertIn(Country, admin.site._registry)
        self.assertIn(City, admin.site._registry)

