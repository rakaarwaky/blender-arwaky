"""Unit tests for MCP surface routing parity (FR-MCP-002).

FR-MCP-002: Route Tool Calls — every tool call routes to the same feature
aggregate the CLI surface uses; the surface never retries, composes, or
reinterprets the result. This suite injects fake container services, captures
the registered tool functions, invokes them, and asserts they delegate to the
correct service method with the correct arguments and pass the result through
unchanged.

Updated for MCP contract-based architecture: routing is now via McpRoutingProtocol
and responses via McpResponseProtocol instead of direct root container imports.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

from modules.mcp.src.surface_execute_command import ExecuteCommandSurface
from modules.mcp.src.surface_health_check import HealthCheckSurface
from modules.mcp.src.surface_list_commands import ListCommandsSurface
from modules.mcp.src.surface_read_skill import SkillDocumentationReader, SkillReadSurface
from modules.shared.src.common.taxonomy_core_vo import Prompt


class FakeOrchestrator:
    """Matches DispatcherOrchestrator's real interface (FR-DSP-002/004)."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    def execute_action(self, action, args):
        self.calls.append(("execute_action", (action, args)))
        return {"routed": "execute_action", "action": action}

    def discover_actions(self, name_filter=None, capability_filter=None, detail_level="standard"):
        self.calls.append(("discover_actions", (name_filter, capability_filter, detail_level)))
        return {"routed": "discover_actions", "filter": capability_filter}


class FakeDiagnostics:
    """Matches DiagnosticsOrchestrator's async get_snapshot interface."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    async def get_snapshot(self, detail_level="summary", section_filter=None):
        self.calls.append(("get_snapshot", (detail_level, section_filter)))
        return {"health": "ok", "detail_level": detail_level}


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


class FakeRoutingProtocol:
    """Fake McpRoutingProtocol implementation for testing."""

    def __init__(self, dispatcher=None, diagnostics=None):
        self._dispatcher = dispatcher
        self._diagnostics = diagnostics

    async def route_tool_call(self, tool_name, payload, tracking_id=None):
        if tool_name == "execute_command":
            action = payload.get("action", "")
            args = payload.get("args", {})
            if self._dispatcher:
                return self._dispatcher.execute_action(action, args)
            raise RuntimeError("Dispatcher aggregate not configured")
        elif tool_name == "list_commands":
            if self._dispatcher:
                return self._dispatcher.discover_actions()
            return {}
        elif tool_name == "health_check":
            if self._diagnostics:
                return await self._diagnostics.get_snapshot()
            return {"health": "ok"}
        raise ValueError(f"Unknown tool: {tool_name}")

    async def validate_tool_input(self, tool_name, payload, strict_mode=True):
        errors = []
        if tool_name == "execute_command":
            action = payload.get("action")
            if not action or not str(action).strip():
                errors.append("action is required")
        return errors


class FakeResponseProtocol:
    """Fake McpResponseProtocol implementation for testing."""

    async def format_response(self, result, tool_name, tracking_id="", error_category=None):
        return {"result": result, "tool": tool_name}

    async def mask_secrets(self, response):
        return response


class TestExecuteCommandRouting:
    """execute_command -> container.routing.route_tool_call (FR-MCP-002)."""

    async def test_routes_to_execute_action(self):
        orch = FakeOrchestrator()
        routing = FakeRoutingProtocol(dispatcher=orch)
        response = FakeResponseProtocol()
        mcp = FakeMCP()

        # Patch create_mcp_feature to return a container with our fakes
        with patch(
            "modules.mcp.src.root_mcp_container.create_mcp_feature",
        ) as mock_create:
            from modules.mcp.src.root_mcp_container import McpContainer

            mock_container = MagicMock(spec=McpContainer)
            mock_container.routing = routing
            mock_container.response = response
            mock_create.return_value = mock_container

            ExecuteCommandSurface.register(mcp, mock_container)
            fn = mcp.tools["execute_command"]
            result = await fn("action_x", {"a": 1})

        assert orch.calls == [("execute_action", ("action_x", {"a": 1}))]
        assert result == {"result": {"routed": "execute_action", "action": "action_x"}, "tool": "execute_command"}

    async def test_defaults_args_to_empty_dict(self):
        orch = FakeOrchestrator()
        routing = FakeRoutingProtocol(dispatcher=orch)
        response = FakeResponseProtocol()
        mcp = FakeMCP()

        with patch(
            "modules.mcp.src.root_mcp_container.create_mcp_feature",
        ) as mock_create:
            from modules.mcp.src.root_mcp_container import McpContainer

            mock_container = MagicMock(spec=McpContainer)
            mock_container.routing = routing
            mock_container.response = response
            mock_create.return_value = mock_container

            ExecuteCommandSurface.register(mcp, mock_container)
            await mcp.tools["execute_command"]("action_y", None)

        assert orch.calls[0][1] == ("action_y", {})


class TestListCommandsRouting:
    """list_commands -> container.routing.route_tool_call (FR-MCP-002)."""

    async def test_routes_to_list_commands(self):
        orch = FakeOrchestrator()
        routing = FakeRoutingProtocol(dispatcher=orch)
        response = FakeResponseProtocol()
        mcp = FakeMCP()

        with patch(
            "modules.mcp.src.root_mcp_container.create_mcp_feature",
        ) as mock_create:
            from modules.mcp.src.root_mcp_container import McpContainer

            mock_container = MagicMock(spec=McpContainer)
            mock_container.routing = routing
            mock_container.response = response
            mock_create.return_value = mock_container

            ListCommandsSurface.register(mcp, mock_container)
            result = await mcp.tools["list_commands"]()

        assert orch.calls[0][0] == "discover_actions"
        assert result["tool"] == "list_commands"
        assert "routed" in result["result"]


class TestReadSkillContextRouting:
    """read_skill_context -> SkillDocumentationReader.read_skill (static docs surface)."""

    def test_routes_to_read_skill_context(self):
        mcp = FakeMCP()
        with patch.object(SkillDocumentationReader, "read_skill", return_value="# skill_x\n\nSkill content."):
            SkillReadSurface.register_read_skill_context(mcp)
            result = mcp.tools["read_skill_context"]("skill_x", None)

        assert result == Prompt("# skill_x\n\nSkill content.")


class TestHealthCheckRouting:
    """health_check -> container.routing.route_tool_call (FR-MCP-002)."""

    async def test_routes_to_health_check(self):
        diag = FakeDiagnostics()
        routing = FakeRoutingProtocol(diagnostics=diag)
        response = FakeResponseProtocol()
        mcp = FakeMCP()

        with patch(
            "modules.mcp.src.root_mcp_container.create_mcp_feature",
        ) as mock_create:
            from modules.mcp.src.root_mcp_container import McpContainer

            mock_container = MagicMock(spec=McpContainer)
            mock_container.routing = routing
            mock_container.response = response
            mock_create.return_value = mock_container

            HealthCheckSurface.register(mcp, mock_container)
            result = await mcp.tools["health_check"]()

        assert len(diag.calls) == 1
        assert diag.calls[0][0] == "get_snapshot"
        assert "health" in str(result)
