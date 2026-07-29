"""Contract: Job event publisher protocol.

Defines IJobEventPublisher for decoupled event emission from repositories.
Repositories emit events through this protocol instead of direct logging.

AES Protocol layer — depends only on Taxonomy.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_job_event import JobEvent


class IJobEventPublisher(ABC):
    """Publish job domain events to subscribers."""

    @abstractmethod
    def emit(self, event: JobEvent) -> None:
        """Emit a job event to all interested subscribers.

        Implementations may log, forward to an external bus, or buffer.
        Subscriber exceptions are isolated and never propagate outward.
        """
        ...
