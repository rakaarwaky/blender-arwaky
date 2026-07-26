"""Config domain: contracts, errors, events, VOs, constants for configuration management."""

from __future__ import annotations

# ─── Contracts (Protocols) ─────────────────────────────────────
from .contract_config_aggregate import IConfigAggregate
from .contract_redaction_rules_protocol import IRedactionRulesProtocol
from .contract_settings_loader_protocol import ISettingsLoaderProtocol
from .contract_settings_metadata_protocol import ISettingsMetadataProtocol
from .contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from .contract_workspace_resolver_protocol import IWorkspaceResolverProtocol

# ─── Taxonomy: Value Objects ───────────────────────────────────
from .taxonomy_config_vo import (
    RedactionRule,
    SensitiveKeyPattern,
    SettingsSnapshot,
    WorkspacePath,
)

# ─── Taxonomy: Events ──────────────────────────────────────────
from .taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
    WorkspaceResolvedEvent,
)

# ─── Taxonomy: Constants ───────────────────────────────────────
from .taxonomy_config_constant import (
    DEFAULT_POLICY_MODE,
    ENV_PREFIX_LEGACY,
    ENV_PREFIX_PRODUCT,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    PROJECT_MARKERS,
    REDACTION_PLACEHOLDER,
    SENSITIVE_KEY_PATTERNS,
)

# ─── Taxonomy: Errors ──────────────────────────────────────────
from .taxonomy_config_error import (
    ConfigError,
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigProviderError,
    ConfigRootResolutionError,
    ConfigTypeError,
    ConfigValidationError,
)

__all__ = [
    # Contracts — Protocols
    "IConfigAggregate",
    "ISettingsLoaderProtocol",
    "ISettingsRetrieverProtocol",
    "IWorkspaceResolverProtocol",
    "ISettingsMetadataProtocol",
    "IRedactionRulesProtocol",
    # Taxonomy — Value Objects
    "SettingsSnapshot",
    "WorkspacePath",
    "RedactionRule",
    "SensitiveKeyPattern",
    # Taxonomy — Events
    "SettingsLoadedEvent",
    "SettingsReloadEvent",
    "WorkspaceResolvedEvent",
    "SettingsValidationWarningEvent",
    # Taxonomy — Constants
    "SENSITIVE_KEY_PATTERNS",
    "PROJECT_MARKERS",
    "MAX_CONFIG_SIZE_BYTES",
    "ENV_PREFIX_PRODUCT",
    "ENV_PREFIX_LEGACY",
    "REDACTION_PLACEHOLDER",
    "POLICY_MODE_STRICT",
    "POLICY_MODE_PERMISSIVE",
    "DEFAULT_POLICY_MODE",
    # Taxonomy — Errors
    "ConfigError",
    "ConfigLoadError",
    "ConfigParseError",
    "ConfigPathError",
    "ConfigProviderError",
    "ConfigRootResolutionError",
    "ConfigTypeError",
    "ConfigValidationError",
]
