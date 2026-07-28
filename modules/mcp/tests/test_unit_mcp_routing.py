"""Unit tests for MCP surface routing parity (FR-MCP-002).

FR-MCP-002: Route Tool Calls — every tool call routes to the same feature
aggregate the CLI surface uses; the surface never retries, composes, or
reinterprets the result. This suite injects a fake agent container, captures
the registered tool functions, invokes them, and asserts they delegate to the
correct orchestrator method with the correct arguments and pass the result
through unchanged.
"""

from __future__ import annotations

from typing import Any

from unittest.mock import patch

from modules.mcp.src.surface_command_execute import CommandExecuteHandler
from modules.mcp.src.surface_commands_list import CommandsListHandler
from modules.mcp.src.surface_health_check import HealthCheckHandler
from modules.mcp.src.surface_skill_read import SkillReadHandler


class FakeOrchestrator:
    """Records every call the surface makes into ``calls``."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    async def execute_action(self, action, args):
        self.calls.append(("execute_action", (action, args)))
        return {"routed": "execute_action", "action": action}

    def list_commands(self, domain, fmt):
        self.calls.append(("list_commands", (domain, fmt)))
        return {"routed": "list_commands"}

    def read_skill_context(self, name, section):
        self.calls.append(("read_skill_context", (name, section)))
        return {"routed": "read_skill_context"}

    def health_check(self):
        self.calls.append(("health_check", ()))
        return {"routed": "health_check"}


class FakeContainer:
    def __init__(self, orchestrator: FakeOrchestrator) -> None:
        self.core_agent_orchestrator = orchestrator


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


class TestExecuteCommandRouting:
    """execute_command -> orchestrator.execute_action (async)."""

    async def test_routes_to_execute_action(self):
        orch = FakeOrchestrator()
        container = FakeContainer(orch)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_command_execute.get_container",
            return_value=container,
        ):
            CommandExecuteHandler.register_execute_command(mcp)
            fn = mcp.tools["execute_command"]
            result = await fn("action_x", {"a": 1})

        assert orch.calls == [("execute_action", ("action_x", {"a": 1}))]
        # Result is passed through unchanged (no reinterpretation).
        assert result == {"routed": "execute_action", "action": "action_x"}

    async def test_defaults_args_to_empty_dict(self):
        orch = FakeOrchestrator()
        container = FakeContainer(orch)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_command_execute.get_container",
            return_value=container,
        ):
            CommandExecuteHandler.register_execute_command(mcp)
            await mcp.tools["execute_command"]("action_y", None)

        assert orch.calls[0][1] == ("action_y", {})


class TestListCommandsRouting:
    """list_commands -> orchestrator.list_commands (sync)."""

    def test_routes_to_list_commands(self):
        orch = FakeOrchestrator()
        container = FakeContainer(orch)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_commands_list.get_container",
            return_value=container,
        ):
            CommandsListHandler.register_list_commands(mcp)
            result = mcp.tools["list_commands"](None, None)

        assert orch.calls[0][0] == "list_commands"
        assert result == {"routed": "list_commands"}


class TestReadSkillContextRouting:
    """read_skill_context -> orchestrator.read_skill_context (sync)."""

    def test_routes_to_read_skill_context(self):
        orch = FakeOrchestrator()
        container = FakeContainer(orch)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_skill_read.get_container",
            return_value=container,
        ):
            SkillReadHandler.register_read_skill_context(mcp)
            result = mcp.tools["read_skill_context"]("skill_x", None)

        assert orch.calls == [("read_skill_context", ("skill_x", None))]
        assert result == {"routed": "read_skill_context"}


class TestHealthCheckRouting:
    """health_check -> orchestrator.health_check (async)."""

    async def test_routes_to_health_check(self):
        orch = FakeOrchestrator()
        container = FakeContainer(orch)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_health_check.get_container",
            return_value=container,
        ):
            HealthCheckHandler.register_health_check(mcp)
            result = await mcp.tools["health_check"]()

        assert orch.calls == [("health_check", ())]
        assert result == {"routed": "health_check"}
