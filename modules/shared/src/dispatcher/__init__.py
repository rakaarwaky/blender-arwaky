"""Dispatcher domain — taxonomy Value Objects and contract protocols.

Shared layer (shared/src/dispatcher/):
  - Taxonomy VOs: ActionMetadataVO, ActionCommandVO, DiscoveryOutcomeVO,
    UnifiedResultEnvelopeVO
  - Contracts: 6 individual protocol ABCs

Capability layer lives in modules/dispatcher/src/.
Agent layer (DispatcherOrchestrator) implements Aggregate facade.
"""

from .taxonomy_action_command_vo import ActionCommandVO
from .taxonomy_action_metadata_vo import ActionMetadataVO
from .taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

__all__ = [
    "ActionMetadataVO",
    "ActionCommandVO",
    "DiscoveryOutcomeVO",
    "UnifiedResultEnvelopeVO",
]

# Protocol imports (contract layer)
from .contract_dispatcher_aggregate import (
    ActionDiscoveryProtocol,
    BackgroundSubmitProtocol,
    CatalogRegistrationProtocol,
    RequestValidationProtocol,
    ResultNormalizationProtocol,
    SyncDispatchProtocol,
)
