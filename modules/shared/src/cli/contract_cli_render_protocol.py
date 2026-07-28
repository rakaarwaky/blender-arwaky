"""CLI domain contract: render output protocol (ABC based).

Defines the protocol for rendering aggregate results for human reading
and machine consumption (JSON). Surface only — no business logic.

FR-CLI-002: Render Terminal Output
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ToolName


class CliRenderProtocol(ABC):
    """Protocol for rendering aggregate results to terminal or JSON."""

    @abstractmethod
    async def render_output(
        self,
        result: dict[str, Any],
        format: str = "text",
        interactive: bool = True,
    ) -> str:
        """Render aggregate results for human reading or machine consumption.

        FR-CLI-002: Human-readable text is default; JSON when requested.
        JSON output is machine-stable with consistent field shape.
        Sensitive values are masked through security policy rules.

        Args:
            result: Aggregate result to render.
            format: Output format — "text" or "json".
            interactive: Whether terminal is interactive (affects decoration).

        Returns:
            Rendered string output.
        """
        pass
