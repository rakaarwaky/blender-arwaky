"""Diagnostics domain contract: health composition protocol (ABC based).

Defines the protocol for aggregating subsystem states into one composed
health view with bounded probes and explicit staleness.

FR-DIA-001: Compose System Health
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import HealthDetailsVO


class HealthCompositionProtocol(ABC):
    """Protocol for composing system health from subsystem states."""

    @abstractmethod
    async def compose_health(
        self,
        launcher_status: str = "unknown",
        gateway_status: str = "unknown",
        config_valid: bool = False,
        job_capacity_available: bool = True,
    ) -> HealthDetailsVO:
        """Aggregate subsystem states into one composed health view.

        FR-DIA-001: Composed health covers launcher, gateway, config, and job capacity.
        Overall status: healthy when all required report healthy;
        degraded when any reports degraded/stale; unhealthy when any fails.

        Each subsystem probe is bounded by probe_timeout_seconds configured
        at construction — slow subsystem becomes degraded/timeout, not stalled
        composition. Stale data carries staleness_delta_seconds indicator when
        composition_timestamp exceeds freshness_tolerance_seconds configured
        at construction.

        Args:
            launcher_status: Process liveness classification.
            gateway_status: Connection state classification.
            config_valid: Whether configuration snapshot is valid.
            job_capacity_available: Whether job capacity has available slots.

        Returns:
            HealthDetailsVO with overall_status, subsystems, staleness indicators, timestamp.
        """
        ...
