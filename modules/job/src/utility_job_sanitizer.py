"""Job sanitization utility (AES utility layer, stateless).

Strips secrets and raw code from free-text details (error messages, cancel
reasons) before they are persisted or emitted in events/snapshots, per
FR-JOB-001 ("Error detail must be sanitized before storage, excluding secrets
and raw code") and FR-JOB-003 ("Cancellation reason must be sanitized").

Depends only on the standard library — no taxonomy, contract, or other layers.
"""

from __future__ import annotations

import re

# Patterns whose values must never be stored: secrets, tokens, credentials.
_SECRET_PATTERN = re.compile(
    r"(?i)(password|passwd|secret|token|api[_-]?key|access[_-]?key|auth|cookie|"
    r"credential|private[_-]?key|authorization)\s*[=:]\s*\S+"
)

# Control characters that should not survive into stored detail.
_CONTROL_PATTERN = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")

# Maximum length for any stored free-text detail.
_MAX_DETAIL_LENGTH = 1000


def sanitize_error_detail(text: str, max_length: int = _MAX_DETAIL_LENGTH) -> str:
    """Return a redacted, length-bounded copy of ``text``.

    Removes credential assignments, control characters, and truncates to
    ``max_length`` characters (appending an ellipsis marker when clipped).
    """
    if not text:
        return ""
    redacted = _SECRET_PATTERN.sub(r"\1=<redacted>", text)
    redacted = _CONTROL_PATTERN.sub(" ", redacted)
    redacted = redacted.replace("\r", " ").replace("\n", " ")
    if len(redacted) > max_length:
        return redacted[:max_length].rstrip() + "…"
    return redacted.strip()
