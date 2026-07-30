"""Discovery filter Value Object — encapsulates discover_actions filter parameters.

Replaces inline str | None / str primitives in contract signatures
with a single typed VO (AES402 compliance).
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DiscoveryFilterVO:
    """Filter criteria for action discovery queries.

    Encapsulates optional name/capability filters and detail level.
    Immutable once created.
    """

    name_filter: str | None = None
    capability_filter: str | None = None
    detail_level: str = "standard"
