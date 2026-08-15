"""MCP routing proxy utilities — pure, stateless functions.

FR-MCP-002: Payload normalization and input validation.
No class, no self, no business rules.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


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
    dispatcher: Any | None = None,
    diagnostics: Any | None = None,
) -> dict[str, Any]:
    """Route a tool call to the correct handler dispatcher.

    Utility function for stateless routing. Used by McpRoutingImpl
    and standalone routing scenarios.

    Args:
        tool_name: Name of the MCP tool to route.
        payload: Tool call arguments.
        dispatcher: Optional dispatcher with execute_action/discover_actions.
        diagnostics: Optional diagnostics with get_snapshot.

    Returns:
        Routing result dict.

    Raises:
        ValueError: Unknown tool_name.
        RuntimeError: Required service not configured.
    """
    if tool_name == "execute_command":
        action = payload.get("action", "")
        args = payload.get("args", {})
        if dispatcher:
            request = ActionCommandVO(action_name=action, parameters=args)
            return dispatcher.execute_action(request)
        raise RuntimeError("Dispatcher aggregate not configured")

    if tool_name == "list_commands":
        if dispatcher:
            return dispatcher.discover_actions()
        return {}

    if tool_name == "health_check":
        if diagnostics:
            return diagnostics.get_snapshot()
        return {"health": "ok"}

    if tool_name == "get_config":
        return {}

    if tool_name == "help":
        return build_help_result(payload.get("topic"))

    raise ValueError(f"Unknown tool: {tool_name}")


def build_help_result(topic: str | None = None) -> dict[str, Any]:
    """Build embedded help from shared static taxonomy constants."""
    from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS
    from modules.shared.src.mcp.taxonomy_mcp_constant import CORE_TOOLS, HELP_SECTIONS, HELP_TOPICS

    selected = str(topic or "overview").strip().lower()
    if selected not in HELP_TOPICS:
        return {"error": f"Unknown help topic: {selected}", "available_topics": list(HELP_TOPICS)}
    result: dict[str, Any] = {
        "topic": selected,
        "available_topics": list(HELP_TOPICS),
        "core_tools": list(CORE_TOOLS),
        "content": HELP_SECTIONS[selected],
    }
    if selected == "actions":
        result["actions"] = [
            {"owner": owner, "name": name, "description": str(spec.get("description", name))}
            for owner, actions in sorted(DISPATCHER_ACTION_SCHEMAS.items())
            for name, spec in sorted(actions.items())
        ]
    return result
