"""Contract tests for the MCP surface tool registry (FR-MCP-001, FR-MCP-002).

FR-MCP-001: Expose MCP Tools — the surface must register exactly the tool set
the dispatcher catalog and owning features declare (execute_command,
list_commands, read_skill_context, health_check).

FR-MCP-002: Route Tool Calls — every registered tool must wire to the same
agent aggregate the CLI surface uses; the surface never redefines semantics.

These tests use a fake MCP router so no live Blender connection or FastMCP
server is required.
"""

from __future__ import annotations

from typing import Any

from modules.mcp.src.surface_execute_command import ExecuteCommandHandler
from modules.mcp.src.surface_list_commands import ListCommandsHandler
from modules.mcp.src.surface_read_skill import SkillReadHandler
from modules.mcp.src.surface_tool_registry import ToolRegistryHandler

REQUIRED_TOOLS = {
    "execute_command",
    "list_commands",
    "read_skill_context",
    "health_check",
}


class FakeMCP:
    """Minimal stand-in for a FastMCP router that captures registered tools."""

    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


class TestToolRegistryContract:
    """FR-MCP-001: the registry exposes exactly the required tool set."""

    def test_registry_handler_has_register_tools(self):
        assert hasattr(ToolRegistryHandler, "register_tools")
        assert callable(ToolRegistryHandler.register_tools)

    def test_register_tools_wires_all_required_tools(self):
        mcp = FakeMCP()
        ToolRegistryHandler.register_tools(mcp)
        assert set(mcp.tools.keys()) == REQUIRED_TOOLS

    def test_register_tools_registers_exactly_four_tools(self):
        mcp = FakeMCP()
        ToolRegistryHandler.register_tools(mcp)
        assert len(mcp.tools) == 4

    def test_each_handler_has_a_register_method(self):
        for handler in (
            ExecuteCommandHandler,
            ListCommandsHandler,
            SkillReadHandler,
            HealthCheckHandler,
        ):
            method = getattr(handler, "register_execute_command", None) or getattr(
                handler, "register_list_commands", None
            ) or getattr(handler, "register_read_skill_context", None) or getattr(
                handler, "register_health_check", None
            )
            assert callable(method), f"{handler.__name__} missing a register_* method"


class TestIndividualToolRegistration:
    """Each tool registers under its canonical name (FR-MCP-001)."""

    def test_execute_command_registers_once(self):
        mcp = FakeMCP()
        ExecuteCommandHandler.register_execute_command(mcp)
        assert list(mcp.tools.keys()) == ["execute_command"]

    def test_list_commands_registers_once(self):
        mcp = FakeMCP()
        ListCommandsHandler.register_list_commands(mcp)
        assert list(mcp.tools.keys()) == ["list_commands"]

    def test_read_skill_context_registers_once(self):
        mcp = FakeMCP()
        SkillReadHandler.register_read_skill_context(mcp)
        assert list(mcp.tools.keys()) == ["read_skill_context"]

    def test_health_check_registers_once(self):
        mcp = FakeMCP()
        HealthCheckHandler.register_health_check(mcp)
        assert list(mcp.tools.keys()) == ["health_check"]
