"""CLI domain contract: error display protocol (ABC based).

Defines the protocol for presenting failures as categorized,
human-actionable guidance while guaranteeing sensitive content
never reaches the terminal.

FR-CLI-003: Display Errors
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ErrorString


class CliErrorProtocol(ABC):
    """Protocol for displaying categorized, actionable error messages."""

    @abstractmethod
    async def display_error(
        self,
        error: ErrorString,
        verbose: bool = False,
        format: str = "text",
    ) -> ErrorString:
        """Present failures as categorized, human-actionable guidance.

        FR-CLI-003: Every displayed error shows its category and includes
        an actionable message with remediation hint. Secrets are masked.
        JSON mode renders errors as structured objects.

        Args:
            error: Error dict with category, message, and optional detail.
            verbose: Whether to include additional structural detail.
            format: Output format — "text" or "json".

        Returns:
            Rendered error display string with exit code guidance.
        """
        pass
