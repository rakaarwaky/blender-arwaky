"""Capability: Telemetry event classifier.

Implements TelemetryClassificationProtocol — handles classifying and categorizing
telemetry events into standardized categories per FR-TLM-002.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import ActionName
from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from modules.shared.src.telemetry.taxonomy_event_constant import FEATURE_AREAS
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ClassificationResult,
    FeatureArea,
    OperationType,
    OutcomeCategory,
    TelemetryCategory,
)

logger = logging.getLogger("blender-arwaky.telemetry")


class TelemetryEventClassifier(TelemetryClassificationProtocol):
    def classify_event(
        self,
        action_type: ActionName,
        feature_area: FeatureArea | None = None,
    ) -> ClassificationResult:
        raw = str(action_type)
        resolved_feature = feature_area or FeatureArea(FEATURE_AREAS.get(raw, "other"))

        category_values = {c.value for c in TelemetryCategory}

        if raw == TelemetryCategory.STARTUP.value:
            return ClassificationResult(
                category=TelemetryCategory.STARTUP,
                feature_area=resolved_feature,
                operation_type=OperationType("execute"),
                outcome_category=OutcomeCategory("success"),
            )
        elif raw == TelemetryCategory.ERROR.value:
            return ClassificationResult(
                category=TelemetryCategory.ERROR,
                feature_area=resolved_feature,
                operation_type=OperationType("execute"),
                outcome_category=OutcomeCategory("error"),
            )
        elif raw in FEATURE_AREAS or raw in category_values:
            return ClassificationResult(
                category=TelemetryCategory.TOOL_EXECUTION,
                feature_area=resolved_feature,
                operation_type=OperationType("execute"),
                outcome_category=OutcomeCategory("success"),
            )

        return ClassificationResult(
            category=TelemetryCategory.OTHER,
            feature_area=resolved_feature,
            operation_type=OperationType("other"),
            outcome_category=OutcomeCategory("error"),
        )
