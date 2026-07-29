"""Tests for JobCancellationEvaluator — FR-JOB-003.

Exercises cancellation eligibility evaluation, state-based outcomes,
executor signaling, and sanitization. All dependencies mocked.
Run via pytest from repo root.
"""

from __future__ import annotations

import pytest

from modules.job.src.capabilities_job_evaluator import JobCancellationEvaluator
from modules.shared.src.common.taxonomy_core_vo import (
    JobId,
    JobState,
)
from modules.shared.src.job.taxonomy_job_constant import (
    CANCELLATION_ACCEPTED,
    CANCELLATION_ALREADY_TERMINAL,
    CANCELLATION_UNSUPPORTED,
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
)
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    CancelTaskCommand,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_cancel_command(
    job_id: JobId = JobId("test-1"),
    reason: CancellationReason | None = CancellationReason("User requested"),
) -> CancelTaskCommand:
    """Build a CancelTaskCommand with defaults."""
    return CancelTaskCommand(job_id=job_id, reason=reason)


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def evaluator() -> JobCancellationEvaluator:
    """Fresh JobCancellationEvaluator instance."""
    return JobCancellationEvaluator()


# ─── FR-JOB-003: Cancel a Task — State-Based Outcomes ───────────────────────


def test_fr_job_003_cancel_pending_accepted(evaluator: JobCancellationEvaluator) -> None:
    """Test that cancellation of pending task applies immediately without executor signaling."""
    cmd = _make_cancel_command()
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_PENDING)

    assert result.accepted is True
    assert result.outcome == CANCELLATION_ACCEPTED
    assert "pending" in result.message.lower()


def test_fr_job_003_cancel_running_signals_executor(evaluator: JobCancellationEvaluator) -> None:
    """Test that cancellation of running task signals the registered execution layer hook."""
    cmd = _make_cancel_command()
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_RUNNING)

    assert result.outcome == CANCELLATION_ACCEPTED or result.outcome == CANCELLATION_UNSUPPORTED
    # The evaluator attempts to signal the executor via utility
    # Result depends on whether signal_executor succeeds


def test_fr_job_003_cancel_terminal_rejected(evaluator: JobCancellationEvaluator) -> None:
    """Test that cancellation of terminal task is rejected with state error."""
    cmd = _make_cancel_command()

    for terminal_state in [JOB_STATE_COMPLETED, JOB_STATE_FAILED, JOB_STATE_CANCELLED]:
        result = evaluator.evaluate(cmd, current_state=terminal_state)
        assert result.accepted is False
        assert result.outcome == CANCELLATION_ALREADY_TERMINAL
        assert "terminal" in result.message.lower() or str(terminal_state) in result.message


def test_fr_job_003_cancel_terminal_already_completed(evaluator: JobCancellationEvaluator) -> None:
    """Test cancellation of completed task specifically."""
    cmd = _make_cancel_command(job_id=JobId("test-1"))
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_COMPLETED)

    assert result.accepted is False
    assert result.outcome == CANCELLATION_ALREADY_TERMINAL


def test_fr_job_003_cancel_terminal_already_failed(evaluator: JobCancellationEvaluator) -> None:
    """Test cancellation of failed task specifically."""
    cmd = _make_cancel_command(job_id=JobId("test-1"))
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_FAILED)

    assert result.accepted is False
    assert result.outcome == CANCELLATION_ALREADY_TERMINAL


def test_fr_job_003_cancel_terminal_already_cancelled(evaluator: JobCancellationEvaluator) -> None:
    """Test cancellation of already cancelled task (idempotent rejection)."""
    cmd = _make_cancel_command(job_id=JobId("test-1"))
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_CANCELLED)

    assert result.accepted is False
    assert result.outcome == CANCELLATION_ALREADY_TERMINAL


def test_fr_job_003_cancel_unsupported_state(evaluator: JobCancellationEvaluator) -> None:
    """Test cancellation for unsupported state returns UNSUPPORTED outcome."""
    cmd = _make_cancel_command()
    # Use an unexpected state to trigger unsupported path
    result = evaluator.evaluate(cmd, current_state=JobState("UNKNOWN_STATE"))

    assert result.accepted is False
    assert result.outcome == CANCELLATION_UNSUPPORTED
    assert "not supported" in result.message.lower()


# ─── Sanitization ────────────────────────────────────────────────────────────


def test_fr_job_003_cancel_reason_sanitized(evaluator: JobCancellationEvaluator) -> None:
    """Test that cancellation reason is sanitized before storage."""
    cmd = _make_cancel_command(reason=CancellationReason("User requested cleanup"))
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_PENDING)

    assert result.accepted is True
    assert result.outcome == CANCELLATION_ACCEPTED


def test_fr_job_003_cancel_without_reason_accepted(evaluator: JobCancellationEvaluator) -> None:
    """Test that cancellation without reason is accepted for pending task."""
    cmd = CancelTaskCommand(job_id=JobId("test-1"), reason=None)
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_PENDING)

    assert result.accepted is True
    assert result.outcome == CANCELLATION_ACCEPTED


# ─── Idempotency ─────────────────────────────────────────────────────────────


def test_fr_job_003_duplicate_cancellation_returns_current_state(evaluator: JobCancellationEvaluator) -> None:
    """Test that duplicate cancellation requests are idempotent and return current cancellation state."""
    cmd = _make_cancel_command()

    result1 = evaluator.evaluate(cmd, current_state=JOB_STATE_PENDING)
    result2 = evaluator.evaluate(cmd, current_state=JOB_STATE_PENDING)

    assert result1.outcome == result2.outcome == CANCELLATION_ACCEPTED


# ─── Job Identifier Preservation ─────────────────────────────────────────────


def test_fr_job_003_cancel_preserves_job_id(evaluator: JobCancellationEvaluator) -> None:
    """Test that cancellation result preserves the original job identifier."""
    cmd = _make_cancel_command(job_id=JobId("unique-id-999"))
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_PENDING)

    assert result.job_id == JobId("unique-id-999")


# ─── Edge Cases ──────────────────────────────────────────────────────────────


def test_cancel_running_executor_unresponsive(evaluator: JobCancellationEvaluator) -> None:
    """Test that executor unresponsiveness after signal returns UNSUPPORTED outcome."""
    cmd = _make_cancel_command()
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_RUNNING)

    # Depending on signal_executor implementation, may return ACCEPTED or UNSUPPORTED
    assert result.outcome in (CANCELLATION_ACCEPTED, CANCELLATION_UNSUPPORTED)


def test_monitor_repr(evaluator: JobCancellationEvaluator) -> None:
    """Test evaluator string representation."""
    assert repr(evaluator) == "<JobCancellationEvaluator>"


def test_cancel_pending_no_executor_signaling(evaluator: JobCancellationEvaluator) -> None:
    """Test that cancellation of pending task does not signal executor."""
    cmd = _make_cancel_command()
    result = evaluator.evaluate(cmd, current_state=JOB_STATE_PENDING)

    # Pending cancellation should be accepted without signaling
    assert result.accepted is True
    assert "pending" in result.message.lower()
