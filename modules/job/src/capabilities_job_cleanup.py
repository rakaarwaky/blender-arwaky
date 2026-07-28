"""Job cleanup: automatic cleanup of finished task records.

FR-JOB-004: Automatic Task Record Cleanup
- Retains terminal records for a configured retention duration, then purges
- Purges oldest terminal records first when a count ceiling is exceeded
- Never purges active (PENDING/RUNNING) tasks
- Drops corrupt/unreadable records with a warning instead of crashing
- Safe against concurrent transitions and reads (shared lock)

AES Capabilities layer — concrete implementation of `JobCleanupProtocol`.
"""

from __future__ import annotations

import logging
import threading
import time

from modules.shared.src.job.contract_job_cleanup_protocol import JobCleanupProtocol
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")

_ACTIVE_STATES = {"PENDING", "RUNNING"}
_TERMINAL_STATES = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}


class JobCleanup(JobCleanupProtocol):
    """Concrete implementation of the job cleanup protocol."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        jobs_store: dict[str, JobStatus],
        lock: threading.RLock | None = None,
    ) -> None:
        self._jobs = jobs_store
        self._lock = lock or threading.RLock()
        # Best-effort record of when a task was first observed terminal, used to
        # approximate finished-time for retention. The shared taxonomy entity
        # does not yet carry timestamps (out-of-scope blocker), so this is the
        # closest faithful substitute.
        self._finished_at: dict[str, float] = {}

    # ─── Block 2: Protocol Method Implementation ─────────────

    def cleanup_expired_tasks(
        self, retention_minutes: int = 10, max_retained: int | None = None
    ) -> dict[str, int]:
        """Remove expired and excess terminal records.

        FR-JOB-004: terminal records past ``retention_minutes`` are purged first;
        when more than ``max_retained`` terminal records exist, the oldest are
        evicted (count-based early eviction under capacity pressure). Active
        tasks are never removed. Returns a summary dict of counts.
        """
        with self._lock:
            now = time.monotonic()
            retention_seconds = float(retention_minutes) * 60.0
            to_remove: set[str] = set()
            warnings = 0

            # Snapshot insertion order (oldest first) for oldest-first eviction.
            ordered_ids = list(self._jobs.keys())
            terminal_ids: list[str] = []

            for job_id in ordered_ids:
                try:
                    status = self._jobs[job_id]
                    state = status.status.value
                except Exception:  # corrupt/unreadable record
                    logger.warning("Dropping corrupt record %s during sweep", job_id)
                    to_remove.add(job_id)
                    warnings += 1
                    continue

                if state in _ACTIVE_STATES:
                    continue

                if state in _TERMINAL_STATES:
                    terminal_ids.append(job_id)
                    if job_id not in self._finished_at:
                        self._finished_at[job_id] = now
                    dwell = now - self._finished_at[job_id]
                    if retention_seconds > 0 and dwell >= retention_seconds:
                        to_remove.add(job_id)

            # Count-based early eviction: keep only the newest ``max_retained``.
            if max_retained is not None and len(terminal_ids) > max_retained:
                excess = len(terminal_ids) - max_retained
                for job_id in terminal_ids[:excess]:
                    to_remove.add(job_id)

            for job_id in to_remove:
                self._jobs.pop(job_id, None)
                self._finished_at.pop(job_id, None)

            active = sum(
                1 for s in self._jobs.values() if s.status.value in _ACTIVE_STATES
            )
            return {
                "removed": len(to_remove),
                "retained": len(self._jobs),
                "active": active,
                "warnings": warnings,
            }
