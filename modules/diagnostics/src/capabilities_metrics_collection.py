"""Capability: Operational metrics collector.

FR-DIA-002: Collect Operational Metrics
Pulls operational counters, gauges, and latency summaries from features
and exposes them as immutable snapshots.
Implements MetricsCollectionProtocol.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from modules.diagnostics.src.contract_metrics_collection_protocol import (
    MetricsCollectionProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class MetricsCollector(MetricsCollectionProtocol):
    """Collect operational metrics from features.

    Pulls counters, gauges, and latency summaries from features at
    configured interval and exposes immutable snapshots.
    """

    def __init__(self) -> None:
        self._metrics_snapshot: dict[str, Any] = {}

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
        source_tool: Any = None,
        tasks_completed: int = 0,
    ) -> dict[str, Any]:
        """Pull operational metrics from features and return snapshot."""
        self._metrics_snapshot = {
            "counters": {
                "pending_operations": pending_operations,
                "reconnect_count": reconnect_count,
                "failed_requests": failed_requests,
                "security_violations": security_violations,
                "tasks_created": tasks_created,
                "tasks_failed": tasks_failed,
                "tasks_completed": tasks_completed,
            },
            "latency_summaries": {
                "execution_latency_ms": execution_latency_ms,
                "command_latency_ms": command_latency_ms,
            },
            "collection_timestamp": datetime.now(timezone.utc).isoformat(),
        }
        return dict(self._metrics_snapshot)
