"""Action request Value Object — merged input and output.

Frozen dataclass following the unified VO pattern:
  - Input fields set by caller
  - Output fields enriched by dispatcher during validation/routing
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ActionCommandVO:
    """Action request — merged input and output in one frozen VO.

    Input (set by caller):
      - action_name, parameters, execution_mode, timeout_override,
        confirmation_flag, tracking_id

    Output (enriched by dispatcher during validation):
      - resolved_metadata, validated_tracking_id, validation_warnings
    """

    # ─── Input ──────────────────────────────────────────────────

    action_name: str
    parameters: dict[str, Any] = field(default_factory=dict)
    execution_mode: str | None = None
    timeout_override: float | None = None
    confirmation_flag: bool = False
    tracking_id: str | None = None

    # ─── Output ─────────────────────────────────────────────────

    resolved_metadata: dict[str, Any] = field(default_factory=dict)
    validated_tracking_id: str = ""
    validation_warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.action_name:
            raise ValueError("action_name must not be empty")

        # Auto-generate tracking ID when absent
        validated = self.tracking_id or str(uuid.uuid4())
        object.__setattr__(self, "validated_tracking_id", validated)
