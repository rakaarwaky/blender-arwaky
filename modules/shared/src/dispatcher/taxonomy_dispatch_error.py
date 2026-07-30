"""Dispatcher taxonomy — Error categories and exceptions for dispatch operations.

Defines the standard error categories used across all dispatcher capabilities
and the DispatchError exception class that carries a category for safe envelope
construction. Exception messages are never propagated to consumers directly.
"""

from __future__ import annotations


class DispatchErrorCategory:
    """Standard error categories for dispatch operations.

    Used by SyncDispatchProtocol, BackgroundSubmitProtocol, and
    ResultNormalizationProtocol when constructing error envelopes.
    """

    VALIDATION: str = "validation_error"
    NOT_FOUND: str = "not_found_error"
    EXECUTION: str = "execution_error"
    CAPACITY: str = "capacity_error"
    UNSUPPORTED: str = "unsupported_error"
    TIMEOUT: str = "timeout_error"
    CONNECTION: str = "connection_error"
    CONFIRMATION: str = "confirmation_error"
    REGISTRATION: str = "registration_error"


class DispatchError(Exception):
    """Dispatch exception with typed category.

    Raised when a dispatch operation fails. The message is safe for logging
    but must NOT be propagated to envelope consumers — use error_category
    for safe consumer-facing classification.
    """

    def __init__(self, message: str, error_category: str = DispatchErrorCategory.EXECUTION) -> None:
        super().__init__(message)
        self.error_category = error_category
