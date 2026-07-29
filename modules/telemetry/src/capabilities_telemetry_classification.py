"""Capability: Telemetry event classifier.

Implements TelemetryClassificationPort — handles classifying and categorizing
telemetry events into standardized categories per FR-TLM-002.
"""

from __future__ import annotations

import logging

from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    FEATURE_AREAS,
    TelemetryCategory,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryEventClassifier(TelemetryClassificationProtocol):
    """Telemetry event classification implementation.

    FR-TLM-002: Classifies events into standardized high-level categories.
    Unrecognized or missing categories default to ERROR (unknown).
    No PII parameters — only category strings for classification.
    """

    def classify_event(
        self,
        action_type: str,
        feature_area: str | None = None,
    ) -> dict[str, str]:
        """Classify an event into a standardized category.

        FR-TLM-002: Every event belongs to exactly one primary category.
        If unrecognized or missing category, defaults to ERROR.

        Args:
            action_type: The candidate action to classify.
            feature_area: Optional feature area hint.

        Returns:
            Dict with categorized event including feature_area, operation_type, outcome_category.
        """
        # Resolve feature area from taxonomy mapping or use provided value
        resolved_feature = feature_area or FEATURE_AREAS.get(action_type, "other")

        # Map raw type string to TelemetryCategory enum
        if action_type is not None:
            try:
                for category in TelemetryCategory:
                    if category.value == action_type:
                        # ERROR category maps to "error" outcome, others to "success"
                        outcome = "error" if category == TelemetryCategory.ERROR else "success"
                        return {
                            "feature_area": resolved_feature,
                            "operation_type": "other",
                            "outcome_category": outcome,
                        }
            except (ValueError, TypeError) as e:
                logger.warning("Failed to classify raw type '%s': %s", action_type, e)

        # Default to ERROR for unrecognized categories (FR-TLM-002)
        logger.debug(
            "No category metadata available, defaulting to ERROR for action_type=%s",
            action_type,
        )
        return {
            "feature_area": resolved_feature,
            "operation_type": "other",
            "outcome_category": "error",
        }
