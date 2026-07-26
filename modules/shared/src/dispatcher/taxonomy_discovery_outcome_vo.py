"""Discovery result Value Object.

Output of FR-DSP-002 ActionDiscoveryProtocol — canonical catalog snapshot with
optional filtering, version, and metadata detail level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class DiscoveryOutcomeVO:
    """Discovery result concept — action list with metadata and catalog version.

    Same canonical shape returned to CLI and MCP consumers.
    """

    # Output fields set by dispatcher
    actions: list[dict[str, Any]] = field(default_factory=list)
    catalog_version: int = 0
    result_count: int = 0
