"""Config domain contract: configuration loading protocol (ABC based).

Defines the protocol for loading, validating, and reloading application settings.

FR-CFG-001: Load and Apply Settings
FR-CFG-003: Resolve Project Workspace Directory
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ConfigPath, ConfigValue


class ConfigLoaderProtocol(ABC):
    """Protocol for loading and validating application configuration."""

    @abstractmethod
    async def load_settings(self, path: str | None = None) -> dict:
        """Load and validate settings from file or default locations.

        FR-CFG-001: Applies strict precedence order (explicit path > env overrides >
        project file > user directory > built-in defaults).
        Parses safely without code execution.
        Returns settings snapshot with metadata (secrets redacted).
        """
        pass

    @abstractmethod
    async def reload_settings(self, path: str | None = None) -> dict:
        """Clear cache and reload settings from file.

        FR-CFG-001: Atomically replaces cached settings.
        Previous valid settings are retained if reload fails.
        Returns updated snapshot with metadata.
        """
        pass

    @abstractmethod
    async def resolve_project_root(self) -> dict:
        """Resolve the project root directory using precedence rules.

        FR-CFG-003: Searches upward for project markers (settings file, manifest,
        version control metadata). Falls back to user config or CWD.
        Returns normalized absolute path and resolution method used.
        """
        pass
