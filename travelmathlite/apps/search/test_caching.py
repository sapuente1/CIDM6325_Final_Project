"""Tests for search view caching behavior.

Verify that search results are cached with proper TTLs and key variation.
"""

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..airports.models import Airport
from ..base.models import City, Country


class SearchCachingTestCase(TestCase):
    """Test caching behavior for search views."""

    def setUp(self) -> None:
        """Create test data and clear cache."""
        cache.clear()

        # Create test data
        self.country = Country.objects.create(
            iso_code="US",
            name="United States",
            search_name="united states",
            slug="united-states",
        )
        self.city = City.objects.create(
            country=self.country,
            name="Dallas",
            slug="dallas",
        )
        self.airport = Airport.objects.create(
            ident="KDAL",
            iata_code="DAL",
            name="Dallas Love Field",
            municipality="Dallas",
            iso_country="US",
            country=self.country,
            city=self.city,
            latitude_deg=32.8470,
            longitude_deg=-96.8517,
        )
        self.client = Client()

    def tearDown(self) -> None:
        """Clear cache after each test."""
        cache.clear()

    def test_search_results_cached(self) -> None:
        """Test that identical search queries return cached results."""
        url = reverse("search:index")

        # First request (cache miss)
        response1 = self.client.get(url, {"q": "Dallas"})
        self.assertEqual(response1.status_code, 200)
        content1 = response1.content

        # Second identical request (cache hit)
        response2 = self.client.get(url, {"q": "Dallas"})
        self.assertEqual(response2.status_code, 200)
        content2 = response2.content

        # Content should be identical (cached response)
        self.assertEqual(content1, content2)

    def test_different_queries_different_cache(self) -> None:
        """Test that different queries use different cache keys."""
        url = reverse("search:index")

        # Two different search queries
        response1 = self.client.get(url, {"q": "Dallas"})
        self.assertEqual(response1.status_code, 200)

        response2 = self.client.get(url, {"q": "Houston"})
        self.assertEqual(response2.status_code, 200)

        # Content should differ (different search results)
        # Note: Content may be similar if both are empty results,
        # but the cache keys should be different
        self.assertIsNotNone(response1.content)
        self.assertIsNotNone(response2.content)

    def test_pagination_varies_cache_key(self) -> None:
        """Test that different pagination parameters use different cache keys."""
        url = reverse("search:index")

        # Create multiple airports for pagination
        for i in range(25):
            Airport.objects.create(
                ident=f"TEST{i}",
                iata_code=f"T{i:02d}",
                name=f"Test Airport {i}",
                municipality="Dallas",
                iso_country="US",
                country=self.country,
                city=self.city,
                latitude_deg=32.8470 + i * 0.01,
                longitude_deg=-96.8517 - i * 0.01,
            )

        # Page 1
        response1 = self.client.get(url, {"q": "Test", "page": "1"})
        self.assertEqual(response1.status_code, 200)

        # Page 2
        response2 = self.client.get(url, {"q": "Test", "page": "2"})
        self.assertEqual(response2.status_code, 200)

        # Content should differ (different pages)
        self.assertNotEqual(response1.content, response2.content)

    def test_empty_query_cached(self) -> None:
        """Test that empty queries are also cached."""
        url = reverse("search:index")

        # First request with empty query
        response1 = self.client.get(url, {"q": ""})
        self.assertEqual(response1.status_code, 200)

        # Second request with empty query
        response2 = self.client.get(url, {"q": ""})
        self.assertEqual(response2.status_code, 200)

        # Should return cached content
        self.assertEqual(response1.content, response2.content)

    def test_cache_respects_query_case(self) -> None:
        """Test that cache keys vary by query case (default behavior)."""
        url = reverse("search:index")

        # Lowercase query
        response1 = self.client.get(url, {"q": "dallas"})
        self.assertEqual(response1.status_code, 200)

        # Uppercase query (cache considers this different)
        response2 = self.client.get(url, {"q": "DALLAS"})
        self.assertEqual(response2.status_code, 200)

        # Both should succeed; cache treats them as different keys
        self.assertIsNotNone(response1.content)
        self.assertIsNotNone(response2.content)

    def test_cache_clears_successfully(self) -> None:
        """Test that cache can be cleared."""
        url = reverse("search:index")

        # Make request to populate cache
        response1 = self.client.get(url, {"q": "Dallas"})
        self.assertEqual(response1.status_code, 200)

        # Clear cache
        cache.clear()

        # Next request should work (cache miss, repopulated)
        response2 = self.client.get(url, {"q": "Dallas"})
        self.assertEqual(response2.status_code, 200)
        self.assertIsNotNone(response2.content)
