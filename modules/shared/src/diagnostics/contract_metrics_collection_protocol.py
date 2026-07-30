"""Diagnostics domain contract: metrics collection protocol (ABC based).

Defines the protocol for pulling operational counters, gauges, and
latency summaries from features at a configured interval.

FR-DIA-002: Collect Operational Metrics
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import MetricsSampleVO, MetricsSnapshotVO


class MetricsCollectionProtocol(ABC):
    """Protocol for collecting operational metrics from features."""

    @abstractmethod
    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO:
        """Pull operational metrics from features and return snapshot.

        FR-DIA-002: Collection is pull-based at configured interval.
        Required metrics include pending operations, reconnect count,
        execution latency, command latency, failed requests, security violations,
        and task lifecycle counters.

        Latency summaries include count, min, max, mean, p50, p95.
        Counters are monotonic per lifetime; restart resets with indicator.
        Snapshot is immutable, safe for concurrent consumers.
        """
        ...
