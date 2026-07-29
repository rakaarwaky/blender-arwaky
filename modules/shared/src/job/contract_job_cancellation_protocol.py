"""Job domain — FR-JOB-003: Cancel a task."""
from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import JobState
from .taxonomy_job_vo import CancelTaskCommand, CancellationResult


class IJobCancellation(ABC):
    @abstractmethod
    def evaluate(self, command: CancelTaskCommand, current_state: JobState) -> CancellationResult: ...
