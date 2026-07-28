"""Capability: CLI output renderer.

Implements CliRenderProtocol — renders aggregate results for human
reading (text) and machine consumption (JSON).

FR-CLI-002: Render Terminal Output
"""

from __future__ import annotations

import json
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ToolName
from modules.shared.src.cli.contract_cli_render_protocol import CliRenderProtocol


class CliRenderCapability(CliRenderProtocol):
    """Business logic for rendering CLI output in text or JSON format."""

    async def render_output(
        self,
        result: dict[str, Any],
        format: str = "text",
        _interactive: bool = True,
    ) -> str:
        """Render aggregate results for human reading or machine consumption.

        FR-CLI-002: Human-readable text is default; JSON when requested.
        JSON output is machine-stable with consistent field shape.

        Args:
            result: Aggregate result to render.
            format: Output format — "text" or "json".
            interactive: Whether terminal is interactive.

        Returns:
            Rendered string output.
        """
        if format == "json":
            return json.dumps(result, default=str, indent=2)

        return self._render_text(result, _interactive)

    def _render_text(self, result: dict[str, Any], _interactive: bool) -> str:
        """Render result as human-readable text."""
        lines: list[str] = []

        success = result.get("success", False)
        command = result.get("command")
        message = result.get("message", "")

        if command:
            lines.append(f"Command: {command}")
        if success:
            lines.append("Status: Success")
        else:
            lines.append("Status: Failed")

        if message:
            lines.append(f"Message: {message}")

        result_data = result.get("result")
        if result_data and isinstance(result_data, dict):
            lines.append("Data:")
            for key, value in result_data.items():
                if key not in ("success", "command", "message", "result"):
                    lines.append(f"  {key}: {value}")

        exit_code = result.get("exit_code")
        if exit_code is not None:
            lines.append(f"Exit Code: {exit_code}")

        return "\n".join(lines)
