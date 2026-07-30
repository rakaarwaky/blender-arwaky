"""Security utility: stateless sensitive-value redaction."""

from __future__ import annotations

import re

from .taxonomy_security_constant import REDACTION_SENSITIVE_PATTERNS

_SENSITIVE_PATTERNS: tuple[re.Pattern[str], ...] = tuple(re.compile(p) for p in REDACTION_SENSITIVE_PATTERNS)

_SENSITIVE_KEY_PATTERNS: tuple[re.Pattern[str], ...] = tuple(
    re.compile(rf"(?i)\b({p})\b", re.IGNORECASE)
    for p in (
        "password",
        "passwd",
        "secret",
        "token",
        "api[_-]?key",
        "access[_-]?key",
        "private[_-]?key",
        "credential",
    )
)


def is_sensitive_key(key: str) -> bool:
    """Return True if the key name looks like a secret holder."""
    return any(p.search(key) for p in _SENSITIVE_KEY_PATTERNS)


def redact_sensitive(value: object) -> object:
    """Recursively mask sensitive values without mutating input objects."""
    if isinstance(value, str):
        text = value
        for pattern in _SENSITIVE_PATTERNS:
            text = pattern.sub("[REDACTED]", text)
        return text

    if isinstance(value, dict):
        redacted: dict[str, object] = {}
        for key, val in value.items():
            if is_sensitive_key(key) and isinstance(val, str):
                candidate = val
                for pattern in _SENSITIVE_PATTERNS:
                    candidate = pattern.sub("[REDACTED]", candidate)
                redacted[key] = "[REDACTED]" if candidate == val else candidate
            else:
                redacted[key] = redact_sensitive(val)
        return redacted

    if isinstance(value, (list, tuple)):
        return type(value)(redact_sensitive(item) for item in value)

    return value
