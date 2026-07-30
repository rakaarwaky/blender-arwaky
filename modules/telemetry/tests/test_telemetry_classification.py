"""Tests for telemetry event classification capability — FR-TLM-002.

FR-TLM-002: Event Categorization through Fixed Feature and Operation Taxonomy
- Events classified into standardized high-level categories
- Unrecognized or missing categories default to ERROR (unknown)
- Every event belongs to exactly one primary category
- No PII parameters — only action type strings for classification
"""

from __future__ import annotations

import pytest

from modules.shared.src.common.taxonomy_core_vo import ActionName
from modules.shared.src.telemetry.taxonomy_telemetry_event import (
    ClassificationResult,
    FeatureArea,
)
from modules.telemetry.src.capabilities_telemetry_classifier import (
    TelemetryEventClassifier,
)


class TestKnownEventTypes:
    def test_error_event_classified(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName("error"))
        assert result.outcome_category == "error"

    def test_startup_event_classified(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName("startup"))
        assert result.outcome_category == "success"

    def test_tool_execution_classified(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName("tool_execution"))
        assert result.outcome_category == "success"


class TestDefaultError:
    def test_unknown_action_defaults_to_error(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName("unknown_type"))
        assert result.outcome_category == "error"

    def test_empty_action_defaults_to_error(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName(""))
        assert result.outcome_category == "error"


class TestFeatureAreaResolution:
    @pytest.mark.parametrize(
        "action_type,expected_feature",
        [
            ("action_execute", "dispatcher"),
            ("health_check", "diagnostics"),
            ("search", "asset"),
            ("render", "render"),
        ],
    )
    def test_action_maps_to_feature_area(self, action_type: str, expected_feature: str) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName(action_type))
        assert result.feature_area == FeatureArea(expected_feature)

    def test_unknown_action_defaults_to_other(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName("unknown_action"))
        assert result.feature_area == FeatureArea("other")

    def test_custom_feature_area_preserved(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName("action_execute"), feature_area=FeatureArea("custom"))
        assert result.feature_area == FeatureArea("custom")


class TestOperationType:
    def test_default_operation_type_is_other(self) -> None:
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(ActionName("unknown_action"))
        assert result.operation_type == "other"
