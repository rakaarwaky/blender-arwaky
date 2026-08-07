"""Capability: Settings retriever (FR-CFG-002).

Implements ISettingsRetrieverProtocol — hierarchical dot-separated
settings value retrieval with safe copy semantics, policy-mode typing,
and escaped-separator path support.
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import ErrorString
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.taxonomy_config_constant import POLICY_MODE_STRICT
from modules.shared.src.config.taxonomy_config_error import ConfigTypeError
from modules.shared.src.config.taxonomy_config_vo import _MISSING, SettingsSnapshot, SettingsValue
from modules.shared.src.config.utility_config_helpers import parse_settings_path


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsRetrieverCapability(ISettingsRetrieverProtocol):
    """FR-CFG-002: Retrieve settings values.

    Thread-safe traversal, deep-copy returns, list indexing support,
    typed getters with policy-mode error handling, escaped separator support.
    No I/O. No file or environment reads per request.
    """

    def __init__(self, policy_mode: str = POLICY_MODE_STRICT, escape_enabled: bool = False) -> None:
        self._policy_mode = policy_mode
        self._escape_enabled = escape_enabled

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_value(
        self,
        snapshot: SettingsSnapshot,
        path: str,
        default: SettingsValue = None,
    ) -> SettingsValue:
        """Retrieve value by dot-separated path. Returns deep copy."""
        segments = parse_settings_path(path, self._escape_enabled)
        return snapshot.get_segments(segments, default)

    def has_value(self, snapshot: SettingsSnapshot, path: str) -> bool:
        """Check if a dot-separated path exists."""
        segments = parse_settings_path(path, self._escape_enabled)
        return snapshot.has_segments(segments)

    def get_string(self, snapshot: SettingsSnapshot, path: str, default: str = "") -> str:
        """Retrieve string value. Returns default on type mismatch."""
        return self._typed(snapshot, path, str, default)

    def get_int(self, snapshot: SettingsSnapshot, path: str, default: int = 0) -> int:
        """Retrieve integer value. Returns default on type mismatch. Bool excluded."""
        return self._typed(snapshot, path, int, default, exclude_bool=True)

    def get_bool(self, snapshot: SettingsSnapshot, path: str, default: bool = False) -> bool:
        """Retrieve boolean value. Returns default on type mismatch."""
        return self._typed(snapshot, path, bool, default)

    def get_float(self, snapshot: SettingsSnapshot, path: str, default: float = 0.0) -> float:
        """Retrieve float value. Returns default on type mismatch. Int coerced."""
        return self._typed(snapshot, path, float, default, coerce_int=True)

# ─── Block 3: Typed Helper ─────────────────────────────────

    def _typed(
        self,
        snapshot: SettingsSnapshot,
        path: str,
        expected: type,
        default: SettingsValue,
        exclude_bool: bool = False,
        coerce_int: bool = False,
    ) -> SettingsValue:
        segments = parse_settings_path(path, self._escape_enabled)
        raw = snapshot.get_segments(segments, _MISSING)
        if raw is _MISSING:
            return default  # missing key never raises in either mode

        if expected is int:
            if isinstance(raw, int) and not (exclude_bool and isinstance(raw, bool)):
                return raw
        elif expected is float:
            if not isinstance(raw, bool):
                if isinstance(raw, int):
                    return float(raw) if coerce_int else default
                if isinstance(raw, float):
                    return raw
        elif isinstance(raw, expected):
            return raw

        if self._policy_mode == POLICY_MODE_STRICT:
            # Sanitize path — use only final segment to avoid leaking structure
            safe_ref = path.rsplit(".", maxsplit=1)[-1] if "." in path else path
            raise ConfigTypeError(
                ErrorString(f"{safe_ref}: expected {expected.__name__}, got {type(raw).__name__}")
            )
        return default

    def __repr__(self) -> str:
        return "SettingsRetrieverCapability()"
