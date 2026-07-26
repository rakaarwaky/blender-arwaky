"""Dispatcher domain contract: background submission protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.

FR-DSP-005: Submit Background Action
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_action_request_vo import ActionCommandVO
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


class BackgroundSubmitProtocol(ABC):
    """Protocol for submitting long-running actions as background jobs."""

    @abstractmethod
    def submit_background(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Submit an action for background execution via job feature.

        FR-DSP-005: Creates job, returns task reference. Enforces capacity limits.
        Returns envelope indicating polling is required for final outcome.
        """
        pass
