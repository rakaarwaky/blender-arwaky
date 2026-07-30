"""Dispatch error taxonomy — constants and domain exception.

FR-DSP-XXX: Exception messages must not leak sensitive information
into result envelopes. Exception details go to logs only.
"""

from __future__ import annotations


class DispatchErrorCategory:
    """Unified error categories for dispatcher result envelopes.

    These constants are used in UnifiedResultEnvelopeVO.error_category
    and by DispatchError for typed error propagation.
    """

    VALIDATION: str = "validation_error"
    NOT_FOUND: str = "not_found_error"
    EXECUTION: str = "execution_error"
    CAPACITY: str = "capacity_error"
    UNSUPPORTED: str = "unsupported_error"
    TIMEOUT: str = "timeout_error"
    CONFIRMATION: str = "confirmation_error"
    REGISTRATION: str = "registration_error"
    CONNECTION: str = "connection_error"


class DispatchError(Exception):
    """Domain exception for dispatch failures with typed error category.

    Carries a DispatchErrorCategory string that the agent layer uses
    to populate the result envelope without leaking exception internals.
    """

    def __init__(self, message: str, error_category: str = DispatchErrorCategory.EXECUTION) -> None:
        super().__init__(message)
        self.error_category = error_category
