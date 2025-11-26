from django.test import TestCase

from apps.airports.models import Airport
from apps.base.models import Country


class AirportQuerySetTests(TestCase):
    def setUp(self) -> None:
        self.us = Country.objects.create(
            iso_code="US",
            name="United States",
            search_name="united states",
            slug="us",
        )
        self.mx = Country.objects.create(
            iso_code="MX",
            name="Mexico",
            search_name="mexico",
            slug="mx",
        )
        Airport.objects.create(
            ident="KDAL",
            iata_code="DAL",
            name="Dallas Love Field",
            airport_type="medium_airport",
            latitude_deg=32.8471,
            longitude_deg=-96.8518,
            iso_country="US",
            country=self.us,
            active=True,
        )
        Airport.objects.create(
            ident="MMMX",
            iata_code="MEX",
            name="Benito Juarez Intl",
            airport_type="large_airport",
            latitude_deg=19.4363,
            longitude_deg=-99.0721,
            iso_country="MX",
            country=self.mx,
            active=True,
        )
        Airport.objects.create(
            ident="INACTIVE",
            iata_code="ZZZ",
            name="Inactive Airport",
            airport_type="small_airport",
            latitude_deg=0.0,
            longitude_deg=0.0,
            iso_country="US",
            country=self.us,
            active=False,
        )

    def test_search_matches_codes_and_country(self) -> None:
        qs = Airport.objects.search("DAL")
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs.first().iata_code, "DAL")

        qs_iso = Airport.objects.search("MX")
        self.assertIn("MX", {a.iso_country for a in qs_iso})

    def test_active_filter_applied(self) -> None:
        results = Airport.objects.search("ZZZ")
        self.assertEqual(results.count(), 0)

