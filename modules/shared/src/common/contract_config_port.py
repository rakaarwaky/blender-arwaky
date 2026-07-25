"""Common contract: application configuration port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_core_vo import ConfigPath, ConfigValue


class ContractConfigPort(ABC):
    """Port interface for accessing application configuration."""

    @abstractmethod
    def get(self, path: ConfigPath, default: ConfigValue = None) -> ConfigValue:
        """Get a config value by dot-notation path (e.g. 'blender.host')."""
        pass
