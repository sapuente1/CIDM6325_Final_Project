from django.test import TestCase

from apps.base.models import City, Country


class CityQuerySetTests(TestCase):
    def setUp(self) -> None:
        self.us = Country.objects.create(iso_code="US", name="United States", search_name="united states", slug="us")
        self.city = City.objects.create(country=self.us, name="Dallas", ascii_name="Dallas", search_name="dallas", slug="us-dallas")

    def test_city_search_case_insensitive(self) -> None:
        qs = City.objects.search("Dallas")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().name, "Dallas")

    def test_city_active_only(self) -> None:
        self.city.active = False
        self.city.save()
        qs = City.objects.search("Dallas")
        self.assertEqual(qs.count(), 0)

