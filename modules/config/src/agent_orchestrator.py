"""Agent: Config feature orchestrator.

Coordinates configuration loading and access.
"""

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigPath, ConfigValue

logger = logging.getLogger("BlenderMCPServer")


class ConfigOrchestrator:
    """Orchestrates configuration operations."""

    def __init__(self, loader: Any):
        self._loader = loader

    def get(self, path: ConfigPath = "", default: ConfigValue = None) -> ConfigValue:
        """Get configuration value by dot-notation path."""
        return self._loader.get(path, default)

    def load(self) -> dict[str, ConfigValue]:
        """Load configuration from file."""
        return self._loader.load_config()
