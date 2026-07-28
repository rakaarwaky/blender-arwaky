"""Tests for telemetry event classification capability — FR-TLM-002.

FR-TLM-002: Event Categorization through Fixed Feature and Operation Taxonomy
- Events classified into standardized high-level categories
- Unrecognized or missing categories default to ERROR (unknown)
- Every event belongs to exactly one primary category
"""

from __future__ import annotations

from modules.shared.src.telemetry.taxonomy_telemetry_event import EventType
from modules.telemetry.src.capabilities_telemetry_classification import (
    TelemetryEventClassifier,
)

# ─── FR-TLM-002: Known Event Types ────────────────────────────────────────


class TestKnownEventTypes:
    """FR-TLM-002: Classification of known event types."""

    def test_error_event_classified(self) -> None:
        """FR-TLM-002: Error events are classified as ERROR."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(error_message="something broke")
        assert result == EventType.ERROR

    def test_tool_execution_classified(self) -> None:
        """FR-TLM-002: Tool execution events are classified as TOOL_EXECUTION."""
        from modules.shared.src.common.taxonomy_core_vo import ToolName

        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(tool_name=ToolName("my_tool"))
        assert result == EventType.TOOL_EXECUTION

    def test_prompt_sent_classified(self) -> None:
        """FR-TLM-002: Prompt events are classified as PROMPT_SENT."""
        from modules.shared.src.common.taxonomy_core_vo import Prompt

        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(prompt_text=Prompt("hello"))
        assert result == EventType.PROMPT_SENT


# ─── FR-TLM-002: Default to ERROR ─────────────────────────────────────────


class TestDefaultError:
    """FR-TLM-002: Unrecognized events default to ERROR per FR-TLM-002."""

    def test_no_metadata_defaults_to_error(self) -> None:
        """FR-TLM-002: Events with no metadata default to ERROR."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event()
        assert result == EventType.ERROR

    def test_unknown_raw_type_defaults_to_error(self) -> None:
        """FR-TLM-002: Unrecognized raw type defaults to ERROR."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(raw_type="unknown_type")
        assert result == EventType.ERROR

    def test_none_raw_type_defaults_to_error(self) -> None:
        """FR-TLM-002: None raw type defaults to ERROR when no other metadata."""
        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(raw_type=None)
        assert result == EventType.ERROR


# ─── FR-TLM-002: Raw Type Matching ────────────────────────────────────────


class TestRawTypeMatching:
    """FR-TLM-002: Raw type string matching to EventType enum."""

    def test_matching_raw_type_returns_correct_event(self) -> None:
        """FR-TLM-002: Valid raw type string matches corresponding EventType."""
        classifier = TelemetryEventClassifier()
        # Assuming EventType has values that match raw strings
        for event_type in EventType:
            result = classifier.classify_event(raw_type=event_type.value)
            assert result == event_type

    def test_raw_type_overrides_no_metadata(self) -> None:
        """FR-TLM-002: Raw type is recognized when no other metadata present."""
        classifier = TelemetryEventClassifier()
        for event_type in EventType:
            result = classifier.classify_event(raw_type=event_type.value)
            assert result == event_type


# ─── FR-TLM-002: Priority Resolution ──────────────────────────────────────


class TestPriorityResolution:
    """FR-TLM-002: Event classification priority resolution."""

    def test_error_overrides_tool_name(self) -> None:
        """FR-TLM-002: Error message takes priority over tool_name when both present."""
        from modules.shared.src.common.taxonomy_core_vo import Prompt, ToolName

        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(
            tool_name=ToolName("test"),
            prompt_text=Prompt("hello"),
            error_message="broken",
        )
        assert result == EventType.ERROR

    def test_tool_name_overrides_prompt(self) -> None:
        """FR-TLM-002: Tool name takes priority over prompt when both present."""
        from modules.shared.src.common.taxonomy_core_vo import Prompt

        classifier = TelemetryEventClassifier()
        result = classifier.classify_event(
            tool_name="my_tool",
            prompt_text=Prompt("hello"),
        )
        assert result == EventType.TOOL_EXECUTION
