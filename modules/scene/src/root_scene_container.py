"""Root layer: Scene DI container.

Wires capabilities to the agent orchestrator.
"""

from __future__ import annotations

import threading

from modules.scene.src.surface_scene_command import SceneCommand
from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)
from modules.shared.src.scene.contract_scene_aggregate import ISceneAggregate


class SceneContainer:
    """Dependency injection container for scene feature."""

    def __init__(
        self,
        code_executor: ICodeExecutionProtocol,
        event_emitter: object | None = None,
    ) -> None:
        _ = SceneCommand
        self._code_executor = code_executor

        self._event_emitter = event_emitter
        self._aggregate: ISceneAggregate | None = None
        self._lock = threading.Lock()

    def get_aggregate(self) -> ISceneAggregate:
        """Return fully wired ISceneAggregate singleton (thread-safe)."""
        if self._aggregate is not None:
            return self._aggregate

        with self._lock:
            if self._aggregate is None:
                from .agent_scene_orchestrator import SceneOrchestrator
                from .capabilities_scene_cleanup_executor import SceneCleanupExecutor
                from .capabilities_scene_inspection_executor import SceneInspectionExecutor

                inspection = SceneInspectionExecutor(self._code_executor, self._event_emitter)
                cleanup = SceneCleanupExecutor(self._code_executor, self._event_emitter)

                self._aggregate = SceneOrchestrator(
                    inspection=inspection,
                    cleanup=cleanup,
                )

        return self._aggregate

    def shutdown(self) -> None:
        """Reset container state."""
        with self._lock:
            self._aggregate = None

    def __repr__(self) -> str:
        return "SceneContainer()"


def create_scene_container(
    code_executor: ICodeExecutionProtocol,
    event_emitter: object | None = None,
) -> SceneContainer:
    """Factory for SceneContainer."""
    return SceneContainer(code_executor=code_executor, event_emitter=event_emitter)
