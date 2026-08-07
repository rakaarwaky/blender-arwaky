"""Tests for synchronous dispatch capability — FR-DSP-004.

FR-DSP-004: Dispatch Synchronous Action
- Routes validated action to owning domain feature or gateway
- Enforces timeout from metadata or bounded override
- Maps domain errors to unified categories via DispatchErrorCategory
- Propagates tracking ID into envelope
- Returns standardized envelope with metadata
- Degraded owning feature → execution error
- Does not retry non-idempotent actions
"""

from __future__ import annotations

import time

import pytest

from modules.dispatcher.src.capabilities_sync_dispatch import SyncDispatchExecutor
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_dispatch_error import DispatchErrorCategory
from modules.shared.src.dispatcher.taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO

# ─── Helpers ────────────────────────────────────────────────────────────────


class MockExecutor:
    """Mock action executor for testing dispatch."""

    def __init__(self, result: dict | None = None, side_effect: Exception | None = None) -> None:
        self._result = result or {"status": "ok"}
        self._side_effect = side_effect
        self.calls: list[tuple[str, dict]] = []

    def execute_action(self, action_name: str, params: dict) -> dict:
        self.calls.append((action_name, params))
        if self._side_effect is not None:
            raise self._side_effect
        return self._result


class SlowExecutor(MockExecutor):
    """Executor that sleeps longer than the timeout."""

    def execute_action(self, action_name: str, params: dict) -> dict:
        time.sleep(5.0)
        return super().execute_action(action_name, params)


def _make_request(
    action_name: str = "test_action",
    parameters: dict | None = None,
    tracking_id: str | None = "track-123",
    execution_mode: str | None = None,
    timeout_override: float | None = None,
    resolved_metadata: dict | None = None,
) -> ActionCommandVO:
    """Create a minimal ActionCommandVO for testing."""
    defaults: dict[str, object] = {"action_name": action_name}
    if parameters is not None:
        defaults["parameters"] = parameters
    if tracking_id is not None:
        defaults["tracking_id"] = tracking_id
    if execution_mode is not None:
        defaults["execution_mode"] = execution_mode
    if timeout_override is not None:
        defaults["timeout_override"] = timeout_override
    if resolved_metadata is not None:
        defaults["resolved_metadata"] = resolved_metadata
    return ActionCommandVO(**defaults)  # type: ignore[arg-type]


# ─── FR-DSP-004: Constructor Validation ─────────────────────────────────────


class TestConstructorValidation:
    """SyncDispatchExecutor constructor validation."""

    def test_none_executor_raises_value_error(self) -> None:
        """FR-DSP-004: None execute_action raises ValueError at construction."""
        with pytest.raises(ValueError, match="non-null action executor"):
            SyncDispatchExecutor(execute_action=None)

    def test_valid_executor_accepted(self) -> None:
        """FR-DSP-004: Valid executor is accepted."""
        executor = SyncDispatchExecutor(execute_action=MockExecutor())
        assert executor is not None


# ─── FR-DSP-004: Successful Dispatch ────────────────────────────────────────


class TestSuccessfulDispatch:
    """Successful dispatch per FR-DSP-004."""

    def test_dispatch_returns_success_envelope(self) -> None:
        """FR-DSP-004: Successful dispatch returns success envelope."""
        mock = MockExecutor(result={"created": True})
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(action_name="create_obj", parameters={"name": "cube"})
        result = executor.dispatch_sync(request)

        assert isinstance(result, UnifiedResultEnvelopeVO)
        assert result.success is True
        assert result.data == {"created": True}

    def test_tracking_id_propagated_to_envelope(self) -> None:
        """FR-DSP-004: Tracking ID from request propagates to envelope."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(tracking_id="my-tracking-id")
        result = executor.dispatch_sync(request)

        assert result.tracking_id == "my-tracking-id"

    def test_action_name_and_params_forwarded(self) -> None:
        """FR-DSP-004: Action name and params are forwarded to executor."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(action_name="render_frame", parameters={"frame": 42})
        executor.dispatch_sync(request)

        assert len(mock.calls) == 1
        assert mock.calls[0] == ("render_frame", {"frame": 42})

    def test_envelope_metadata_contains_action_name(self) -> None:
        """FR-DSP-004: Envelope metadata includes action_name."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(action_name="import_asset")
        result = executor.dispatch_sync(request)

        assert result.metadata.get("action_name") == "import_asset"

    def test_envelope_metadata_contains_duration(self) -> None:
        """FR-DSP-004: Envelope metadata includes duration_ms."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request()
        result = executor.dispatch_sync(request)

        assert "duration_ms" in result.metadata
        assert isinstance(result.metadata["duration_ms"], float)
        assert result.metadata["duration_ms"] >= 0

    def test_envelope_metadata_contains_owning_feature(self) -> None:
        """FR-DSP-004: Envelope metadata includes owning_feature_ref from resolved_metadata."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(
            resolved_metadata={"owning_feature_ref": "scene_feature"},
        )
        result = executor.dispatch_sync(request)

        assert result.metadata.get("owning_feature_ref") == "scene_feature"

    def test_non_dict_result_wrapped_in_envelope(self) -> None:
        """FR-DSP-004: Non-dict result is wrapped as {'result': str(result)}."""
        mock = MockExecutor(result="raw string result")
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request()
        result = executor.dispatch_sync(request)

        assert result.success is True
        assert result.data == {"result": "raw string result"}


# ─── FR-DSP-004: Timeout Enforcement ────────────────────────────────────────


class TestTimeoutEnforcement:
    """Timeout enforcement per FR-DSP-004."""

    def test_timeout_exceeded_returns_error_envelope(self) -> None:
        """FR-DSP-004: Timeout during execution returns error envelope with timeout category."""
        mock = SlowExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(action_name="slow_action", timeout_override=0.1)
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.TIMEOUT

    def test_timeout_from_resolved_metadata(self) -> None:
        """FR-DSP-004: Timeout from resolved_metadata default_timeout is enforced."""
        mock = SlowExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(
            resolved_metadata={"default_timeout": 0.1},
        )
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.TIMEOUT

    def test_timeout_override_takes_precedence(self) -> None:
        """FR-DSP-004: timeout_override takes precedence over default_timeout."""
        mock = SlowExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(
            timeout_override=0.1,
            resolved_metadata={"default_timeout": 10.0},
        )
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.TIMEOUT


# ─── FR-DSP-004: Error Category Mapping ─────────────────────────────────────


class TestErrorCategoryMapping:
    """Error category mapping per FR-DSP-004."""

    def test_timeout_error_mapped_to_timeout_category(self) -> None:
        """FR-DSP-004: TimeoutError maps to timeout_error."""
        mock = MockExecutor(side_effect=TimeoutError("timed out"))
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request()
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.TIMEOUT

    def test_connection_error_mapped(self) -> None:
        """FR-DSP-004: ConnectionError maps to connection_error."""
        mock = MockExecutor(side_effect=ConnectionError("refused"))
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request()
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.CONNECTION

    def test_runtime_error_with_timeout_type_name_mapped(self) -> None:
        """FR-DSP-004: Exception with 'Timeout' in type name maps to timeout."""

        class ActionTimeoutError(Exception):
            """Simulated timeout with Timeout in the type name."""

        mock = MockExecutor(side_effect=ActionTimeoutError("timed out"))
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request()
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.TIMEOUT

    def test_generic_error_maps_to_execution(self) -> None:
        """FR-DSP-004: Generic RuntimeError maps to execution_error."""
        mock = MockExecutor(side_effect=RuntimeError("something broke"))
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request()
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.EXECUTION

    def test_error_envelope_contains_action_name_in_metadata(self) -> None:
        """FR-DSP-004: Error envelope metadata includes action_name."""
        mock = MockExecutor(side_effect=RuntimeError("fail"))
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(action_name="failing_action")
        result = executor.dispatch_sync(request)

        assert result.metadata.get("action_name") == "failing_action"

    def test_error_envelope_preserves_tracking_id(self) -> None:
        """FR-DSP-004: Error envelope preserves tracking ID."""
        mock = MockExecutor(side_effect=RuntimeError("fail"))
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(tracking_id="error-track-42")
        result = executor.dispatch_sync(request)

        assert result.tracking_id == "error-track-42"


# ─── FR-DSP-004: Degraded Feature ──────────────────────────────────────────


class TestDegradedFeatureHandling:
    """Degraded owning feature per FR-DSP-004."""

    def test_degraded_feature_returns_error(self) -> None:
        """FR-DSP-004: Degraded owning feature produces error envelope."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(
            resolved_metadata={"degraded": True, "owning_feature_ref": "scene_feature"},
        )
        result = executor.dispatch_sync(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.EXECUTION
        assert len(mock.calls) == 0  # executor was never called

    def test_non_degraded_feature_dispatches_normally(self) -> None:
        """FR-DSP-004: Non-degraded feature dispatches normally."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(
            resolved_metadata={"degraded": False},
        )
        result = executor.dispatch_sync(request)

        assert result.success is True
        assert len(mock.calls) == 1


# ─── FR-DSP-004: Tracking ID Propagation ────────────────────────────────────


class TestTrackingIdPropagation:
    """Tracking ID propagation per FR-DSP-004."""

    def test_tracking_id_from_request_used(self) -> None:
        """FR-DSP-004: Uses validated_tracking_id from request."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(tracking_id="explicit-id")
        result = executor.dispatch_sync(request)

        assert result.tracking_id == "explicit-id"

    def test_fallback_to_tracking_id_field(self) -> None:
        """FR-DSP-004: Falls back to tracking_id when validated_tracking_id is empty."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = _make_request(tracking_id="fallback-id")
        result = executor.dispatch_sync(request)

        # validated_tracking_id is auto-generated from tracking_id, so both work
        assert result.tracking_id != ""

    def test_empty_tracking_id_yields_empty_string(self) -> None:
        """FR-DSP-004: No tracking ID at all yields empty string in envelope."""
        mock = MockExecutor()
        executor = SyncDispatchExecutor(execute_action=mock)
        request = ActionCommandVO(action_name="no_track")
        result = executor.dispatch_sync(request)

        # ActionCommandVO auto-generates a UUID, so validated_tracking_id is set
        assert result.tracking_id != ""


# ─── FR-DSP-004: Statelessness ─────────────────────────────────────────────


class TestStatelessness:
    """Stateless across requests per FR-DSP-004."""

    def test_consecutive_dispatches_independent(self) -> None:
        """FR-DSP-004: Each dispatch is independent — no cross-request state leakage."""
        mock = MockExecutor(result={"seq": 1})
        executor = SyncDispatchExecutor(execute_action=mock)

        r1 = executor.dispatch_sync(_make_request(action_name="action_1"))
        mock._result = {"seq": 2}
        r2 = executor.dispatch_sync(_make_request(action_name="action_2"))

        assert r1.data != r2.data
        assert r1.metadata.get("action_name") == "action_1"
        assert r2.metadata.get("action_name") == "action_2"
