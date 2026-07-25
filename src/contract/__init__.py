"""Contract layer exports — AES Ports, Protocols, and Aggregate/VO types.

This module provides backward-compatible imports for existing layer files.
New contract files are organized under modules/shared/src/<domain>/

Naming convention:
- *_aggregate.py    : Structural contracts for agents/orchestrators
- *_vo.py           : Data Transfer Objects (Value Objects)
- *_protocol.py     : Protocol (ABC-based) definitions
- *_port.py         : Port interfaces and connection/configuration abstractions
"""

# Aggregate imports (structural contracts for agents — stay in src/contract/)
from .agent_base_aggregate import AgentBaseContainerAggregate
from .agent_di_aggregate import AgentDiContainerAggregate
from .agent_factory_aggregate import AgentFactoryRegistryAggregate
from .core_agent_aggregate import CoreAgentOrchestratorAggregate
from .expert_base_aggregate import ExpertBaseOrchestratorAggregate
from .refinement_expert_aggregate import RefinementExpertOrchestratorAggregate
from .search_expert_aggregate import SearchExpertOrchestratorAggregate
from .server_bootstrap_aggregate import ServerBootstrapManagerAggregate
from .setup_expert_aggregate import SetupExpertOrchestratorAggregate
from .system_prompt_aggregate import SystemPromptManagerAggregate
from .system_utils_aggregate import SystemUtilsCoordinatorAggregate
from .workflow_agent_aggregate import WorkflowAgentOrchestratorAggregate

# Backward-compatible config value
from modules.shared.src.common.taxonomy_core_vo import ConfigValue

__all__ = [
    # Aggregate — Structural
    "AgentBaseContainerAggregate",
    "AgentDiContainerAggregate",
    "AgentFactoryRegistryAggregate",
    "CoreAgentOrchestratorAggregate",
    "ExpertBaseOrchestratorAggregate",
    "RefinementExpertOrchestratorAggregate",
    "SearchExpertOrchestratorAggregate",
    "ServerBootstrapManagerAggregate",
    "SetupExpertOrchestratorAggregate",
    "SystemPromptManagerAggregate",
    "SystemUtilsCoordinatorAggregate",
    "WorkflowAgentOrchestratorAggregate",
    # Config
    "ConfigValue",
]
