"""Dispatcher agent: Aggregate facade for action catalog, validation, dispatch, and normalization.

Implements the DispatcherOrchestrator Aggregate — coordinates all dispatcher capabilities
to provide a unified action routing facade for CLI and MCP consumers.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.dispatcher.contract_action_discovery_protocol import (
    ActionDiscoveryProtocol,
)
from modules.shared.src.dispatcher.contract_background_submit_protocol import (
    BackgroundSubmitProtocol,
)
from modules.shared.src.dispatcher.contract_catalog_registration_protocol import (
    CatalogRegistrationProtocol,
)
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.contract_request_validation_protocol import (
    RequestValidationProtocol,
)
from modules.shared.src.dispatcher.contract_result_normalization_protocol import (
    ResultNormalizationProtocol,
)
from modules.shared.src.dispatcher.contract_sync_dispatch_protocol import (
    SyncDispatchProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_action_metadata_vo import ActionMetadataVO
from modules.shared.src.dispatcher.taxonomy_dispatch_error import (
    DispatchError,
    DispatchErrorCategory,
)
from modules.shared.src.dispatcher.taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

logger = logging.getLogger("BlenderMCPServer")


class DispatcherOrchestrator(IDispatcherAggregate):
    """Aggregate facade coordinating all dispatcher capabilities.

    Provides unified action discovery, registration, validation, dispatch,
    background submission, and result normalization for CLI and MCP consumers.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        catalog_registration: CatalogRegistrationProtocol,
        action_discovery: ActionDiscoveryProtocol,
        request_validation: RequestValidationProtocol,
        sync_dispatch: SyncDispatchProtocol | None = None,
        background_submit: BackgroundSubmitProtocol | None = None,
        result_normalization: ResultNormalizationProtocol | None = None,
    ) -> None:
        self._catalog_reg = catalog_registration
        self._discovery = action_discovery
        self._validation = request_validation
        self._dispatch = sync_dispatch
        self._bg_submit = background_submit
        self._normalization = result_normalization

    # ─── Block 2: Protocol Method Implementation (Aggregate Facade) ──

    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO:
        """FR-DSP-001: Register an action in the catalog."""
        return self._catalog_reg.register_action(metadata)

    def discover_actions(
        self,
        name_filter: str | None = None,
        capability_filter: str | None = None,
        detail_level: str = "standard",
    ) -> DiscoveryOutcomeVO:
        """FR-DSP-002: Discover actions from the catalog."""
        return self._discovery.discover_actions(
            name_filter=name_filter,
            capability_filter=capability_filter,
            detail_level=detail_level,
        )

    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO:
        """FR-DSP-003: Validate an action request against the catalog."""
        return self._validation.validate_request(request)

    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """FR-DSP-004: Dispatch a validated action synchronously."""
        if self._dispatch is None:
            raise RuntimeError("SyncDispatchProtocol not configured")
        return self._dispatch.dispatch_sync(request)

    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """FR-DSP-005: Submit an action for background execution."""
        if self._bg_submit is None:
            raise RuntimeError("BackgroundSubmitProtocol not configured")
        return self._bg_submit.submit_background(request)

    def normalize_result(
        self,
        raw_outcome: dict[str, Any],
        tracking_id: str,
        is_background: bool = False,
    ) -> UnifiedResultEnvelopeVO:
        """FR-DSP-006: Normalize any outcome into a unified result envelope."""
        if self._normalization is None:
            raise RuntimeError("ResultNormalizationProtocol not configured")
        return self._normalization.normalize_result(raw_outcome, tracking_id, is_background)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Execute an action through the full dispatcher pipeline."""
        try:
            validated = self.validate_request(request)

            bg_eligible = validated.resolved_metadata.get("background_eligibility_flag", False)
            long_running = validated.resolved_metadata.get("long_running_flag", False)

            if bg_eligible or long_running:
                return self.submit_background(validated)

            return self.dispatch_sync(validated)

        except DispatchError as e:
            logger.error("Dispatch rejected: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message=self._safe_message(e),
                tracking_id=request.validated_tracking_id,
                error_category=e.error_category,
            )

        except Exception as e:
            logger.error("Unexpected dispatch failure: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Action execution failed unexpectedly",
                tracking_id=request.validated_tracking_id,
                error_category=DispatchErrorCategory.EXECUTION,
            )

    @staticmethod
    def _safe_message(error: Exception) -> str:
        return "Action request could not be processed"

    def __repr__(self) -> str:
        return (
            f"DispatcherOrchestrator("
            f"catalog_reg={self._catalog_reg is not None}, "
            f"validation={self._validation is not None}, "
            f"dispatch={self._dispatch is not None}, "
            f"bg_submit={self._bg_submit is not None}, "
            f"normalization={self._normalization is not None}"
            f")"
        )
