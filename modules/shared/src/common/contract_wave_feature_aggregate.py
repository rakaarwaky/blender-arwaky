"""Shared aggregate boundary for feature agents."""

from __future__ import annotations

from typing import Protocol

from .taxonomy_core_vo import ObjectName


class IWaveFeatureAggregate(Protocol):
    _taxonomy_type = ObjectName
    """Boundary exposed by feature agents to outer layers."""
