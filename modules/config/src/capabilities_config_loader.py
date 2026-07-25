"""Capability: Configuration loader.

Implements ConfigLoaderProtocol — handles loading, validating, and reloading
application settings through the utility layer's ApplicationConfigLoader.
"""

from __future__ import annotations

import logging

from modules.shared.src.config.contract_config_loader_protocol import ConfigLoaderProtocol

logger = logging.getLogger("BlenderMCPServer")


class ConfigLoaderCapability(ConfigLoaderProtocol):
    """Business logic for configuration loading and validation."""

    def __init__(self, config_loader: object) -> None:
        """Initialize with a config loader from the utility layer.

        Args:
            config_loader: A callable or utility capability that loads YAML-based
                application configuration.
        """
        self._config_loader = config_loader

    async def load_settings(self, path: str | None = None) -> dict:
        """Load and validate settings from file or default locations.

        FR-CFG-001: Applies strict precedence order (explicit path > env overrides >
        project file > user directory > built-in defaults).
        Parses safely without code execution.
        Returns settings snapshot with metadata (secrets redacted).

        Args:
            path: Optional explicit configuration file path.

        Returns:
            Dictionary with success status, settings snapshot, and metadata.
        """
        logger.info("Loading settings (path=%s)...", path)

        try:
            result = self._config_loader.load_config(path)
            if isinstance(result, dict):
                return result
            return {
                "success": True,
                "settings": result,
                "metadata": {},
                "message": "Settings loaded successfully",
            }
        except Exception as e:
            logger.error("Load settings failed: %s", e)
            return {
                "success": False,
                "settings": None,
                "metadata": {},
                "message": f"Failed to load settings: {e}",
            }

    async def reload_settings(self, path: str | None = None) -> dict:
        """Clear cache and reload settings from file.

        FR-CFG-001: Atomically replaces cached settings.
        Previous valid settings are retained if reload fails.
        Returns updated snapshot with metadata.

        Args:
            path: Optional explicit configuration file path.

        Returns:
            Dictionary with success status, settings snapshot, and metadata.
        """
        logger.info("Reloading settings (path=%s)...", path)

        try:
            result = self._config_loader.reload_config(path)
            if isinstance(result, dict):
                return result
            return {
                "success": True,
                "settings": result,
                "metadata": {},
                "message": "Settings reloaded successfully",
            }
        except Exception as e:
            logger.error("Reload settings failed: %s", e)
            return {
                "success": False,
                "settings": None,
                "metadata": {},
                "message": f"Failed to reload settings: {e}",
            }

    async def resolve_project_root(self) -> dict:
        """Resolve the project root directory using precedence rules.

        FR-CFG-003: Searches upward for project markers (settings file, manifest,
        version control metadata). Falls back to user config or CWD.
        Returns normalized absolute path and resolution method used.

        Returns:
            Dictionary with success status, resolved path, and message.
        """
        logger.info("Resolving project root...")

        try:
            result = self._config_loader.resolve_project_root()
            if isinstance(result, dict):
                return result
            return {
                "success": True,
                "path": result,
                "message": f"Project root resolved: {result}",
            }
        except Exception as e:
            logger.error("Resolve project root failed: %s", e)
            return {
                "success": False,
                "path": None,
                "message": f"Failed to resolve project root: {e}",
            }
