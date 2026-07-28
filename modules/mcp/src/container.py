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
    from modules.diagnostics.src.capabilities_health_composition import DiagnosticsCapability
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
    _diagnostics: DiagnosticsCapability | None = None
    _skill_reader: SkillDocumentationReader | None = None

    @classmethod
    def get_instance(cls) -> MCPContainer:
        """Return the singleton MCPContainer instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _init_orchestrator(cls) -> None:
        """Lazy-initialize a fully-wired core agent orchestrator on first access.

        Uses the dispatcher composition root so the orchestrator's capabilities
        (catalog, discovery, validation, dispatch, normalization) are present and
        routed tool calls return real results instead of raising on unwired deps.
        """
        if cls._orchestrator is not None:
            return
        # Import here to avoid circular imports at module level.
        from modules.dispatcher.src.root_dispatcher_container import create_dispatcher_feature

        cls._orchestrator = create_dispatcher_feature()

    @property
    def core_agent_orchestrator(self) -> IDispatcherAggregate:
        """Return the core agent orchestrator (DispatcherOrchestrator)."""
        if self._orchestrator is None:
            self._init_orchestrator()
        assert self._orchestrator is not None
        return self._orchestrator

    @property
    def diagnostics(self) -> DiagnosticsCapability:
        """Return the diagnostics capability for health snapshots.

        FR-MCP-001 / FR-MCP-002: the health_check tool is owned by the diagnostics
        feature, not the dispatcher. Lazily constructed (stateless snapshot source).
        """
        if self._diagnostics is None:
            from modules.diagnostics.src.capabilities_health_composition import DiagnosticsCapability

            self._diagnostics = DiagnosticsCapability()
        assert self._diagnostics is not None
        return self._diagnostics

    @property
    def skill_reader(self) -> SkillDocumentationReader:
        """Return the static SKILL.md documentation reader.

        FR-MCP-001 / FR-MCP-002: the read_skill_context tool reads from the static
        documentation surface (versioned SKILL.md files), not a live aggregate.
        """
        if self._skill_reader is None:
            from modules.mcp.src.surface_skill_read import SkillDocumentationReader

            self._skill_reader = SkillDocumentationReader()
        assert self._skill_reader is not None
        return self._skill_reader


def get_container() -> MCPContainer:
    """Return the singleton MCPContainer for MCP surface handlers.

    Usage:
        orchestrator = get_container().core_agent_orchestrator
        result = orchestrator.execute_action(action, args)  # sync facade
    """
    return MCPContainer.get_instance()
