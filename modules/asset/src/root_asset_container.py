"""Root layer: Dependency injection container for the asset feature.

Wires asset capabilities to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured AssetOrchestrator.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .agent_asset_orchestrator import AssetOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class AssetContainer:
    """DI container that wires asset capabilities to the agent orchestrator."""

    def __init__(
        self,
        connection: object,
        security_validator: object | None = None,
        security_supervisor: object | None = None,
        job_scheduler: object | None = None,
        config_getter: object | None = None,
        gateway_client: object | None = None,
    ) -> None:
        self._connection = connection
        self._security_validator = security_validator
        self._security_supervisor = security_supervisor
        self._job_scheduler = job_scheduler
        self._config_getter = config_getter
        self._gateway_client = gateway_client
        self._lock = threading.Lock()
        self._orchestrator: AssetOrchestrator | None = None

    def get_orchestrator(self) -> AssetOrchestrator:
        if self._orchestrator is not None:
            return self._orchestrator

        with self._lock:
            if self._orchestrator is not None:
                return self._orchestrator

            from .agent_asset_orchestrator import AssetOrchestrator
            from .capabilities_asset_download import AssetDownloadCapability
            from .capabilities_asset_extract import AssetExtractCapability
            from .capabilities_asset_import import AssetImportCapability
            from .capabilities_asset_provider import AssetProviderMetadataCapability
            from .capabilities_asset_search_handler import AssetSearchHandler

            search = AssetSearchHandler(self._connection)
            download = AssetDownloadCapability(
                security_validator=self._security_validator,
                job_scheduler=self._job_scheduler,
                config_getter=self._config_getter,
            )
            extract = AssetExtractCapability(
                security_supervisor=self._security_supervisor,
            )
            import_ = AssetImportCapability(
                gateway_client=self._gateway_client,
                config_getter=self._config_getter,
            )
            metadata = AssetProviderMetadataCapability()

            self._orchestrator = AssetOrchestrator(
                search_capability=search,
                download_capability=download,
                extract_capability=extract,
                import_capability=import_,
                metadata_capability=metadata,
            )

        logger.info("Asset container fully wired")
        return self._orchestrator

    def shutdown(self) -> None:
        with self._lock:
            self._orchestrator = None

    def __repr__(self) -> str:
        return "AssetContainer()"


def create_asset_container(connection: object) -> AssetContainer:
    return AssetContainer(connection=connection)
