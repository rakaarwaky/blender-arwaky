"""Action request Value Object.

Represents an incoming action request with parameters, execution mode hints,
and optional metadata (tracking ID, confirmation flag, timeout override).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionRequestVO:
    """Action request — input payload for dispatcher validation and routing.

    Input fields set by caller; output fields (if any) enriched during processing.
    """

    # Required
    action_name: str
    parameters: dict[str, Any] = field(default_factory=dict)

    # Optional metadata
    execution_mode: str | None = None
    timeout_override: float | None = None
    confirmation_flag: bool = False
    tracking_id: str | None = None

    def __post_init__(self) -> None:
        if not self.action_name:
            raise ValueError("action_name must not be empty")
