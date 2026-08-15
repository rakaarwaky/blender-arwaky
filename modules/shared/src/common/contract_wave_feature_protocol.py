"""Shared protocol marker for feature capability implementations."""

from __future__ import annotations

from typing import Protocol

from .taxonomy_core_vo import ObjectName


class IWaveFeatureProtocol(Protocol):
    _taxonomy_type = ObjectName
    """Boundary implemented by feature capabilities and consumed by agents."""
