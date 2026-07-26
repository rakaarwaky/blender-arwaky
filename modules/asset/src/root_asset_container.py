"""Root layer: Dependency injection container for the asset feature.

Wires asset capabilities (search collector, import/export executor,
provider adapters) to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured AssetOrchestrator.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_orchestrator import AssetOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class AssetContainer:
    """DI container that wires asset capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared asset management.
    All components are lazy-instantiated on first access.
    """

    def __init__(self, command_sender: object) -> None:
        """Initialize with a command sender from the server module.

        Args:
            command_sender: A callable that sends commands to Blender.
        """
        self._command_sender = command_sender
        self._lock = threading.Lock()
        self._orchestrator: AssetOrchestrator | None = None

    def get_orchestrator(self) -> AssetOrchestrator:
        """Return a fully wired AssetOrchestrator (singleton).

        Lazy-initializes all dependencies on first call.
        Subsequent calls return the same orchestrator instance.
        """
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_orchestrator import AssetOrchestrator
            from .capabilities_asset_search_collector import AssetSearchCollector
            from .capabilities_polyhaven_adapter import PolyhavenAssetAdapter
            from .capabilities_sketchfab_adapter import SketchfabAssetAdapter

            # Register provider adapters
            providers: dict[str, object] = {
                "Polyhaven": PolyhavenAssetAdapter(self._command_sender),
                "Sketchfab": SketchfabAssetAdapter(self._command_sender),
            }

            collector = AssetSearchCollector(providers)
            self._orchestrator = AssetOrchestrator(collector=collector)

        logger.info("Asset container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        """Shut down asset components."""
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "AssetContainer()"


def create_asset_container(command_sender: object) -> AssetContainer:
    """Factory function to create a new asset container.

    Args:
        command_sender: A callable that sends commands to Blender.

    Returns:
        Configured AssetContainer instance.
    """
    return AssetContainer(command_sender=command_sender)
