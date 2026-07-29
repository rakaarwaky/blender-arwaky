"""Asset domain contract: download to cache protocol (ABC based).

Defines the protocol for downloading asset files to local cache
with integrity verification, overwrite policy, and background coordination.

FR-AST-002: Download Asset to Cache
AES Contract layer — pure ABC definitions, no implementation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetType,
    FilePath,
    MaxSize,
    ProviderName,
    ResolutionPreference,
)


class AssetDownloadProtocol(ABC):
    """Protocol for downloading asset files to local cache.

    FR-AST-002: Validates cache destination through security policy,
    reuses valid cached artifact, writes temporary artifact then finalizes
    atomically, verifies integrity checksum when available, coordinates
    large downloads through job feature.
    """

    @abstractmethod
    async def download_to_cache(
        self,
        provider: ProviderName,
        asset_id: AssetId,
        asset_type: AssetType,
        cache_dir: FilePath,
        resolution: ResolutionPreference | None = None,
        overwrite_policy: str = "reuse",
        max_size: MaxSize | None = None,
        background: bool = False,
    ) -> dict[str, Any]:
        """Download asset file from provider into local cache.

        FR-AST-002: Cache location from configuration; paths validated
        through security policy. Existing cached artifact follows configured
        overwrite policy (reuse, overwrite, unique variant). Integrity
        checksum verified when provider supplies one. Large downloads
        submitted through job feature with task reference returned.

        Args:
            provider: Provider identifier.
            asset_id: Asset identifier from provider.
            asset_type: Type of asset being downloaded.
            cache_dir: Cache directory from configuration.
            resolution: Optional resolution preference.
            overwrite_policy: reuse/overwrite/unique variant.
            max_size: Maximum download size limit.
            background: Whether to submit as background job.

        Returns:
            Dict with success indicator, local artifact reference,
            downloaded size, cache status, integrity status, and message;
            or task reference when submitted as background download.
        """
        ...
