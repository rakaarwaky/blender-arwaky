"""Config domain contract: configuration port interface.

Defines the contract for loading and accessing application configuration.
AES Port layer — depends only on taxonomy entities.

FR-CFG-005: Configuration Access Contract
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ConfigPath, ConfigValue


class ConfigPort(ABC):
    """Port interface for accessing application configuration (FR-CFG-005).

    Implementations must be stateless or thread-safe.
    Implementations must not expose mutable internal configuration state.
    """

    @abstractmethod
    def get(self, path: ConfigPath, default: ConfigValue = None) -> ConfigValue:
        """Get a config value by dot-notation path (e.g. 'server.port')."""
        pass

    # Optional contract methods (FR-CFG-005)
    def has(self, path: str) -> bool:
        """Check if a configuration key exists at the given path.

        Default implementation returns False. Override for existence checking.
        """
        return False

    def get_string(self, path: str, default: str = "") -> str:
        """Retrieve a string configuration value."""
        value = self.get(path, default)
        return value if isinstance(value, str) else default

    def get_int(self, path: str, default: int = 0) -> int:
        """Retrieve an integer configuration value."""
        value = self.get(path, default)
        return value if isinstance(value, int) and not isinstance(value, bool) else default

    def get_bool(self, path: str, default: bool = False) -> bool:
        """Retrieve a boolean configuration value."""
        value = self.get(path, default)
        return value if isinstance(value, bool) else default

    def get_float(self, path: str, default: float = 0.0) -> float:
        """Retrieve a float configuration value."""
        value = self.get(path, default)
        return value if isinstance(value, float) else default
