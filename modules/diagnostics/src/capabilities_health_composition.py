"""Capability: System health composer.

FR-DIA-001: Compose System Health
Aggregates subsystem states into one composed health view with bounded
probes and explicit staleness.
Implements HealthCompositionProtocol.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from modules.diagnostics.src.contract_health_composition_protocol import (
    HealthCompositionProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class HealthComposer(HealthCompositionProtocol):
    """Compose system health from subsystem states.

    Aggregates launcher, gateway, config, and job capacity into a single
    health view. Overall status derives deterministically.
    """

    def __init__(self) -> None:
        self._health_state: dict[str, Any] = {}

    async def compose_health(
        self,
        launcher_status: str = "unknown",
        gateway_status: str = "unknown",
        config_valid: bool = False,
        job_capacity_available: bool = True,
        source_tool: Any = None,
    ) -> dict[str, Any]:
        """Aggregate subsystem states into one composed health view."""
        subsystems: dict[str, str] = {
            "launcher": launcher_status,
            "gateway": gateway_status,
            "config": "healthy" if config_valid else "unhealthy",
            "job_capacity": "healthy" if job_capacity_available else "degraded",
        }

        statuses = list(subsystems.values())
        if all(s == "healthy" for s in statuses):
            overall = "healthy"
        elif any(s in ("unhealthy", "failed", "unreachable") for s in statuses):
            overall = "unhealthy"
        else:
            overall = "degraded"

        self._health_state = {
            "overall_status": overall,
            "subsystems": subsystems,
            "composition_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return dict(self._health_state)
