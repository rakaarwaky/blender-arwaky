"""Config feature module — application configuration management.

FR-CFG-001: Load and Apply Settings
FR-CFG-002: Retrieve Settings Values
FR-CFG-003: Resolve Project Workspace Directory
FR-CFG-004: Provide Settings Metadata
FR-CFG-005: Provide Redaction Rules

Architecture:
- Agent: ConfigOrchestrator (orchestration only)
- Capabilities: SettingsLoader, SettingsRetriever, WorkspaceResolver,
  SettingsMetadata, RedactionRules
- Contract: IConfigAggregate facade + 5 protocols
"""

from modules.shared.src.config.utility_config_helpers import parse_env_value, search_project_root

from .src.agent_config_orchestrator import ConfigOrchestrator
from .src.capabilities_redaction_rules import RedactionRulesCapability
from .src.capabilities_settings_loader import SettingsLoaderCapability
from .src.capabilities_settings_metadata import SettingsMetadataCapability
from .src.capabilities_settings_retriever import SettingsRetrieverCapability
from .src.capabilities_workspace_resolver import WorkspaceResolverCapability
from .src.root_config_container import ConfigContainer

__all__ = [
    "ConfigOrchestrator",
    "SettingsLoaderCapability",
    "SettingsRetrieverCapability",
    "WorkspaceResolverCapability",
    "SettingsMetadataCapability",
    "RedactionRulesCapability",
    "ConfigContainer",
    "parse_env_value",
    "search_project_root",
]
