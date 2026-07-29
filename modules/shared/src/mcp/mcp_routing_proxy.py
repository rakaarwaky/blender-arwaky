"""MCP routing proxy utilities — pure, stateless functions.

FR-MCP-002: Payload normalization and input validation.
No class, no self, no business rules.
"""

from __future__ import annotations

from typing import Any, Callable

from modules.shared.src.mcp.contract_mcp_protocol import McpRoutingProtocol


def normalize_payload(payload: Any) -> dict[str, Any]:
    """Ensure payload is a dict; coerce non-dict to empty dict."""
    if isinstance(payload, dict):
        return payload
    return {}


def validate_execute_command_input(payload: dict[str, Any]) -> list[str]:
    """Validate surface-level input shape for execute_command tool.

    Checks that 'action' field is present and non-empty.
    Semantic validation is delegated to the dispatcher.
    """
    action = payload.get("action")
    if not action or not str(action).strip():
        return ["action is required"]
    return []


def route_tool_call(
    tool_name: str,
    payload: dict[str, Any],
    dispatcher: Callable | None = None,
) -> dict[str, Any]:
    """Route tool call to correct aggregate.

    FR-MCP-002: Every tool routes to same aggregate as CLI command.
    Divergence from CLI semantics is a defect.
    """
    if tool_name == "execute_command":
        action = payload.get("action", "")
        args = normalize_payload(payload.get("args"))
        if dispatcher:
            return dispatcher.execute_action(action, args)
        raise RuntimeError("Dispatcher aggregate not configured")

    routing_map: dict[str, Callable] = {
        "list_commands": lambda d: d.discover_actions() if d else {},
        "health_check": lambda _: {},
        "get_config": lambda _: {},
        "read_skill_context": lambda _: {},
    }

    handler = routing_map.get(tool_name)
    if handler:
        return handler(dispatcher)

    raise ValueError(f"Unknown tool: {tool_name}")
