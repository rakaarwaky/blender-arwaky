"""Job domain contract: job aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for job lifecycle operations: track, update, finalize, cancel, cleanup.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import ErrorString, JobId, ResultUrl
from .taxonomy_job_status_entity import JobStatus


class IJobAggregate(ABC):
    @abstractmethod
    def track_new_task(
        self,
        operation_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[JobId, JobStatus]:
        ...

    @abstractmethod
    def update_progress(
        self,
        job_id: JobId,
        progress: float,
        message: str = "",
    ) -> JobStatus:
        ...

    @abstractmethod
    def finalize_task_success(
        self,
        job_id: JobId,
        result_url: ResultUrl | None = None,
        summary: str = "",
    ) -> JobStatus:
        ...

    @abstractmethod
    def finalize_task_failure(
        self,
        job_id: JobId,
        error_message: ErrorString,
        error_category: str = "",
    ) -> JobStatus:
        ...

    @abstractmethod
    def get_task_status(self, job_id: JobId) -> JobStatus | None:
        ...

    @abstractmethod
    def cancel_task(
        self,
        job_id: JobId,
        reason: ErrorString = "",
    ) -> tuple[bool, str]:
        ...

    @abstractmethod
    def cleanup_expired_tasks(self, max_retained: int = 100) -> dict[str, int]:
        ...
