"""Telemetry domain contract: event classification protocol (ABC based).

FR-TLM-002: Classify and Categorize Events
Assigns events to fixed, low-cardinality taxonomy.
No PII parameters — only category strings for classification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.telemetry.taxonomy_telemetry_event import TelemetryCategory


class TelemetryClassificationProtocol(ABC):
    """Async protocol for classifying telemetry events into fixed taxonomy."""

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
        ...


class TelemetryClassificationPort(ABC):
    """Sync facade for orchestrator consumption."""

    @abstractmethod
    def classify_event(self, raw_type: str) -> TelemetryCategory:
        """Classify an event into a standardized category.

        FR-TLM-002: Tag the event with a high-level category.
        If unrecognized or missing category, default to ERROR (unknown).
        """
        ...
