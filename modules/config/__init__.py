"""Config feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/config/)   → VOs, Errors, Events, Constants
  - Contract (shared/src/config/)   → 5 individual protocols + Aggregate ABC
  - Capabilities (5 executors)      → One per FR-CFG operation
  - Agent                           → ConfigOrchestrator (implements Aggregate facade)
  - Root                            → ConfigContainer (DI wiring)
"""

from .src.agent_config_orchestrator import ConfigOrchestrator
from .src.capabilities_redaction_rules import RedactionRulesCapability
from .src.capabilities_settings_loader import SettingsLoaderCapability
from .src.capabilities_settings_metadata import SettingsMetadataCapability
from .src.capabilities_settings_retriever import SettingsRetrieverCapability
from .src.capabilities_workspace_resolver import WorkspaceResolverCapability
from .src.root_config_container import ConfigContainer

__all__ = [
    "ConfigOrchestrator",
    "RedactionRulesCapability",
    "SettingsLoaderCapability",
    "SettingsMetadataCapability",
    "SettingsRetrieverCapability",
    "WorkspaceResolverCapability",
    "ConfigContainer",
]
