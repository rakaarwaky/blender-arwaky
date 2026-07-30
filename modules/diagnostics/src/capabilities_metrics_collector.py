"""Capability: Operational metrics collector.

FR-DIA-002: Collect Operational Metrics
Pulls operational counters, gauges, and latency summaries from features
and exposes them as immutable snapshots.
Implements MetricsCollectionProtocol and MetricsStateProviderProtocol.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from modules.shared.src.diagnostics.contract_metrics_collection_protocol import (
    MetricsCollectionProtocol,
)
from modules.shared.src.diagnostics.contract_metrics_state_provider_protocol import (
    MetricsStateProviderProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    LatencySummaryVO,
    MetricsSampleVO,
    MetricsSnapshotVO,
)

logger = logging.getLogger(__name__)


class MetricsCollector(MetricsCollectionProtocol, MetricsStateProviderProtocol):
    """Collect operational metrics from features.

    Pulls counters, gauges, and latency summaries from features at
    configured interval and exposes immutable snapshots.
    """

    def __init__(self) -> None:
        self._counters: dict[str, int] = {}
        self._latency_buffers: dict[str, list[float]] = {}
        self._collection_timestamp: str = ""
        self._counter_reset_indicator: bool = False
        self._last_snapshot: MetricsSnapshotVO | None = None

    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO | None = None,
    ) -> MetricsSnapshotVO:
        """Pull operational metrics from features and return snapshot."""
        now = datetime.now(timezone.utc)
        self._collection_timestamp = now.isoformat()
        sample = sample or MetricsSampleVO()

        self._counters["pending_operations"] = sample.pending_operations
        self._counters["reconnect_count"] = sample.reconnect_count
        self._counters["failed_requests"] = sample.failed_requests
        self._counters["security_violations"] = sample.security_violations
        self._counters["tasks_created"] = sample.tasks_created
        self._counters["tasks_failed"] = sample.tasks_failed
        self._counters["tasks_completed"] = sample.tasks_completed

        if sample.execution_latency_ms > 0:
            buf = self._latency_buffers.setdefault("execution_latency_ms", [])
            buf.append(sample.execution_latency_ms)
        if sample.command_latency_ms > 0:
            buf = self._latency_buffers.setdefault("command_latency_ms", [])
            buf.append(sample.command_latency_ms)

        latency_summaries: dict[str, LatencySummaryVO] = {}
        for key, buf in self._latency_buffers.items():
            if len(buf) >= 2:
                sorted_buf = sorted(buf)
                count = len(sorted_buf)
                latency_summaries[key] = LatencySummaryVO(
                    count=count,
                    min_ms=sorted_buf[0],
                    max_ms=sorted_buf[-1],
                    mean_ms=sum(sorted_buf) / count,
                    p50_ms=sorted_buf[int(0.5 * count)],
                    p95_ms=sorted_buf[int(0.95 * (count - 1))],
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

        freshness: dict[str, str] = {
            "counters": "fresh",
            "latency_summaries": "fresh" if latency_summaries else "no_data",
        }

        self._last_snapshot = MetricsSnapshotVO(
            counters=dict(self._counters),
            latency_summaries=latency_summaries,
            freshness_indicators=freshness,
            collection_timestamp=self._collection_timestamp,
            counter_reset_indicator=self._counter_reset_indicator,
        )
        return self._last_snapshot

    async def get_metrics(self) -> MetricsSnapshotVO | None:
        """Return the latest metrics snapshot for snapshot provider contract."""
        return self._last_snapshot

    def __repr__(self) -> str:
        return "MetricsCollector()"
