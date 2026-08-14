"""Root layer: Dependency injection container for the asset feature.

Wires asset capabilities to the agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured AssetOrchestrator.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from modules.shared.src.asset.contract_asset_provider_connection_protocol import (
    IAssetProviderConnection,
)

if TYPE_CHECKING:
    from .agent_asset_orchestrator import AssetOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class AssetContainer:
    """DI container that wires asset capabilities to the agent orchestrator.

    CE02: FRD config keys (`overwrite_policy`, `enabled_providers`,
    `maximum_download_size`, `cache_eviction_policy`) are read from
    config_getter when available, otherwise fall back to defaults.
    """

    def __init__(
        self,
        connection: IAssetProviderConnection,
        security_validator: object | None = None,
        security_supervisor: object | None = None,
        job_scheduler: object | None = None,
        config_getter: object | None = None,
        gateway_client: object | None = None,
        event_publisher: object | None = None,
    ) -> None:
        self._connection = connection
        self._security_validator = security_validator
        self._security_supervisor = security_supervisor
        self._job_scheduler = job_scheduler
        self._config_getter = config_getter
        self._gateway_client = gateway_client
        self._event_publisher = event_publisher
        self._lock = threading.Lock()
        self._orchestrator: AssetOrchestrator | None = None

    def _get_config_value(self, key: str, default: object) -> object:
        """Read a config key from config_getter, falling back to default."""
        if self._config_getter is None:
            return default
        try:
            # Attempt to read the config value from the config getter.
            # The config_getter protocol may or may not expose a
            # get_value method; fall back gracefully.
            if hasattr(self._config_getter, "get_value"):
                return self._config_getter.get_value(key) or default
        except Exception:
            logger.debug("Config key %s not available, using default", key)
        return default

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

            # CE02: Read FRD config keys (wired per capability's own config_getter)
            enabled_providers = self._get_config_value("enabled_providers", None)

            search = AssetSearchHandler(
                self._connection,
                enabled_providers=enabled_providers if isinstance(enabled_providers, list) else None,
            )
            download = AssetDownloadCapability(
                security_validator=self._security_validator,
                job_scheduler=self._job_scheduler,
                config_aggregate=self._config_getter,
            )
            extract = AssetExtractCapability(
                security_supervisor=self._security_supervisor,
            )
            import_ = AssetImportCapability(
                gateway_client=self._gateway_client,
                config_getter=self._config_getter,
                event_publisher=self._event_publisher,
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


def create_asset_container(
    connection: IAssetProviderConnection,
    event_publisher: object | None = None,
) -> AssetContainer:
    return AssetContainer(connection=connection, event_publisher=event_publisher)
