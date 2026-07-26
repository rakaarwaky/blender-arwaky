"""Capability: Settings retriever (FR-CFG-002).

Implements ISettingsRetrieverProtocol — hierarchical dot-separated
settings value retrieval with safe copy semantics.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsRetrieverCapability(ISettingsRetrieverProtocol):
    """FR-CFG-002: Retrieve settings values.

    Thread-safe traversal, deep-copy returns, list indexing support.
    No I/O. No file or environment reads per request.
    """

    def __init__(self) -> None:
        pass

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_value(
        self,
        snapshot: SettingsSnapshot,
        path: str,
        default: Any = None,
    ) -> Any:
        """Retrieve value by dot-separated path. Returns deep copy."""
        return snapshot.get(path, default)

    def has_value(self, snapshot: SettingsSnapshot, path: str) -> bool:
        """Check if a dot-separated path exists."""
        return snapshot.has(path)

    def get_string(self, snapshot: SettingsSnapshot, path: str, default: str = "") -> str:
        """Retrieve string value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, str) else default

    def get_int(self, snapshot: SettingsSnapshot, path: str, default: int = 0) -> int:
        """Retrieve integer value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, int) and not isinstance(value, bool) else default

    def get_bool(self, snapshot: SettingsSnapshot, path: str, default: bool = False) -> bool:
        """Retrieve boolean value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, bool) else default

    def get_float(self, snapshot: SettingsSnapshot, path: str, default: float = 0.0) -> float:
        """Retrieve float value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, float) else default

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "SettingsRetrieverCapability()"
