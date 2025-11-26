from django.test import Client, TestCase
from django.urls import reverse

from apps.airports.models import Airport, Country


class FlyOrDriveViewTests(TestCase):
    def setUp(self) -> None:
        country = Country.objects.create(name="Testland", iso_code="TL")
        self.origin_airport = Airport.objects.create(
            ident="TEST1",
            iata_code="AAA",
            name="Alpha Airport",
            airport_type="medium_airport",
            latitude_deg=10.0,
            longitude_deg=10.0,
            iso_country="TL",
            country=country,
            municipality="Alpha",
            active=True,
        )
        self.dest_airport = Airport.objects.create(
            ident="TEST2",
            iata_code="BBB",
            name="Beta Airport",
            airport_type="medium_airport",
            latitude_deg=11.0,
            longitude_deg=11.0,
            iso_country="TL",
            country=country,
            municipality="Beta",
            active=True,
        )
        self.client = Client()

    def test_get_renders(self) -> None:
        url = reverse("calculators:fly_or_drive")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Fly or Drive")

    def test_post_returns_results(self) -> None:
        url = reverse("calculators:fly_or_drive")
        resp = self.client.post(
            url,
            {
                "origin": "10,10",
                "destination": "11,11",
                "trip_type": "one-way",
                "passengers": 1,
                "unit": "km",
                "route_factor": 1.2,
                "avg_speed_kmh": 80,
                "fuel_economy_l_per_100km": 7.5,
                "fuel_price_per_liter": 1.5,
                "fare_per_km": 0.15,
            },
        )
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, "Driving")
        self.assertContains(resp, "Flying")
