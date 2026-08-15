"""Contract tests for the MCP surface tool registry (FR-MCP-001, FR-MCP-002).

FR-MCP-001: Expose MCP Tools — the surface must register exactly the tool set
the dispatcher catalog and owning features declare (execute_command,
list_commands, help, health_check, get_config).

FR-MCP-002: Route Tool Calls — every registered tool must wire to the same
agent aggregate the CLI surface uses; the surface never redefines semantics.

These tests use a fake MCP router so no live Blender connection or FastMCP
server is required.
"""

from __future__ import annotations

from typing import Any

from modules.mcp.src.surface_execute_command import ExecuteCommandSurface
from modules.mcp.src.surface_get_config import GetConfigSurface
from modules.mcp.src.surface_health_check import HealthCheckSurface
from modules.mcp.src.surface_help import HelpSurface
from modules.mcp.src.surface_list_commands import ListCommandsSurface
from modules.mcp.src.surface_scene_tools import SceneToolsSurface
from modules.mcp.src.surface_tool_registry import ToolRegistrySurface

REQUIRED_TOOLS = {
    "execute_command",
    "get_config",
    "health_check",
    "list_commands",
    "help",
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


class FakeContainer:
    """Minimal DI container stub for surface registration tests."""

    routing: Any = None
    schema: Any = None
    response: Any = None


FAKE_CONTAINER = FakeContainer()


class TestToolRegistryContract:
    """FR-MCP-001: the registry exposes exactly the required tool set."""

    def test_registry_surface_has_register_tools(self):
        assert hasattr(ToolRegistrySurface, "register_tools")
        assert callable(ToolRegistrySurface.register_tools)

    def test_register_tools_registers_core_tools(self):
        """The public registry exposes exactly the five core tools."""
        mcp = FakeMCP()
        ToolRegistrySurface.register_tools(mcp, FAKE_CONTAINER)
        assert set(mcp.tools) == REQUIRED_TOOLS

    def test_each_surface_has_register_method(self):
        """Each core surface class exposes the shared register method."""
        assert hasattr(ExecuteCommandSurface, "register")
        assert hasattr(ListCommandsSurface, "register")
        assert hasattr(HealthCheckSurface, "register")
        assert hasattr(GetConfigSurface, "register")
        assert hasattr(HelpSurface, "register")


class TestIndividualToolRegistration:
    """Each tool registers under its canonical name (FR-MCP-001)."""

    def test_execute_command_registers_once(self):
        mcp = FakeMCP()
        ExecuteCommandSurface.register(mcp, FAKE_CONTAINER)
        assert "execute_command" in mcp.tools

    def test_list_commands_registers_once(self):
        mcp = FakeMCP()
        ListCommandsSurface.register(mcp, FAKE_CONTAINER)
        assert "list_commands" in mcp.tools

    def test_help_registers_once(self):
        mcp = FakeMCP()
        HelpSurface.register(mcp, FAKE_CONTAINER)
        assert "help" in mcp.tools

    def test_health_check_registers_once(self):
        mcp = FakeMCP()
        HealthCheckSurface.register(mcp, FAKE_CONTAINER)
        assert "health_check" in mcp.tools

    def test_get_config_registers_once(self):
        mcp = FakeMCP()
        GetConfigSurface.register(mcp, FAKE_CONTAINER)
        assert "get_config" in mcp.tools

    def test_inspect_scene_registers_once(self):
        class FakeAggregate:
            async def get_scene_info(self, request):
                return request

            async def cleanup_scene(self, request):
                return request

        mcp = FakeMCP()
        SceneToolsSurface.register_scene_tools(mcp, aggregate_factory=lambda: FakeAggregate())
        assert "inspect_scene" in mcp.tools

    def test_cleanup_scene_registers_once(self):
        class FakeAggregate:
            async def get_scene_info(self, request):
                return request

            async def cleanup_scene(self, request):
                return request

        mcp = FakeMCP()
        SceneToolsSurface.register_scene_tools(mcp, aggregate_factory=lambda: FakeAggregate())
        assert "cleanup_scene" in mcp.tools
