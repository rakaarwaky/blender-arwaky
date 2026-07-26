"""Contract: Telemetry classification port interface.

Defines the contract for classifying and categorizing telemetry events.
AES Port layer — depends only on taxonomy entities.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import Details, ErrorMessage, Prompt, ToolName
from .taxonomy_telemetry_event import EventType


class TelemetryClassificationPort(ABC):
    """Port interface for telemetry event classification and categorization."""

    @abstractmethod
    def classify_event(
        self,
        raw_type: str | None = None,
        tool_name: ToolName | None = None,
        prompt_text: Prompt | None = None,
        error_message: ErrorMessage | None = None,
        metadata: Details | None = None,
    ) -> EventType:
        """Classify an event into a standardized category.

        FR-TLM-002: Tag the event with a high-level category.
        If unrecognized or missing category, default to ERROR (unknown).
        """
        pass