"""Telemetry domain contract: event classification protocol (ABC based).

Defines the protocol for assigning events to fixed, low-cardinality
taxonomy so analytics remain comparable across versions.

FR-TLM-002: Classify and Categorize Events
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ActionName


class TelemetryClassificationProtocol(ABC):
    """Protocol for classifying telemetry events into fixed taxonomy."""

    @abstractmethod
    async def classify_event(
        self,
        action_type: ActionName,
        feature_area: str | None = None,
    ) -> dict[str, Any]:
        """Assign event to fixed taxonomy (feature area, operation type, outcome).

        FR-TLM-002: Feature area covers surfaces like object, scene, render.
        Operation type covers create, update, delete, query, execute.
        Unknown actions resolve to 'other' category; raw names never transmitted.

        Args:
            action_type: The candidate action to classify.
            feature_area: Optional feature area hint.

        Returns:
            Dict with categorized event including feature_area, operation_type, outcome_category.
        """
        pass

# --- Merged from contract_telemetry_classification.py ---

"""Contract: Telemetry classification port interface.

Defines the contract for classifying and categorizing telemetry events.
AES Port layer — depends only on taxonomy entities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import Details, ErrorMessage, Prompt, ToolName
from .taxonomy_telemetry_event import EventType


class TelemetryClassificationPort(ABC):
    """Port interface for telemetry event classification and categorization."""

    @abstractmethod
    def classify_event(
        self,
        raw_type: str | None = None,
        tool_name: ToolName | None = None,
        prompt_text: Prompt | None = None,
        error_message: ErrorMessage | None = None,
        metadata: Details | None = None,
    ) -> EventType:
        """Classify an event into a standardized category.

        FR-TLM-002: Tag the event with a high-level category.
        If unrecognized or missing category, default to ERROR (unknown).
        """
        pass
