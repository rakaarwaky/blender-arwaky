"""Capability: Settings loader (FR-CFG-001).

Implements ISettingsLoaderProtocol — handles loading, validating, and
reloading application settings with deterministic precedence rules.

Business logic only: YAML parsing, precedence merging, environment
override application, schema validation, typed conversion, size limits,
runtime overrides, thread-safe single-load caching.
"""

from __future__ import annotations

import copy
import os
import threading
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ConfigMetadata,
    ConfigPath,
    OverrideCount,
    ParseWarning,
    SourceLocation,
    Timestamp,
    ValidationWarning,
)
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    DEFAULT_POLICY_MODE,
    DEFAULT_SETTINGS,
    ENV_PREFIX_PRODUCT,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    RESERVED_ENV_KEYS,
    SETTINGS_SCHEMA,
)
from modules.shared.src.config.taxonomy_config_error import (
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigValidationError,
)
from modules.shared.src.config.taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
)
from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot
from modules.shared.src.config.utility_config_helpers import (
    apply_env_overrides,
    deep_merge_dicts,
    load_yaml_safe,
    resolve_default_config_path,
    set_nested_value,
    validate_settings_schema,
)

ConfigFileLoader = Any  # Callable[[ConfigPath], dict[str, Any]]


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsLoaderCapability(ISettingsLoaderProtocol):
    """FR-CFG-001: Load and apply settings.

    Responsible for: YAML safe parsing, environment override application
    with typed conversion, precedence merging, schema validation, size
    limits, runtime overrides, immutable snapshot creation, policy-mode
    error handling, and thread-safe single-load caching.
    """

    def __init__(
        self,
        config_file_loader: ConfigFileLoader | None = None,
        policy_mode: str = DEFAULT_POLICY_MODE,
        defaults: Mapping[str, Any] | None = None,
        schema: Mapping[str, Any] | None = None,
        config_v2_enabled: bool = False,
    ) -> None:
        self._file_loader = config_file_loader or load_yaml_safe
        self._policy_mode = policy_mode
        self._defaults = dict(defaults) if defaults is not None else copy.deepcopy(DEFAULT_SETTINGS)
        self._schema = dict(schema) if schema is not None else copy.deepcopy(SETTINGS_SCHEMA)
        self._config_v2_enabled = config_v2_enabled
        self._lock = threading.Lock()
        # cached state
        self._cached: SettingsSnapshot | None = None
        self._cached_data: dict[str, Any] | None = None
        self._last_metadata: ConfigMetadata = ConfigMetadata()

# ─── Block 2: Protocol Method Implementation ──────────────

    def load_settings(
        self,
        path: ConfigPath | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> SettingsSnapshot:
        """Load settings from sources, apply precedence, validate, return immutable snapshot."""
        with self._lock:
            # Single-load guarantee (Q19): identical cached snapshot returned.
            if overrides is None and path is None and self._cached is not None:
                return self._cached

            if path is not None or self._cached is None:
                merged, filedata, metadata = self._build_core(path)
                self._cached_data = filedata
                self._cached = SettingsSnapshot(_data=merged)
                self._last_metadata = metadata

            # Runtime overrides are caller-scoped — never cached (A5).
            if overrides is not None and self._config_v2_enabled:
                structured: dict[str, Any] = {}
                for dotted_key, value in overrides.items():
                    segments = tuple(dotted_key.split("."))
                    set_nested_value(structured, segments, value)
                final = deep_merge_dicts(self._cached_data, structured)
                return SettingsSnapshot(_data=final)

            if overrides is not None and not self._config_v2_enabled:
                self._last_metadata = ConfigMetadata(
                    source=self._last_metadata.source,
                    exists=self._last_metadata.exists,
                    overrides=self._last_metadata.overrides,
                    parse_warnings=(
                        *self._last_metadata.parse_warnings,
                        ParseWarning("runtime overrides ignored; BLENDERMCP_CONFIG_V2 off"),
                    ),
                    validation_warnings=self._last_metadata.validation_warnings,
                )

            return self._cached

    def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot. Retains previous on failure (permissive)."""
        with self._lock:
            try:
                merged, filedata, metadata = self._build_core(path)
                # build-then-swap = atomic; never set cache to None before build
                self._cached_data = filedata
                self._cached = SettingsSnapshot(_data=merged)
                self._last_metadata = metadata
                return self._cached
            except Exception:
                if self._policy_mode == POLICY_MODE_PERMISSIVE and self._cached is not None:
                    return self._cached
                raise

    def get_last_metadata(self) -> ConfigMetadata:
        """Return metadata from the most recent successful load."""
        return self._last_metadata

    def emit_loaded_event(self) -> SettingsLoadedEvent:
        """Build a settings-loaded event from the most recent load metadata."""
        metadata = self._last_metadata
        return SettingsLoadedEvent(
            source_summary=str(metadata.source) if metadata.source is not None else "",
            override_count=int(metadata.overrides),
            warning_count=len(metadata.parse_warnings) + len(metadata.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

    def emit_reload_event(self) -> SettingsReloadEvent:
        """Build a settings-reload event from the most recent load metadata."""
        metadata = self._last_metadata
        return SettingsReloadEvent(
            source_summary=str(metadata.source) if metadata.source is not None else "",
            override_count=int(metadata.overrides),
            warning_count=len(metadata.parse_warnings) + len(metadata.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

    def emit_validation_warning_event(self) -> SettingsValidationWarningEvent | None:
        """Return warning event iff permissive mode and validation warnings exist."""
        if self._policy_mode != POLICY_MODE_PERMISSIVE:
            return None
        metadata = self._last_metadata
        if not metadata.validation_warnings:
            return None
        return SettingsValidationWarningEvent(
            source_summary=str(metadata.source) if metadata.source is not None else "",
            override_count=int(metadata.overrides),
            warning_count=len(metadata.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

# ─── Block 3: Core Build ───────────────────────────────────

    def _build_core(
        self, path: ConfigPath | None
    ) -> tuple[dict[str, Any], dict[str, Any], ConfigMetadata]:
        """Build merged settings + raw file data + metadata.

        Returns (merged, filedata, metadata). ``filedata`` is what gets cached
        (used as base for caller-scoped runtime overrides).
        """
        resolved = resolve_default_config_path(path)
        p = Path(str(resolved))

        parse_warnings: list[ParseWarning] = []
        file_data: dict[str, Any] = {}

        # Directory path
        if p.is_dir():
            if self._policy_mode == POLICY_MODE_STRICT:
                raise ConfigPathError(f"{resolved} is a directory")
            parse_warnings.append(ParseWarning(f"{resolved} is a directory; using defaults"))
        elif not p.is_file():
            # Missing file: never fatal in any mode (Q6).
            parse_warnings.append(
                ParseWarning(f"settings file not found: {resolved}; using defaults")
            )
        else:
            # Size limit (flag-gated)
            if self._config_v2_enabled and p.stat().st_size > MAX_CONFIG_SIZE_BYTES:
                if self._policy_mode == POLICY_MODE_STRICT:
                    raise ConfigLoadError(
                        f"settings file too large: {resolved} exceeds {MAX_CONFIG_SIZE_BYTES} bytes"
                    )
                parse_warnings.append(ParseWarning(f"settings file too large: {resolved}; skipped"))
            else:
                try:
                    file_data = self._file_loader(ConfigPath(str(p)))
                except (ConfigParseError, ConfigLoadError, ConfigValidationError):
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise
                    parse_warnings.append(
                        ParseWarning(f"failed to parse {resolved}; using defaults")
                    )
                    file_data = {}
                except Exception as exc:
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise ConfigLoadError(f"Failed to load settings: {exc}") from exc
                    parse_warnings.append(
                        ParseWarning(f"failed to load {resolved}; using defaults")
                    )
                    file_data = {}

        # Merge precedence: defaults < file < env
        merged = deep_merge_dicts(dict(self._defaults), file_data)
        merged, env_count = apply_env_overrides(
            merged, os.environ, ENV_PREFIX_PRODUCT, RESERVED_ENV_KEYS
        )

        # Schema (flag-gated)
        validation_warnings: list[ValidationWarning] = []
        if self._config_v2_enabled:
            errors, warnings = validate_settings_schema(merged, self._schema)
            if errors and self._policy_mode == POLICY_MODE_STRICT:
                raise ConfigValidationError("; ".join(errors))
            validation_warnings.extend(warnings)
            validation_warnings.extend(errors)

        metadata = ConfigMetadata(
            source=SourceLocation(str(resolved)),
            exists=p.is_file(),
            overrides=OverrideCount(env_count),
            parse_warnings=tuple(parse_warnings),
            validation_warnings=tuple(validation_warnings),
        )
        return merged, file_data, metadata
