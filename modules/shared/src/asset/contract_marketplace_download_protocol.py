"""Asset domain contract: marketplace download protocol (ABC based).

Defines the protocol for downloading and optionally importing models from marketplaces.
AES Contract layer — pure ABC definitions, no implementation.

FR-AST-006: Download from Model Marketplaces
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
)


class MarketplaceDownloadResult:
    """Result from marketplace download and optional import."""

    def __init__(
        self,
        success: bool,
        file_path: str | None = None,
        imported: bool = False,
        object_name: str | None = None,
        cached: bool = False,
        message: str = "",
        error: str | None = None,
    ) -> None:
        self.success = success
        self.file_path = file_path
        self.imported = imported
        self.object_name = object_name
        self.cached = cached
        self.message = message
        self.error = error


class MarketplaceDownloadProtocol(ABC):
    """Protocol for downloading models from marketplaces."""

    @abstractmethod
    async def download_marketplace_model(
        self,
        model_id: AssetId,
        destination_policy: str = "unique",
        import_enabled: bool = False,
        scale_normalization: bool = False,
    ) -> MarketplaceDownloadResult:
        """Download a specific 3D model from marketplace with optional import.

        FR-AST-006: Downloads strictly into allowed cache directory.
        Safely extracts compressed archives (path traversal prevention).
        Optionally imports into 3D application with scale normalization.
        Preserves marketplace attribution and license metadata.
        """
        pass