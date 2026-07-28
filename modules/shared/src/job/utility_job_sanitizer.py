# modules/shared/src/job/utility_job_sanitizer.py
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import ErrorString
from .taxonomy_job_vo import CancellationReason

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SENSITIVE_KEYS = frozenset({"password", "token", "secret", "api_key", "auth"})


def sanitize_text(value: str, max_length: int) -> str:
    """Strip control characters and truncate to max_length."""
    cleaned = _CONTROL_CHARS.sub("", value).strip()
    return cleaned[:max_length]


def sanitize_error(value: ErrorString) -> ErrorString:
    """Sanitize an error string, preserving type."""
    return ErrorString(sanitize_text(str(value), 500))


def sanitize_progress_message(value: Any | None) -> str | None:
    """Sanitize an optional progress message string."""
    if value is None:
        return None
    cleaned = sanitize_text(str(value), 500)
    return cleaned if cleaned else None


def sanitize_cancellation_reason(value: CancellationReason | None) -> CancellationReason | None:
    """Sanitize an optional cancellation reason."""
    if value is None:
        return None
    cleaned = sanitize_text(str(value), 500)
    return CancellationReason(cleaned) if cleaned else None


def redact_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    """Shallow-copy metadata, redacting values for known sensitive keys."""
    if not metadata:
        return {}
    return {
        k: ("***" if k.lower() in _SENSITIVE_KEYS else v)
        for k, v in metadata.items()
    }
