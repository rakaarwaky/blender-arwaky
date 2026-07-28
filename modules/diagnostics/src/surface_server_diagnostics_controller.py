"""Surface: Server diagnostics controller for metrics JSON serialization.

Depends only on the aggregate contract and taxonomy VOs.
Formats metrics as JSON-compatible dict for CLI/MCP transport layers.
"""

from __future__ import annotations

import time
from typing import Any

from modules.shared.src.gateway.contract_gateway_aggregate import IBlenderServerAggregate
from modules.shared.src.gateway.taxonomy_gateway_vo import ServerMetrics


class ServerDiagnosticsController:
    """Formats server metrics as JSON-compatible output.

    Consumes the aggregate contract and serializes ServerMetrics
    into a dict suitable for CLI output or MCP transport.
    """

    def __init__(self, aggregate: IBlenderServerAggregate) -> None:
        """Initialize with the server aggregate.

        Args:
            aggregate: The IBlenderServerAggregate implementation.
        """
        self._aggregate = aggregate

    async def get_metrics_json(self, request_id: str | None = None) -> dict[str, Any]:
        """Get metrics formatted as a JSON-compatible dictionary.

        Includes timestamp and request ID for traceability.

        Args:
            request_id: Optional tracking ID.

        Returns:
            Dictionary with metrics data suitable for JSON serialization.
        """
        metrics = await self._aggregate.get_metrics(request_id)
        return self._format_metrics(metrics, request_id)

    @staticmethod
    def _format_metrics(metrics: ServerMetrics, request_id: str | None) -> dict[str, Any]:
        """Format ServerMetrics as a JSON-compatible dict.

        Args:
            metrics: The ServerMetrics VO to format.
            request_id: Optional tracking ID.

        Returns:
            Dictionary suitable for JSON serialization.
        """
        return {
            "request_id": request_id,
            "timestamp": time.monotonic(),
            "metrics": {
                "pending_operations": metrics.pending_operations,
                "running_operations": metrics.running_operations,
                "reconnect_count": metrics.reconnect_count,
                "failed_request_count": metrics.failed_request_count,
                "security_violation_count": metrics.security_violation_count,
                "code_execution_count": metrics.code_execution_count,
                "command_count": metrics.command_count,
                "task_created_count": metrics.task_created_count,
                "task_completed_count": metrics.task_completed_count,
                "task_failed_count": metrics.task_failed_count,
                "task_timeout_count": metrics.task_timeout_count,
                "task_cancelled_count": metrics.task_cancelled_count,
                "average_code_latency_ms": metrics.average_code_latency_ms,
                "average_command_latency_ms": metrics.average_command_latency_ms,
                "last_updated_at": metrics.last_updated_at,
            },
        }
