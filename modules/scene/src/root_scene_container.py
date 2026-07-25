"""Root layer: Dependency injection container for the scene feature.

Wires scene capabilities to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured SceneOrchestrator.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_orchestrator import SceneOrchestrator
    from .capabilities_scene_inspection_adapter import SceneInspectionAdapter
    from .capabilities_scene_operate_executor import SceneOperateExecutor

logger = logging.getLogger("BlenderMCPServer")


class SceneContainer:
    """DI container that wires scene capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared scene management.
    All components are lazy-instantiated on first access.
    """

    def __init__(self, code_executor: object) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor
        self._lock = threading.Lock()
        self._orchestrator: SceneOrchestrator | None = None

    def get_orchestrator(self) -> SceneOrchestrator:
        """Return a fully wired SceneOrchestrator (singleton).

        Lazy-initializes all dependencies on first call.
        Subsequent calls return the same orchestrator instance.
        """
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_orchestrator import SceneOrchestrator
            from .capabilities_scene_operate_executor import SceneOperateExecutor

            executor = SceneOperateExecutor(self._code_executor)
            self._orchestrator = SceneOrchestrator(executor=executor)

        logger.info("Scene container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        """Shut down scene components."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "SceneContainer()"


def create_scene_container(code_executor: object) -> SceneContainer:
    """Factory function to create a new scene container.

    Args:
        code_executor: A callable or server capability that executes Python code.

    Returns:
        Configured SceneContainer instance.
    """
    return SceneContainer(code_executor=code_executor)
