"""Diagnostics domain contract: health composition protocol (ABC based).

Defines the protocol for aggregating subsystem states into one composed
health view with bounded probes and explicit staleness.

FR-DIA-001: Compose System Health
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class HealthCompositionProtocol(ABC):
    """Protocol for composing system health from subsystem states."""

    @abstractmethod
    async def compose_health(
        self,
        launcher_status: str = "unknown",
        gateway_status: str = "unknown",
        config_valid: bool = False,
        job_capacity_available: bool = True,
    ) -> dict[str, Any]:
        """Aggregate subsystem states into one composed health view.

        FR-DIA-001: Composed health covers launcher, gateway, config, and job capacity.
        Overall status: healthy when all required report healthy;
        degraded when any reports degraded/stale; unhealthy when any fails.

        Args:
            launcher_status: Process liveness classification.
            gateway_status: Connection state classification.
            config_valid: Whether configuration snapshot is valid.
            job_capacity_available: Whether job capacity has available slots.

        Returns:
            Dict with overall status, per-subsystem map, and composition timestamp.
        """
        pass