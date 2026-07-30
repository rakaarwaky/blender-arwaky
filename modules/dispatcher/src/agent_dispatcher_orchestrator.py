"""Dispatcher agent: Aggregate facade for action catalog, validation, dispatch, and normalization.

Implements the DispatcherOrchestrator Aggregate — coordinates all dispatcher capabilities
to provide a unified action routing facade for CLI and MCP consumers.

Structure:
  1. Constants & configuration
  2. Protocol method implementations (Aggregate facade methods)
  3. Dunder methods, factories, and helpers
"""

import logging

from modules.shared.src.dispatcher.contract_action_discovery_protocol import ActionDiscoveryProtocol
from modules.shared.src.dispatcher.contract_background_submit_protocol import BackgroundSubmitProtocol
from modules.shared.src.dispatcher.contract_catalog_registration_protocol import CatalogRegistrationProtocol
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
from modules.shared.src.dispatcher.taxonomy_discovery_filter_vo import DiscoveryFilterVO
from modules.shared.src.dispatcher.taxonomy_discovery_outcome_vo import DiscoveryOutcomeVO
from modules.shared.src.dispatcher.taxonomy_dispatch_error import (
    DispatchError,
    DispatchErrorCategory,
)
from modules.shared.src.dispatcher.taxonomy_raw_outcome_vo import RawOutcomeVO
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
        sync_dispatch: SyncDispatchProtocol,
        background_submit: BackgroundSubmitProtocol,
        result_normalization: ResultNormalizationProtocol,
    ) -> None:
        self._catalog_reg = catalog_registration
        self._discovery = action_discovery
        self._validation = request_validation
        self._dispatch = sync_dispatch
        self._bg_submit = background_submit
        self._normalization = result_normalization

    # ─── Block 2: Protocol Method Implementation (Aggregate Facade) ──

    def register_action(self, metadata: ActionMetadataVO) -> ActionMetadataVO:
        """Register an action in the catalog.

        FR-DSP-001: Delegates to CatalogRegistrationProtocol.
        """
        if self._catalog_reg is None:
            raise RuntimeError("CatalogRegistrationProtocol not configured")
        return self._catalog_reg.register_action(metadata)

    def discover_actions(self, filter_criteria: DiscoveryFilterVO) -> DiscoveryOutcomeVO:
        """Discover actions from the catalog.

        FR-DSP-002: Delegates to ActionDiscoveryProtocol.
        Returns canonical shape to all consumers.
        """
        if self._discovery is None:
            raise RuntimeError("ActionDiscoveryProtocol not configured")
        return self._discovery.discover_actions(filter_criteria)

    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO:
        """Validate an action request against the catalog.

        FR-DSP-003: Delegates to RequestValidationProtocol.
        Unknown action -> not found error; invalid params -> field-level detail.
        Returns enriched same VO type (merged input+output pattern).
        """
        if self._validation is None:
            raise RuntimeError("RequestValidationProtocol not configured")
        return self._validation.validate_request(request)

    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Dispatch a validated action synchronously to its owning feature.

        FR-DSP-004: Delegates to SyncDispatchProtocol.
        Routes to owning feature, enforces timeout, maps errors.
        """
        if self._dispatch is None:
            raise RuntimeError("SyncDispatchProtocol not configured")
        return self._dispatch.dispatch_sync(request)

    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Submit an action for background execution via job feature.

        FR-DSP-005: Delegates to BackgroundSubmitProtocol.
        Creates job, returns task reference. Enforces capacity limits.
        """
        if self._bg_submit is None:
            raise RuntimeError("BackgroundSubmitProtocol not configured")
        return self._bg_submit.submit_background(request)

    def normalize_result(self, raw_outcome: RawOutcomeVO) -> UnifiedResultEnvelopeVO:
        """Normalize any dispatcher outcome into a unified result envelope.

        FR-DSP-006: Delegates to ResultNormalizationProtocol.
        Never leaks secrets; truncates oversized data; falls back to safe error.
        """
        if self._normalization is None:
            raise RuntimeError("ResultNormalizationProtocol not configured")
        return self._normalization.normalize_result(raw_outcome)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def execute_action(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Execute an action through the full dispatcher pipeline.

        This is the main facade method — validates, dispatches, and normalizes
        in a single call for consumers who don't need intermediate results.
        """
        try:
            validated = self.validate_request(request)

            bg_eligible = validated.resolved_metadata.get("background_eligibility_flag", False)
            long_running = validated.resolved_metadata.get("long_running_flag", False)

            if bg_eligible or long_running:
                envelope = self.submit_background(validated)
            else:
                envelope = self.dispatch_sync(validated)

            return envelope

        except DispatchError as e:
            logger.error("Dispatch rejected: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message=self._safe_message(e),
                tracking_id=request.validated_tracking_id,
                error_category=e.error_category,
            )

        except Exception as e:
            logger.exception("Unexpected dispatch failure")
            return UnifiedResultEnvelopeVO.error_envelope(
                message="Action execution failed unexpectedly",
                tracking_id=request.validated_tracking_id,
                error_category=DispatchErrorCategory.EXECUTION,
            )

    @staticmethod
    def _safe_message(error: Exception) -> str:
        """Return a safe, sanitized error message for external consumers.

        Do not return raw exception text to consumers.
        Keep detailed diagnostics in logs only.
        """
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
