"""Job domain contract: job cleanup protocol (ABC based).

Defines the protocol for automatic cleanup of finished task records.
AES Contract layer — pure ABC definitions, no implementation.

FR-JOB-004: Automatic Task Record Cleanup
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class JobCleanupProtocol(ABC):
    """Protocol for automatic cleanup of expired task records."""

    @abstractmethod
    def cleanup_expired_tasks(self, retention_minutes: int = 10) -> dict[str, int]:
        """Remove old, finished task records based on retention policy.

        FR-JOB-004: Only removes tasks in terminal states (Completed, Failed, Cancelled).
        Returns summary with removed and retained counts.
        """
        pass