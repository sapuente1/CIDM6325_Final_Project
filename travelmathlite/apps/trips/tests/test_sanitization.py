"""Ensure saved calculations render sanitized input."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.trips.models import SavedCalculation

User = get_user_model()


class SavedCalculationSanitizationTests(TestCase):
    """Verify user-provided saved calculation fields are sanitized in templates."""

    def setUp(self) -> None:  # noqa: D401
        self.user = User.objects.create_user(username="sanitizer", password="testpass123")

    def test_saved_list_sanitizes_inputs(self) -> None:
        calc = SavedCalculation.objects.create(user=self.user, calculator_type="distance", inputs="{}", outputs="{}")
        calc.set_inputs({"note": '<script>alert(1)</script><b>ok</b>'})
        calc.save()

        self.client.force_login(self.user)
        resp = self.client.get(reverse("trips:saved_list"))

        content = resp.content.decode()
        self.assertEqual(resp.status_code, 200)
        self.assertNotIn("<script>alert(1)", content)
        self.assertIn("<b>ok</b>", content)
        self.assertIn("alert(1)", content)
