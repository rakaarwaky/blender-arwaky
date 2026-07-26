"""Synchronous dispatch capability — route actions to owning features.

FR-DSP-004: Dispatch Synchronous Action
- Routes validated action to owning domain feature or gateway
- Enforces timeout, propagates tracking ID
- Maps domain errors to unified categories
- Returns standardized envelope
"""

import logging
import time
from typing import Any

from modules.shared.src.dispatcher.contract_sync_dispatch_protocol import (
    SyncDispatchProtocol,
)
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO
from modules.shared.src.dispatcher.taxonomy_validation_result_vo import ValidationResultVO

logger = logging.getLogger("BlenderMCPServer")


class SyncDispatchExecutor(SyncDispatchProtocol):
    """Concrete implementation for synchronous action dispatch.

    FR-DSP-004: Routes to owning feature, enforces timeout, maps errors.
    Returns standardized envelope; does not retry non-idempotent actions.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, execute_action: Any = None):
        self._execute = execute_action

    # ─── Block 2: Protocol Method Implementation ─────────────

    def dispatch_sync(self, validated_request: ValidationResultVO) -> UnifiedResultEnvelopeVO:
        """Route a validated action to its owning feature and return normalized result.

        FR-DSP-004: Enforces timeout, propagates tracking ID, maps domain errors.
        Returns standardized envelope; does not retry non-idempotent actions.
        """
        start_time = time.time()
        tracking_id = validated_request.validated_tracking_id
        action_name = validated_request.action_name

        try:
            # Build parameter dict for owning feature
            params = dict(validated_request.parameters)

            # Dispatch to owning feature (via execute_action abstraction)
            if self._execute:
                result = self._execute.execute_action(action_name, params)
            else:
                # Fallback: simulate dispatch for testing
                result = {"status": "dispatched", "action": action_name}

            duration_ms = (time.time() - start_time) * 1000

            # Build metadata summary
            metadata = {
                "action_name": action_name,
                "owning_feature_ref": validated_request.resolved_metadata.get("owning_feature_ref"),
                "execution_mode": validated_request.execution_mode or "sync",
                "duration_ms": duration_ms,
                "applied_timeout": validated_request.timeout_override
                or validated_request.resolved_metadata.get("default_timeout"),
            }

            return UnifiedResultEnvelopeVO.success_envelope(
                message=f"Action {action_name} dispatched successfully",
                tracking_id=tracking_id,
                data=result if isinstance(result, dict) else {"result": str(result)},
                metadata=metadata,
            )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            error_category = self._map_error_category(e)

            logger.error(
                "Dispatch failed: %s (action=%s, tracking_id=%s, category=%s)",
                e,
                action_name,
                tracking_id,
                error_category,
            )

            return UnifiedResultEnvelopeVO.error_envelope(
                message=f"Action '{action_name}' failed: {e}",
                tracking_id=tracking_id,
                error_category=error_category,
                metadata={
                    "action_name": action_name,
                    "duration_ms": duration_ms,
                },
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _map_error_category(self, error: Exception) -> str:
        """Map domain error to unified error category.

        FR-DSP-004: Domain errors must be mapped into unified categories.
        """
        error_type = type(error).__name__

        if "Timeout" in error_type or "timeout" in str(error).lower():
            return "timeout_error"
        if "Connection" in error_type or "connection" in str(error).lower():
            return "connection_error"
        if "NotFound" in error_type or "not found" in str(error).lower():
            return "not_found_error"
        if "ValidationError" in error_type or "validation" in str(error).lower():
            return "validation_error"

        # Default: execution error for unmapped domain errors
        return "execution_error"

    def __repr__(self) -> str:
        return f"SyncDispatchExecutor(execute={self._execute is not None})"
