"""Dispatcher feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/dispatcher/) → VOs: ActionMetadataVO, ActionCommandVO,
    ValidationOutcomeVO, DiscoveryOutcomeVO, UnifiedResultEnvelopeVO
  - Contract (shared/src/dispatcher/) → 6 individual protocols
  - Capabilities (6 executors)        → One per FR operation
  - Agent                             → DispatcherOrchestrator (Aggregate facade)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from .agent_dispatcher_orchestrator import DispatcherOrchestrator
from .capabilities_action_discovery import ActionDiscoveryExecutor
from .capabilities_background_submit import BackgroundSubmitExecutor
from .capabilities_catalog_registration import CatalogRegistrationExecutor
from .capabilities_request_validation import RequestValidationExecutor
from .capabilities_result_normalization import ResultNormalizationExecutor
from .capabilities_sync_dispatch import SyncDispatchExecutor

__all__ = [
    "ActionDiscoveryExecutor",
    "BackgroundSubmitExecutor",
    "CatalogRegistrationExecutor",
    "DispatcherOrchestrator",
    "RequestValidationExecutor",
    "ResultNormalizationExecutor",
    "SyncDispatchExecutor",
]
