"""Job domain — FR-JOB-004: Automatic task record cleanup."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import Timestamp
from .taxonomy_job_vo import CleanupDecision, JobPolicy, JobStatusSnapshot


class IJobCleanup(ABC):
    @abstractmethod
    def resolve(
        self,
        terminal: tuple[JobStatusSnapshot, ...],
        running: tuple[JobStatusSnapshot, ...],
        now: Timestamp,
        policy: JobPolicy,
    ) -> CleanupDecision: ...
