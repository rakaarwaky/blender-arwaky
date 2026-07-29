"""Config feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/config/)   → VOs, Errors, Events, Constants
  - Contract (shared/src/config/)   → 5 individual protocols + Aggregate ABC
  - Capabilities (5 executors)        → One per FR-CFG operation
  - Agent                             → ConfigOrchestrator (implements Aggregate facade)
  - Root                              → ConfigContainer (DI wiring)
"""

from .agent_config_orchestrator import ConfigOrchestrator
from .capabilities_redaction_rules import RedactionRulesCapability
from .capabilities_settings_loader import SettingsLoaderCapability
from .capabilities_settings_metadata import SettingsMetadataCapability
from .capabilities_settings_retriever import SettingsRetrieverCapability
from .capabilities_workspace_resolver import WorkspaceResolverCapability
from .root_config_container import ConfigContainer

__all__ = [
    "ConfigOrchestrator",
    "RedactionRulesCapability",
    "SettingsLoaderCapability",
    "SettingsMetadataCapability",
    "SettingsRetrieverCapability",
    "WorkspaceResolverCapability",
    "ConfigContainer",
]
