"""Dispatcher domain — taxonomy Value Objects and contract protocols.

Shared layer (shared/src/dispatcher/):
  - Taxonomy VOs: ActionMetadataVO, ActionCommandVO, DiscoveryOutcomeVO,
    UnifiedResultEnvelopeVO
  - Contracts: 6 individual protocol ABCs

Capability layer lives in modules/dispatcher/src/.
Agent layer (DispatcherOrchestrator) implements Aggregate facade.
"""

from .contract_action_discovery_protocol import ActionDiscoveryProtocol
from .contract_background_submit_protocol import BackgroundSubmitProtocol
from .contract_catalog_registration_protocol import CatalogRegistrationProtocol
from .contract_dispatcher_aggregate import IDispatcherAggregate
from .contract_request_validation_protocol import RequestValidationProtocol
from .contract_result_normalization_protocol import ResultNormalizationProtocol
from .contract_sync_dispatch_protocol import SyncDispatchProtocol
from .taxonomy_action_command_vo import ActionCommandVO
from .taxonomy_action_metadata_vo import ActionMetadataVO
from .taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from .taxonomy_dispatch_error import DispatchError, DispatchErrorCategory
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

__all__ = [
    "ActionMetadataVO",
    "ActionCommandVO",
    "DispatchError",
    "DispatchErrorCategory",
    "DiscoveryOutcomeVO",
    "UnifiedResultEnvelopeVO",
    "ActionDiscoveryProtocol",
    "BackgroundSubmitProtocol",
    "CatalogRegistrationProtocol",
    "RequestValidationProtocol",
    "ResultNormalizationProtocol",
    "SyncDispatchProtocol",
    "IDispatcherAggregate",
]
