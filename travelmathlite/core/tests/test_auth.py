"""Authentication and authorization flow tests (Brief adr-1.0.11-05).

Covers:
- Login/logout happy paths
- Signup flow
- Access control on protected views
"""

from __future__ import annotations

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AuthFlowTests(TestCase):
    """Tests for login, logout, signup, and protected views."""

    def setUp(self) -> None:  # noqa: D401
        self.password = "testpass123"
        self.user = User.objects.create_user(username="authuser", password=self.password)

    def test_login_page_renders(self) -> None:
        url = reverse("accounts:login")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "registration/login.html")

    def test_login_success_redirects_to_home(self) -> None:
        url = reverse("accounts:login")
        resp = self.client.post(url, {"username": self.user.username, "password": self.password})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("base:index"))

        # Client should be authenticated; protected view should now be accessible
        profile_url = reverse("accounts:profile")
        resp_profile = self.client.get(profile_url)
        self.assertEqual(resp_profile.status_code, 200)

    def test_logout_redirects_to_home_and_deauthenticates(self) -> None:
        # Log in first
        self.client.login(username=self.user.username, password=self.password)

        url = reverse("accounts:logout")
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("base:index"))

        # After logout, protected view should redirect to login with next param
        profile_url = reverse("accounts:profile")
        resp_profile = self.client.get(profile_url)
        self.assertEqual(resp_profile.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp_profile.url)
        self.assertIn("next=", resp_profile.url)

    def test_signup_creates_user_and_redirects_to_login(self) -> None:
        url = reverse("accounts:signup")
        payload = {
            "username": "newuser",
            "password1": "StrongPassw0rd!",
            "password2": "StrongPassw0rd!",
        }
        resp = self.client.post(url, payload)
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp.url, reverse("accounts:login"))
        self.assertTrue(User.objects.filter(username="newuser").exists())

    def test_protected_profile_redirects_anonymous_to_login(self) -> None:
        profile_url = reverse("accounts:profile")
        resp = self.client.get(profile_url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn(reverse("accounts:login"), resp.url)
        self.assertIn("next=", resp.url)
