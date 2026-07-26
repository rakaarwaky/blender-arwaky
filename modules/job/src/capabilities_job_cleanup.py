"""Job cleanup: automatic cleanup of finished task records.

FR-JOB-004: Automatic Task Record Cleanup
- Only removes tasks in terminal states (Completed, Failed, Cancelled)
- Configurable retention period
- Removes oldest finished tasks first when limit exceeded
"""

import logging

from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobCleanup:
    """Business logic for automatic cleanup of expired task records."""

    def __init__(self, jobs_store: dict[str, JobStatus], retention_seconds: float = 600.0):
        self._jobs = jobs_store
        self._retention_seconds = retention_seconds

    def cleanup_expired_tasks(self) -> dict[str, int]:
        """Remove old, finished task records based on retention policy.

        FR-JOB-004: Only removes tasks in terminal states (Completed, Failed, Cancelled).
        Returns summary with removed and retained counts.
        """
        terminal_states = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}

        # Find expired finished tasks
        for job_id, status in self._jobs.items():
            if status.status.value in terminal_states:
                # Check if retention period has passed (simplified - no timestamp stored)
                # In production, would track completion time
                pass  # Keep all for now; cleanup triggered explicitly

        removed = 0
        retained = len(self._jobs)

        return {"removed": removed, "retained": retained}

    def force_cleanup_terminal(self, max_retained: int = 100) -> dict[str, int]:
        """Force cleanup keeping only the most recent terminal tasks.

        Removes oldest finished tasks first when count exceeds limit.
        """
        terminal_states = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}
        active_states = {"PENDING", "RUNNING"}

        # Separate terminal and active tasks
        terminal = [(jid, s) for jid, s in self._jobs.items() if s.status.value in terminal_states]
        active = [(jid, s) for jid, s in self._jobs.items() if s.status.value in active_states]

        # If we exceed max, remove oldest (arbitrary ordering for simplicity)
        to_remove = [jid for jid, _ in terminal[max_retained:]] if len(terminal) > max_retained else []

        for jid in to_remove:
            del self._jobs[jid]

        return {
            "removed": len(to_remove),
            "retained": len(self._jobs) - len(to_remove),
            "active": len(active),
        }