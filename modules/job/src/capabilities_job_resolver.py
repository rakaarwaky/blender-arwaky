# modules/job/src/capabilities_job_resolver.py
"""Capability: Job cleanup resolver (FR-JOB-004).

Resolves which terminal records to purge and which running
records to time out. Stateless — receives data, returns decision.
"""
from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import JobId, Timestamp
from modules.shared.src.job.contract_job_cleanup_protocol import IJobCleanup
from modules.shared.src.job.taxonomy_job_vo import (
    CleanupDecision,
    JobPolicy,
    JobStatusSnapshot,
)

# ─── Block 1: Class Definition & Constructor ─────────────────────────────────


class JobCleanupResolver(IJobCleanup):
    """Resolves cleanup decisions per FR-JOB-004."""

    # ─── Block 2: Domain Protocol Method Implementation ──────────────────────

    def resolve(
        self,
        terminal: tuple[JobStatusSnapshot, ...],
        running: tuple[JobStatusSnapshot, ...],
        now: Timestamp,
        policy: JobPolicy,
    ) -> CleanupDecision:
        """Resolve which records to purge and which running tasks to time out.

        - Stale running tasks identified when policy enabled
        - Expired terminal records identified, oldest first
        - Max record count enforced
        - Corrupt/missing timestamps produce warnings
        """
        warnings: list[str] = []

        stale_ids = self._resolve_stale(running, now, policy, warnings)
        purge_ids = self._resolve_expired(terminal, now, policy, warnings)
        purge_ids = self._enforce_max(terminal, purge_ids, policy)

        return CleanupDecision(
            purge_ids=tuple(purge_ids),
            stale_timeout_ids=tuple(stale_ids),
            warnings=tuple(warnings),
        )

    # ─── Block 3: Dunder Methods, Factories, and Private Helpers ─────────────

    def __repr__(self) -> str:
        return "<JobCleanupResolver>"

    def _resolve_stale(
        self,
        running: tuple[JobStatusSnapshot, ...],
        now: Timestamp,
        policy: JobPolicy,
        warnings: list[str],
    ) -> list[JobId]:
        if not policy.stale_recovery_enabled:
            return []

        stale: list[JobId] = []
        for snap in running:
            if snap.started_at is None:
                warnings.append(f"running task {snap.job_id} missing started_at")
                continue
            age = float(now) - float(snap.started_at)
            if age > policy.stale_running_lifetime_seconds:
                stale.append(snap.job_id)
        return stale

    def _resolve_expired(
        self,
        terminal: tuple[JobStatusSnapshot, ...],
        now: Timestamp,
        policy: JobPolicy,
        warnings: list[str],
    ) -> list[JobId]:
        sortable: list[tuple[float, JobId]] = []
        for snap in terminal:
            finished = snap.finished_at if snap.finished_at is not None else snap.updated_at
            if finished is None:
                warnings.append(f"terminal task {snap.job_id} missing timestamps")
                continue
            sortable.append((float(finished), snap.job_id))

        sortable.sort(key=lambda item: item[0])

        purge: list[JobId] = []
        for finished_at, job_id in sortable:
            if float(now) - finished_at >= policy.retention_seconds:
                purge.append(job_id)
        return purge

    def _enforce_max(
        self,
        terminal: tuple[JobStatusSnapshot, ...],
        already_purging: list[JobId],
        policy: JobPolicy,
    ) -> list[JobId]:
        purging_set = {str(jid) for jid in already_purging}
        remaining = [s for s in terminal if str(s.job_id) not in purging_set]

        if len(remaining) <= policy.max_records:
            return already_purging

        sortable: list[tuple[float, JobId]] = []
        for snap in remaining:
            finished = snap.finished_at if snap.finished_at is not None else snap.updated_at
            ts = float(finished) if finished is not None else 0.0
            sortable.append((ts, snap.job_id))

        sortable.sort(key=lambda item: item[0])
        excess = len(remaining) - policy.max_records
        return already_purging + [jid for _, jid in sortable[:excess]]
