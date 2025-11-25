"""Tests for auth endpoint rate limiting."""

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse

User = get_user_model()


@override_settings(
    RATE_LIMIT_AUTH_ENABLED=True,
    RATE_LIMIT_AUTH_MAX_REQUESTS=2,
    RATE_LIMIT_AUTH_WINDOW=60,
    CACHES={
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "ratelimit-tests",
        }
    },
)
class RateLimitTests(TestCase):
    """Ensure rate limits return 429 after threshold."""

    def setUp(self) -> None:  # noqa: D401
        self.user = User.objects.create_user(username="rateuser", password="pass123")
        self.client = Client(enforce_csrf_checks=True)

    def _get_csrf_token(self, url: str) -> str:
        resp = self.client.get(url)
        return resp.cookies["csrftoken"].value

    def test_login_rate_limit_blocks_after_threshold(self) -> None:
        login_url = reverse("accounts:login")
        csrf = self._get_csrf_token(login_url)

        for attempt in range(2):
            resp = self.client.post(
                login_url,
                {"username": "wrong", "password": "bad"},
                REMOTE_ADDR="192.0.2.10",
                HTTP_X_CSRFTOKEN=csrf,
            )
            self.assertNotEqual(resp.status_code, 429, msg=f"Unexpected 429 on attempt {attempt}")

        blocked = self.client.post(
            login_url,
            {"username": "wrong", "password": "bad"},
            REMOTE_ADDR="192.0.2.10",
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(blocked.status_code, 429)

    def test_signup_rate_limit_blocks_after_threshold(self) -> None:
        signup_url = reverse("accounts:signup")
        csrf = self._get_csrf_token(signup_url)

        for attempt in range(2):
            resp = self.client.post(
                signup_url,
                {"username": f"user{attempt}", "password1": "StrongPassw0rd!", "password2": "StrongPassw0rd!"},
                REMOTE_ADDR="192.0.2.20",
                HTTP_X_CSRFTOKEN=csrf,
            )
            # Signup errors but should not be 429 until threshold exceeded
            self.assertNotEqual(resp.status_code, 429, msg=f"Unexpected 429 on attempt {attempt}")

        blocked = self.client.post(
            signup_url,
            {"username": "user-final", "password1": "StrongPassw0rd!", "password2": "StrongPassw0rd!"},
            REMOTE_ADDR="192.0.2.20",
            HTTP_X_CSRFTOKEN=csrf,
        )
        self.assertEqual(blocked.status_code, 429)
