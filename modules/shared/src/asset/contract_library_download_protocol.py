"""Asset domain contract: library download protocol (ABC based).

Defines the protocol for downloading assets from dedicated asset libraries.
AES Contract layer — pure ABC definitions, no implementation.

FR-AST-004: Download from External Asset Libraries
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetTypeFilter,
)
from .taxonomy_asset_vo import AssetDownloadCacheVO


class LibraryDownloadProtocol(ABC):
    """Protocol for downloading assets from dedicated asset libraries."""

    @abstractmethod
    async def download_library_asset(
        self,
        asset_id: AssetId,
        asset_type: AssetTypeFilter,
        resolution: str | None = None,
        overwrite_policy: str = "reject",
    ) -> AssetDownloadCacheVO:
        """Download a specific HDRI or texture to local cache.

        FR-AST-004: Downloads to strictly allowed cache directory.
        Respects overwrite policy (reuse, overwrite, unique variant).
        Validates downloaded file existence and non-zero size.
        Returns cached status (reused vs newly downloaded).
        """
        pass