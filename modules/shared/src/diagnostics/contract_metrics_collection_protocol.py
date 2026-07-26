"""Diagnostics domain contract: metrics collection protocol (ABC based).

Defines the protocol for pulling operational counters, gauges, and
latency summaries from features at a configured interval.

FR-DIA-002: Collect Operational Metrics
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class MetricsCollectionProtocol(ABC):
    """Protocol for collecting operational metrics from features."""

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
    ) -> dict[str, Any]:
        """Pull operational metrics from features and return snapshot.

        FR-DIA-002: Collection is pull-based at configured interval.
        Required metrics include pending operations, reconnect count,
        execution latency, command latency, failed requests, security violations,
        and task lifecycle counters.

        Args:
            pending_operations: Current pending operation count.
            reconnect_count: Total reconnection attempts.
            execution_latency_ms: Execution latency summary in ms.
            command_latency_ms: Command latency summary in ms.
            failed_requests: Total failed request count.
            security_violations: Total security violation count.
            tasks_created: Total tasks created counter.
            tasks_failed: Total tasks failed counter.
            tasks_completed: Total tasks completed counter.

        Returns:
            Dict with metrics snapshot including counters, gauges, and timestamps.
        """
        pass
