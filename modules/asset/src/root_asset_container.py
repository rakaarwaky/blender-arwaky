"""Root layer: Dependency injection container for the asset feature.

Wires asset capabilities (search, download, extract, import, metadata) to
the agent orchestrator and bootstraps the system.
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

    def __init__(self, connection: object) -> None:
        self._connection = connection
        self._lock = threading.Lock()
        self._orchestrator: AssetOrchestrator | None = None

    def get_orchestrator(self) -> AssetOrchestrator:
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_orchestrator import AssetOrchestrator
            from .capabilities_asset_search import AssetSearchCapability

            search = AssetSearchCapability(self._connection)
            self._orchestrator = AssetOrchestrator(collector=search)

        logger.info("Asset container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "AssetContainer()"


def create_asset_container(connection: object) -> AssetContainer:
    return AssetContainer(connection=connection)
