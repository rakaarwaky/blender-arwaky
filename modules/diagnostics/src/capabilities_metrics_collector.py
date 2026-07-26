"""Capability: Metrics collector that subscribes to the event bus.

Maintains counters and averages from published events.
Implements IEventSubscriber and IMetricsProvider.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING

from modules.diagnostics.src import IEventSubscriber, IMetricsProvider
from modules.gateway.src import (
    CodeExecuted,
    CodeExecutionFailed,
    CommandDispatched,
    CommandFailed,
    CommandTimedOut,
    ConnectionEstablished,
    ConnectionLost,
    ConnectionReconnectAttempted,
    ConnectionReconnectFailed,
    OperationRejected,
    SecurityViolationDetected,
    ServerEvent,
    ServerMetrics,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
    TaskTimedOut,
)

logger = logging.getLogger("BlenderMCPServer")


class MetricsCollector(IEventSubscriber, IMetricsProvider):
    """Collects metrics from server events and exposes them as ServerMetrics.

    Subscribes to the event bus and updates counters for all observed events.
    Thread-safe under asyncio — uses no locks because single-threaded event loop.
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = {
            "pending_operations": 0,
            "running_operations": 0,
            "reconnect_count": 0,
            "failed_request_count": 0,
            "security_violation_count": 0,
            "code_execution_count": 0,
            "command_count": 0,
            "task_created_count": 0,
            "task_completed_count": 0,
            "task_failed_count": 0,
            "task_timeout_count": 0,
            "task_cancelled_count": 0,
        }
        self._code_latencies: list[float] = []
        self._command_latencies: list[float] = []
        self._last_updated_at: float = time.monotonic()

    async def handle(self, event: ServerEvent) -> None:  # type: ignore[override]
        """Handle events and update metrics counters."""
        now = time.monotonic()
        updated = False

        if isinstance(event, ConnectionEstablished):
            pass  # No counter increment needed

        elif isinstance(event, ConnectionLost):
            pass

        elif isinstance(event, ConnectionReconnectAttempted):
            self._counters["reconnect_count"] += 1
            updated = True

        elif isinstance(event, ConnectionReconnectFailed):
            self._counters["reconnect_count"] += 1
            self._counters["failed_request_count"] += 1
            updated = True

        elif isinstance(event, CodeExecuted):
            self._counters["code_execution_count"] += 1
            self._code_latencies.append(event.execution_time_ms)
            if len(self._code_latencies) > 100:
                self._code_latencies = self._code_latencies[-100:]
            updated = True

        elif isinstance(event, CodeExecutionFailed):
            self._counters["failed_request_count"] += 1
            updated = True

        elif isinstance(event, SecurityViolationDetected):
            self._counters["security_violation_count"] += 1
            updated = True

        elif isinstance(event, TaskCreated):
            self._counters["task_created_count"] += 1
            updated = True

        elif isinstance(event, TaskCompleted):
            self._counters["task_completed_count"] += 1
            updated = True

        elif isinstance(event, TaskFailed):
            self._counters["task_failed_count"] += 1
            updated = True

        elif isinstance(event, TaskTimedOut):
            self._counters["task_timeout_count"] += 1
            updated = True

        elif isinstance(event, TaskCancelled):
            self._counters["task_cancelled_count"] += 1
            updated = True

        elif isinstance(event, CommandDispatched):
            self._counters["command_count"] += 1
            self._command_latencies.append(event.execution_time_ms)
            if len(self._command_latencies) > 100:
                self._command_latencies = self._command_latencies[-100:]
            updated = True

        elif isinstance(event, CommandFailed):
            self._counters["failed_request_count"] += 1
            updated = True

        elif isinstance(event, CommandTimedOut):
            self._counters["failed_request_count"] += 1
            updated = True

        elif isinstance(event, OperationRejected):
            self._counters["failed_request_count"] += 1
            updated = True

        if updated:
            self._last_updated_at = now

    async def get_metrics(self, request_id: str | None = None) -> ServerMetrics:
        """Return current metrics as an immutable ServerMetrics VO.

        Args:
            request_id: Optional tracking ID.

        Returns:
            ServerMetrics with all counters and averages.
        """
        return ServerMetrics(
            pending_operations=self._counters["pending_operations"],
            running_operations=self._counters["running_operations"],
            reconnect_count=self._counters["reconnect_count"],
            failed_request_count=self._counters["failed_request_count"],
            security_violation_count=self._counters["security_violation_count"],
            code_execution_count=self._counters["code_execution_count"],
            command_count=self._counters["command_count"],
            task_created_count=self._counters["task_created_count"],
            task_completed_count=self._counters["task_completed_count"],
            task_failed_count=self._counters["task_failed_count"],
            task_timeout_count=self._counters["task_timeout_count"],
            task_cancelled_count=self._counters["task_cancelled_count"],
            average_code_latency_ms=(
                sum(self._code_latencies) / len(self._code_latencies)
                if self._code_latencies
                else 0.0
            ),
            average_command_latency_ms=(
                sum(self._command_latencies) / len(self._command_latencies)
                if self._command_latencies
                else 0.0
            ),
            last_updated_at=self._last_updated_at,
            request_id=request_id,
        )
