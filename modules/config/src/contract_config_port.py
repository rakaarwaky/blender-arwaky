"""
Contract: Port interface for application configuration.

Defines the contract for loading configuration values (YAML, env, etc.).
AES Port layer — depends only on taxonomy entities.
"""

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ConfigPath, ConfigValue


class ConfigPort(ABC):
    """Port interface for accessing application configuration."""

    @abstractmethod
    def get(self, path: ConfigPath, default: ConfigValue = None) -> ConfigValue:
        """Get a config value by dot-notation path (e.g. 'blender.host')."""
        pass
