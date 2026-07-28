"""Telemetry domain contract: telemetry aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for telemetry operations: record, classify, enrich, session.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    DurationMs,
    ErrorMessage,
    ErrorString,
    SessionId,
    SuccessFlag,
)


class ITelemetryAggregate(ABC):
    @abstractmethod
    def record_startup_event(self) -> None: ...

    @abstractmethod
    def record_action_execution(
        self,
        action_name: ActionName,
        success: SuccessFlag,
        duration_ms: DurationMs,
    ) -> None: ...

    @abstractmethod
    def record_system_error(
        self,
        error_category: ErrorString,
        context: ErrorMessage,
    ) -> None: ...

    @abstractmethod
    def get_session_id(self) -> SessionId: ...

    @abstractmethod
    def initialize_session(self) -> None: ...

    @abstractmethod
    def get_environment_metadata(self) -> dict[str, Any]: ...
