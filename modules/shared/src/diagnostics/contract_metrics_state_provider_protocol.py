"""Diagnostics domain contract: metrics state provider protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import MetricsSnapshotVO


class MetricsStateProviderProtocol(ABC):
    """Provides the latest metrics snapshot for diagnostics snapshots."""

    @abstractmethod
    async def get_metrics(self) -> MetricsSnapshotVO | None: ...
