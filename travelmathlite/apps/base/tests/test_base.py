from django.test import TestCase
from django.urls import reverse


class BaseURLsAndTemplatesTests(TestCase):
    def test_reverse_index(self) -> None:
        self.assertEqual(reverse("base:index"), "/")

    def test_index_renders_with_partial(self) -> None:
        url = reverse("base:index")
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "base/index.html")
        # Global base template lives at travelmathlite/templates/base.html
        self.assertTemplateUsed(resp, "base.html")
        self.assertContains(resp, "Quickly estimate distances and costs, find nearby airports, and save trips.")

    def test_base_template_includes_bootstrap_and_htmx_assets(self) -> None:
        resp = self.client.get(reverse("base:index"))
        self.assertContains(resp, "cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css")
        self.assertContains(resp, "cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js")
        self.assertContains(resp, "unpkg.com/htmx.org@2.0.3/dist/htmx.min.js")
        self.assertContains(resp, 'data-bs-toggle="collapse"')
        self.assertContains(resp, "navbar-toggler-icon")
