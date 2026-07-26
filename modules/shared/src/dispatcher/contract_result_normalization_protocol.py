"""Dispatcher domain contract: result normalization protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.

FR-DSP-006: Normalize Operation Result
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


class ResultNormalizationProtocol(ABC):
    """Protocol for normalizing all dispatcher outcomes into unified envelopes."""

    @abstractmethod
    def normalize_result(
        self,
        raw_outcome: dict[str, Any],
        tracking_id: str,
        is_background: bool = False,
    ) -> UnifiedResultEnvelopeVO:
        """Normalize any dispatch or submission outcome into a unified result envelope.

        FR-DSP-006: Never leaks secrets; truncates oversized data; falls back to safe error.
        Returns identical shape for CLI and MCP consumers.
        """
        pass
