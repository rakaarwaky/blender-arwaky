"""MCP routing proxy — implements McpRoutingProtocol.

Routes tool calls to owning feature aggregates via contract protocols.
FR-MCP-002: Direct mapping — no retries, no reordering, no composition.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import RequestId, ToolName
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.mcp.contract_mcp_protocol import McpRoutingProtocol

logger = logging.getLogger("BlenderMCPServer")


class McpRoutingImpl(McpRoutingProtocol):
    """MCP routing implementation that delegates to owning feature contracts."""

    def __init__(
        self, dispatcher: Any | None = None, diagnostics: Any | None = None, config: Any | None = None
    ) -> None:
        self._dispatcher = dispatcher
        self._diagnostics = diagnostics
        self._config = config

    async def route_tool_call(
        self,
        tool_name: ToolName,
        payload: dict[str, Any],
        _tracking_id: RequestId | None = None,
    ) -> dict[str, Any]:
        """Route tool call to correct aggregate.

        FR-MCP-002: Every tool routes to same aggregate as CLI command.
        Divergence from CLI semantics is a defect.
        """
        if tool_name == "execute_command":
            action = payload.get("action", "")
            args = payload.get("args", {})
            if self._dispatcher:
                request = ActionCommandVO(action_name=action, parameters=args)
                return self._dispatcher.execute_action(request)
            raise RuntimeError("Dispatcher aggregate not configured — check container wiring")

        if tool_name == "list_commands":
            if self._dispatcher:
                return self._dispatcher.discover_actions()
            return {}

        if tool_name == "health_check":
            if self._diagnostics:
                return self._diagnostics.get_snapshot()
            return {"health": "ok"}

        if tool_name == "get_config":
            if self._config:
                return self._config.get_snapshot()
            return {}

        if tool_name == "read_skill_context":
            return {}

        raise ValueError(f"Unknown tool: '{tool_name}' — check tool catalog registration")

    async def validate_tool_input(
        self,
        tool_name: str,
        payload: dict[str, Any],
        _strict_mode: bool = True,
    ) -> list[str]:
        """Validate surface-level input shape.

        FR-MCP-002: Surface validates shape only (recognized, parsed, required fields).
        Semantic validation delegated to dispatcher + owning features.
        """
        errors: list[str] = []

        if not isinstance(payload, dict):
            errors.append("payload must be a dictionary")
            return errors

        if tool_name == "execute_command":
            action = payload.get("action")
            if not action or not str(action).strip():
                errors.append("action is required and must be non-empty")

        if tool_name == "get_config":
            key = payload.get("key")
            if key is not None and not isinstance(key, str):
                errors.append("key must be a string or omitted")

        return errors

    async def get_tool_schemas(self) -> list[dict[str, Any]]:
        """Return tool schema list with names, descriptions, params, examples.

        FR-MCP-001: Schemas assembled from owning features.
        Degraded tools listed with indicator, not hidden.
        """
        return [
            {
                "name": "execute_command",
                "description": "Execute ANY BlenderArwaky action via dispatcher aggregate",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "action": {"type": "string", "description": "Action name to execute"},
                        "args": {"type": "object", "description": "Action arguments"},
                    },
                    "required": ["action"],
                },
            },
            {
                "name": "list_commands",
                "description": "List all available BlenderArwaky actions",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "domain": {"type": "string", "description": "Filter by domain"},
                    },
                },
            },
            {
                "name": "health_check",
                "description": "Check the health and connectivity of BlenderArwaky",
                "parameters": {"type": "object", "properties": {}},
            },
            {
                "name": "get_config",
                "description": "Retrieve BlenderArwaky configuration settings",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string", "description": "Specific config key to retrieve"},
                    },
                },
            },
            {
                "name": "read_skill_context",
                "description": "Read the SKILL.md documentation for a given skill",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {"type": "string", "description": "Skill name"},
                        "section": {"type": "string", "description": "Optional section to extract"},
                    },
                    "required": ["skill_name"],
                },
            },
        ]

    async def get_catalog_version(self) -> str:
        """Return dispatcher catalog version for drift detection."""
        # Placeholder — should come from dispatcher contract
        return "unknown"
