"""Telemetry domain contract: event classification protocol (ABC based).

FR-TLM-002: Classify and Categorize Events
Assigns events to fixed, low-cardinality taxonomy.
No PII parameters — only category strings for classification.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ActionName
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ClassificationResult,
    FeatureArea,
)


class TelemetryClassificationProtocol(ABC):
    """Sync protocol for classifying telemetry events into fixed taxonomy."""

    @abstractmethod
    def classify_event(
        self,
        action_type: ActionName,
        feature_area: FeatureArea | None = None,
    ) -> ClassificationResult:
        """Assign event to fixed taxonomy (feature area, operation type, outcome).

        FR-TLM-002: Feature area covers surfaces like object, scene, render.
        Operation type covers create, update, delete, query, execute.
        Unknown actions resolve to 'other' category; raw names never transmitted.

        Args:
            action_type: The candidate action to classify.
            feature_area: Optional feature area hint.

        Returns:
            ClassificationResult with categorized event.
        """
        ...
