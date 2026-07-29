"""Tests for telemetry event classification capability — FR-TLM-002.

FR-TLM-002: Event Categorization through Fixed Feature and Operation Taxonomy
- Events classified into standardized high-level categories
- Unrecognized or missing categories default to ERROR (unknown)
- Every event belongs to exactly one primary category
- No PII parameters — only action type strings for classification
"""

from __future__ import annotations

import pytest

from modules.shared.src.telemetry.taxonomy_telemetry_event import TelemetryCategory
from modules.telemetry.src.capabilities_telemetry_classification import (
    TelemetryEventClassifier,
)


# ─── FR-TLM-002: Known Event Types ────────────────────────────────────────


class TestKnownEventTypes:
    """FR-TLM-002: Classification of known event types."""

    def test_error_event_classified(self) -> None:
        """FR-TLM-002: Error events are classified as ERROR."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("error")
        assert result["outcome_category"] == "error"

    def test_startup_event_classified(self) -> None:
        """FR-TLM-002: Startup events are classified as STARTUP."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("startup")
        assert result["outcome_category"] == "success"

    def test_tool_execution_classified(self) -> None:
        """FR-TLM-002: Tool execution events are classified as TOOL_EXECUTION."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("tool_execution")
        assert result["outcome_category"] == "success"


# ─── FR-TLM-002: Default to ERROR ─────────────────────────────────────────


class TestDefaultError:
    """FR-TLM-002: Unrecognized events default to ERROR per FR-TLM-002."""

    def test_unknown_action_defaults_to_error(self) -> None:
        """FR-TLM-002: Unrecognized action defaults to ERROR."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("unknown_type")
        assert result["outcome_category"] == "error"

    def test_empty_action_defaults_to_error(self) -> None:
        """FR-TLM-002: Empty action defaults to ERROR."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("")
        assert result["outcome_category"] == "error"


# ─── FR-TLM-002: Feature Area Resolution ──────────────────────────────────


class TestFeatureAreaResolution:
    """FR-TLM-002: Feature area resolution from action type."""

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
        """FR-TLM-002: Known actions resolve to correct feature area."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(action_type)
        assert result["feature_area"] == expected_feature

    def test_unknown_action_defaults_to_other(self) -> None:
        """FR-TLM-002: Unknown actions default to 'other' feature area."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("unknown_action")
        assert result["feature_area"] == "other"

    def test_custom_feature_area_preserved(self) -> None:
        """FR-TLM-002: Explicit feature area overrides default resolution."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("action_execute", feature_area="custom")
        assert result["feature_area"] == "custom"


# ─── FR-TLM-002: Operation Type Resolution ────────────────────────────────


class TestOperationType:
    """FR-TLM-002: Operation type defaults to 'other' for unknown actions."""

    def test_default_operation_type_is_other(self) -> None:
        """FR-TLM-002: Default operation type is 'other' for unknown actions."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event("unknown_action")
        assert result["operation_type"] == "other"
