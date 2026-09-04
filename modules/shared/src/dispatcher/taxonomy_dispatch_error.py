"""Dispatcher taxonomy — Error categories and exceptions for dispatch operations.

Defines the standard error categories used across all dispatcher capabilities
and the DispatchError exception class that carries a category for safe envelope
construction. Exception messages are never propagated to consumers directly.
"""

from __future__ import annotations

from typing import Final

from modules.shared.src.common.taxonomy_core_vo import ErrorString
from modules.shared.src.dispatcher.taxonomy_dispatch_constant import (
    DISPATCH_ERROR_CATEGORY_BLOCKED,
    DISPATCH_ERROR_CATEGORY_CAPACITY,
    DISPATCH_ERROR_CATEGORY_CONFIRMATION,
    DISPATCH_ERROR_CATEGORY_CONNECTION,
    DISPATCH_ERROR_CATEGORY_EXECUTION,
    DISPATCH_ERROR_CATEGORY_NOT_FOUND,
    DISPATCH_ERROR_CATEGORY_REGISTRATION,
    DISPATCH_ERROR_CATEGORY_TIMEOUT,
    DISPATCH_ERROR_CATEGORY_UNSUPPORTED,
    DISPATCH_ERROR_CATEGORY_VALIDATION,
)


class DispatchErrorCategory:
    """Standard error categories for dispatch operations."""

    VALIDATION: Final[str] = DISPATCH_ERROR_CATEGORY_VALIDATION
    NOT_FOUND: Final[str] = DISPATCH_ERROR_CATEGORY_NOT_FOUND
    EXECUTION: Final[str] = DISPATCH_ERROR_CATEGORY_EXECUTION
    CAPACITY: Final[str] = DISPATCH_ERROR_CATEGORY_CAPACITY
    BLOCKED: Final[str] = DISPATCH_ERROR_CATEGORY_BLOCKED
    UNSUPPORTED: Final[str] = DISPATCH_ERROR_CATEGORY_UNSUPPORTED
    TIMEOUT: Final[str] = DISPATCH_ERROR_CATEGORY_TIMEOUT
    CONNECTION: Final[str] = DISPATCH_ERROR_CATEGORY_CONNECTION
    CONFIRMATION: Final[str] = DISPATCH_ERROR_CATEGORY_CONFIRMATION
    REGISTRATION: Final[str] = DISPATCH_ERROR_CATEGORY_REGISTRATION


class DispatchError(Exception):
    """Dispatch exception with typed category.

    Raised when a dispatch operation fails. The message is safe for logging
    but must NOT be propagated to envelope consumers — use error_category
    for safe consumer-facing classification.
    """

    def __init__(
        self,
        message: ErrorString | str | None = None,
        error_category: object = DispatchErrorCategory.EXECUTION,
    ) -> None:
        err_msg = ErrorString(str(message)) if message is not None else ErrorString("")
        super().__init__(str(err_msg))
        self.error_category = str(error_category)
