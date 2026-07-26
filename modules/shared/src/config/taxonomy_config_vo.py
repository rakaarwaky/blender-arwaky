"""Config domain value objects.

Immutable domain types for configuration management:
- SettingsSnapshot: merged, immutable settings container
- WorkspacePath: resolved project workspace directory
- RedactionRule: pattern-based sensitive value masking rule
- SensitiveKeyPattern: key-level sensitivity detection
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SettingsSnapshot:
    """Immutable snapshot of merged configuration values.

    Created after load/reload. Never mutated after construction.
    Supports deep traversal via get() without exposing internals.
    """

    _data: dict[str, Any] = field(repr=False, default_factory=dict)

    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve value by dot-separated path. Returns deep copy."""
        if not path:
            return copy.deepcopy(self._data)

        keys = path.split(".")
        value: Any = self._data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    value = value[idx] if 0 <= idx < len(value) else default
                except (ValueError, IndexError):
                    return default
            else:
                return default

        return copy.deepcopy(value)

    def has(self, path: str) -> bool:
        """Check if a dot-separated path exists in the snapshot."""
        if not path:
            return True

        keys = path.split(".")
        value: Any = self._data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    value = value[idx] if 0 <= idx < len(value) else None
                except (ValueError, IndexError):
                    return False
            else:
                return False

        return True

    def to_dict(self) -> dict[str, Any]:
        """Return deep copy of raw settings dict."""
        return copy.deepcopy(self._data)


@dataclass(frozen=True)
class WorkspacePath:
    """Resolved project workspace directory path."""

    path: str
    strategy: str

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("WorkspacePath.path must not be empty")
        if not self.strategy:
            raise ValueError("WorkspacePath.strategy must not be empty")


@dataclass(frozen=True)
class RedactionRule:
    """Rule for redacting sensitive configuration values.

    Defines which keys are sensitive and how to mask them.
    """

    key_patterns: tuple[str, ...] = field(default_factory=tuple)
    placeholder: str = "***REDACTED***"
    full_redact: bool = True

    def matches_key(self, key: str) -> bool:
        """Check if a key matches any of the sensitive patterns."""
        key_lower = key.lower()
        return any(pattern.lower() in key_lower for pattern in self.key_patterns)


@dataclass(frozen=True)
class SensitiveKeyPattern:
    """Pattern for detecting sensitive configuration keys."""

    pattern: str
    description: str = ""
    full_redact: bool = True
