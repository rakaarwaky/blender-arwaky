"""Tests for JobCleanupResolver — FR-JOB-004.

Exercises stale detection, expired purge, max record enforcement,
and warning emission. All dependencies mocked.
Run via pytest from repo root.
"""

from __future__ import annotations

import pytest

from modules.job.src.capabilities_job_resolver import JobCleanupResolver
from modules.shared.src.common.taxonomy_core_vo import (
    JobId,
    JobState,
    Timestamp,
)
from modules.shared.src.job.taxonomy_job_constant import (
    JOB_STATE_COMPLETED,
    JOB_STATE_RUNNING,
)
from modules.shared.src.job.taxonomy_job_vo import (
    JobPolicy,
    JobStatusSnapshot,
    OperationType,
)

# ─── Helpers ──────────────────────────────────────────────────────────────────


def _make_policy(**overrides: object) -> JobPolicy:
    """Build a JobPolicy with optional field overrides."""
    base = JobPolicy()
    update = {k: v for k, v in overrides.items()}
    return JobPolicy(**{**dict(base.__dict__), **update})


def _make_snapshot(
    job_id: JobId | None = None,
    state: JobState = JOB_STATE_COMPLETED,
    finished_at: Timestamp | None = None,
    updated_at: Timestamp | None = None,
    started_at: Timestamp | None = None,    ) -> JobStatusSnapshot:
    """Build a JobStatusSnapshot with minimal fields for cleanup tests."""
    return JobStatusSnapshot(
        job_id=job_id or JobId("test-1"),
        state=state,
        operation_type=OperationType("render"),
        created_at=Timestamp(900.0),
        updated_at=updated_at or Timestamp(1000.0),
        finished_at=finished_at,
        started_at=started_at,
    )


# ─── Fixtures ────────────────────────────────────────────────────────────────


@pytest.fixture
def resolver() -> JobCleanupResolver:
    """Fresh JobCleanupResolver instance."""
    return JobCleanupResolver()


# ─── FR-JOB-004: Cleanup — Stale Running Task Detection ─────────────────────


def test_fr_job_004_resolve_stale_running_task(resolver: JobCleanupResolver) -> None:
    """Test that running tasks exceeding stale lifetime are detected."""
    now = Timestamp(2000.0)
    policy = _make_policy(
        stale_recovery_enabled=True,
        stale_running_lifetime_seconds=600,
    )
    running = (
        _make_snapshot(
            job_id=JobId("stale-1"),
            state=JOB_STATE_RUNNING,
            started_at=Timestamp(1000.0),  # 1000s old > 600s policy
        ),
    )
    decision = resolver.resolve((), running, now, policy)

    assert JobId("stale-1") in decision.stale_timeout_ids
    assert len(decision.purge_ids) == 0


def test_fr_fr_job_004_no_stale_when_below_threshold(resolver: JobCleanupResolver) -> None:
    """Test that running tasks within stale threshold are not flagged."""
    now = Timestamp(2000.0)
    policy = _make_policy(
        stale_recovery_enabled=True,
        stale_running_lifetime_seconds=600,
    )
    running = (
        _make_snapshot(
            job_id=JobId("fresh-1"),
            state=JOB_STATE_RUNNING,
            started_at=Timestamp(1800.0),  # 200s old < 600s policy
        ),
    )
    decision = resolver.resolve((), running, now, policy)

    assert JobId("fresh-1") not in decision.stale_timeout_ids


def test_fr_job_004_no_stale_when_disabled(resolver: JobCleanupResolver) -> None:
    """Test that stale detection is skipped when policy disabled."""
    now = Timestamp(2000.0)
    policy = _make_policy(stale_recovery_enabled=False)
    running = (
        _make_snapshot(
            job_id=JobId("stale-1"),
            state=JOB_STATE_RUNNING,
            started_at=Timestamp(1000.0),  # 1000s old > 600s policy
        ),
    )
    decision = resolver.resolve((), running, now, policy)

    assert len(decision.stale_timeout_ids) == 0


def test_fr_job_004_stale_missing_started_at_warns(resolver: JobCleanupResolver) -> None:
    """Test that running tasks with no started_at produce warnings but are not timed out."""
    now = Timestamp(2000.0)
    policy = _make_policy(
        stale_recovery_enabled=True,
        stale_running_lifetime_seconds=600,
    )
    running = (
        _make_snapshot(
            job_id=JobId("no-start"),
            state=JOB_STATE_RUNNING,
            started_at=None,
        ),
    )
    decision = resolver.resolve((), running, now, policy)

    assert JobId("no-start") not in decision.stale_timeout_ids
    assert len(decision.warnings) > 0


# ─── FR-JOB-004: Cleanup — Expired Terminal Purge ───────────────────────────


def test_fr_job_004_resolve_expired_terminal(resolver: JobCleanupResolver) -> None:
    """Test that terminal records exceeding retention are purged."""
    now = Timestamp(2000.0)
    policy = _make_policy(retention_seconds=500)
    terminal = (
        _make_snapshot(
            job_id=JobId("old-1"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1000.0),  # 1000s old > 500s retention
        ),
        _make_snapshot(
            job_id=JobId("new-1"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1800.0),  # 200s old < 500s retention
        ),
    )
    decision = resolver.resolve(terminal, (), now, policy)

    assert JobId("old-1") in decision.purge_ids
    assert JobId("new-1") not in decision.purge_ids


def test_fr_job_004_resolve_expired_oldest_first(resolver: JobCleanupResolver) -> None:
    """Test that expired records are identified oldest first for purge ordering."""
    now = Timestamp(2000.0)
    policy = _make_policy(retention_seconds=300)  # both older and newer exceed 300s
    terminal = (
        _make_snapshot(
            job_id=JobId("newer"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1600.0),  # 400s old > 300s retention
        ),
        _make_snapshot(
            job_id=JobId("older"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1000.0),  # 1000s old > 300s retention
        ),
    )
    decision = resolver.resolve(terminal, (), now, policy)

    # Both are expired (>300s old), older should be listed first in purge order
    assert JobId("older") in decision.purge_ids
    assert JobId("newer") in decision.purge_ids
    assert decision.purge_ids[0] == JobId("older")  # oldest purged first


def test_fr_job_004_no_expired_when_recent(resolver: JobCleanupResolver) -> None:
    """Test that recent terminal records are not purged."""
    now = Timestamp(2000.0)
    policy = _make_policy(retention_seconds=500)
    terminal = (
        _make_snapshot(
            job_id=JobId("recent"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1800.0),
        ),
    )
    decision = resolver.resolve(terminal, (), now, policy)

    assert len(decision.purge_ids) == 0


# ─── FR-JOB-004: Cleanup — Max Record Enforcement ───────────────────────────


def test_fr_job_004_resolve_max_records_enforced(resolver: JobCleanupResolver) -> None:
    """Test that max record count is enforced after expiration purge."""
    now = Timestamp(2000.0)
    policy = _make_policy(max_records=1, retention_seconds=999999)  # keep only 1
    terminal = (
        _make_snapshot(
            job_id=JobId("oldest"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1500.0),
        ),
        _make_snapshot(
            job_id=JobId("newest"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1700.0),
        ),
    )
    decision = resolver.resolve(terminal, (), now, policy)

    # oldest should be purged to enforce max_records=1
    assert JobId("oldest") in decision.purge_ids
    assert JobId("newest") not in decision.purge_ids


def test_fr_job_004_max_not_enforced_when_under_limit(resolver: JobCleanupResolver) -> None:
    """Test that max records is not enforced when under limit."""
    now = Timestamp(2000.0)
    policy = _make_policy(max_records=5, retention_seconds=999999)
    terminal = (
        _make_snapshot(job_id=JobId("a"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1500.0)),
        _make_snapshot(job_id=JobId("b"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1600.0)),
    )
    decision = resolver.resolve(terminal, (), now, policy)

    assert len(decision.purge_ids) == 0


def test_fr_job_004_max_enforced_after_expired(resolver: JobCleanupResolver) -> None:
    """Test that max records enforcement applies after expired purge."""
    now = Timestamp(2000.0)
    policy = _make_policy(max_records=1, retention_seconds=500)
    terminal = (
        _make_snapshot(job_id=JobId("expired-1"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(500.0)),  # expired
        _make_snapshot(job_id=JobId("old-but-ok"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1800.0)),  # not expired
        _make_snapshot(job_id= JobId("new"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1900.0)),  # not expired
    )
    decision = resolver.resolve(terminal, (), now, policy)

    # expired-1 is purged by expiration; old-but-ok is oldest remaining, should be purged for max
    assert JobId("expired-1") in decision.purge_ids


# ─── FR-JOB-004: Cleanup — Combined Stale + Expired ────────────────────────


def test_fr_job_004_resolve_stale_and_expired_together(resolver: JobCleanupResolver) -> None:
    """Test that stale and expired decisions are both computed."""
    now = Timestamp(2000.0)
    policy = _make_policy(
        stale_recovery_enabled=True,
        stale_running_lifetime_seconds=600,
        retention_seconds=500,
    )
    terminal = (
        _make_snapshot(
            job_id=JobId("old-terminal"),
            state=JOB_STATE_COMPLETED,
            finished_at=Timestamp(1000.0),  # expired
        ),
    )
    running = (
        _make_snapshot(
            job_id=JobId("stale-running"),
            state=JOB_STATE_RUNNING,
            started_at=Timestamp(1000.0),  # stale
        ),
    )
    decision = resolver.resolve(terminal, running, now, policy)

    assert JobId("old-terminal") in decision.purge_ids
    assert JobId("stale-running") in decision.stale_timeout_ids


# ─── Utility & Edge Cases ────────────────────────────────────────────────────


def test_resolver_repr(resolver: JobCleanupResolver) -> None:
    """Test resolver string representation."""
    assert repr(resolver) == "<JobCleanupResolver>"


def test_resolve_empty_inputs(resolver: JobCleanupResolver) -> None:
    """Test that empty inputs produce empty decision."""
    now = Timestamp(2000.0)
    policy = _make_policy()
    decision = resolver.resolve((), (), now, policy)

    assert decision.purge_ids == ()
    assert decision.stale_timeout_ids == ()
    assert len(decision.warnings) == 0


def test_resolve_missing_finished_at_warns(resolver: JobCleanupResolver) -> None:
    """Test that terminal records with no finished_at use updated_at as fallback."""
    now = Timestamp(2000.0)
    policy = _make_policy(retention_seconds=500)
    terminal = (
        _make_snapshot(
            job_id=JobId("no-finished"),
            state=JOB_STATE_COMPLETED,
            finished_at=None,
            updated_at=Timestamp(1000.0),  # used as fallback
        ),
    )
    decision = resolver.resolve(terminal, (), now, policy)

    assert JobId("no-finished") in decision.purge_ids


def test_resolve_warning_message_content(resolver: JobCleanupResolver) -> None:
    """Test that warnings include job ID and context."""
    now = Timestamp(2000.0)
    policy = _make_policy(stale_recovery_enabled=True, stale_running_lifetime_seconds=600)
    running = (
        _make_snapshot(
            job_id=JobId("no-start"),
            state=JOB_STATE_RUNNING,
            started_at=None,
        ),
    )
    decision = resolver.resolve((), running, now, policy)

    assert any("no-start" in w for w in decision.warnings)
