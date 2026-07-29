"""Tests for JobCapacityChecker — FR-JOB-005.

Exercises capacity evaluation, decision outcomes, and context inclusion.
Run via pytest from repo root.
"""

from __future__ import annotations

import pytest

from modules.job.src.capabilities_job_checker import JobCapacityChecker
from modules.shared.src.job.taxonomy_job_vo import (
    JobPolicy,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_policy(**overrides: object) -> JobPolicy:
    """Build a JobPolicy with optional field overrides."""
    base = JobPolicy()
    update = {k: v for k, v in overrides.items()}
    return JobPolicy(**{**dict(base.__dict__), **update})


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def checker() -> JobCapacityChecker:
    """Fresh JobCapacityChecker instance."""
    return JobCapacityChecker()


# ─── FR-JOB-005: Enforce Background Capacity ────────────────────────────────


def test_fr_job_005_accepts_under_limit(checker: JobCapacityChecker) -> None:
    """Test that capacity evaluation accepts when under limit."""
    policy = _make_policy(max_active=10)
    decision = checker.evaluate(active_count=5, policy=policy)

    assert decision.accepted is True
    assert decision.available == 5
    assert decision.active == 5
    assert decision.limit == 10
    assert decision.reason == ""


def test_fr_job_005_accepts_one_over_limit(checker: JobCapacityChecker) -> None:
    """Test that capacity accepts when one slot remaining."""
    policy = _make_policy(max_active=5)
    decision = checker.evaluate(active_count=4, policy=policy)

    assert decision.accepted is True
    assert decision.available == 1


def test_fr_job_005_rejects_at_limit(checker: JobCapacityChecker) -> None:
    """Test that capacity rejects when at limit with context."""
    policy = _make_policy(max_active=5)
    decision = checker.evaluate(active_count=5, policy=policy)

    assert decision.accepted is False
    assert decision.available == 0
    assert decision.active == 5
    assert decision.limit == 5
    assert "Background capacity exceeded" in decision.reason
    assert "5/5" in decision.reason


def test_fr_job_005_rejects_over_limit(checker: JobCapacityChecker) -> None:
    """Test that capacity rejects when over limit."""
    policy = _make_policy(max_active=5)
    decision = checker.evaluate(active_count=10, policy=policy)

    assert decision.accepted is False
    assert decision.available == 0
    assert decision.active == 10


def test_fr_job_005_zero_active_accepted(checker: JobCapacityChecker) -> None:
    """Test that zero active tasks are accepted."""
    policy = _make_policy(max_active=5)
    decision = checker.evaluate(active_count=0, policy=policy)

    assert decision.accepted is True
    assert decision.available == 5


def test_fr_job_005_capacity_includes_active_count_context(checker: JobCapacityChecker) -> None:
    """Test that capacity error includes current active count for retry decisions."""
    policy = _make_policy(max_active=3)
    decision = checker.evaluate(active_count=3, policy=policy)

    assert decision.reason == "Background capacity exceeded: 3/3 active tasks"


def test_fr_job_005_large_limit(checker: JobCapacityChecker) -> None:
    """Test with large limit value."""
    policy = _make_policy(max_active=1000)
    decision = checker.evaluate(active_count=999, policy=policy)

    assert decision.accepted is True
    assert decision.available == 1


def test_fr_job_005_limit_one(checker: JobCapacityChecker) -> None:
    """Test with limit of one — single slot capacity."""
    policy = _make_policy(max_active=1)
    decision = checker.evaluate(active_count=0, policy=policy)

    assert decision.accepted is True
    assert decision.available == 1

    decision_rejected = checker.evaluate(active_count=1, policy=policy)
    assert decision_rejected.accepted is False
    assert decision_rejected.available == 0


# ─── Utility & Edge Cases ────────────────────────────────────────────────────


def test_checker_repr(checker: JobCapacityChecker) -> None:
    """Test checker string representation."""
    assert repr(checker) == "<JobCapacityChecker>"


def test_decision_fields_complete(checker: JobCapacityChecker) -> None:
    """Test that CapacityDecision includes all required fields."""
    policy = _make_policy(max_active=5)
    decision = checker.evaluate(active_count=3, policy=policy)

    assert isinstance(decision.accepted, bool)
    assert isinstance(decision.active, int)
    assert isinstance(decision.limit, int)
    assert isinstance(decision.available, int)
    assert isinstance(decision.reason, str)


def test_decision_rejected_has_reason(checker: JobCapacityChecker) -> None:
    """Test that rejected decisions always have a reason."""
    policy = _make_policy(max_active=5)
    decision = checker.evaluate(active_count=5, policy=policy)

    assert decision.reason != ""
    assert len(decision.reason) > 0


def test_decision_accepted_empty_reason(checker: JobCapacityChecker) -> None:
    """Test that accepted decisions have empty reason."""
    policy = _make_policy(max_active=5)
    decision = checker.evaluate(active_count=2, policy=policy)

    assert decision.reason == ""
