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
from modules.diagnostics.src.taxonomy_diagnostics_vo import (
    LatencySummaryVO,
    MetricsSnapshotVO,
)

logger = logging.getLogger(__name__)


class MetricsCollector(MetricsCollectionProtocol):
    """Collect operational metrics from features.

    Pulls counters, gauges, and latency summaries from features at
    configured interval and exposes immutable snapshots.
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._latency_buffers: dict[str, list[float]] = {}
        self._collection_timestamp: str = ""
        self._counter_reset_indicator: bool = False

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
    ) -> MetricsSnapshotVO:
        """Pull operational metrics from features and return snapshot."""
        now = datetime.now(timezone.utc)
        self._collection_timestamp = now.isoformat()

        # Accumulate counters (monotonic per lifetime)
        self._counters["pending_operations"] = pending_operations
        self._counters["reconnect_count"] = reconnect_count
        self._counters["failed_requests"] = failed_requests
        self._counters["security_violations"] = security_violations
        self._counters["tasks_created"] = tasks_created
        self._counters["tasks_failed"] = tasks_failed
        self._counters["tasks_completed"] = tasks_completed

        # Accumulate latency buffers for proper summaries
        if execution_latency_ms > 0:
            buf = self._latency_buffers.setdefault("execution_latency_ms", [])
            buf.append(execution_latency_ms)
        if command_latency_ms > 0:
            buf = self._latency_buffers.setdefault("command_latency_ms", [])
            buf.append(command_latency_ms)

        # Build latency summaries from accumulated data
        latency_summaries: dict[str, LatencySummaryVO] = {}
        for key, buf in self._latency_buffers.items():
            if len(buf) >= 2:
                sorted_buf = sorted(buf)
                count = len(sorted_buf)
                min_ms = sorted_buf[0]
                max_ms = sorted_buf[-1]
                mean_ms = sum(sorted_buf) / count
                p50_idx = int(0.5 * count)
                p95_idx = int(0.95 * (count - 1))
                latency_summaries[key] = LatencySummaryVO(
                    count=count,
                    min_ms=min_ms,
                    max_ms=max_ms,
                    mean_ms=mean_ms,
                    p50_ms=sorted_buf[p50_idx],
                    p95_ms=sorted_buf[p95_idx],
                )
            elif len(buf) == 1:
                latency_summaries[key] = LatencySummaryVO(
                    count=1,
                    min_ms=buf[0],
                    max_ms=buf[0],
                    mean_ms=buf[0],
                    p50_ms=buf[0],
                    p95_ms=buf[0],
                )

        # Freshness indicators
        freshness: dict[str, str] = {
            "counters": "fresh",
            "latency_summaries": "fresh" if latency_summaries else "no_data",
        }

        return MetricsSnapshotVO(
            counters=dict(self._counters),
            latency_summaries=latency_summaries,
            freshness_indicators=freshness,
            collection_timestamp=self._collection_timestamp,
            counter_reset_indicator=self._counter_reset_indicator,
        )

    def __repr__(self) -> str:
        return "MetricsCollector()"
