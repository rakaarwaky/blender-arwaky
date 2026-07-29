"""Diagnostics domain contract: logging policy protocol (ABC based).

Defines the protocol for enforcing one structured logging policy for
the whole system, with redaction applied at ingestion.

FR-DIA-004: Structured Logging Policy
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import Details, ToolName


class LoggingPolicyProtocol(ABC):
    """Protocol for enforcing structured logging policy with redaction."""

    @abstractmethod
    async def log_record(
        self,
        level: str,
        source_feature: str,
        message: str,
        fields: dict[str, Any] | None = None,
        tracking_id: str | None = None,
        source_tool: ToolName | None = None,
    ) -> Details:
        """Write sanitized structured log entry.

        FR-DIA-004: All features log through diagnostics policy.
        Redaction applied at ingestion before any destination write.
        Logging must not block callers; records buffer under backpressure.

        Args:
            level: Log level (debug, info, warning, error).
            source_feature: Feature emitting the log.
            message: Log message text.
            fields: Optional structured fields.
            tracking_id: Optional tracking identifier.

        Returns:
            Dict with logging confirmation and destination metadata.
        """
        pass
