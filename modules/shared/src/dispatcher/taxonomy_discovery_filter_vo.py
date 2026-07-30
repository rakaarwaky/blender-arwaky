"""Dispatcher taxonomy — Discovery filter Value Object and detail-level constants.

Replaces raw string arguments in discovery contracts with a typed VO.
"""

from __future__ import annotations

from dataclasses import dataclass


class DiscoveryDetailLevel:
    """Detail level constants for action discovery."""

    STANDARD: str = "standard"
    FULL: str = "full"


@dataclass(frozen=True)
class DiscoveryFilterVO:
    """Filter criteria for action discovery.

    Encapsulates name filter, capability filter, and detail level.
    Validates detail level at construction.
    """

    name_filter: str | None = None
    capability_filter: str | None = None
    detail_level: str = DiscoveryDetailLevel.STANDARD

    def __post_init__(self) -> None:
        if self.detail_level not in (DiscoveryDetailLevel.STANDARD, DiscoveryDetailLevel.FULL):
            raise ValueError(f"Unsupported detail level: {self.detail_level}")
