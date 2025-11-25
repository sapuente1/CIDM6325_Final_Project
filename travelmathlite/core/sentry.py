"""Optional Sentry initialization guarded by environment flags."""

from __future__ import annotations

import os
from typing import Any


def init_sentry() -> None:
    """Initialize Sentry only when SENTRY_DSN is provided."""
    dsn = os.getenv("SENTRY_DSN")
    if not dsn:
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.django import DjangoIntegration
    except Exception:
        # Sentry SDK not installed; skip initialization
        return

    sentry_sdk.init(
        dsn=dsn,
        integrations=[DjangoIntegration()],
        traces_sample_rate=float(os.getenv("SENTRY_TRACES_SAMPLE_RATE", "0.0")),
        environment=os.getenv("SENTRY_ENV", "local"),
        release=os.getenv("SENTRY_RELEASE"),
    )
