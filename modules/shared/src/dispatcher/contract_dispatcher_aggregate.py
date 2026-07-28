"""Aggregate contract for the dispatcher feature.

Aggregates all protocol contracts into a single unified interface.
"""

from .contract_action_discovery_protocol import ActionDiscoveryProtocol
from .contract_background_submit_protocol import BackgroundSubmitProtocol
from .contract_catalog_registration_protocol import CatalogRegistrationProtocol
from .contract_request_validation_protocol import RequestValidationProtocol
from .contract_result_normalization_protocol import ResultNormalizationProtocol
from .contract_sync_dispatch_protocol import SyncDispatchProtocol

__all__ = [
    "ActionDiscoveryProtocol",
    "BackgroundSubmitProtocol",
    "CatalogRegistrationProtocol",
    "RequestValidationProtocol",
    "ResultNormalizationProtocol",
    "SyncDispatchProtocol",
]
