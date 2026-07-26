"""Telemetry domain contract: event classification protocol (ABC based).

Defines the protocol for assigning events to fixed, low-cardinality
taxonomy so analytics remain comparable across versions.

FR-TLM-002: Classify and Categorize Events
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class TelemetryClassificationProtocol(ABC):
    """Protocol for classifying telemetry events into fixed taxonomy."""

    @abstractmethod
    async def classify_event(
        self,
        action_type: str,
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