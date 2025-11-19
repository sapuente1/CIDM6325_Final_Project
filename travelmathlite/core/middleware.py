"""Middleware for request ID tracking and timing.

Implements request ID injection and duration tracking as specified in ADR-1.0.9.
Ensures every request has a unique identifier and timing information for logging.
"""

import time
import uuid
from collections.abc import Callable

from django.http import HttpRequest, HttpResponse


class RequestIDMiddleware:
    """Inject X-Request-ID and track request duration.

    This middleware:
    - Reads X-Request-ID from request headers or generates a UUID4
    - Attaches request_id to the request object for logging
    - Records start/end timestamps and calculates duration_ms
    - Adds X-Request-ID to the response headers
    - Survives exceptions to ensure duration is always available

    Invariants:
    - INV-1: request.request_id is always present (never None)
    - INV-2: request.duration_ms is logged even when exceptions occur
    """

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """Initialize middleware with the next handler in the chain.

        Args:
            get_response: The next middleware or view to call.
        """
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        """Process request, inject request ID, and track duration.

        Args:
            request: The incoming HTTP request.

        Returns:
            The HTTP response with X-Request-ID header added.
        """
        # Read X-Request-ID from headers or generate a new UUID4
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())

        # Attach request_id to request for logging (INV-1)
        request.request_id = request_id  # type: ignore[attr-defined]

        # Record start time
        start_time = time.perf_counter()

        try:
            # Process the request through the rest of the middleware chain
            response = self.get_response(request)
        finally:
            # Calculate duration even if an exception occurred (INV-2)
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000.0
            request.duration_ms = duration_ms  # type: ignore[attr-defined]

        # Add X-Request-ID to response headers
        response["X-Request-ID"] = request_id

        return response
