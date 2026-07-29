"""Config domain contract: config getter protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-CFG-002: Retrieve configuration values for cache and settings.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_config_vo import SettingsSnapshot as _SettingsSnapshot  # AES202: mandatory taxonomy import


class ConfigGetterProtocol(ABC):
    """Protocol for retrieving configuration values.

    Capability uses this to read cache location, settings,
    and other configuration parameters.
    """

    @abstractmethod
    def get(self, key: str, default: str | None = None) -> str | None:
        """Retrieve a configuration value by key."""
        ...
