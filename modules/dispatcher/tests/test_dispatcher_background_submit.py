"""Tests for background submission capability — FR-DSP-005.

FR-DSP-005: Submit Background Action
- Only for actions with background eligibility flag
- Creates job via job feature, returns task reference
- Capacity limit enforced; exhaustion → capacity error, no orphan job
- Atomic: job created + acknowledged before success
- Duplicate with idempotency hint may return existing task ref
- Result clearly indicates polling required
"""

from __future__ import annotations

import pytest

from modules.dispatcher.src.capabilities_background_submit import BackgroundSubmitExecutor
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_dispatch_error import DispatchErrorCategory
from modules.shared.src.job.taxonomy_job_vo import (
    CreateTaskCommand,
    JobStatusSnapshot,
)

# ─── Helpers ────────────────────────────────────────────────────────────────


class _MockState:
    """Minimal state wrapper exposing .value for snapshot.state.value access."""

    def __init__(self, value: str) -> None:
        self.value = value


class MockJobTracker:
    """Mock job lifecycle tracker for testing background submission."""

    def __init__(
        self,
        job_id: str = "job-001",
        state_value: str = "pending",
        active_count_value: int = 0,
        should_fail: bool = False,
    ) -> None:
        self._job_id = job_id
        self._state_value = state_value
        self._active_count_value = active_count_value
        self._should_fail = should_fail
        self.created_commands: list[CreateTaskCommand] = []

    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        self.created_commands.append(command)
        if self._should_fail:
            raise RuntimeError("Job creation failed")

        from modules.shared.src.common.taxonomy_core_vo import JobId, Timestamp

        return JobStatusSnapshot(
            job_id=JobId(self._job_id),
            state=_MockState(self._state_value),  # type: ignore[arg-type]
            operation_type=command.operation_type,
            created_at=Timestamp(0.0),
            updated_at=Timestamp(0.0),
        )

    def active_count(self) -> int:
        return self._active_count_value


class MissingCreateTaskTracker:
    """Tracker with active_count but no create_task — should trigger interface error."""

    def active_count(self) -> int:
        return 5


def _make_request(
    action_name: str = "render_scene",
    tracking_id: str | None = "track-bg-001",
    resolved_metadata: dict | None = None,
    execution_mode: str | None = None,
) -> ActionCommandVO:
    """Create an ActionCommandVO for background submission testing."""
    defaults: dict[str, object] = {"action_name": action_name}
    if tracking_id is not None:
        defaults["tracking_id"] = tracking_id
    if resolved_metadata is not None:
        defaults["resolved_metadata"] = resolved_metadata
    if execution_mode is not None:
        defaults["execution_mode"] = execution_mode
    return ActionCommandVO(**defaults)  # type: ignore[arg-type]


# ─── FR-DSP-005: Constructor Validation ─────────────────────────────────────


class TestConstructorValidation:
    """BackgroundSubmitExecutor constructor validation."""

    def test_none_tracker_raises_value_error(self) -> None:
        """FR-DSP-005: None job_tracker raises ValueError at construction."""
        with pytest.raises(ValueError, match="requires a job tracker"):
            BackgroundSubmitExecutor(job_tracker=None)

    def test_valid_tracker_accepted(self) -> None:
        """FR-DSP-005: Valid tracker is accepted."""
        executor = BackgroundSubmitExecutor(job_tracker=MockJobTracker())
        assert executor is not None


# ─── FR-DSP-005: Background Eligibility ────────────────────────────────────


class TestBackgroundEligibility:
    """Background eligibility enforcement per FR-DSP-005."""

    def test_ineligible_action_returns_unsupported_error(self) -> None:
        """FR-DSP-005: Non-background-eligible action returns unsupported error."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": False},
        )
        result = executor.submit_background(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.UNSUPPORTED
        assert len(tracker.created_commands) == 0

    def test_eligible_action_proceeds(self) -> None:
        """FR-DSP-005: Background-eligible action proceeds to job creation."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is True
        assert len(tracker.created_commands) == 1

    def test_missing_flag_defaults_to_ineligible(self) -> None:
        """FR-DSP-005: Missing background_eligibility_flag defaults to ineligible."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(resolved_metadata={})
        result = executor.submit_background(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.UNSUPPORTED


# ─── FR-DSP-005: Capacity Enforcement ──────────────────────────────────────


class TestCapacityEnforcement:
    """Capacity enforcement per FR-DSP-005."""

    def test_at_capacity_returns_capacity_error(self) -> None:
        """FR-DSP-005: Capacity exceeded returns capacity error, no job created."""
        tracker = MockJobTracker(active_count_value=50)
        executor = BackgroundSubmitExecutor(job_tracker=tracker, background_capacity=50)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.CAPACITY
        assert len(tracker.created_commands) == 0

    def test_over_capacity_returns_capacity_error(self) -> None:
        """FR-DSP-005: Over capacity returns capacity error."""
        tracker = MockJobTracker(active_count_value=100)
        executor = BackgroundSubmitExecutor(job_tracker=tracker, background_capacity=50)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.CAPACITY

    def test_under_capacity_proceeds(self) -> None:
        """FR-DSP-005: Under capacity proceeds to job creation."""
        tracker = MockJobTracker(active_count_value=10)
        executor = BackgroundSubmitExecutor(job_tracker=tracker, background_capacity=50)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is True
        assert len(tracker.created_commands) == 1

    def test_exact_boundary_capacity_rejected(self) -> None:
        """FR-DSP-005: Exactly at capacity is rejected (>= check)."""
        tracker = MockJobTracker(active_count_value=50)
        executor = BackgroundSubmitExecutor(job_tracker=tracker, background_capacity=50)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is False


# ─── FR-DSP-005: Fail-Closed on Missing Interface ───────────────────────────


class TestFailClosedCapacity:
    """Fail-closed when tracker lacks active_count per WARNING DF-2."""

    def test_missing_active_count_raises_runtime_error(self) -> None:
        """Tracker without active_count triggers RuntimeError (fail-closed)."""
        tracker = object()  # bare object with no methods
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        with pytest.raises(RuntimeError, match="active_count"):
            executor.submit_background(request)


# ─── FR-DSP-005: Job Creation ───────────────────────────────────────────────


class TestJobCreation:
    """Job creation per FR-DSP-005."""

    def test_success_envelope_contains_task_reference(self) -> None:
        """FR-DSP-005: Success envelope contains task_reference."""
        tracker = MockJobTracker(job_id="job-abc")
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is True
        assert result.data is not None
        assert result.data.get("task_reference") == "job-abc"

    def test_envelope_metadata_contains_action_name(self) -> None:
        """FR-DSP-005: Envelope metadata includes action_name."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            action_name="render_scene",
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.metadata.get("action_name") == "render_scene"

    def test_envelope_metadata_indicates_polling_required(self) -> None:
        """FR-DSP-005: Envelope metadata indicates polling is required."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.metadata.get("polling_required") is True

    def test_envelope_contains_polling_warning(self) -> None:
        """FR-DSP-005: Success envelope includes polling warning."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert any("polling" in w.lower() for w in result.warnings)

    def test_tracking_id_propagated(self) -> None:
        """FR-DSP-005: Tracking ID propagated to envelope."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            tracking_id="bg-track-99",
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.tracking_id == "bg-track-99"

    def test_create_task_command_contains_operation_type(self) -> None:
        """FR-DSP-005: CreateTaskCommand uses action_name as operation_type."""
        tracker = MockJobTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            action_name="bake_lighting",
            resolved_metadata={"background_eligibility_flag": True},
        )
        executor.submit_background(request)

        assert len(tracker.created_commands) == 1
        cmd = tracker.created_commands[0]
        assert str(cmd.operation_type) == "bake_lighting"


# ─── FR-DSP-005: Job Creation Failure ──────────────────────────────────────


class TestJobCreationFailure:
    """Job creation failure per FR-DSP-005."""

    def test_creation_failure_returns_execution_error(self) -> None:
        """FR-DSP-005: Job creation failure returns execution error."""
        tracker = MockJobTracker(should_fail=True)
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.EXECUTION
        assert result.tracking_id == "track-bg-001"

    def test_no_task_reference_on_failure(self) -> None:
        """FR-DSP-005: Failed job creation yields no task reference."""
        tracker = MockJobTracker(should_fail=True)
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is False
        assert result.data is None or result.data.get("task_reference") is None


# ─── FR-DSP-005: Tracker Interface Missing ──────────────────────────────────


class TestTrackerInterfaceMissing:
    """Tracker lacking task creation interface per FR-DSP-005."""

    def test_no_create_or_track_returns_execution_error(self) -> None:
        """FR-DSP-005: Tracker with active_count but no create_task/track_new_task returns error."""
        tracker = MissingCreateTaskTracker()
        executor = BackgroundSubmitExecutor(job_tracker=tracker)
        request = _make_request(
            resolved_metadata={"background_eligibility_flag": True},
        )
        result = executor.submit_background(request)

        assert result.success is False
        assert result.error_category == DispatchErrorCategory.EXECUTION
