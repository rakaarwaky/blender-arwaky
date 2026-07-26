"""Unified result envelope Value Object.

Output of FR-DSP-006 ResultNormalizationProtocol — single envelope shape consumed
by CLI and MCP layers for all dispatcher outcomes (success, error, background submission).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class UnifiedResultEnvelopeVO:
    """Unified result envelope — standardized output for all dispatcher operations.

    Contains success indicator, data payload, error category, message, tracking ID,
    warnings, and metadata summary. Never leaks secrets or sensitive paths.
    """

    # Required fields
    success: bool = False
    message: str = ""
    tracking_id: str = ""

    # Optional fields (set when applicable)
    data: dict[str, Any] | None = None
    error_category: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    # Computed flags
    data_truncated: bool = False

    @classmethod
    def success_envelope(
        cls,
        message: str,
        tracking_id: str,
        data: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UnifiedResultEnvelopeVO:
        """Create a success envelope."""
        return cls(
            success=True,
            message=message,
            tracking_id=tracking_id,
            data=data,
            warnings=list(warnings) if warnings else [],
            metadata=dict(metadata) if metadata else {},
        )

    @classmethod
    def error_envelope(
        cls,
        message: str,
        tracking_id: str,
        error_category: str,
        data: dict[str, Any] | None = None,
        warnings: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> UnifiedResultEnvelopeVO:
        """Create an error envelope with category."""
        return cls(
            success=False,
            message=message,
            tracking_id=tracking_id,
            error_category=error_category,
            data=data,
            warnings=list(warnings) if warnings else [],
            metadata=dict(metadata) if metadata else {},
        )

    @classmethod
    def safe_error_envelope(cls, message: str = "Envelope construction failed") -> UnifiedResultEnvelopeVO:
        """Fallback envelope when envelope construction itself fails."""
        return cls(
            success=False,
            message=message,
            tracking_id="",
            error_category="execution_error",
        )
