"""Dispatcher domain errors and error categories.

Taxonomy layer:
  - Stable error categories from FRD.
  - Explicit error type consumed by agent and capabilities.
"""

from __future__ import annotations


class DispatchErrorCategory:
    """FRD-aligned dispatcher error categories."""

    VALIDATION = "validation_error"
    NOT_FOUND = "not_found_error"
    EXECUTION = "execution_error"
    CAPACITY = "capacity_error"
    UNSUPPORTED = "unsupported_error"
    TIMEOUT = "timeout_error"
    CONFIRMATION = "confirmation_error"
    REGISTRATION = "registration_error"


class DispatchError(Exception):
    """Domain error carrying a stable dispatcher error category."""

    def __init__(
        self,
        message: str,
        error_category: str = DispatchErrorCategory.EXECUTION,
        field_name: str | None = None,
    ) -> None:
        super().__init__(message)
        self.error_category = error_category
        self.field_name = field_name
