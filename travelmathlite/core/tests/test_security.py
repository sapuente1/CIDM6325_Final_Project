"""Security tests for headers and CSRF."""

from django.test import Client, TestCase, override_settings
from django.urls import reverse


@override_settings(
    DEBUG=False,
    ALLOWED_HOSTS=["testserver"],
    SECURE_HSTS_SECONDS=31536000,
    SECURE_HSTS_INCLUDE_SUBDOMAINS=True,
    SECURE_CONTENT_TYPE_NOSNIFF=True,
    SECURE_REFERRER_POLICY="strict-origin-when-cross-origin",
    X_FRAME_OPTIONS="DENY",
)
class SecurityHeaderTests(TestCase):
    """Verify security headers emitted in production-like settings."""

    def test_security_headers_present_on_secure_request(self) -> None:
        client = Client()
        resp = client.get("/", secure=True)

        self.assertEqual(resp.headers.get("Strict-Transport-Security"), "max-age=31536000; includeSubDomains")
        self.assertEqual(resp.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(resp.headers.get("X-Frame-Options"), "DENY")
        self.assertEqual(resp.headers.get("Referrer-Policy"), "strict-origin-when-cross-origin")


@override_settings(RATE_LIMIT_AUTH_ENABLED=False)
class CSRFSecurityTests(TestCase):
    """Ensure CSRF tokens are present and enforced on auth endpoints."""

    def test_login_page_has_csrf_token(self) -> None:
        resp = self.client.get(reverse("accounts:login"))
        self.assertContains(resp, "csrfmiddlewaretoken")

    def test_post_without_csrf_is_rejected(self) -> None:
        client = Client(enforce_csrf_checks=True)
        resp = client.post(reverse("accounts:login"), {"username": "u", "password": "p"})
        self.assertEqual(resp.status_code, 403)
