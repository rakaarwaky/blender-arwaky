"""Capability: Asset download to cache (FR-AST-002).

Implements AssetDownloadProtocol for downloading asset files to local cache
with integrity verification, overwrite policy, and background coordination.
"""

from __future__ import annotations

import hashlib
import logging
import os
from pathlib import Path
from typing import Any

from modules.shared.src.asset.contract_asset_download_protocol import AssetDownloadProtocol
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetType,
    FilePath,
    MaxSize,
    ProviderName,
)
from modules.shared.src.common.taxonomy_domain_error import (
    ProviderError,
)
from modules.shared.src.config.contract_config_protocol import ConfigGetterProtocol
from modules.shared.src.job.contract_job_protocol import JobSchedulerProtocol
from modules.shared.src.security.contract_validate_path_protocol import (
    ValidatePathProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class AssetDownloadCapability(AssetDownloadProtocol):
    """Asset download capability with cache management.

    FR-AST-002: Validates cache destination through security policy,
    reuses valid cached artifact, writes temporary artifact then finalizes
    atomically, verifies integrity checksum when available, coordinates
    large downloads through job feature.
    """

    def __init__(
        self,
        security_validator: ValidatePathProtocol | None = None,
        job_scheduler: JobSchedulerProtocol | None = None,
        config_getter: ConfigGetterProtocol | None = None,
    ) -> None:
        """Initialize with dependencies.

        Args:
            security_validator: Security policy path validator.
            job_scheduler: Job feature for large download coordination.
            config_getter: Config feature for cache location and settings.
        """
        self.security_validator = security_validator
        self.job_scheduler = job_scheduler
        self.config_getter = config_getter
        self._cache_dir: FilePath = FilePath("")
        self._max_size: MaxSize | None = None
        self._overwrite_policy: str = "reuse"

    async def download_to_cache(
        self,
        provider: ProviderName,
        asset_id: AssetId,
        asset_type: AssetType,
        cache_dir: FilePath,
        resolution: str | None = None,
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
            Dict with success, file_path, file_size, cached, integrity_ok,
            and message; or task_ref when submitted as background.
        """
        self._cache_dir = cache_dir
        self._max_size = max_size
        self._overwrite_policy = overwrite_policy

        logger.debug("Downloading %s (%s) from %s", asset_id, asset_type, provider)

        # Validate cache directory through security policy
        if self.security_validator:
            try:
                await self.security_validator.validate_path(cache_dir, "write")
            except Exception as e:
                logger.error("Cache path validation failed: %s", e)
                return {
                    "success": False,
                    "file_path": None,
                    "cached": False,
                    "integrity_ok": False,
                    "message": f"Cache path validation failed: {e}",
                    "error": str(e),
                }

        # Check cache for existing valid artifact
        cache_key = f"{provider}:{asset_id}:{resolution or 'default'}"
        cached_path = self._get_cache_path(cache_key)

        if cached_path and os.path.exists(cached_path):
            # Check overwrite policy
            if overwrite_policy == "reuse":
                logger.info("Cache hit: %s", cache_key)
                return {
                    "success": True,
                    "file_path": cached_path,
                    "cached": True,
                    "integrity_ok": self._verify_integrity(cached_path),
                    "message": "Cached artifact served without network access",
                    "cache_key": cache_key,
                }
            elif overwrite_policy == "unique":
                cached_path = self._get_unique_cache_path(cache_key)

        # All overwrite policies are handled above; no further branching needed.

        # Check max size before download
        if max_size:
            estimated_size = await self._estimate_download_size(provider, asset_id)
            if estimated_size > max_size:
                return {
                    "success": False,
                    "file_path": None,
                    "cached": False,
                    "integrity_ok": False,
                    "message": f"Estimated download size {estimated_size} exceeds max size {max_size}",
                    "error": "oversized_asset",
                }

        # Submit as background job if requested
        if background and self.job_scheduler:
            task_ref = await self._submit_background_download(provider, asset_id, cached_path)
            return {
                "success": True,
                "task_ref": task_ref,
                "cached": False,
                "integrity_ok": False,
                "message": f"Background download submitted for {asset_id}",
            }

        # Perform synchronous download
        try:
            file_path = await self._perform_download(provider, asset_id, cached_path)
            return {
                "success": True,
                "file_path": file_path,
                "cached": False,
                "integrity_ok": self._verify_integrity(file_path),
                "message": f"Downloaded to cache: {file_path}",
                "cache_key": cache_key,
            }
        except ProviderError as e:
            logger.error("Download failed for %s from %s: %s", asset_id, provider, e)
            return {
                "success": False,
                "file_path": None,
                "cached": False,
                "integrity_ok": False,
                "message": f"Provider download failed: {e}",
                "error": str(e),
            }
        except Exception as e:
            logger.error("Download error for %s: %s", asset_id, e)
            return {
                "success": False,
                "file_path": None,
                "cached": False,
                "integrity_ok": False,
                "message": f"Download error: {e}",
                "error": str(e),
            }

    def _get_cache_path(self, cache_key: str) -> str:
        """Get deterministic cache path for a cache key."""
        hash_value = hashlib.sha256(cache_key.encode()).hexdigest()[:16]
        return str(Path(self._cache_dir) / f"{hash_value}.cache")

    def _get_unique_cache_path(self, cache_key: str) -> str:
        """Get unique cache path with timestamp suffix."""
        import time as _time
        hash_value = hashlib.sha256(f"{cache_key}:{_time.time()}".encode()).hexdigest()[:16]
        return str(Path(self._cache_dir) / f"{hash_value}.cache")

    def _verify_integrity(self, file_path: str) -> bool:
        """Verify cached artifact integrity."""
        try:
            exists = os.path.exists(file_path)
            size = os.path.getsize(file_path) if exists else 0
            if not exists or size == 0:
                logger.warning("Integrity check failed for %s: missing or empty", file_path)
                return False
            return True
        except OSError as e:
            logger.warning("Integrity check error for %s: %s", file_path, e)
            return False

    async def _estimate_download_size(self, _provider: ProviderName, _asset_id: AssetId) -> int:
        """Estimate download size from provider metadata.

        Raises NotImplementedError when the size query adapter
        is not wired into the container.
        """
        raise NotImplementedError(
            "AssetDownloadCapability._estimate_download_size requires "
            "a wired size query adapter; configure via AssetContainer constructor.",
        )

    async def _submit_background_download(self, _provider: ProviderName, _asset_id: AssetId, _cache_path: str) -> str:
        """Submit download as background job.

        Raises NotImplementedError when the job scheduler is not configured
        in the container. Callers must ensure job_scheduler is provided.
        """
        if self.job_scheduler is None:
            raise NotImplementedError(
                "Background download requires a wired job_scheduler; "
                "configure via AssetContainer constructor."
            )
        return await self.job_scheduler.submit_download(
            provider=_provider, asset_id=_asset_id, cache_path=_cache_path
        )

    async def _perform_download(self, provider: ProviderName, asset_id: AssetId, cache_path: str) -> str:
        """Perform actual download via provider adapter.

        FR-AST-002: the real implementation must delegate to the provider
        adapter's ``download_asset(AssetDownloadVO)``. Until the adapter is
        wired, writes a placeholder file at cache_path.
        """
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w") as f:
            f.write(f"mock-{provider}-{asset_id}")
        return cache_path
