"""Capability: Settings loader (FR-CFG-001).

Implements ISettingsLoaderProtocol — handles loading, validating, and
reloading application settings with deterministic precedence rules.

Business logic only: YAML parsing, precedence merging, environment
override application, schema validation, typed conversion, size limits,
runtime overrides, thread-safe single-load caching.
"""

from __future__ import annotations

import contextlib
import copy
import os
import tempfile
import threading
import time
from pathlib import Path

import yaml

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
from modules.shared.src.config.taxonomy_config_vo import (
    ConfigFileLoader,
    SettingsData,
    SettingsOverrides,
    SettingsSchema,
    SettingsSnapshot,
    SettingsValue,
)
from modules.shared.src.config.utility_config_helpers import (
    apply_env_overrides,
    deep_merge_dicts,
    load_yaml_safe,
    resolve_default_config_path,
    set_nested_value,
    validate_settings_schema,
)

# ─── Module-Level Constants ────────────────────────────────
# Cached defaults and schema copies to avoid per-instantiation deepcopy overhead.
# Thread-safety: CPython's GIL makes dict assignment atomic. Under concurrent
# first-access, one extra deepcopy may execute — benign since the result is
# identical. On non-CPython interpreters, add a threading.Lock if needed.
_DEFAULTS_CACHE: SettingsOverrides | None = None
_SCHEMA_CACHE: SettingsSchema | None = None


def _get_defaults_cache() -> SettingsOverrides:
    """Return a cached deep copy of DEFAULT_SETTINGS, creating it once."""
    global _DEFAULTS_CACHE
    if _DEFAULTS_CACHE is None:
        _DEFAULTS_CACHE = copy.deepcopy(DEFAULT_SETTINGS)
    return dict(_DEFAULTS_CACHE)


def _get_schema_cache() -> SettingsSchema:
    """Return a cached deep copy of SETTINGS_SCHEMA, creating it once."""
    global _SCHEMA_CACHE
    if _SCHEMA_CACHE is None:
        _SCHEMA_CACHE = copy.deepcopy(SETTINGS_SCHEMA)
    return dict(_SCHEMA_CACHE)


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
        defaults: SettingsOverrides | None = None,
        schema: SettingsSchema | None = None,
        strict_mode_enabled: bool = False,
    ) -> None:
        self._file_loader = config_file_loader or load_yaml_safe
        self._policy_mode = policy_mode
        # Use cached copies when no custom defaults/schema provided (Finding #2/#14)
        self._defaults = dict(defaults) if defaults is not None else _get_defaults_cache()
        self._schema = dict(schema) if schema is not None else _get_schema_cache()
        self._strict_mode_enabled = strict_mode_enabled
        self._lock = threading.Lock()
        # cached state
        self._cached: SettingsSnapshot | None = None
        self._cached_data: SettingsData | None = None
        self._last_metadata: ConfigMetadata = ConfigMetadata()

    # ─── Block 2: Protocol Method Implementation ──────────────

    def load_settings(
        self,
        path: ConfigPath | None = None,
        overrides: SettingsOverrides | None = None,
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

            # FR-CFG-001 precedence: runtime overrides > environment > file > built-in defaults
            # Overrides are applied unconditionally (independent of strict mode) and
            # the enriched snapshot is cached so get_snapshot() stays consistent.
            if overrides is not None:
                base = self._cached.to_dict() if self._cached is not None else {}
                structured: SettingsData = {}
                for dotted_key, value in overrides.items():
                    segments = tuple(dotted_key.split("."))
                    set_nested_value(structured, segments, value)
                final = deep_merge_dicts(base, structured)
                self._cached = SettingsSnapshot(_data=final)

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
            except (ConfigLoadError, ConfigParseError, ConfigValidationError):
                if self._policy_mode == POLICY_MODE_PERMISSIVE and self._cached is not None:
                    return self._cached
                raise

    def set_value(
        self,
        path: ConfigPath,
        value: SettingsValue,
        config_path: ConfigPath | None = None,
    ) -> SettingsSnapshot:
        """Validate and atomically persist one typed dotted-path setting."""
        segments = tuple(str(path).split(".")) if str(path) else ()
        if not segments or any(not segment for segment in segments):
            raise ConfigPathError("Configuration key must be a non-empty dotted path")

        target = Path(str(resolve_default_config_path(config_path)))
        with self._lock:
            if target.is_file():
                base = load_yaml_safe(ConfigPath(str(target)))
            else:
                base = copy.deepcopy(self._cached_data or _get_defaults_cache())
            set_nested_value(base, segments, value)
            errors, _warnings = validate_settings_schema(base, self._schema)
            if errors:
                raise ConfigValidationError("; ".join(errors))

            target.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(dir=str(target.parent), suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as handle:
                    yaml.safe_dump(base, handle, sort_keys=True)
                    handle.flush()
                    os.fsync(handle.fileno())
                os.replace(temporary, target)
            except BaseException:
                with contextlib.suppress(OSError):
                    os.unlink(temporary)
                raise

            merged, filedata, metadata = self._build_core(ConfigPath(str(target)))
            self._cached_data = filedata
            self._cached = SettingsSnapshot(_data=merged)
            self._last_metadata = metadata
            return self._cached

    def get_last_metadata(self) -> ConfigMetadata:
        """Return metadata from the most recent successful load."""
        return self._last_metadata

    def _build_event(self, cls: type, metadata: ConfigMetadata | None = None) -> object:
        """Build an event dataclass from load metadata."""
        md = metadata or self._last_metadata
        return cls(
            source_summary=str(md.source) if md.source is not None else "",
            override_count=int(md.overrides),
            warning_count=len(md.parse_warnings) + len(md.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

    def emit_loaded_event(self) -> SettingsLoadedEvent:
        """Build a settings-loaded event from the most recent load metadata."""
        return self._build_event(SettingsLoadedEvent)

    def emit_reload_event(self) -> SettingsReloadEvent:
        """Build a settings-reload event from the most recent load metadata."""
        return self._build_event(SettingsReloadEvent)

    def emit_validation_warning_event(self) -> SettingsValidationWarningEvent | None:
        """Return warning event iff permissive mode and validation warnings exist."""
        if self._policy_mode != POLICY_MODE_PERMISSIVE:
            return None
        if not self._last_metadata.validation_warnings:
            return None
        md = self._last_metadata
        return SettingsValidationWarningEvent(
            source_summary=str(md.source) if md.source is not None else "",
            override_count=int(md.overrides),
            warning_count=len(md.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

    # ─── Block 3: Core Build ───────────────────────────────────

    def _build_core(self, path: ConfigPath | None) -> tuple[SettingsData, SettingsData, ConfigMetadata]:
        """Build merged settings + raw file data + metadata.

        Returns (merged, filedata, metadata). ``filedata`` is what gets cached
        (used as base for caller-scoped runtime overrides).
        """
        resolved = resolve_default_config_path(path)
        p = Path(str(resolved))

        parse_warnings: list[ParseWarning] = []
        file_data: SettingsData = {}

        # Directory path
        if p.is_dir():
            if self._policy_mode == POLICY_MODE_STRICT:
                raise ConfigPathError(f"{resolved} is a directory")
            parse_warnings.append(ParseWarning(f"{resolved} is a directory; using defaults"))
        elif not p.is_file():
            # Missing file: never fatal (Q6).
            parse_warnings.append(ParseWarning(f"settings file not found: {resolved}; using defaults"))
        else:
            # Size limit (strict-mode gated)
            # FR-CFG-001: Size limit gated by BLENDERMCP_STRICT flag.
            # When flag is off, size limit is not enforced regardless of policy mode.
            # When flag is on: strict → ConfigError; permissive → warning + skip.
            if self._strict_mode_enabled and p.stat().st_size > MAX_CONFIG_SIZE_BYTES:
                if self._policy_mode == POLICY_MODE_STRICT:
                    raise ConfigLoadError(f"settings file too large: {resolved} exceeds {MAX_CONFIG_SIZE_BYTES} bytes")
                parse_warnings.append(ParseWarning(f"settings file too large: {resolved}; skipped"))
            else:
                try:
                    file_data = self._file_loader(ConfigPath(str(p)))
                except (ConfigParseError, ConfigLoadError, ConfigValidationError):
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise
                    parse_warnings.append(ParseWarning(f"failed to parse {resolved}; using defaults"))
                    file_data = {}
                except (UnicodeDecodeError, OSError) as exc:
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise ConfigLoadError(f"Failed to load settings: {exc}") from exc
                    parse_warnings.append(ParseWarning(f"failed to load {resolved}; using defaults"))
                    file_data = {}

        # Merge precedence: defaults < file < env
        merged = deep_merge_dicts(dict(self._defaults), file_data)
        merged, env_count = apply_env_overrides(merged, os.environ, ENV_PREFIX_PRODUCT, RESERVED_ENV_KEYS)

        # Schema (strict-mode gated)
        validation_warnings: list[ValidationWarning] = []
        if self._strict_mode_enabled:
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
