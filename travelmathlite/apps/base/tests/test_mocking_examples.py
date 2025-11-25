"""Example mocking and time-freezing patterns (Brief adr-1.0.11-07).

These are illustrative tests to show how to use MockingTestCase and TimeTestCase
to keep tests deterministic (INV-1).
"""

from __future__ import annotations

import sys
from types import SimpleNamespace

from django.utils import timezone

from .base import MockingTestCase, TimeTestCase

try:  # pragma: no cover - defensive import shim
    import requests  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - fallback when requests not installed
    requests = SimpleNamespace(get=lambda *args, **kwargs: None, post=lambda *args, **kwargs: None)
    sys.modules["requests"] = requests


class HttpMockExamples(MockingTestCase):
    """Demonstrate mocking external HTTP calls."""

    def test_mock_http_get_replaces_requests_get(self) -> None:
        """requests.get is patched to return deterministic data."""
        payload = {"message": "ok"}
        mock_get = self.mock_http_get("https://example.com/api/status", payload, status_code=201)

        response = requests.get("https://example.com/api/status")

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), payload)
        # Ensure mock was started and tracked for cleanup
        self.assertIsNotNone(mock_get)
        self.assertEqual(len(self._mocks), 1)

    def test_mock_external_api_patches_arbitrary_function(self) -> None:
        """Arbitrary function patched with return value."""
        self.mock_external_api("django.utils.timezone.now", return_value=timezone.datetime(2025, 11, 19))

        now = timezone.now()
        self.assertEqual(now.year, 2025)
        self.assertEqual(now.month, 11)
        self.assertEqual(now.day, 19)


class TimeFreezingExamples(TimeTestCase):
    """Demonstrate freezing time for deterministic tests."""

    def test_freeze_time_for_duration(self) -> None:
        """timezone.now returns the frozen moment until cleanup."""
        frozen = self.get_fixed_datetime(2025, 11, 19, hour=12, minute=34, second=56)
        self.freeze_time(frozen)

        self.assertEqual(timezone.now(), frozen)
        # A second call should still return the frozen time (no drift)
        self.assertEqual(timezone.now(), frozen)
