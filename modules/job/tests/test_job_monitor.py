"""Tests for JobStatusMonitor — FR-JOB-002.

Exercises snapshot projection, redaction, visibility rules,
and applicability flags. All dependencies mocked.
Run via pytest from repo root.
"""

from __future__ import annotations

import pytest

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    ResultUrl,
    Timestamp,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    CorrelationId,
    ErrorCategory,
    ProgressMessage,
)
from modules.shared.src.job.contract_job_monitor_protocol import IJobMonitor
from modules.shared.src.job.taxonomy_job_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    TERMINAL_JOB_STATES,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    JobStatusSnapshot,
    OperationType,
)

from modules.job.src.capabilities_job_monitor import JobStatusMonitor


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_snapshot(**overrides: object) -> JobStatusSnapshot:
    """Build a JobStatusSnapshot with optional field overrides."""
    base = JobStatusSnapshot(
        job_id=JobId("test-1"),
        state=JOB_STATE_PENDING,
        operation_type=OperationType("render"),
        created_at=Timestamp(1000.0),
        updated_at=Timestamp(1000.0),
    )
    update = {k: v for k, v in overrides.items()}
    return JobStatusSnapshot(**{**dict(base.__dict__), **update})


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def monitor() -> JobStatusMonitor:
    """Fresh JobStatusMonitor instance."""
    return JobStatusMonitor()


# ─── FR-JOB-002: Monitor Task Status — Snapshot Projection ───────────────────


def test_fr_job_002_project_pending_snapshot(monitor: JobStatusMonitor) -> None:
    """Test projection of PENDING snapshot — no result or error visible."""
    raw = _make_snapshot(
        state=JOB_STATE_PENDING,
        progress=Progress(0.0),
        result_url=ResultUrl("/tmp/test.png"),  # Should be hidden
        error=ErrorString("error"),  # Should be hidden
    )

    projected = monitor.project(raw)

    assert projected.state == JOB_STATE_PENDING
    assert projected.result_url is None  # Result only visible after COMPLETED
    assert projected.error is None  # Error only visible after FAILED
    assert projected.is_terminal is False
    assert projected.is_cancellable is True
    assert projected.progress_applicable is False


def test_fr_job_002_project_running_snapshot(monitor: JobStatusMonitor) -> None:
    """Test projection of RUNNING snapshot — progress applicable, result hidden."""
    raw = _make_snapshot(
        state=JOB_STATE_RUNNING,
        progress=Progress(50.0),
        progress_message=ProgressMessage("Halfway"),
        result_url=ResultUrl("/tmp/test.png"),  # Should be hidden
    )

    projected = monitor.project(raw)

    assert projected.state == JOB_STATE_RUNNING
    assert projected.result_url is None
    assert projected.error is None
    assert projected.is_terminal is False
    assert projected.is_cancellable is True
    assert projected.progress_applicable is True


def test_fr_job_002_project_completed_snapshot(monitor: JobStatusMonitor) -> None:
    """Test projection of COMPLETED snapshot — result visible, progress at 100%."""
    raw = _make_snapshot(
        state=JOB_STATE_COMPLETED,
        progress=Progress(100.0),
        progress_message=ProgressMessage("Render complete"),
        result_url=ResultUrl("/tmp/render.png"),
    )

    projected = monitor.project(raw)

    assert projected.state == JOB_STATE_COMPLETED
    assert projected.result_url == ResultUrl("/tmp/render.png")  # Result visible
    assert projected.error is None  # No error on completed
    assert projected.is_terminal is True
    assert projected.is_cancellable is False
    assert projected.progress_applicable is False


def test_fr_job_002_project_failed_snapshot(monitor: JobStatusMonitor) -> None:
    """Test projection of FAILED snapshot — error visible, sanitized."""
    raw = _make_snapshot(
        state=JOB_STATE_FAILED,
        error=ErrorString("Render failed: out of memory"),
        error_category=ErrorCategory("MEMORY"),
    )

    projected = monitor.project(raw)

    assert projected.state == JOB_STATE_FAILED
    assert projected.error == ErrorString("Render failed: out of memory")  # Error visible
    assert projected.error_category == ErrorCategory("MEMORY")
    assert projected.result_url is None  # No result on failed
    assert projected.is_terminal is True
    assert projected.is_cancellable is False
    assert projected.progress_applicable is False


def test_fr_job_002_project_cancelled_snapshot(monitor: JobStatusMonitor) -> None:
    """Test projection of CANCELLED snapshot — terminal, no result or error."""
    raw = _make_snapshot(
        state=JOB_STATE_CANCELLED,
        metadata=(("api_key", "secret-123"), ("safe", "value")),
    )

    projected = monitor.project(raw)

    assert projected.state == JOB_STATE_CANCELLED
    assert projected.is_terminal is True
    assert projected.is_cancellable is False


# ─── Metadata Redaction ──────────────────────────────────────────────────────


def test_fr_job_002_project_redacts_sensitive_metadata(monitor: JobStatusMonitor) -> None:
    """Test that sensitive metadata is redacted before snapshot emission."""
    raw = _make_snapshot(
        state=JOB_STATE_PENDING,
        metadata=(
            ("api_key", "secret-key-abc"),
            ("token", "jwt-token-xyz"),
            ("safe_field", "public value"),
            ("password", "hunter2"),
        ),
    )

    projected = monitor.project(raw)

    # Redacted fields should not contain secrets
    for key, val in projected.metadata:
        if key in ("api_key", "token", "password"):
            assert "secret-key-abc" not in val
            assert "jwt-token-xyz" not in val
            assert "hunter2" not in val


def test_fr_job_002_project_empty_metadata_returns_empty(monitor: JobStatusMonitor) -> None:
    """Test that empty metadata returns empty projected metadata."""
    raw = _make_snapshot(state=JOB_STATE_PENDING, metadata=tuple())
    projected = monitor.project(raw)
    assert projected.metadata == tuple()


# ─── Visibility Rules ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "state,result_url,error",
    [
        (JOB_STATE_COMPLETED, ResultUrl("/tmp/out.png"), None),
        (JOB_STATE_FAILED, None, ErrorString("fail")),
        (JOB_STATE_PENDING, ResultUrl("/tmp/test.png"), ErrorString("error")),
        (JOB_STATE_RUNNING, ResultUrl("/tmp/test.png"), ErrorString("error")),
        (JOB_STATE_CANCELLED, ResultUrl("/tmp/out.png"), ErrorString("error")),
    ],
)
def test_fr_job_002_result_visible_only_after_completed(
    monitor: JobStatusMonitor,
    state: JobState,
    result_url: ResultUrl | None,
    error: ErrorString | None,
) -> None:
    """Test that result reference is visible only after completed state."""
    raw = _make_snapshot(state=state, result_url=result_url, error=error)
    projected = monitor.project(raw)

    if state == JOB_STATE_COMPLETED:
        assert projected.result_url == result_url
    else:
        assert projected.result_url is None


@pytest.mark.parametrize(
    "state,error",
    [
        (JOB_STATE_FAILED, ErrorString("fail")),
        (JOB_STATE_COMPLETED, ErrorString("error")),
        (JOB_STATE_PENDING, ErrorString("error")),
        (JOB_STATE_RUNNING, ErrorString("error")),
        (JOB_STATE_CANCELLED, ErrorString("error")),
    ],
)
def test_fr_job_002_error_visible_only_after_failed(
    monitor: JobStatusMonitor,
    state: JobState,
    error: ErrorString | None,
) -> None:
    """Test that error detail is visible only after failed state."""
    raw = _make_snapshot(state=state, error=error)
    projected = monitor.project(raw)

    if state == JOB_STATE_FAILED:
        assert projected.error == error
    else:
        assert projected.error is None


# ─── Cancellable Flag ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "state,is_cancellable",
    [
        (JOB_STATE_PENDING, True),
        (JOB_STATE_RUNNING, True),
        (JOB_STATE_COMPLETED, False),
        (JOB_STATE_FAILED, False),
        (JOB_STATE_CANCELLED, False),
    ],
)
def test_fr_job_002_cancellable_flag_exposed(
    monitor: JobStatusMonitor,
    state: JobState,
    is_cancellable: bool,
) -> None:
    """Test that cancellable flag is exposed correctly based on state."""
    raw = _make_snapshot(state=state)
    projected = monitor.project(raw)
    assert projected.is_cancellable == is_cancellable


# ─── Progress Applicability ──────────────────────────────────────────────────


@pytest.mark.parametrize(
    "state,progress_applicable",
    [
        (JOB_STATE_RUNNING, True),
        (JOB_STATE_PENDING, False),
        (JOB_STATE_COMPLETED, False),
        (JOB_STATE_FAILED, False),
        (JOB_STATE_CANCELLED, False),
    ],
)
def test_fr_job_002_progress_applicable_flag(
    monitor: JobStatusMonitor,
    state: JobState,
    progress_applicable: bool,
) -> None:
    """Test that progress applicability is indicated correctly per state."""
    raw = _make_snapshot(state=state)
    projected = monitor.project(raw)
    assert projected.progress_applicable == progress_applicable


# ─── Utility & Edge Cases ────────────────────────────────────────────────────


def test_monitor_repr(monitor: JobStatusMonitor) -> None:
    """Test monitor string representation."""
    assert repr(monitor) == "<JobStatusMonitor>"


def test_project_preserves_job_id(monitor: JobStatusMonitor) -> None:
    """Test that projection preserves the original job identifier."""
    raw = _make_snapshot(state=JOB_STATE_PENDING, job_id=JobId("unique-id-999"))
    projected = monitor.project(raw)
    assert projected.job_id == JobId("unique-id-999")


def test_project_preserves_operation_type(monitor: JobStatusMonitor) -> None:
    """Test that projection preserves the original operation type."""
    raw = _make_snapshot(
        state=JOB_STATE_PENDING,
        operation_type=OperationType("download"),
    )
    projected = monitor.project(raw)
    assert projected.operation_type == OperationType("download")


def test_project_preserves_timestamps(monitor: JobStatusMonitor) -> None:
    """Test that projection preserves created_at and updated_at timestamps."""
    raw = _make_snapshot(
        state=JOB_STATE_PENDING,
        created_at=Timestamp(1000.0),
        updated_at=Timestamp(1001.0),
    )
    projected = monitor.project(raw)
    assert projected.created_at == Timestamp(1000.0)
    assert projected.updated_at == Timestamp(1001.0)


def test_project_preserves_correlation_id(monitor: JobStatusMonitor) -> None:
    """Test that projection preserves the correlation identifier."""
    raw = _make_snapshot(
        state=JOB_STATE_PENDING,
        correlation_id=CorrelationId("req-abc-123"),
    )
    projected = monitor.project(raw)
    assert projected.correlation_id == CorrelationId("req-abc-123")
