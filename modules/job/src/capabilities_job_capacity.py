"""Job capacity enforcement capability.

FR-JOB-005: Enforce Background Capacity
- Limits the number of concurrently active background tasks
- Job feature is the only path to background execution
- New tasks rejected (CapacityError) when the limit is reached
- Domain features must not bypass the capacity check

AES Capabilities layer — concrete implementation of JobCapacityProtocol.
"""

from __future__ import annotations

import logging
from collections.abc import Callable

from modules.shared.src.common.taxonomy_core_vo import JobId
from modules.shared.src.job.contract_job_capacity_protocol import JobCapacityProtocol

logger = logging.getLogger("BlenderMCPServer")


class CapacityError(Exception):
    """Raised when a background task is rejected due to capacity limits."""


class JobCapacityEnforcer(JobCapacityProtocol):
    """Concrete capacity gate for concurrent background tasks.

    FR-JOB-005: The single authority on how many background tasks may run.
    Reservations are tracked here; the active-count source is injected so the
    capability is testable without a live tracker.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        max_concurrent: int = 100,
        active_source: Callable[[], int] | None = None,
    ) -> None:
        self._max_concurrent = max_concurrent
        self._active_source = active_source or (lambda: 0)
        self._reserved: dict[str, int] = {}

    # ─── Block 2: Protocol Method Implementation ─────────────

    def check_capacity(self, requested: int = 1) -> tuple[bool, int]:
        """Return (accepted, current_active_count) without reserving.

        FR-JOB-005: Rejects when current active + requested would exceed max.
        """
        current = self.active_count()
        accepted = current + requested <= self._max_concurrent
        return accepted, current

    def reserve_slot(self, job_id: JobId) -> bool:
        """Reserve one concurrency slot for an accepted task.

        FR-JOB-005: Returns False if capacity would be exceeded; callers must
        not launch background work without a successful reservation.
        """
        accepted, _ = self.check_capacity(1)
        if not accepted:
            logger.warning("Capacity exceeded; rejecting reservation %s", job_id)
            return False
        self._reserved[str(job_id)] = 1
        return True

    def release_slot(self, job_id: JobId) -> None:
        """Release the concurrency slot held by a finished task."""
        self._reserved.pop(str(job_id), None)

    def active_count(self) -> int:
        """Current active count = injected source + local reservations."""
        return self._active_source() + len(self._reserved)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    @property
    def max_concurrent(self) -> int:
        return self._max_concurrent

    def __repr__(self) -> str:
        return f"JobCapacityEnforcer(max={self._max_concurrent}, active={self.active_count()})"
