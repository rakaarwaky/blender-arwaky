"""Asset domain contract: download to cache protocol (ABC based).

Defines the protocol for downloading asset files to local cache
with integrity verification and overwrite policy.

FR-AST-002: Download Asset to Cache
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_asset_vo import AssetDownloadCacheVO


class AssetDownloadProtocol(ABC):
    """Protocol for downloading asset files to local cache."""

    @abstractmethod
    async def download_to_cache(self, vo: AssetDownloadCacheVO) -> AssetDownloadCacheVO:
        """Download asset file from provider into local cache.

        FR-AST-002: Validates cache destination through security policy,
        reuses valid cached artifact, writes temporary artifact then finalizes
        atomically, verifies integrity checksum when available.
        """
        ...
