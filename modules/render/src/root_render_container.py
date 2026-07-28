"""Root layer: Render DI container.

Wires render capabilities to the agent orchestrator.
"""

from __future__ import annotations

import threading
from typing import TYPE_CHECKING

from modules.shared.src.gateway.contract_code_execution_protocol import (
    ICodeExecutionProtocol,
)

if TYPE_CHECKING:
    from .agent_render_orchestrator import RenderOrchestrator


class RenderContainer:
    """Dependency injection container for render feature."""

    def __init__(self, code_executor: ICodeExecutionProtocol) -> None:
        self._code_executor = code_executor
        self._lock = threading.Lock()
        self._orchestrator: RenderOrchestrator | None = None

    def get_orchestrator(self) -> RenderOrchestrator:
        """Return fully wired RenderOrchestrator singleton."""
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_render_orchestrator import RenderOrchestrator
            from .capabilities_render_camera_config_executor import (
                RenderCameraConfigExecutor,
            )
            from .capabilities_render_hdri_config_executor import (
                RenderHdriConfigExecutor,
            )
            from .capabilities_render_scene_image_executor import (
                RenderSceneImageExecutor,
            )
            from .capabilities_render_viewport_capture_executor import (
                RenderViewportCaptureExecutor,
            )

            viewport_capture = RenderViewportCaptureExecutor(self._code_executor)
            scene_image = RenderSceneImageExecutor(self._code_executor)
            camera_config = RenderCameraConfigExecutor(self._code_executor)
            hdri_config = RenderHdriConfigExecutor(self._code_executor)

            self._orchestrator = RenderOrchestrator(
                viewport_capture=viewport_capture,
                scene_image=scene_image,
                camera_config=camera_config,
                hdri_config=hdri_config,
            )

        return self._orchestrator

    def shutdown(self) -> None:
        """Reset container state."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "RenderContainer()"


def create_render_container(code_executor: ICodeExecutionProtocol) -> RenderContainer:
    """Factory for RenderContainer."""
    return RenderContainer(code_executor=code_executor)