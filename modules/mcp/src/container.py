"""MCP Module DI Container — core orchestrator accessor.

Provides get_container() for surface handlers to access the core agent
orchestrator (DispatcherOrchestrator) via its aggregate contract.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate


class MCPContainer:
    """DI container for the MCP module.

    Exposes the core_agent_orchestrator (DispatcherOrchestrator) which
    implements IDispatcherAggregate and provides execute_action() dispatch.
    """

    _instance: MCPContainer | None = None
    _orchestrator: IDispatcherAggregate | None = None

    @classmethod
    def get_instance(cls) -> MCPContainer:
        """Return the singleton MCPContainer instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def _init_orchestrator(cls) -> None:
        """Lazy-initialize the core agent orchestrator on first access."""
        if cls._orchestrator is not None:
            return
        # Import here to avoid circular imports at module level
        from modules.dispatcher.src.agent_dispatcher_orchestrator import DispatcherOrchestrator

        cls._orchestrator = DispatcherOrchestrator()

    @property
    def core_agent_orchestrator(self) -> IDispatcherAggregate:
        """Return the core agent orchestrator (DispatcherOrchestrator)."""
        if self._orchestrator is None:
            self._init_orchestrator()
        assert self._orchestrator is not None
        return self._orchestrator


def get_container() -> MCPContainer:
    """Return the singleton MCPContainer for MCP surface handlers.

    Usage:
        orchestrator = get_container().core_agent_orchestrator
        result = await orchestrator.execute_action(action, args)
    """
    return MCPContainer.get_instance()
