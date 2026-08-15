"""Job domain — FR-JOB-002: Monitor task status."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_job_vo import JobStatusSnapshot


class IJobMonitor(ABC):
    @abstractmethod
    def project(self, snapshot: JobStatusSnapshot) -> JobStatusSnapshot: ...
