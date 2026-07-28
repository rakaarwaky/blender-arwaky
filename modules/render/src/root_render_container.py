"""Root layer: Dependency injection container for the render feature.

Wires render capabilities to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured RenderOrchestrator.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .agent_render_orchestrator import RenderOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class RenderContainer:
    """DI container that wires render capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared render management.
    All components are lazy-instantiated on first access.
    """

    def __init__(
        self,
        code_executor: object,
        gateway_client: Any | None = None,
        security_validator: Any | None = None,
        asset_feature: Any | None = None,
        config_getter: Any | None = None,
    ) -> None:
        """Initialize with dependencies for render capabilities.

        Args:
            code_executor: A callable or server capability that executes Python code.
            gateway_client: Gateway feature for Blender command transport.
            security_validator: Security policy for path validation.
            asset_feature: Asset feature for HDRI file acquisition.
            config_getter: Config feature for settings and policies.
        """
        self._code_executor = code_executor
        self._gateway_client = gateway_client
        self._security_validator = security_validator
        self._asset_feature = asset_feature
        self._config_getter = config_getter
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

            from .agent_render_orchestrator import RenderOrchestrator
            from .capabilities_camera_config import CameraConfigCapability
            from .capabilities_hdri_config import HdriConfigCapability
            from .capabilities_render_operate_executor import RenderOperateExecutor

            executor = RenderOperateExecutor(self._code_executor)
            camera_cap = CameraConfigCapability(
                gateway_client=self._gateway_client,
                security_validator=self._security_validator,
                config_getter=self._config_getter,
            )
            hdri_cap = HdriConfigCapability(
                gateway_client=self._gateway_client,
                security_validator=self._security_validator,
                asset_feature=self._asset_feature,
                config_getter=self._config_getter,
            )
            self._orchestrator = RenderOrchestrator(
                executor=executor,
                camera_config=camera_cap,
                hdri_config=hdri_cap,
            )

        logger.info("Render container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        """Shut down render components."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "RenderContainer()"


def create_render_container(
    code_executor: object,
    gateway_client: Any | None = None,
    security_validator: Any | None = None,
    asset_feature: Any | None = None,
    config_getter: Any | None = None,
) -> RenderContainer:
    """Factory function to create a new render container.

    Args:
        code_executor: A callable or server capability that executes Python code.
        gateway_client: Gateway feature for Blender command transport.
        security_validator: Security policy for path validation.
        asset_feature: Asset feature for HDRI file acquisition.
        config_getter: Config feature for settings and policies.

    Returns:
        Configured RenderContainer instance.
    """
    return RenderContainer(
        code_executor=code_executor,
        gateway_client=gateway_client,
        security_validator=security_validator,
        asset_feature=asset_feature,
        config_getter=config_getter,
    )
