"""Template filters for HTML sanitization."""

from __future__ import annotations

from django import template

from apps.base.utils.sanitize import sanitize_html as _sanitize_html

register = template.Library()


@register.filter(name="sanitize_html")
def sanitize_html(value: str | None) -> str:
    """Sanitize user-provided HTML with bleach allowlists."""
    return _sanitize_html(value)
