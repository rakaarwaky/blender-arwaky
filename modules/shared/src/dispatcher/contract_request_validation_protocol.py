"""Dispatcher domain contract: request validation protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.

FR-DSP-003: Validate Action Request
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_action_request_vo import ActionCommandVO


class RequestValidationProtocol(ABC):
    """Protocol for validating action requests against catalog schema."""

    @abstractmethod
    def validate_request(self, request: ActionCommandVO) -> ActionCommandVO:
        """Validate an action request against the catalog.

        FR-DSP-003: Unknown action produces error; invalid params produce field-level detail.
        Generates tracking ID when absent. Does not mutate request or catalog state.
        Returns enriched same VO type with resolved_metadata and validated_tracking_id.
        """
        ...
