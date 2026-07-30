"""Diagnostics domain contract: health state provider protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_diagnostics_vo import HealthDetailsVO


class HealthStateProviderProtocol(ABC):
    """Provides cached or freshly composed health state for snapshots."""

    @abstractmethod
    async def get_health(self) -> HealthDetailsVO | None: ...
