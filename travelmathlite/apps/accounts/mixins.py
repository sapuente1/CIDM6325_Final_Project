"""Mixins for account views."""

from __future__ import annotations

from django.conf import settings
from django.core.cache import cache
from django.http import HttpRequest, HttpResponse


class RateLimitMixin:
    """Simple in-cache rate limiting for POST requests."""

    rate_limit_prefix = "auth"

    def get_rate_limit_config(self) -> tuple[bool, int, int]:
        enabled = getattr(settings, "RATE_LIMIT_AUTH_ENABLED", False)
        max_requests = int(getattr(settings, "RATE_LIMIT_AUTH_MAX_REQUESTS", 5))
        window = int(getattr(settings, "RATE_LIMIT_AUTH_WINDOW", 60))
        return enabled, max_requests, window

    def get_rate_limit_key(self, request: HttpRequest) -> str:
        identifier = request.META.get("REMOTE_ADDR") or request.POST.get("username") or "anonymous"
        return f"{self.rate_limit_prefix}:{request.path}:{identifier}"

    def check_rate_limit(self, request: HttpRequest) -> HttpResponse | None:
        enabled, max_requests, window = self.get_rate_limit_config()
        if not enabled or request.method != "POST":
            return None

        key = self.get_rate_limit_key(request)
        # Ensure the key exists for increment
        cache.add(key, 0, timeout=window)
        try:
            count = cache.incr(key)
        except Exception:
            cache.set(key, 1, timeout=window)
            count = 1

        if count > max_requests:
            return HttpResponse("Too many attempts. Please wait and try again.", status=429)
        return None

    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        limited_response = self.check_rate_limit(request)
        if limited_response:
            return limited_response
        return super().dispatch(request, *args, **kwargs)
