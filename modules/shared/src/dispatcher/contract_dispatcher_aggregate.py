"""Dispatcher domain contract: dispatcher aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for action dispatch operations: discovery, validation, dispatch, normalization.
"""

from __future__ import annotations

from .contract_action_discovery_protocol import ActionDiscoveryProtocol
from .contract_background_submit_protocol import BackgroundSubmitProtocol
from .contract_catalog_registration_protocol import CatalogRegistrationProtocol
from .contract_request_validation_protocol import RequestValidationProtocol
from .contract_result_normalization_protocol import ResultNormalizationProtocol
from .contract_sync_dispatch_protocol import SyncDispatchProtocol
from .taxonomy_action_command_vo import ActionCommandVO
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


class IDispatcherAggregate(
    CatalogRegistrationProtocol,
    ActionDiscoveryProtocol,
    RequestValidationProtocol,
    SyncDispatchProtocol,
    BackgroundSubmitProtocol,
    ResultNormalizationProtocol,
):
    """Aggregate facade for dispatcher operations.

    Agent implements this aggregate (DispatcherOrchestrator). Surface layers depend on it.
    Provides action discovery, request validation, synchronous dispatch, background submission, and result normalization.
    """

    def execute_action(
        self,
        request: ActionCommandVO,
    ) -> UnifiedResultEnvelopeVO:
        """Execute action facade method."""
        ...
