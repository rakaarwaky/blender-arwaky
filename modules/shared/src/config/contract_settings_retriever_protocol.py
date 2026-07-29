"""Contract: Settings retriever protocol (FR-CFG-002).

Defines the inbound behavior interface for hierarchical dot-separated
settings value retrieval with safe copy semantics.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import ConfigPath
from .taxonomy_config_vo import SettingsSnapshot


class ISettingsRetrieverProtocol(ABC):
    """Protocol for retrieving settings values (FR-CFG-002)."""

    @abstractmethod
    def get_value(
        self,
        snapshot: SettingsSnapshot,
        path: ConfigPath,
        default: Any = None,
    ) -> Any:
        """Retrieve a value by dot-separated path. Returns deep copy to prevent mutation."""
        ...

    @abstractmethod
    def has_value(self, snapshot: SettingsSnapshot, path: ConfigPath) -> bool:
        """Check if a dot-separated path exists in the snapshot."""
        ...

    @abstractmethod
    def get_string(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: str = ""
    ) -> str:
        """Retrieve a string value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_int(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: int = 0
    ) -> int:
        """Retrieve an integer value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_bool(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: bool = False
    ) -> bool:
        """Retrieve a boolean value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_float(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: float = 0.0
    ) -> float:
        """Retrieve a float value. Returns default on type mismatch."""
        ...
