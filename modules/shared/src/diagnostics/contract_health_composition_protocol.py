"""Diagnostics domain contract: health composition protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import HealthCompositionRequestVO, HealthDetailsVO


class HealthCompositionProtocol(ABC):
    """Contract protocol for health status composition."""

    @abstractmethod
    async def compose_health(
        self,
        request: HealthCompositionRequestVO,
    ) -> HealthDetailsVO:
        """Compose health status across all registered subsystem probes."""
        ...

    @abstractmethod
    async def get_health(self) -> HealthDetailsVO | None:
        """Return cached or freshly composed health state for snapshots."""
        ...
