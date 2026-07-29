"""Job domain — FR-JOB-005: Enforce background capacity."""
from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_job_vo import CapacityDecision, JobPolicy


class IJobCapacity(ABC):
    @abstractmethod
    def evaluate(self, active_count: int, policy: JobPolicy) -> CapacityDecision: ...
