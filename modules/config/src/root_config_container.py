"""Root: Config feature DI container.

Wires capabilities to contract protocols and bootstraps the config feature.
Single composition root for the config module.
"""

from __future__ import annotations

import os

from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    CONFIG_V2_FLAG_ENV,
    DEFAULT_POLICY_MODE,
)
from modules.shared.src.config.utility_config_helpers import (
    load_yaml_safe,
    parse_env_value,
    resolve_default_config_path,
)

from .agent_config_orchestrator import ConfigOrchestrator
from .capabilities_redaction_rules import RedactionRulesCapability
from .capabilities_settings_loader import SettingsLoaderCapability
from .capabilities_settings_metadata import SettingsMetadataCapability
from .capabilities_settings_retriever import SettingsRetrieverCapability
from .capabilities_workspace_resolver import WorkspaceResolverCapability


class ConfigContainer:
    """DI container for the config feature.

    Wires capabilities to protocol interfaces and constructs the
    IConfigAggregate facade (ConfigOrchestrator).
    """

    def __init__(
        self,
        config_file_loader: object | None = None,
        policy_mode: str = DEFAULT_POLICY_MODE,
        explicit_workspace: str | None = None,
        extra_redaction_patterns: tuple[str, ...] = (),
        config_v2_enabled: bool | None = None,
    ) -> None:
        # Flag read once at construction (None → resolve via env truthiness).
        if config_v2_enabled is None:
            v2 = parse_env_value(os.environ.get(CONFIG_V2_FLAG_ENV, ""))
            config_v2_enabled = v2 is True
        else:
            config_v2_enabled = bool(config_v2_enabled)

        default_config_path = resolve_default_config_path(None)

        self._loader: ISettingsLoaderProtocol = SettingsLoaderCapability(
            config_file_loader=config_file_loader or load_yaml_safe,
            policy_mode=policy_mode,
            config_v2_enabled=config_v2_enabled,
        )
        self._retriever: ISettingsRetrieverProtocol = SettingsRetrieverCapability(
            policy_mode=policy_mode,
            escape_enabled=config_v2_enabled,
        )
        self._workspace_resolver: IWorkspaceResolverProtocol = WorkspaceResolverCapability(
            explicit_override=explicit_workspace,
            config_path=default_config_path,
        )
        self._metadata_provider: ISettingsMetadataProtocol = SettingsMetadataCapability(
            metadata_supplier=self._loader.get_last_metadata,
        )
        self._redaction_rules: IRedactionRulesProtocol = RedactionRulesCapability(
            extra_patterns=extra_redaction_patterns,
        )

    def build(self) -> IConfigAggregate:
        """Construct and return the wired ConfigOrchestrator."""
        return ConfigOrchestrator(
            loader=self._loader,
            retriever=self._retriever,
            workspace_resolver=self._workspace_resolver,
            metadata_provider=self._metadata_provider,
            redaction_rules=self._redaction_rules,
        )