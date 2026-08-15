"""Contract: Settings retriever protocol (FR-CFG-002)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ConfigPath
from .taxonomy_config_vo import (
    DEFAULT_CONFIG_FLOAT,
    DEFAULT_CONFIG_INT,
    DEFAULT_CONFIG_STRING,
    ConfigFloatValue,
    ConfigIntValue,
    ConfigStringValue,
    SettingsSnapshot,
    SettingsValue,
)


class ISettingsRetrieverProtocol(ABC):
    """Protocol for retrieving settings values (FR-CFG-002)."""

    @abstractmethod
    def get_value(
        self,
        snapshot: SettingsSnapshot,
        path: ConfigPath,
        default: SettingsValue = None,
    ) -> SettingsValue:
        """Retrieve a value by dot-separated path."""
        ...

    @abstractmethod
    def has_value(self, snapshot: SettingsSnapshot, path: ConfigPath) -> bool:
        """Check if a dot-separated path exists in the snapshot."""
        ...

    @abstractmethod
    def get_string(
        self,
        snapshot: SettingsSnapshot,
        path: ConfigPath,
        default: ConfigStringValue = DEFAULT_CONFIG_STRING,
    ) -> ConfigStringValue:
        """Retrieve a string value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_int(
        self,
        snapshot: SettingsSnapshot,
        path: ConfigPath,
        default: ConfigIntValue = DEFAULT_CONFIG_INT,
    ) -> ConfigIntValue:
        """Retrieve an integer value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_bool(self, snapshot: SettingsSnapshot, path: ConfigPath, default: bool = False) -> bool:
        """Retrieve a boolean value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_float(
        self,
        snapshot: SettingsSnapshot,
        path: ConfigPath,
        default: ConfigFloatValue = DEFAULT_CONFIG_FLOAT,
    ) -> ConfigFloatValue:
        """Retrieve a float value. Returns default on type mismatch."""
        ...
