"""Root layer: Dependency injection container for the render feature.

Wires render capabilities to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured RenderOrchestrator.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_orchestrator import RenderOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class RenderContainer:
    """DI container that wires render capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared render management.
    All components are lazy-instantiated on first access.
    """

    def __init__(self, code_executor: object) -> None:
        """Initialize with a code executor from the server module.

        Args:
            code_executor: A callable or server capability that executes Python code.
        """
        self._code_executor = code_executor
        self._lock = threading.Lock()
        self._orchestrator: RenderOrchestrator | None = None

    def get_orchestrator(self) -> RenderOrchestrator:
        """Return a fully wired RenderOrchestrator (singleton).

        Lazy-initializes all dependencies on first call.
        Subsequent calls return the same orchestrator instance.
        """
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_orchestrator import RenderOrchestrator
            from .capabilities_render_operate_executor import RenderOperateExecutor

            executor = RenderOperateExecutor(self._code_executor)
            self._orchestrator = RenderOrchestrator(executor=executor)

        logger.info("Render container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        """Shut down render components."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "RenderContainer()"


def create_render_container(code_executor: object) -> RenderContainer:
    """Factory function to create a new render container.

    Args:
        code_executor: A callable or server capability that executes Python code.

    Returns:
        Configured RenderContainer instance.
    """
    return RenderContainer(code_executor=code_executor)
