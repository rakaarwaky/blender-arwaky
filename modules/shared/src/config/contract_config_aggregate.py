"""Contract: Config aggregate facade.

Unified interface for the config feature consumed by the Surface layer.
Combines settings loading, retrieval, workspace resolution, metadata, and
redaction into a single entry point.

Implemented by Agent layer (ConfigOrchestrator).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from .taxonomy_config_constant import EVENT_RING_BUFFER_SIZE
from .taxonomy_config_vo import RedactionRule, SettingsSnapshot, WorkspacePath


class IConfigAggregate(ABC):
    """Aggregate facade for the config feature.

    Surface layer delegates all config operations through this interface.
    """

    # ─── Lifecycle ──────────────────────────────────────────────

    @abstractmethod
    def load(
        self,
        path: ConfigPath | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> SettingsSnapshot:
        """Load settings and return immutable snapshot."""
        ...

    @abstractmethod
    def reload(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached settings snapshot."""
        ...

    @abstractmethod
    def get_snapshot(self) -> SettingsSnapshot:
        """Return current cached settings snapshot (lazy-loads if needed)."""
        ...

    # ─── Retrieval (FR-CFG-002) ────────────────────────────────

    @abstractmethod
    def get(self, path: ConfigPath = "", default: Any = None) -> Any:
        """Retrieve value by dot-separated path from current snapshot."""
        ...

    @abstractmethod
    def has(self, path: ConfigPath) -> bool:
        """Check if a dot-separated path exists in the current snapshot."""
        ...

    @abstractmethod
    def get_string(self, path: ConfigPath, default: str = "") -> str:
        """Retrieve string value."""
        ...

    @abstractmethod
    def get_int(self, path: ConfigPath, default: int = 0) -> int:
        """Retrieve integer value."""
        ...

    @abstractmethod
    def get_bool(self, path: ConfigPath, default: bool = False) -> bool:
        """Retrieve boolean value."""
        ...

    @abstractmethod
    def get_float(self, path: ConfigPath, default: float = 0.0) -> float:
        """Retrieve float value."""
        ...

    # ─── Workspace (FR-CFG-003) ────────────────────────────────

    @abstractmethod
    def resolve_workspace(self) -> WorkspacePath:
        """Resolve project workspace directory."""
        ...

    # ─── Metadata (FR-CFG-004) ────────────────────────────────

    @abstractmethod
    def get_metadata(self) -> ConfigMetadata | None:
        """Return settings loading metadata (secrets excluded)."""
        ...

    # ─── Events (T-09) ─────────────────────────────────────────

    @abstractmethod
    def recent_events(self, limit: int = EVENT_RING_BUFFER_SIZE) -> tuple[dict[str, Any], ...]:
        """Return recent config domain events, oldest → newest."""
        ...

    # ─── Redaction (FR-CFG-005) ────────────────────────────────

    @abstractmethod
    def get_redaction_rule(self) -> RedactionRule:
        """Return authoritative redaction rule."""
        ...

    @abstractmethod
    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively redact sensitive values in a dictionary."""
        ...
