"""Cross-cutting contract: execute action protocol (ABC based)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_core_vo import ActionName, Details, Prompt


class ExecuteActionProtocol(ABC):
    """Entry point interface for executing any BlenderArwaky action."""

    @abstractmethod
    async def execute(self, action: ActionName, args: Details | None = None) -> Prompt:
        """Dispatch an action to the orchestrator."""
        pass
