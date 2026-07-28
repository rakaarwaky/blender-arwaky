"""Utility: Request ID generation for server domain.

Stateless function that generates UUID4 tracking IDs for all
requests, responses, and events.
"""

from __future__ import annotations

import uuid


def new_request_id() -> str:
    """Generate a new UUID4 request ID string.

    Returns:
        A UUID4 formatted string (e.g., '550e8400-e2eb-11da-...').

    Used by the orchestrator when clients do not provide a tracking ID.
    """
    return str(uuid.uuid4())
