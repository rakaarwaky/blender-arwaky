"""Unit tests for MCP surface routing parity (FR-MCP-002).

FR-MCP-002: Route Tool Calls — every tool call routes to the same feature
aggregate the CLI surface uses; the surface never retries, composes, or
reinterprets the result. This suite injects fake container services, captures
the registered tool functions, invokes them, and asserts they delegate to the
correct service method with the correct arguments and pass the result through
unchanged.
"""

from __future__ import annotations

from typing import Any

from unittest.mock import patch

from modules.mcp.src.surface_command_execute import CommandExecuteHandler
from modules.mcp.src.surface_commands_list import CommandsListHandler
from modules.mcp.src.surface_health_check import HealthCheckHandler
from modules.mcp.src.surface_skill_read import SkillReadHandler
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


class FakeSkillReader:
    """Matches SkillDocumentationReader's read_skill interface."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, tuple]] = []

    def read_skill(self, skill_name, section=None):
        self.calls.append(("read_skill", (skill_name, section)))
        return f"# {skill_name}\n\nSkill content."


class FakeContainer:
    def __init__(
        self,
        orchestrator: FakeOrchestrator,
        diagnostics: FakeDiagnostics,
        skill_reader: FakeSkillReader,
    ) -> None:
        self.core_agent_orchestrator = orchestrator
        self.diagnostics = diagnostics
        self.skill_reader = skill_reader


class FakeMCP:
    def __init__(self) -> None:
        self.tools: dict[str, Any] = {}

    def tool(self):
        def decorator(fn):
            self.tools[fn.__name__] = fn
            return fn

        return decorator


class TestExecuteCommandRouting:
    """execute_command -> orchestrator.execute_action (sync facade, FR-DSP-004)."""

    async def test_routes_to_execute_action(self):
        orch = FakeOrchestrator()
        diag = FakeDiagnostics()
        reader = FakeSkillReader()
        container = FakeContainer(orch, diag, reader)
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
        diag = FakeDiagnostics()
        reader = FakeSkillReader()
        container = FakeContainer(orch, diag, reader)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_command_execute.get_container",
            return_value=container,
        ):
            CommandExecuteHandler.register_execute_command(mcp)
            await mcp.tools["execute_command"]("action_y", None)

        assert orch.calls[0][1] == ("action_y", {})


class TestListCommandsRouting:
    """list_commands -> orchestrator.discover_actions (FR-DSP-002)."""

    def test_routes_to_list_commands(self):
        orch = FakeOrchestrator()
        diag = FakeDiagnostics()
        reader = FakeSkillReader()
        container = FakeContainer(orch, diag, reader)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_commands_list.get_container",
            return_value=container,
        ):
            CommandsListHandler.register_list_commands(mcp)
            result = mcp.tools["list_commands"](None, None)

        assert orch.calls[0][0] == "discover_actions"
        assert result == {"routed": "discover_actions", "filter": None}


class TestReadSkillContextRouting:
    """read_skill_context -> skill_reader.read_skill (static docs surface)."""

    def test_routes_to_read_skill_context(self):
        orch = FakeOrchestrator()
        diag = FakeDiagnostics()
        reader = FakeSkillReader()
        container = FakeContainer(orch, diag, reader)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_skill_read.get_container",
            return_value=container,
        ):
            SkillReadHandler.register_read_skill_context(mcp)
            result = mcp.tools["read_skill_context"]("skill_x", None)

        assert reader.calls[0][0] == "read_skill"
        assert result == Prompt("# skill_x\n\nSkill content.")


class TestHealthCheckRouting:
    """health_check -> diagnostics.get_snapshot (FR-DIA-001)."""

    async def test_routes_to_health_check(self):
        orch = FakeOrchestrator()
        diag = FakeDiagnostics()
        reader = FakeSkillReader()
        container = FakeContainer(orch, diag, reader)
        mcp = FakeMCP()
        with patch(
            "modules.mcp.src.surface_health_check.get_container",
            return_value=container,
        ):
            HealthCheckHandler.register_health_check(mcp)
            result = await mcp.tools["health_check"]()

        assert diag.calls == [("get_snapshot", ("summary", None))]
        assert "health" in str(result)
