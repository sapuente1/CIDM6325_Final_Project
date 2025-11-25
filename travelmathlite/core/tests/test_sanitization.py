"""Tests for HTML sanitization utilities and template filters."""

from django.template import Context, Template
from django.test import SimpleTestCase, override_settings

from apps.base.utils.sanitize import sanitize_html


class SanitizationTests(SimpleTestCase):
    """Verify bleach-based sanitization keeps allowlists and strips unsafe input."""

    @override_settings(
        BLEACH_ALLOWED_TAGS=["b", "a"],
        BLEACH_ALLOWED_ATTRIBUTES={"a": ["href"]},
        BLEACH_ALLOWED_PROTOCOLS=["http", "https"],
    )
    def test_sanitize_html_strips_disallowed_and_unsafe_protocols(self) -> None:
        html = '<script>alert("x")</script><b>bold</b><a href="javascript:alert(1)">link</a>'

        cleaned = sanitize_html(html)

        self.assertNotIn("<script", cleaned)
        self.assertIn("<b>bold</b>", cleaned)
        self.assertIn("<a", cleaned)
        self.assertNotIn("javascript:", cleaned)

    def test_template_filter_applies_bleach_clean(self) -> None:
        tmpl = Template("{% load sanitize %}{{ value|sanitize_html }}")
        rendered = tmpl.render(
            Context({"value": '<img src=x onerror="alert(1)"><strong>safe</strong><em>ok</em>'})
        )

        self.assertNotIn("<img", rendered)
        self.assertIn("<strong>safe</strong>", rendered)
        self.assertIn("<em>ok</em>", rendered)
