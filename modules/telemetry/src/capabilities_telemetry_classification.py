"""Capability: Telemetry event classifier.

Implements TelemetryClassificationPort — handles classifying and categorizing
telemetry events into standardized categories per FR-TLM-002.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    Details,
    ErrorMessage,
    Prompt,
    ToolName,
)
from modules.shared.src.telemetry.contract_telemetry_classification_protocol import (
    TelemetryClassificationProtocol,
)
from modules.shared.src.telemetry.taxonomy_telemetry_event import EventType

logger = logging.getLogger("blender-arwaky-telemetry-service")


class TelemetryEventClassifier(TelemetryClassificationProtocol):
    """Telemetry event classification implementation.

    FR-TLM-002: Classifies events into standardized high-level categories.
    Unrecognized or missing categories default to ERROR (unknown).
    """

    def classify_event(
        self,
        raw_type: str | None = None,
        tool_name: ToolName | None = None,
        prompt_text: Prompt | None = None,
        error_message: ErrorMessage | None = None,
        metadata: Details | None = None,
    ) -> EventType:
        """Classify an event into a standardized category.

        FR-TLM-002: Every event belongs to exactly one primary category.
        If unrecognized or missing category, defaults to ERROR.
        """
        # Map raw type string to EventType enum
        if raw_type is not None:
            try:
                # Try to find matching EventType by value
                for event_type in EventType:
                    if event_type.value == raw_type:
                        return event_type
            except Exception as e:
                logger.debug("Failed to classify raw type '%s': %s", raw_type, e)

        # Infer category from available metadata
        if error_message is not None:
            # Events with errors are classified as ERROR
            return EventType.ERROR

        if tool_name is not None:
            # Tool executions are classified as TOOL_EXECUTION
            return EventType.TOOL_EXECUTION

        if prompt_text is not None:
            # Prompt-based events are classified as PROMPT_SENT
            return EventType.PROMPT_SENT

        # Default to ERROR for unrecognized categories (FR-TLM-002)
        logger.debug(
            "No category metadata available, defaulting to ERROR for raw_type=%s",
            raw_type,
        )
        return EventType.ERROR
