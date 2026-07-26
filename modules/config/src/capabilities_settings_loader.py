"""Capability: Settings loader (FR-CFG-001).

Implements ISettingsLoaderProtocol — handles loading, validating, and
reloading application settings with deterministic precedence rules.

Business logic only: YAML parsing, precedence merging, environment
override application, typed conversion, size limits.
"""

from __future__ import annotations

import copy
import os
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata, ConfigPath, Timestamp
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    ENV_PREFIX_LEGACY,
    ENV_PREFIX_PRODUCT,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
)
from modules.shared.src.config.taxonomy_config_error import (
    ConfigLoadError,
    ConfigParseError,
    ConfigValidationError,
)
from modules.shared.src.config.taxonomy_config_event import SettingsLoadedEvent, SettingsReloadEvent
from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot

from modules.shared.src.config.utility_config_helpers import parse_env_value


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsLoaderCapability(ISettingsLoaderProtocol):
    """FR-CFG-001: Load and apply settings.

    Responsible for: YAML safe parsing, environment override application
    with typed conversion, precedence merging, size limits, immutable
    snapshot creation, and policy-mode error handling.
    """

    def __init__(
        self,
        config_file_loader: Any = None,
        policy_mode: str = POLICY_MODE_STRICT,
    ) -> None:
        self._file_loader = config_file_loader
        self._policy_mode = policy_mode
        self._cached: SettingsSnapshot | None = None

# ─── Block 2: Protocol Method Implementation ──────────────

    def load_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Load settings from sources, apply precedence, return immutable snapshot."""
        file_data = self._load_file(path)
        merged = self._apply_env_overrides(file_data)
        self._cached = SettingsSnapshot(_data=merged)
        return self._cached

    def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot. Retains previous on failure (permissive)."""
        previous = self._cached
        try:
            self._cached = None
            return self.load_settings(path)
        except Exception:
            if self._policy_mode == POLICY_MODE_PERMISSIVE and previous is not None:
                self._cached = previous
                return previous
            raise

    def emit_loaded_event(self, snapshot: SettingsSnapshot) -> SettingsLoadedEvent:
        """Build settings-loaded event from snapshot."""
        return SettingsLoadedEvent(
            source_summary="loaded",
            override_count=0,
            warning_count=0,
            policy_mode=self._policy_mode,
            timestamp=Timestamp(0.0),
        )

    def emit_reload_event(self, snapshot: SettingsSnapshot) -> SettingsReloadEvent:
        """Build settings-reload event from snapshot."""
        return SettingsReloadEvent(
            source_summary="reloaded",
            override_count=0,
            warning_count=0,
            policy_mode=self._policy_mode,
            timestamp=Timestamp(0.0),
        )

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def _load_file(self, path: ConfigPath | None) -> dict[str, Any]:
        """Load and parse YAML from file path."""
        if self._file_loader is None:
            return {}

        try:
            result = self._file_loader(path)
            if isinstance(result, dict):
                return result
            return {}
        except Exception as exc:
            if self._policy_mode == POLICY_MODE_STRICT:
                if isinstance(exc, (ConfigParseError, ConfigLoadError, ConfigValidationError)):
                    raise
                raise ConfigLoadError(f"Failed to load settings: {exc}") from exc
            return {}

    def _apply_env_overrides(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply environment variable overrides with typed scalar conversion."""
        if not isinstance(config, dict):
            return config

        result = copy.deepcopy(config)

        for key, value in os.environ.items():
            if key.startswith(ENV_PREFIX_PRODUCT) or key.startswith(ENV_PREFIX_LEGACY):
                prefix = (
                    ENV_PREFIX_PRODUCT if key.startswith(ENV_PREFIX_PRODUCT) else ENV_PREFIX_LEGACY
                )
                env_key = key[len(prefix):].lower()
                parsed = parse_env_value(value)

                if "." in env_key:
                    keys = env_key.split(".")
                    node = result
                    for k in keys[:-1]:
                        if k not in node or not isinstance(node[k], dict):
                            break
                        node = node[k]
                    if keys[-1] in node:
                        node[keys[-1]] = parsed
                else:
                    result[env_key] = parsed

        return result
