# modules/shared/src/job/utility_job_sanitizer.py
"""Job sanitization utilities — stateless standalone functions.

"""
from __future__ import annotations

import re
from collections.abc import Mapping

from ..common.taxonomy_core_vo import ErrorString
from .taxonomy_job_constant import (
    MAX_CANCELLATION_REASON_LENGTH,
    MAX_ERROR_CATEGORY_LENGTH,
    MAX_ERROR_LENGTH,
    MAX_METADATA_KEY_LENGTH,
    MAX_METADATA_KEYS,
    MAX_METADATA_VALUE_LENGTH,
    MAX_OPERATION_TYPE_LENGTH,
    MAX_PROGRESS_MESSAGE_LENGTH,
)
from .taxonomy_job_vo import CancellationReason, ErrorCategory, OperationType, ProgressMessage

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SENSITIVE_KEYS = frozenset({
    "password", "token", "secret", "api_key", "auth",
    "credential", "authorization", "session", "cookie",
})
_REDACTED_PLACEHOLDER = "[REDACTED]"


def sanitize_text(value: str, max_length: int) -> str:
    """Strip control characters, trim whitespace, truncate to max_length."""
    cleaned = _CONTROL_CHARS.sub("", value).strip()
    return cleaned[:max_length]


def sanitize_operation_type(value: str) -> OperationType:
    """Sanitize operation type string to bounded OperationType VO."""
    return OperationType(sanitize_text(value, MAX_OPERATION_TYPE_LENGTH))


def sanitize_error(value: ErrorString) -> ErrorString:
    """Sanitize error string, stripping control chars and truncating."""
    return ErrorString(sanitize_text(str(value), MAX_ERROR_LENGTH))


def sanitize_error_category(value: str) -> ErrorCategory | None:
    """Sanitize error category. Returns None if empty after cleaning."""
    cleaned = sanitize_text(value, MAX_ERROR_CATEGORY_LENGTH)
    return ErrorCategory(cleaned) if cleaned else None


def sanitize_progress_message(value: str | None) -> ProgressMessage | None:
    """Sanitize optional progress message. Returns None if input None or empty."""
    if value is None:
        return None
    cleaned = sanitize_text(value, MAX_PROGRESS_MESSAGE_LENGTH)
    return ProgressMessage(cleaned) if cleaned else None


def sanitize_cancellation_reason(value: CancellationReason | None) -> CancellationReason | None:
    """Sanitize optional cancellation reason. Returns None if input None or empty."""
    if value is None:
        return None
    cleaned = sanitize_text(str(value), MAX_CANCELLATION_REASON_LENGTH)
    return CancellationReason(cleaned) if cleaned else None


def redact_metadata(metadata: Mapping[str, str] | None) -> dict[str, str]:
    """Copy metadata with sensitive keys redacted and values truncated.

    - Max MAX_METADATA_KEYS entries kept.
    - Keys matching _SENSITIVE_KEYS get value replaced with [REDACTED].
    - All other values sanitized and truncated.
    - Empty or None input returns empty dict.
    """
    if not metadata:
        return {}

    safe: dict[str, str] = {}
    for i, (key, value) in enumerate(metadata.items()):
        if i >= MAX_METADATA_KEYS:
            break

        clean_key = sanitize_text(str(key), MAX_METADATA_KEY_LENGTH)
        if not clean_key:
            continue

        if clean_key.lower() in _SENSITIVE_KEYS:
            safe[clean_key] = _REDACTED_PLACEHOLDER
        else:
            safe[clean_key] = sanitize_text(str(value), MAX_METADATA_VALUE_LENGTH)

    return safe
