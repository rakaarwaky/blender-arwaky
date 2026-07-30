"""Discovery filter Value Object.

Taxonomy layer:
  - Filter criteria for action discovery.
  - Uses stable constants for detail level.
"""

from __future__ import annotations

from dataclasses import dataclass


class DiscoveryDetailLevel:
    """Standard detail levels for action discovery."""

    STANDARD = "standard"
    FULL = "full"


@dataclass(frozen=True)
class DiscoveryFilterVO:
    """Filter criteria for action discovery."""

    name_filter: str | None = None
    capability_filter: str | None = None
    detail_level: str = DiscoveryDetailLevel.STANDARD

    def __post_init__(self) -> None:
        if self.detail_level not in (
            DiscoveryDetailLevel.STANDARD,
            DiscoveryDetailLevel.FULL,
        ):
            raise ValueError(f"Unsupported detail level: {self.detail_level}")
