"""Synchronous dispatch capability — route actions to owning features.

FR-DSP-004: Dispatch Synchronous Action
- Routes validated action to owning domain feature or gateway
- Enforces timeout, propagates tracking ID
- Maps domain errors to unified categories
- Returns standardized envelope
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FuturesTimeoutError

from modules.shared.src.dispatcher.contract_execute_action_protocol import (
    ExecuteActionProtocol,
)
from modules.shared.src.dispatcher.contract_sync_dispatch_protocol import (
    SyncDispatchProtocol,
)
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

logger = logging.getLogger("BlenderMCPServer")


class SyncDispatchExecutor(SyncDispatchProtocol):
    """Concrete implementation for synchronous action dispatch.

    FR-DSP-004: Routes to owning feature, enforces timeout, maps errors.
    Returns standardized envelope; does not retry non-idempotent actions.
    Implements context manager protocol for proper ThreadPoolExecutor cleanup.

    Raises ValueError at construction if execute_action is None —
    this prevents fake-success responses (FR-DSP-004 routing integrity).
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, execute_action: ExecuteActionProtocol) -> None:
        if execute_action is None:
            raise ValueError(
                "SyncDispatchExecutor requires a non-null action executor. "
                "Ensure the owning feature executor is wired in the container."
            )
        self._execute: ExecuteActionProtocol = execute_action
        self._pool = ThreadPoolExecutor(max_workers=1)

    def __enter__(self) -> "SyncDispatchExecutor":
        """Enter context manager."""
        return self

    def __exit__(self, exc_type: object, exc_val: object, exc_tb: object) -> None:
        """Exit context manager — shut down the thread pool."""
        self._pool.shutdown(wait=True)

    # ─── Block 2: Protocol Method Implementation ─────────────

    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Route a validated action to its owning feature and return normalized result.

        FR-DSP-004: Enforces timeout, propagates tracking ID, maps domain errors.
        Never synthesises fake success — requires a wired executor at construction.
        """
        start_time = time.time()
        tracking_id = request.validated_tracking_id or request.tracking_id or ""
        action_name = request.action_name

        try:
            params = dict(request.parameters)
            applied_timeout = request.timeout_override or request.resolved_metadata.get("default_timeout") or 0.0

            # FR-DSP-004: Check for degraded owning feature before dispatching
            if request.resolved_metadata.get("degraded", False):
                owning_feature = request.resolved_metadata.get("owning_feature_ref", "unknown")
                raise RuntimeError(f"Owning feature {owning_feature} is degraded")

            if applied_timeout and applied_timeout > 0:
                # Enforce the action timeout (FR-DSP-004) on the owning-feature call.
                future = self._pool.submit(self._execute.execute_action, action_name, params)
                try:
                    result = future.result(timeout=applied_timeout)
                except FuturesTimeoutError:
                    raise TimeoutError(f"Action '{action_name}' exceeded timeout {applied_timeout}s") from None
            else:
                result = self._execute.execute_action(action_name, params)

            duration_ms = (time.time() - start_time) * 1000

            metadata = {
                "action_name": action_name,
                "owning_feature_ref": request.resolved_metadata.get("owning_feature_ref"),
                "execution_mode": request.execution_mode or "sync",
                "duration_ms": duration_ms,
                "applied_timeout": applied_timeout,
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
                message=f"Action '{action_name}' failed",
                tracking_id=tracking_id,
                error_category=error_category,
                metadata={
                    "action_name": action_name,
                    "duration_ms": duration_ms,
                },
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _map_error_category(self, error: Exception) -> str:
        """Map domain error to unified error category (FR-DSP-004)."""
        error_type = type(error).__name__

        if error_type == "TimeoutError" or "Timeout" in error_type:
            return "timeout_error"
        if "Timeout" in str(error).lower():
            return "timeout_error"
        if "Connection" in error_type or "connection" in str(error).lower():
            return "connection_error"
        if "NotFound" in error_type or "not found" in str(error).lower():
            return "not_found_error"
        if "ValidationError" in error_type or "validation" in str(error).lower():
            return "validation_error"

        return "execution_error"

    def __repr__(self) -> str:
        return f"SyncDispatchExecutor(execute={self._execute is not None})"
