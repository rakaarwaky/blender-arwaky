"""MCP routing proxy — implements McpRoutingProtocol.

Routes tool calls to owning feature aggregates via contract protocols.
FR-MCP-002: Direct mapping — no retries, no reordering, no composition.
"""

from __future__ import annotations

import logging
from typing import Protocol

from modules.shared.src.mcp.contract_mcp_protocol import McpRoutingProtocol
from modules.shared.src.utility_envelope import (
    normalize_payload,
    validate_execute_command_input,
)

logger = logging.getLogger("BlenderMCPServer")


class _DispatcherProtocol(Protocol):
    """Protocol for dispatcher aggregates that handle tool routing."""

    def execute_action(self, action: str, args: dict[str, object]) -> dict[str, object]:
        ...

    def discover_actions(self, name_filter: str | None = None, capability_filter: str | None = None, detail_level: str = "standard") -> dict[str, object]:
        ...


class McpRoutingImpl(McpRoutingProtocol):
    """MCP routing implementation that delegates to owning feature contracts."""

    def __init__(self, dispatcher_aggregate: _DispatcherProtocol | None = None) -> None:
        self._dispatcher = dispatcher_aggregate

    async def route_tool_call(
        self,
        tool_name: str,
        payload: dict[str, object],
        tracking_id: str | None = None,
    ) -> dict[str, object]:
        """Route tool call to correct aggregate.

        FR-MCP-002: Every tool routes to same aggregate as CLI command.
        Divergence from CLI semantics is a defect.
        """
        if tool_name == "execute_command":
            action = payload.get("action", "")
            args = normalize_payload(payload.get("args"))
            if self._dispatcher:
                return self._dispatcher.execute_action(action, args)
            raise RuntimeError("Dispatcher aggregate not configured")

        # Route other tools based on tool_name mapping
        routing_map: dict[str, callable] = {
            "list_commands": lambda: self._dispatcher.discover_actions() if self._dispatcher else {},
            "health_check": lambda: {},  # Would route to diagnostics
            "get_config": lambda: {},  # Would route to config
            "read_skill_context": lambda: {},  # Would read static docs
        }

        handler = routing_map.get(tool_name)
        if handler:
            return handler()

        raise ValueError(f"Unknown tool: {tool_name}")

    async def validate_tool_input(
        self,
        tool_name: str,
        payload: dict[str, object],
        strict_mode: bool = True,
    ) -> list[str]:
        """Validate surface-level input shape.

        FR-MCP-002: Surface validates shape only (recognized, parsed, required fields).
        Semantic validation delegated to dispatcher + owning features.
        """
        if tool_name == "execute_command":
            return validate_execute_command_input(payload, strict_mode)

        return []
