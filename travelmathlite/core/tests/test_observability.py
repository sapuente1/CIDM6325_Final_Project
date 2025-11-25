"""Observability tests for logging, error pages, and Sentry toggle."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import patch

from django.http import HttpResponseServerError
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from core.logging import JSONFormatter
from core.sentry import init_sentry
from apps.base.views import IndexView


class LoggingTests(TestCase):
    """Verify structured logging includes request metadata."""

    def test_json_formatter_includes_request_fields(self) -> None:
        formatter = JSONFormatter()

        class Record:
            levelname = "INFO"
            module = "testmod"

            def getMessage(self) -> str:
                return "request completed"

        record = Record()
        record.request_id = "req-123"
        record.duration_ms = 12.5
        record.path = "/health/"
        record.method = "GET"
        record.status_code = 200
        record.exc_info = None

        payload = json.loads(formatter.format(record))  # type: ignore[arg-type]
        self.assertEqual(payload["request_id"], "req-123")
        self.assertEqual(payload["duration_ms"], 12.5)
        self.assertEqual(payload["path"], "/health/")
        self.assertEqual(payload["method"], "GET")
        self.assertEqual(payload["status_code"], 200)

    def test_request_logging_middleware_emits_log(self) -> None:
        with self.assertLogs("request", level="INFO") as captured:
            self.client.get(reverse("base:index"))

        joined = "\n".join(captured.output)
        self.assertIn("request completed", joined)


@override_settings(DEBUG=False, ALLOWED_HOSTS=["testserver"])
class ErrorTemplateTests(TestCase):
    """Ensure 404/500 templates render."""

    def setUp(self) -> None:  # noqa: D401
        self.client = Client(raise_request_exception=False)

    def test_404_template_used(self) -> None:
        resp = self.client.get("/does-not-exist/")
        self.assertEqual(resp.status_code, 404)
        self.assertTemplateUsed(resp, "404.html")

    def test_500_template_used(self) -> None:
        with patch.object(IndexView, "get", side_effect=Exception("boom")):
            resp = self.client.get(reverse("base:index"))
        self.assertEqual(resp.status_code, 500)
        self.assertTemplateUsed(resp, "500.html")


class SentryToggleTests(TestCase):
    """Validate Sentry init is guarded by DSN and missing SDK is handled."""

    @patch.dict(
        "sys.modules",
        {
            "sentry_sdk": SimpleNamespace(init=lambda *args, **kwargs: None),
            "sentry_sdk.integrations": {},
            "sentry_sdk.integrations.django": SimpleNamespace(DjangoIntegration=lambda: "django"),
        },
    )
    @patch("os.getenv", side_effect=lambda k, default=None: {"SENTRY_DSN": "fake-dsn", "SENTRY_ENV": "test"}.get(k, default))
    def test_sentry_init_runs_when_dsn_present(self, mock_getenv) -> None:  # type: ignore[override]
        with patch("sentry_sdk.init") as init_mock:
            init_sentry()
            init_mock.assert_called_once()

    @patch.dict("sys.modules", {})
    @patch("os.getenv", side_effect=lambda k, default=None: None)
    def test_sentry_skips_when_dsn_missing(self, mock_getenv) -> None:  # type: ignore[override]
        # Should not raise
        init_sentry()
