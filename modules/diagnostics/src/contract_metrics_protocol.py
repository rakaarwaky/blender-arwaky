"""Contract: Metrics provider protocol for server diagnostics.

Implemented by metrics collector capability.
AES Protocol layer — depends only on Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.gateway.src.taxonomy_server_vo import ServerMetrics


class IMetricsProvider(ABC):
    """Provide server metrics snapshot."""

    @abstractmethod
    async def get_metrics(
        self,
        request_id: str | None = None,
    ) -> ServerMetrics:
        """Return current server metrics as an immutable ServerMetrics VO."""
        ...