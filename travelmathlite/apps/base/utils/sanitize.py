"""HTML sanitization helpers using bleach.

Centralizes allowlists so templates and views sanitize user-provided HTML safely.
"""

from __future__ import annotations

import bleach
from django.conf import settings
from django.utils.safestring import mark_safe


def sanitize_html(value: str | None) -> str:
    """Sanitize HTML using bleach with project allowlists."""
    cleaned = bleach.clean(
        value or "",
        tags=getattr(settings, "BLEACH_ALLOWED_TAGS", []),
        attributes=getattr(settings, "BLEACH_ALLOWED_ATTRIBUTES", {}),
        protocols=getattr(settings, "BLEACH_ALLOWED_PROTOCOLS", ["http", "https", "mailto"]),
        strip=getattr(settings, "BLEACH_STRIP", True),
        strip_comments=getattr(settings, "BLEACH_STRIP_COMMENTS", True),
    )
    return mark_safe(cleaned)
