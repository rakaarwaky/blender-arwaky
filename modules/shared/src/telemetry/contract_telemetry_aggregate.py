"""Telemetry domain contract: telemetry aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for telemetry operations: record, classify, enrich, session.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ITelemetryAggregate(ABC):
    @abstractmethod
    def record_startup_event(self) -> None:
        ...

    @abstractmethod
    def record_action_execution(
        self,
        action_name: str,
        success: bool,
        duration_ms: float,
    ) -> None:
        ...

    @abstractmethod
    def record_system_error(self, error_category: str, context: str) -> None:
        ...

    @abstractmethod
    def get_session_id(self) -> str:
        ...

    @abstractmethod
    def initialize_session(self) -> None:
        ...

    @abstractmethod
    def get_environment_metadata(self) -> dict[str, Any]:
        ...
