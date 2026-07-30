"""Config domain value objects.

Immutable domain types for configuration management:
- SettingsSnapshot: merged, immutable settings container
- WorkspacePath: resolved project workspace directory
- RedactionRule: pattern-based sensitive value masking rule

Domain type aliases for YAML-parsed configuration values:
- SettingsValue: recursive YAML-parsed value type
- SettingsData: top-level parsed YAML dict
- SettingsOverrides: caller-supplied dot-path key=value overrides
- SettingsSchema: validation schema shape
- EventPayload: JSON-safe serialized domain event dict
- ConfigFileLoader: callable signature for YAML file loaders
"""

from __future__ import annotations

import copy
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import ConfigPath

# ─── Domain Type Aliases ──────────────────────────────────────────────────────
# Typed aliases for YAML-parsed configuration values.
# Defined here so all layers import from taxonomy, not from typing.

# Recursive YAML value — a primitive or nested container YAML can produce.
# Use this wherever raw YAML data flows through the system.
SettingsValue = str | int | float | bool | None | list["SettingsValue"] | dict[str, "SettingsValue"]

# Top-level settings dict — what a YAML loader returns after parsing.
SettingsData = dict[str, SettingsValue]

# Caller-supplied overrides — dot-path keys mapping to setting values.
SettingsOverrides = Mapping[str, SettingsValue]

# Validation schema shape — mirrors the structure of SettingsData.
SettingsSchema = dict[str, SettingsValue]

# JSON-safe event payload — emitted to the event ring buffer.
# Values are restricted to JSON primitives; no nested containers.
EventPayload = dict[str, str | int | float | bool | None]

# YAML file loader callable — receives a config path, returns parsed data.
ConfigFileLoader = Callable[[ConfigPath], SettingsData]

_MISSING = "__SENTINEL_MISSING__"  # module-private sentinel


@dataclass(frozen=True)
class SettingsSnapshot:
    """Immutable snapshot of merged configuration values.

    Created after load/reload. Never mutated after construction.
    Supports deep traversal via get()/get_segments() without exposing internals.
    """

    _data: SettingsData = field(repr=False, default_factory=dict)

    # ─── Segment traversal (T-04) ───────────────────────────────
    # These operate on pre-split segment tuples so the retriever can forward
    # escape-aware segments. get()/has() delegate to them.

    def get_segments(self, segments: tuple[str, ...], default: SettingsValue = None) -> SettingsValue:
        """Retrieve value by pre-split segment tuple. Returns deep copy."""
        if not segments:
            return copy.deepcopy(self._data)

        value: SettingsValue = self._data
        for segment in segments:
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            elif isinstance(value, list):
                try:
                    idx = int(segment)
                except (ValueError, TypeError):
                    return default
                if not isinstance(idx, int) or isinstance(idx, bool):
                    return default
                if 0 <= idx < len(value):
                    value = value[idx]
                else:
                    return default  # out-of-range: stop, do not continue with default as node
            else:
                return default

        return copy.deepcopy(value)

    def has_segments(self, segments: tuple[str, ...]) -> bool:
        """Check if a pre-split segment tuple exists in the snapshot."""
        if not segments:
            return True

        value: SettingsValue = self._data
        for segment in segments:
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            elif isinstance(value, list):
                try:
                    idx = int(segment)
                except (ValueError, TypeError):
                    return False
                if not isinstance(idx, int) or isinstance(idx, bool):
                    return False
                if 0 <= idx < len(value):
                    value = value[idx]
                else:
                    return False
            else:
                return False

        return True

    # ─── Dot-path delegation (T-04) ─────────────────────────────

    def get(self, path: str, default: SettingsValue = None) -> SettingsValue:
        """Retrieve value by dot-separated path. Returns deep copy."""
        return self.get_segments(tuple(path.split(".")) if path else (), default)

    def has(self, path: str) -> bool:
        """Check if a dot-separated path exists in the snapshot."""
        return self.has_segments(tuple(path.split(".")) if path else ())

    def to_dict(self) -> SettingsData:
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
        """Check if a key matches one of the sensitive patterns.

        Substring semantics are intentional (PM Q14): e.g. ``auth`` also
        matches ``author`` — an accepted false positive.
        """
        key_lower = key.lower()
        for pattern in self.key_patterns:
            if pattern.lower() in key_lower:
                return True
        return False
