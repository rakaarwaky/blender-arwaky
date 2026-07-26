"""Dispatcher domain contract: synchronous dispatch protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.

FR-DSP-004: Dispatch Synchronous Action
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_action_request_vo import ActionCommandVO
from .taxonomy_unified_result_envelope_vo import UnifiedResultEnvelopeVO


class SyncDispatchProtocol(ABC):
    """Protocol for routing validated actions to owning features synchronously."""

    @abstractmethod
    def dispatch_sync(self, request: ActionCommandVO) -> UnifiedResultEnvelopeVO:
        """Route a validated action to its owning feature and return normalized result.

        FR-DSP-004: Enforces timeout, propagates tracking ID, maps domain errors.
        Returns standardized envelope; does not retry non-idempotent actions.
        """
        ...
