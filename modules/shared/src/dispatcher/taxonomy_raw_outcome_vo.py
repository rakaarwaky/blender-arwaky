"""Raw outcome Value Object — encapsulates unnormalized dispatch outcomes.

Replaces dict[str, object] / str / bool primitives in contract signatures
with a single typed VO (AES402 compliance).
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class RawOutcomeVO:
    """Raw unnormalized outcome from a dispatch operation.

    Encapsulates the primitive fields that ResultNormalizationProtocol
    processes into a UnifiedResultEnvelopeVO.
    """

    success: bool = False
    message: str = ""
    tracking_id: str = ""
    is_background: bool = False
    data: dict[str, object] | None = None
    error_category: str | None = None
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)
