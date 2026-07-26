"""Dispatcher agent: Aggregate facade for action catalog, validation, dispatch, and normalization.

Implements the DispatcherOrchestrator Aggregate — coordinates all dispatcher capabilities
to provide a unified action routing facade for CLI and MCP consumers.

Structure:
  1. Constants & configuration
  2. Protocol method implementations (Aggregate facade methods)
  3. Dunder methods, factories, and helpers
"""

import logging
from typing import Any

from modules.shared.src.dispatcher.contract_action_discovery_protocol import ActionDiscoveryProtocol
from modules.shared.src.dispatcher.contract_background_submit_protocol import BackgroundSubmitProtocol
from modules.shared.src.dispatcher.contract_catalog_registration_protocol import CatalogRegistrationProtocol
from modules.shared.src.dispatcher.contract_request_validation_protocol import RequestValidationProtocol
from modules.shared.src.dispatcher.contract_result_normalization_protocol import ResultNormalizationProtocol
from modules.shared.src.dispatcher.contract_sync_dispatch_protocol import SyncDispatchProtocol
from modules.shared.src.dispatcher.taxonomy_action_request_vo import ActionRequestVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO
from modules.shared.src.dispatcher.taxonomy_validation_result_vo import ValidationResultVO

logger = logging.getLogger("BlenderMCPServer")


class DispatcherOrchestrator:
    """Aggregate facade coordinating all dispatcher capabilities.

    Provides unified action discovery, registration, validation, dispatch,
    background submission, and result normalization for CLI and MCP consumers.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        catalog_registration: CatalogRegistrationProtocol | None = None,
        action_discovery: ActionDiscoveryProtocol | None = None,
        request_validation: RequestValidationProtocol | None = None,
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

    def register_action(self, metadata: Any) -> Any:
        """Register an action in the catalog.

        FR-DSP-001: Delegates to CatalogRegistrationProtocol.
        """
        if self._catalog_reg is None:
            raise RuntimeError("CatalogRegistrationProtocol not configured")
        return self._catalog_reg.register_action(metadata)

    def discover_actions(
        self,
        name_filter: str | None = None,
        capability_filter: str | None = None,
        detail_level: str = "standard",
    ) -> dict[str, Any]:
        """Discover actions from the catalog.

        FR-DSP-002: Delegates to ActionDiscoveryProtocol.
        Returns canonical shape to all consumers.
        """
        if self._discovery is None:
            raise RuntimeError("ActionDiscoveryProtocol not configured")
        return self._discovery.discover_actions(
            name_filter=name_filter,
            capability_filter=capability_filter,
            detail_level=detail_level,
        )

    def validate_request(self, request: ActionRequestVO) -> ValidationResultVO:
        """Validate an action request against the catalog.

        FR-DSP-003: Delegates to RequestValidationProtocol.
        Unknown action → not found error; invalid params → field-level detail.
        """
        if self._validation is None:
            raise RuntimeError("RequestValidationProtocol not configured")
        return self._validation.validate_request(request)

    def dispatch_sync(self, validated_request: ValidationResultVO) -> UnifiedResultEnvelopeVO:
        """Dispatch a validated action synchronously to its owning feature.

        FR-DSP-004: Delegates to SyncDispatchProtocol.
        Routes to owning feature, enforces timeout, maps errors.
        """
        if self._dispatch is None:
            raise RuntimeError("SyncDispatchProtocol not configured")
        return self._dispatch.dispatch_sync(validated_request)

    def submit_background(self, request: ActionRequestVO) -> UnifiedResultEnvelopeVO:
        """Submit an action for background execution via job feature.

        FR-DSP-005: Delegates to BackgroundSubmitProtocol.
        Creates job, returns task reference. Enforces capacity limits.
        """
        if self._bg_submit is None:
            raise RuntimeError("BackgroundSubmitProtocol not configured")
        return self._bg_submit.submit_background(request)

    def normalize_result(
        self,
        raw_outcome: dict[str, Any],
        tracking_id: str,
        is_background: bool = False,
    ) -> UnifiedResultEnvelopeVO:
        """Normalize any dispatcher outcome into a unified result envelope.

        FR-DSP-006: Delegates to ResultNormalizationProtocol.
        Never leaks secrets; truncates oversized data; falls back to safe error.
        """
        if self._normalization is None:
            raise RuntimeError("ResultNormalizationProtocol not configured")
        return self._normalization.normalize_result(raw_outcome, tracking_id, is_background)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def execute_action(self, action_name: str, parameters: dict[str, Any]) -> dict[str, Any]:
        """Execute an action through the full dispatcher pipeline.

        This is the main facade method — validates, dispatches, and normalizes
        in a single call for consumers who don't need intermediate results.
        """
        # Build request
        request = ActionRequestVO(action_name=action_name, parameters=parameters)

        try:
            # Step 1: Validate
            validated = self.validate_request(request)

            # Step 2: Dispatch (sync or background based on eligibility)
            bg_eligible = validated.resolved_metadata.get("background_eligibility_flag", False)
            long_running = validated.resolved_metadata.get("long_running_flag", False)

            if bg_eligible or long_running:
                # Submit as background job
                envelope = self.submit_background(request)
            else:
                # Dispatch synchronously
                envelope = self.dispatch_sync(validated)

            return envelope

        except ValueError as e:
            logger.error("Action execution failed: %s", e)
            return UnifiedResultEnvelopeVO.error_envelope(
                message=str(e),
                tracking_id="",
                error_category="validation_error",
            ).__dict__

        except Exception as e:
            logger.error("Unexpected dispatch failure: %s", e)
            return UnifiedResultEnvelopeVO.safe_error_envelope(str(e)).__dict__

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
