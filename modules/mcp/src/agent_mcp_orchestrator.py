"""MCP Module DI Container — core orchestrator accessor.

Provides get_container() for surface handlers to access the core agent
orchestrator (DispatcherOrchestrator) via its aggregate contract, plus the
supporting aggregates the MCP tool set needs:

- ``core_agent_orchestrator`` (dispatcher feature) — execute_action / discover_actions
- ``diagnostics`` (diagnostics feature)        — health snapshots (FR-MCP-001/002:
  the Health check tool is owned by the diagnostics feature, not the dispatcher)
- ``skill_reader`` (static documentation surface) — SKILL.md reader for the
  read_skill_context tool (FR-MCP-001/002: static documentation surface)

FR-MCP-002: every MCP tool routes to the same feature aggregate the CLI surface
uses. The dispatcher orchestrator is assembled through the dispatcher composition
root so routed calls are functional rather than raising on unwired dependencies.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.diagnostics.src.agent_diagnostics_orchestrator import (
        DiagnosticsOrchestrator,
    )
    from modules.dispatcher.src.agent_dispatcher_orchestrator import DispatcherOrchestrator
    from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
    from modules.mcp.src.surface_skill_read import SkillDocumentationReader


class MCPContainer:
    """DI container for the MCP module.

    Exposes the core_agent_orchestrator (DispatcherOrchestrator) which
    implements IDispatcherAggregate and provides execute_action() / discover_actions().
    Also exposes the diagnostics and skill-reader aggregates required by the
    health_check and read_skill_context tools per the FR-MCP-001 tool mapping.
    """

    _instance: MCPContainer | None = None
    _orchestrator: IDispatcherAggregate | None = None
    _diagnostics: DiagnosticsOrchestrator | None = None
    _skill_reader: SkillDocumentationReader | None = None

    def __init__(self) -> None:
        raise RuntimeError("Use MCPContainer.get_container() instead")

    @classmethod
    def get_container(cls) -> MCPContainer:
        """Return the singleton MCPContainer."""
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._wired = False
        return cls._instance

    @classmethod
    def wire(
        cls,
        orchestrator: IDispatcherAggregate | None = None,
        diagnostics: DiagnosticsOrchestrator | None = None,
        skill_reader: SkillDocumentationReader | None = None,
    ) -> None:
        """Wire the MCP module with the given aggregates."""
        container = cls.get_container()
        container._orchestrator = orchestrator
        container._diagnostics = diagnostics
        container._skill_reader = skill_reader
        container._wired = True

    @property
    def diagnostics(self) -> DiagnosticsOrchestrator:
        """Return the diagnostics aggregate facade."""
        if not self._wired or self._diagnostics is None:
            raise RuntimeError("MCP diagnostics not wired")
        return self._diagnostics

    @property
    def core_agent_orchestrator(self) -> IDispatcherAggregate:
        """Return the core agent orchestrator implementing IDispatcherAggregate."""
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("MCP orchestrator not wired")
        return self._orchestrator

    @property
    def skill_reader(self) -> SkillDocumentationReader:
        """Return the skill documentation reader."""
        if not self._wired or self._skill_reader is None:
            raise RuntimeError("MCP skill reader not wired")
        return self._skill_reader


def create_container() -> MCPContainer:
    """Factory function to create and wire the MCP container."""
    container = MCPContainer.get_container()
    return container
