"""Agent: Config feature orchestrator.

Coordinates configuration loading and access through the ConfigPort contract.
Exposes reload, metadata, and enhanced operations per FR-CFG requirements.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata, ConfigPath, ConfigValue

if TYPE_CHECKING:
    from .utility_config_loader import ApplicationConfigLoader

logger = logging.getLogger("BlenderMCPServer")


class ConfigOrchestrator:
    """Orchestrates configuration operations via ConfigPort."""

    def __init__(self, loader: ApplicationConfigLoader) -> None:  # type: ignore[name-defined]
        self._loader = loader

    def get(self, path: ConfigPath = "", default: ConfigValue = None) -> ConfigValue:
        """Get configuration value by dot-notation path."""
        return self._loader.get(path, default)

    def load(self) -> tuple[ConfigValue, ConfigMetadata]:
        """Load configuration from file and return snapshot with metadata."""
        return self._loader.load_config()

    def reload(self) -> tuple[ConfigValue, ConfigMetadata]:
        """Reload configuration atomically, replacing cached snapshot."""
        return self._loader.reload_config()

    def get_metadata(self) -> ConfigMetadata | None:
        """Retrieve configuration loading metadata (secrets excluded)."""
        return self._loader.get_metadata()

    def has(self, path: str) -> bool:
        """Check if a configuration key exists at the given path."""
        return self._loader.has(path)

    def get_string(self, path: str, default: str = "") -> str:
        """Retrieve a string configuration value."""
        return self._loader.get_string(path, default)

    def get_int(self, path: str, default: int = 0) -> int:
        """Retrieve an integer configuration value."""
        return self._loader.get_int(path, default)

    def get_bool(self, path: str, default: bool = False) -> bool:
        """Retrieve a boolean configuration value."""
        return self._loader.get_bool(path, default)

    def get_float(self, path: str, default: float = 0.0) -> float:
        """Retrieve a float configuration value."""
        return self._loader.get_float(path, default)

    def get_snapshot(self) -> ConfigValue:
        """Return an immutable/copy-protected configuration snapshot."""
        return self._loader.get_snapshot()
