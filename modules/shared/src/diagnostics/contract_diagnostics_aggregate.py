"""Diagnostics domain contract: diagnostics aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for diagnostics operations: health, metrics, audit, logging, snapshot.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ToolName


class IDiagnosticsAggregate(ABC):
    @abstractmethod
    async def compose_health(
        self,
        launcher_status: str = "unknown",
        gateway_status: str = "unknown",
        config_valid: bool = False,
        job_capacity_available: bool = True,
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def get_snapshot(
        self,
        detail_level: str = "summary",
        section_filter: list[str] | None = None,
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def log_record(
        self,
        level: str,
        source_feature: str,
        message: str,
        fields: dict[str, Any] | None = None,
        tracking_id: str | None = None,
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def collect_metrics_snapshot(
        self,
        pending_operations: int = 0,
        reconnect_count: int = 0,
        execution_latency_ms: float = 0.0,
        command_latency_ms: float = 0.0,
        failed_requests: int = 0,
        security_violations: int = 0,
        tasks_created: int = 0,
        tasks_failed: int = 0,
        tasks_completed: int = 0,
    ) -> dict[str, Any]: ...

    @abstractmethod
    async def emit_audit_event(
        self,
        category: str,
        severity: str,
        source_feature: str,
        operation_type: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any]: ...
