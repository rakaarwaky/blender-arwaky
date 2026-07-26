"""Dispatcher domain — taxonomy Value Objects and contract protocols.

Shared layer (shared/src/dispatcher/):
  - Taxonomy VOs: ActionMetadataVO, ActionRequestVO, ValidationResultVO,
    DiscoveryResultVO, UnifiedResultEnvelopeVO
  - Contracts: 6 individual protocol ABCs

Capability layer lives in modules/dispatcher/src/.
Agent layer (DispatcherOrchestrator) implements Aggregate facade.
"""

from .taxonomy_action_metadata_vo import ActionMetadataVO
from .taxonomy_action_request_vo import ActionRequestVO
from .taxonomy_discovery_result_vo import DiscoveryResultVO
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO
from .taxonomy_validation_result_vo import ValidationResultVO

__all__ = [
    "ActionMetadataVO",
    "ActionRequestVO",
    "DiscoveryResultVO",
    "UnifiedResultEnvelopeVO",
    "ValidationResultVO",
]

# Protocol imports (contract layer)
from .contract_action_discovery_protocol import ActionDiscoveryProtocol
from .contract_background_submit_protocol import BackgroundSubmitProtocol
from .contract_catalog_registration_protocol import CatalogRegistrationProtocol
from .contract_request_validation_protocol import RequestValidationProtocol
from .contract_result_normalization_protocol import ResultNormalizationProtocol
from .contract_sync_dispatch_protocol import SyncDispatchProtocol

__all__ += [
    "CatalogRegistrationProtocol",
    "ActionDiscoveryProtocol",
    "RequestValidationProtocol",
    "SyncDispatchProtocol",
    "BackgroundSubmitProtocol",
    "ResultNormalizationProtocol",
]
