"""Validated request Value Object.

Output of FR-DSP-003 RequestValidationProtocol — enriched request with resolved
action metadata, tracking ID, and validation warnings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ValidationResultVO:
    """Validated request concept — enriched request after catalog lookup and schema validation.

    Output fields set by dispatcher during validation; caller sets input fields.
    """

    # Copied from ActionRequestVO
    action_name: str
    parameters: dict[str, Any]
    execution_mode: str | None = None
    timeout_override: float | None = None
    confirmation_flag: bool = False
    tracking_id: str | None = None

    # Enriched by dispatcher
    resolved_metadata: dict[str, Any] = field(default_factory=dict)
    validated_tracking_id: str = ""
    validation_warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Auto-generate tracking ID when absent."""
        if not self.validated_tracking_id and self.tracking_id:
            object.__setattr__(self, "validated_tracking_id", self.tracking_id)
        elif not self.validated_tracking_id:
            import uuid

            object.__setattr__(self, "validated_tracking_id", str(uuid.uuid4()))
