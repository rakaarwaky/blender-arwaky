# modules/job/src/capabilities_job_monitor.py
"""Capability: Job status monitor (FR-JOB-002).

Projects raw snapshots into consumer-safe read models.
Applies redaction, visibility rules, and applicability flags.
"""
from __future__ import annotations

from modules.shared.src.job.contract_job_monitor_protocol import IJobMonitor
from modules.shared.src.job.taxonomy_job_constant import (
    ACTIVE_JOB_STATES,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_RUNNING,
    TERMINAL_JOB_STATES,
)
from modules.shared.src.job.taxonomy_job_vo import JobStatusSnapshot
from modules.shared.src.job.utility_job_sanitizer import redact_metadata

# ─── Block 1: Class Definition & Constructor ─────────────────────────────────


class JobStatusMonitor(IJobMonitor):
    """Projects raw snapshots into safe, consumer-ready read models."""

    # ─── Block 2: Domain Protocol Method Implementation ──────────────────────

    def project(self, snapshot: JobStatusSnapshot) -> JobStatusSnapshot:
        """Project a raw snapshot into a consumer-safe read model.

        - Result reference visible only after COMPLETED
        - Error detail visible only after FAILED
        - Metadata redacted (defense-in-depth)
        - Progress applicability indicated
        - Cancellable flag exposed
        """
        safe_metadata = self._redact(snapshot.metadata)

        return JobStatusSnapshot(
            job_id=snapshot.job_id,
            state=snapshot.state,
            operation_type=snapshot.operation_type,
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
            progress=snapshot.progress,
            progress_message=snapshot.progress_message,
            result_url=snapshot.result_url if snapshot.state == JOB_STATE_COMPLETED else None,
            error=snapshot.error if snapshot.state == JOB_STATE_FAILED else None,
            error_category=snapshot.error_category if snapshot.state == JOB_STATE_FAILED else None,
            correlation_id=snapshot.correlation_id,
            started_at=snapshot.started_at,
            finished_at=snapshot.finished_at,
            metadata=safe_metadata,
            is_terminal=snapshot.state in TERMINAL_JOB_STATES,
            is_cancellable=snapshot.state in ACTIVE_JOB_STATES,
            progress_applicable=snapshot.state == JOB_STATE_RUNNING,
        )

    # ─── Block 3: Dunder Methods, Factories, and Private Helpers ─────────────

    def __repr__(self) -> str:
        return "<JobStatusMonitor>"

    def _redact(self, metadata: tuple[tuple[str, str], ...]) -> tuple[tuple[str, str], ...]:
        if not metadata:
            return metadata
        redacted = redact_metadata(dict(metadata))
        return tuple(sorted(redacted.items()))
