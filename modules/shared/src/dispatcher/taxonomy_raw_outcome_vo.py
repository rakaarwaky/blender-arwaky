"""Dispatcher taxonomy — Raw outcome Value Object for normalization input.

Replaces raw dict[str, Any] in normalization contracts with a typed VO.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RawOutcomeVO:
    """Raw result produced by sync dispatch or background submission.

    This VO replaces raw dict[str, Any] in normalization contracts.
    """

    success: bool
    message: str
    tracking_id: str
    is_background: bool = False
    data: dict[str, Any] | None = None
    error_category: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)
