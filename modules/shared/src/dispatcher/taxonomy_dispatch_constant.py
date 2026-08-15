"""Dispatcher taxonomy — Domain constants for action metadata fields.

Centralises string constants used across dispatcher contracts, capabilities,
and surfaces. Replaces raw string literals with named constants.
"""

from __future__ import annotations

from typing import Final

# Risk level constants
RISK_LEVEL_LOW: Final[str] = "low"
RISK_LEVEL_MEDIUM: Final[str] = "medium"
RISK_LEVEL_HIGH: Final[str] = "high"

# Timeout class constants
TIMEOUT_CLASS_SHORT: Final[str] = "short"
TIMEOUT_CLASS_DEFAULT: Final[str] = "default"
TIMEOUT_CLASS_LONG: Final[str] = "long"
TIMEOUT_CLASS_EXTENDED: Final[str] = "extended"

# Execution mode constants
EXECUTION_MODE_SYNC: Final[str] = "sync"
EXECUTION_MODE_BACKGROUND: Final[str] = "background"

# Error category constants
DISPATCH_ERROR_CATEGORY_VALIDATION: Final[str] = "validation_error"
DISPATCH_ERROR_CATEGORY_NOT_FOUND: Final[str] = "not_found_error"
DISPATCH_ERROR_CATEGORY_EXECUTION: Final[str] = "execution_error"
DISPATCH_ERROR_CATEGORY_CAPACITY: Final[str] = "capacity_error"
DISPATCH_ERROR_CATEGORY_UNSUPPORTED: Final[str] = "unsupported_error"
DISPATCH_ERROR_CATEGORY_BLOCKED: Final[str] = "blocked_error"
DISPATCH_ERROR_CATEGORY_TIMEOUT: Final[str] = "timeout_error"
DISPATCH_ERROR_CATEGORY_CONNECTION: Final[str] = "connection_error"
DISPATCH_ERROR_CATEGORY_CONFIRMATION: Final[str] = "confirmation_error"
DISPATCH_ERROR_CATEGORY_REGISTRATION: Final[str] = "registration_error"
