"""Capability: System health composer.

FR-DIA-001: Compose System Health
Aggregates subsystem states into one composed health view with bounded
probes and explicit staleness. Probe timeout and freshness tolerance are
configured at construction via the container (FRD config keys).
Implements HealthCompositionProtocol.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone

from modules.shared.src.diagnostics.contract_health_composition_protocol import (
    HealthCompositionProtocol,
)
from modules.shared.src.diagnostics.taxonomy_diagnostics_vo import (
    HealthCompositionRequestVO,
    HealthDetailsVO,
    SubsystemHealthVO,
)


class HealthComposer(HealthCompositionProtocol):
    """Compose system health from subsystem states.

    Aggregates launcher, gateway, config, and job capacity into a single
    health view with bounded probes and explicit staleness.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        probe_timeout_seconds: float = 5.0,
        freshness_tolerance_seconds: float = 10.0,
    ) -> None:
        self._probe_timeout_seconds = probe_timeout_seconds
        self._freshness_tolerance_seconds = freshness_tolerance_seconds
        self._composition_cache: HealthDetailsVO | None = None
        self._cache_time: float = 0.0
        self._cache_key: tuple | None = None

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def compose_health(
        self,
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO:
        """Aggregate subsystem states into one composed health view.

        FR-DIA-001: Composed health covers launcher, gateway, config, and job capacity.
        Overall status: healthy when all required report healthy;
        degraded when a subsystem reports degraded/stale; unhealthy when a subsystem fails.
        """
        now = datetime.now(timezone.utc)
        now_ts = now.timestamp()

        current_key = (
            request.launcher_status,
            request.gateway_status,
            request.config_valid,
            request.job_capacity_available,
        )

        if (
            self._composition_cache is not None
            and self._cache_time > 0
            and self._cache_key == current_key
            and (now_ts - self._cache_time) < self._freshness_tolerance_seconds
        ):
            cache = self._composition_cache
            staleness = {}
            for sub in cache.subsystems:
                if sub.staleness_delta_seconds > 0:
                    staleness[sub.name] = sub.staleness_delta_seconds
            return HealthDetailsVO(
                overall_status=cache.overall_status,
                subsystems=cache.subsystems,
                staleness_indicators=staleness,
                composition_timestamp=cache.composition_timestamp,
            )

        subsystems: list[SubsystemHealthVO] = []

        try:
            launcher_status = await asyncio.wait_for(
                self._probe_launcher(request.launcher_status),
                timeout=self._probe_timeout_seconds,
            )
            launcher_probe = self._probe_timeout_seconds * 1000
        except asyncio.TimeoutError:
            launcher_status = "timeout"
            launcher_probe = self._probe_timeout_seconds * 1000

        subsystems.append(SubsystemHealthVO(
            name="launcher",
            status=launcher_status,
            probe_duration_ms=launcher_probe,
        ))

        try:
            gateway_status = await asyncio.wait_for(
                self._probe_gateway(request.gateway_status),
                timeout=self._probe_timeout_seconds,
            )
            gateway_probe = self._probe_timeout_seconds * 1000
        except asyncio.TimeoutError:
            gateway_status = "timeout"
            gateway_probe = self._probe_timeout_seconds * 1000

        subsystems.append(SubsystemHealthVO(
            name="gateway",
            status=gateway_status,
            probe_duration_ms=gateway_probe,
        ))

        config_status = "healthy" if request.config_valid else "unhealthy"
        subsystems.append(SubsystemHealthVO(name="config", status=config_status))

        job_status = "healthy" if request.job_capacity_available else "degraded"
        subsystems.append(SubsystemHealthVO(name="job_capacity", status=job_status))

        all_healthy = True
        has_unhealthy = False
        for s in subsystems:
            if s.status != "healthy":
                all_healthy = False
            if s.status in ("unhealthy", "failed", "unreachable", "timeout"):
                has_unhealthy = True

        if all_healthy:
            overall = "healthy"
        elif has_unhealthy:
            overall = "unhealthy"
        else:
            overall = "degraded"

        staleness = {}
        if request.launcher_status == "unknown" or request.gateway_status == "unknown":
            staleness["launcher"] = 0.0
            staleness["gateway"] = 0.0

        timestamp = now.isoformat()
        result = HealthDetailsVO(
            overall_status=overall,
            subsystems=tuple(subsystems),
            staleness_indicators=staleness,
            composition_timestamp=timestamp,
        )

        self._composition_cache = result
        self._cache_time = now_ts
        self._cache_key = current_key

        return result

    async def get_health(self) -> HealthDetailsVO | None:
        """Return the most recently composed health state for snapshot provider contract."""
        return self._composition_cache

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    async def _probe_launcher(self, status: str) -> str:
        """Simulate launcher probe — returns status."""
        return status

    async def _probe_gateway(self, status: str) -> str:
        """Simulate gateway probe — returns status."""
        return status

    def __repr__(self) -> str:
        return "HealthComposer()"
