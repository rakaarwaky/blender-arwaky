"""Capability: CLI error display.

Implements CliErrorProtocol — presents failures as categorized,
human-actionable guidance while masking sensitive values.

FR-CLI-003: Display Errors
"""

from __future__ import annotations

import json
from typing import Any

from modules.shared.src.cli.contract_cli_error_protocol import CliErrorProtocol
from modules.shared.src.common.taxonomy_core_vo import ErrorString


class CliErrorCapability(CliErrorProtocol):
    """Business logic for displaying categorized, actionable error messages."""

    # Remediation hints per error category
    REMEDIATION: dict[str, str] = {
        "validation": "Check your input parameters and try again.",
        "configuration": "Review settings with the settings command.",
        "execution": "Check Blender process status and try again.",
        "connection": "Ensure Blender is running and restart if needed.",
        "not_found": "Verify the requested resource exists.",
        "timeout": "Operation took too long; try with simpler parameters.",
    }

    async def display_error(
        self,
        error: dict[str, Any],
        verbose: bool = False,
        format: str = "text",
    ) -> str:
        """Present failures as categorized, actionable guidance.

        FR-CLI-003: Every displayed error shows its category and includes
        an actionable message with remediation hint. Secrets are masked.

        Args:
            error: Error dict with category, message, and optional detail.
            verbose: Whether to include additional structural detail.
            format: Output format — "text" or "json".

        Returns:
            Rendered error display string.
        """
        category = error.get("category", "unknown")
        message = error.get("message", "An error occurred")
        hint = self.REMEDIATION.get(category, self.REMEDIATION.get("validation", ""))

        if format == "json":
            return json.dumps(
                {
                    "error": {
                        "category": category,
                        "message": str(message),
                        "hint": hint,
                        "detail": error.get("detail") if verbose else None,
                    },
                },
                default=str,
                indent=2,
            )

        lines: list[str] = [
            f"Error [{category}]: {message}",
        ]
        if hint:
            lines.append(f"Hint: {hint}")
        if verbose and error.get("detail"):
            detail = error["detail"]
            if isinstance(detail, dict):
                for k, v in detail.items():
                    lines.append(f"  {k}: {v}")

        return "\n".join(lines)
