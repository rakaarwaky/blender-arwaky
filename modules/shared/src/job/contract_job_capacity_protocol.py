"""Job domain contract: background capacity enforcement protocol (ABC based).

AES Contract layer — pure ABC definition, no implementation.

FR-JOB-005: Enforce Background Capacity
- Limits the number of concurrently active background tasks
- Job feature is the only path to background execution
- New tasks rejected with CapacityError when limit reached
- Domain features must not bypass capacity check
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import JobId


class JobCapacityProtocol(ABC):
    """Protocol for enforcing background task concurrency capacity."""

    @abstractmethod
    def check_capacity(self, requested: int = 1) -> tuple[bool, int]:
        """Return (accepted, current_active_count) for a requested number of tasks.

        FR-JOB-005: Rejects (accepted=False) when adding `requested` would exceed
        the configured maximum concurrent background task count.
        """
        pass

    @abstractmethod
    def reserve_slot(self, job_id: JobId) -> bool:
        """Reserve a concurrency slot for an accepted task.

        FR-JOB-005: Returns False if capacity would be exceeded; callers must
        not bypass this to launch background work.
        """
        pass

    @abstractmethod
    def release_slot(self, job_id: JobId) -> None:
        """Release the concurrency slot held by a finished task."""
        pass

    @abstractmethod
    def active_count(self) -> int:
        """Current number of active (non-terminal) background tasks."""
        pass
