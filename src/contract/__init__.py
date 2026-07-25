"""Contract layer exports — AES Ports, Protocols, and Aggregate/VO types.

This module re-exports from modules.shared.src/ (organized by domain)
for backward compatibility with existing layer files.

Naming convention:
- *_aggregate.py    : Structural contracts for agents/orchestrators
- *_vo.py           : Data Transfer Objects (Value Objects)
- *_protocol.py     : Protocol (ABC-based) definitions
- *_port.py         : Port interfaces and connection/configuration abstractions
"""

# Re-export protocols from new domain locations (backward-compatible names)
from modules.shared.src import (
    ContractSceneOperateProtocol as SceneOperateProtocol,
    ContractObjectOperateProtocol as ObjectOperateProtocol,
    ContractRenderOperateProtocol as RenderOperateProtocol,
    ContractImportExportProtocol as ImportExportProtocol,
    ContractAssetSearchProtocol as AssetSearchProtocol,
    ContractWorkflowProtocol as WorkflowProtocol,
    ContractExecuteActionProtocol as ExecuteActionProtocol,
)

# Re-export ports from new domain locations (backward-compatible names)
from modules.shared.src import (
    ContractBlenderPort as BlenderPort,
    ContractBlenderConnectionPort as BlenderConnectionPort,
    ContractConfigPort as ConfigPort,
    ContractCommandCatalogPort as CommandCatalogPort,
    ContractCodeExecutionPort as CodeExecutionPort,
    ContractSceneInspectionPort as SceneInspectionPort,
    ContractAssetProviderPort as AssetProviderPort,
    ContractTelemetryRecordingPort as TelemetryRecordingPort,
)

# Backward-compatible ConfigValue alias
from modules.shared.src.common.taxonomy_core_vo import ConfigValue

# Keep aggregate imports from existing location (agent layer concerns)
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
    # Protocols (backward-compatible aliases)
    "SceneOperateProtocol",
    "ObjectOperateProtocol",
    "RenderOperateProtocol",
    "ImportExportProtocol",
    "AssetSearchProtocol",
    "WorkflowProtocol",
    "ExecuteActionProtocol",
    # Ports (backward-compatible aliases)
    "CommandCatalogPort",
    "AssetProviderPort",
    "BlenderPort",
    "BlenderConnectionPort",
    "CodeExecutionPort",
    "SceneInspectionPort",
    "TelemetryRecordingPort",
    "ConfigPort",
    "ConfigValue",
]
