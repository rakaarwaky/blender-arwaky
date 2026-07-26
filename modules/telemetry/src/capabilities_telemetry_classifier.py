"""Capability: Telemetry event classifier.

Implements TelemetryClassificationProtocol — assigns events to fixed,
low-cardinality taxonomy so analytics remain comparable across versions.

FR-TLM-002: Classify and Categorize Events
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.telemetry.contract_telemetry_classification_protocol import TelemetryClassificationProtocol


class TelemetryClassificationCapability(TelemetryClassificationProtocol):
    """Business logic for classifying telemetry events into fixed taxonomy."""

    # Operation type taxonomy
    OPERATION_TYPES: dict[str, str] = {
        "action_execute": "execute",
        "action_list": "query",
        "health_check": "query",
        "settings_view": "query",
        "task_status": "query",
        "task_cancel": "delete",
        "search": "search",
        "download": "create",
        "import": "create",
        "render": "execute",
        "screenshot": "query",
    }

    # Outcome categories (fixed cardinality)
    OUTCOME_CATEGORIES = ["success", "failure", "rejected", "cancelled", "timeout"]

    async def classify_event(
        self,
        action_type: str,
        feature_area: str | None = None,
    ) -> dict[str, Any]:
        """Assign event to fixed taxonomy.

        FR-TLM-002: Feature area covers surfaces like object, scene, render.
        Operation type covers create, update, delete, query, execute.
        Unknown actions resolve to 'other' category; raw names never transmitted.

        Args:
            action_type: The candidate action to classify.
            feature_area: Optional feature area hint.

        Returns:
            Dict with categorized event including feature_area, operation_type, outcome_category.
        """
        # Determine feature area
        if feature_area is None:
            # Infer from action type
            mapping = {
                "action_execute": "dispatcher",
                "action_list": "dispatcher",
                "health_check": "diagnostics",
                "settings_view": "config",
                "task_status": "job",
                "task_cancel": "job",
                "search": "asset",
                "download": "asset",
                "import": "asset",
                "render": "render",
                "screenshot": "render",
            }
            feature_area = mapping.get(action_type, "other")

        # Determine operation type
        operation_type = self.OPERATION_TYPES.get(action_type, "other")

        return {
            "feature_area": feature_area,
            "operation_type": operation_type,
            "outcome_category": "success",  # Default; caller overrides
        }
