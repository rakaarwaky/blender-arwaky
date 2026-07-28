"""Root layer: Scene DI container.

Wires capabilities to the agent orchestrator.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)

if TYPE_CHECKING:
    from .agent_scene_orchestrator import SceneOrchestrator


class SceneContainer:
    """Dependency injection container for scene feature."""

    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._code_executor = code_executor
        self._lock = threading.Lock()
        self._orchestrator: SceneOrchestrator | None = None

    def get_orchestrator(self) -> SceneOrchestrator:
        """Return fully wired SceneOrchestrator singleton."""
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_scene_orchestrator import SceneOrchestrator
            from .capabilities_scene_cleanup_executor import SceneCleanupExecutor
            from .capabilities_scene_inspection_executor import SceneInspectionExecutor

            inspection = SceneInspectionExecutor(self._code_executor)
            cleanup = SceneCleanupExecutor(self._code_executor)

            self._orchestrator = SceneOrchestrator(
                inspection=inspection,
                cleanup=cleanup,
            )

        return self._orchestrator

    def shutdown(self) -> None:
        """Reset container state."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "SceneContainer()"


def create_scene_container(code_executor: ICodeExecutionProtocol) -> SceneContainer:
    """Factory for SceneContainer."""
    return SceneContainer(code_executor=code_executor)