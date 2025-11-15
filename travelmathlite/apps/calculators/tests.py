from django.test import TestCase
from django.urls import reverse

from .geo import (
    calculate_distance_between_points,
    estimate_driving_distance,
    geodesic_distance,
    haversine_distance,
    km_to_miles,
    miles_to_km,
)


class CalculatorsURLsAndTemplatesTests(TestCase):
    def test_reverse_index(self) -> None:
        self.assertEqual(reverse("calculators:index"), "/calculators/")

    def test_index_renders_with_partial(self) -> None:
        url = reverse("calculators:index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "calculators/index.html")
        self.assertTemplateUsed(resp, "base.html")
        self.assertContains(resp, "This is the Calculators app partial include.")


class UnitConversionTests(TestCase):
    """Test unit conversion functions for mathematical correctness."""

    def test_km_to_miles_conversion(self) -> None:
        """Test kilometer to miles conversion."""
        self.assertAlmostEqual(km_to_miles(100), 62.1371, places=4)
        self.assertAlmostEqual(km_to_miles(1), 0.621371, places=6)
        self.assertEqual(km_to_miles(0), 0.0)

    def test_miles_to_km_conversion(self) -> None:
        """Test miles to kilometers conversion."""
        self.assertAlmostEqual(miles_to_km(100), 160.934, places=3)
        self.assertAlmostEqual(miles_to_km(1), 1.60934, places=5)
        self.assertEqual(miles_to_km(0), 0.0)

    def test_round_trip_conversion(self) -> None:
        """Test that converting km -> miles -> km returns original value."""
        original_km = 100.0
        converted_miles = km_to_miles(original_km)
        back_to_km = miles_to_km(converted_miles)
        self.assertAlmostEqual(back_to_km, original_km, places=3)

    def test_reverse_round_trip_conversion(self) -> None:
        """Test that converting miles -> km -> miles returns original value."""
        original_miles = 100.0
        converted_km = miles_to_km(original_miles)
        back_to_miles = km_to_miles(converted_km)
        self.assertAlmostEqual(back_to_miles, original_miles, places=3)


class HaversineDistanceTests(TestCase):
    """Test haversine distance calculations with known city pairs."""

    def test_nyc_to_la_distance(self) -> None:
        """Test New York to Los Angeles distance (~3944 km)."""
        # NYC: 40.7128° N, 74.0060° W
        # LA: 34.0522° N, 118.2437° W
        distance = haversine_distance(40.7128, -74.0060, 34.0522, -118.2437)
        # Expected distance is approximately 3944 km
        self.assertGreater(distance, 3900)
        self.assertLess(distance, 4000)

    def test_london_to_paris_distance(self) -> None:
        """Test London to Paris distance (~344 km)."""
        # London: 51.5074° N, 0.1278° W
        # Paris: 48.8566° N, 2.3522° E
        distance = haversine_distance(51.5074, -0.1278, 48.8566, 2.3522)
        # Expected distance is approximately 344 km
        self.assertGreater(distance, 340)
        self.assertLess(distance, 350)

    def test_same_point_distance(self) -> None:
        """Test that distance from a point to itself is zero."""
        distance = haversine_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertAlmostEqual(distance, 0.0, places=10)

    def test_short_distance(self) -> None:
        """Test a short distance (within same city)."""
        # Two points in Manhattan, approximately 1 km apart
        distance = haversine_distance(40.7589, -73.9851, 40.7489, -73.9680)
        self.assertGreater(distance, 0.5)
        self.assertLess(distance, 2.0)

    def test_antipodal_points(self) -> None:
        """Test distance between antipodal points (opposite sides of Earth)."""
        # North Pole to South Pole
        distance = haversine_distance(90, 0, -90, 0)
        # Expected distance is approximately half Earth's circumference (~20,000 km)
        self.assertGreater(distance, 19000)
        self.assertLess(distance, 21000)


class GeodesicDistanceTests(TestCase):
    """Test geodesic distance calculations (uses geopy if available, falls back to haversine)."""

    def test_geodesic_nyc_to_la(self) -> None:
        """Test geodesic distance from NYC to LA."""
        distance = geodesic_distance(40.7128, -74.0060, 34.0522, -118.2437)
        self.assertGreater(distance, 3900)
        self.assertLess(distance, 4000)

    def test_geodesic_london_to_paris(self) -> None:
        """Test geodesic distance from London to Paris."""
        distance = geodesic_distance(51.5074, -0.1278, 48.8566, 2.3522)
        self.assertGreater(distance, 340)
        self.assertLess(distance, 350)

    def test_geodesic_same_point(self) -> None:
        """Test geodesic distance from a point to itself is zero."""
        distance = geodesic_distance(40.7128, -74.0060, 40.7128, -74.0060)
        self.assertAlmostEqual(distance, 0.0, places=10)

    def test_geodesic_matches_haversine(self) -> None:
        """Test that geodesic and haversine give similar results for moderate distances."""
        lat1, lon1 = 51.5074, -0.1278
        lat2, lon2 = 48.8566, 2.3522
        geodesic = geodesic_distance(lat1, lon1, lat2, lon2)
        haversine = haversine_distance(lat1, lon1, lat2, lon2)
        # Should be within 1% of each other
        difference = abs(geodesic - haversine)
        self.assertLess(difference, geodesic * 0.01)


class DrivingDistanceEstimateTests(TestCase):
    """Test driving distance estimation with route factors."""

    def test_default_route_factor(self) -> None:
        """Test driving estimate with default route factor (1.2)."""
        straight_line = 100.0
        driving = estimate_driving_distance(straight_line)
        self.assertEqual(driving, 120.0)

    def test_custom_route_factor(self) -> None:
        """Test driving estimate with custom route factor."""
        straight_line = 100.0
        driving = estimate_driving_distance(straight_line, route_factor=1.3)
        self.assertEqual(driving, 130.0)

    def test_route_factor_of_one(self) -> None:
        """Test that route factor of 1.0 returns same as input."""
        straight_line = 100.0
        driving = estimate_driving_distance(straight_line, route_factor=1.0)
        self.assertEqual(driving, straight_line)

    def test_zero_distance(self) -> None:
        """Test driving estimate for zero distance."""
        driving = estimate_driving_distance(0.0)
        self.assertEqual(driving, 0.0)


class CalculateDistanceBetweenPointsTests(TestCase):
    """Test the main distance calculation function."""

    def test_calculate_distance_km_only(self) -> None:
        """Test distance calculation in kilometers without driving estimate."""
        flight, driving = calculate_distance_between_points(
            40.7128, -74.0060, 34.0522, -118.2437, unit="km", include_driving_estimate=False
        )
        self.assertGreater(flight, 3900)
        self.assertLess(flight, 4000)
        self.assertEqual(driving, 0.0)

    def test_calculate_distance_miles_only(self) -> None:
        """Test distance calculation in miles without driving estimate."""
        flight, driving = calculate_distance_between_points(
            40.7128, -74.0060, 34.0522, -118.2437, unit="miles", include_driving_estimate=False
        )
        # Approximately 2451 miles
        self.assertGreater(flight, 2400)
        self.assertLess(flight, 2500)
        self.assertEqual(driving, 0.0)

    def test_calculate_distance_with_driving_estimate_km(self) -> None:
        """Test distance with driving estimate in kilometers."""
        flight, driving = calculate_distance_between_points(
            40.7128,
            -74.0060,
            34.0522,
            -118.2437,
            unit="km",
            include_driving_estimate=True,
            route_factor=1.2,
        )
        self.assertGreater(flight, 3900)
        self.assertLess(flight, 4000)
        self.assertGreater(driving, flight)
        # Driving should be approximately 1.2x flight distance
        self.assertAlmostEqual(driving / flight, 1.2, places=10)

    def test_calculate_distance_with_driving_estimate_miles(self) -> None:
        """Test distance with driving estimate in miles."""
        flight, driving = calculate_distance_between_points(
            40.7128,
            -74.0060,
            34.0522,
            -118.2437,
            unit="miles",
            include_driving_estimate=True,
            route_factor=1.2,
        )
        self.assertGreater(flight, 2400)
        self.assertLess(flight, 2500)
        self.assertGreater(driving, flight)
        # Driving should be approximately 1.2x flight distance
        self.assertAlmostEqual(driving / flight, 1.2, places=10)

    def test_calculate_distance_custom_route_factor(self) -> None:
        """Test distance calculation with custom route factor."""
        flight, driving = calculate_distance_between_points(
            51.5074,
            -0.1278,
            48.8566,
            2.3522,
            unit="km",
            include_driving_estimate=True,
            route_factor=1.5,
        )
        self.assertAlmostEqual(driving / flight, 1.5, places=10)

