"""Config domain: contracts, errors, events, VOs, constants, utilities for configuration management."""

from __future__ import annotations

# ─── Taxonomy Module Barrel Exports ────────────────────────
from . import taxonomy_config_constant, taxonomy_config_error, taxonomy_config_event, taxonomy_config_vo

# ─── Contracts (Protocols) ─────────────────────────────────────
from .contract_config_aggregate import IConfigAggregate
from .contract_redaction_rules_protocol import IRedactionRulesProtocol
from .contract_settings_loader_protocol import ISettingsLoaderProtocol
from .contract_settings_metadata_protocol import ISettingsMetadataProtocol
from .contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from .contract_workspace_resolver_protocol import IWorkspaceResolverProtocol

# ─── Taxonomy: Constants ───────────────────────────────────────
from .taxonomy_config_constant import (
    CONFIG_PATH_ENV,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_POLICY_MODE,
    DEFAULT_SETTINGS,
    ENV_PREFIX_PRODUCT,
    EVENT_RING_BUFFER_SIZE,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    PROJECT_MARKERS,
    REDACTION_PLACEHOLDER,
    RESERVED_ENV_KEYS,
    SENSITIVE_KEY_PATTERNS,
    SETTINGS_SCHEMA,
    STRICT_MODE_FLAG_ENV,
    WORKSPACE_ROOT_ENV,
)

# ─── Taxonomy: Errors ──────────────────────────────────────────
from .taxonomy_config_error import (
    ConfigError,
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigRootResolutionError,
    ConfigTypeError,
    ConfigValidationError,
)

# ─── Taxonomy: Events ──────────────────────────────────────────
from .taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
    WorkspaceResolvedEvent,
)

# ─── Taxonomy: Value Objects ───────────────────────────────────
from .taxonomy_config_vo import (
    RedactionRule,
    SettingsSnapshot,
    WorkspacePath,
)

# ─── Utility ───────────────────────────────────────────────────
from .utility_config_helpers import parse_env_value, search_project_root

__all__ = [
    "IConfigAggregate",
    "ISettingsLoaderProtocol",
    "ISettingsRetrieverProtocol",
    "IWorkspaceResolverProtocol",
    "ISettingsMetadataProtocol",
    "IRedactionRulesProtocol",
    "SettingsSnapshot",
    "WorkspacePath",
    "RedactionRule",
    "SettingsLoadedEvent",
    "SettingsReloadEvent",
    "WorkspaceResolvedEvent",
    "SettingsValidationWarningEvent",
    "SENSITIVE_KEY_PATTERNS",
    "PROJECT_MARKERS",
    "MAX_CONFIG_SIZE_BYTES",
    "ENV_PREFIX_PRODUCT",
    "CONFIG_PATH_ENV",
    "STRICT_MODE_FLAG_ENV",
    "WORKSPACE_ROOT_ENV",
    "DEFAULT_CONFIG_FILENAME",
    "RESERVED_ENV_KEYS",
    "EVENT_RING_BUFFER_SIZE",
    "DEFAULT_SETTINGS",
    "SETTINGS_SCHEMA",
    "REDACTION_PLACEHOLDER",
    "POLICY_MODE_STRICT",
    "POLICY_MODE_PERMISSIVE",
    "DEFAULT_POLICY_MODE",
    "parse_env_value",
    "search_project_root",
    "ConfigError",
    "ConfigLoadError",
    "ConfigParseError",
    "ConfigPathError",
    "ConfigRootResolutionError",
    "ConfigTypeError",
    "ConfigValidationError",
]
