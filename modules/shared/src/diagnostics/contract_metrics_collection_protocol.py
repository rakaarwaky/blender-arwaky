"""Diagnostics domain contract: metrics collection protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import MetricsSampleVO, MetricsSnapshotVO


class MetricsCollectionProtocol(ABC):
    """Contract protocol for performance metrics collection.

    FR-DIA-002: Performance metrics collection capturing latency,
    throughput, error rates, and resource utilization counters.
    """

    @abstractmethod
    async def collect_metrics_snapshot(
        self,
        sample: MetricsSampleVO,
    ) -> MetricsSnapshotVO:
        """Collect and record a performance metrics sample."""
        ...
