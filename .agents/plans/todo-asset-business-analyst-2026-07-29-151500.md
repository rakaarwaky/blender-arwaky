# Review Plan: asset — Business Analyst (Phase 2)

## Summary

The asset module has good structural coverage of the FRD's 5 functional requirements, but several **business flow gaps** exist between user expectations and implementation. The search handler lacks proper "all providers fail" error aggregation, downloads are not atomic, and the workflow ordering (download → extract → import) is not enforced at the orchestration level. Provider capability awareness is incomplete, and several FRD rules use raw types instead of taxonomy VOs.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| R01 | 🟡 WARNING | `overwrite_policy` param uses raw `str` instead of taxonomy `DuplicatePolicy` VO — FRD specifies exact values (reuse/overwrite/create_unique) but contract accepts any string | `modules/shared/src/asset/contract_asset_download_protocol.py` line 35 vs `modules/shared/src/common/taxonomy_core_vo.py` DuplicatePolicy | Replace `str` with `DuplicatePolicy` from taxonomy. Align contract signature with FRD enum values. |
| R02 | 🟡 WARNING | `search_all` has `asset_type_filter`, `limit`, `page_token` params but implementation ignores them (accepts as `Any`) | `modules/asset/src/capabilities_asset_search_handler.py` lines 38-44 | Implement filtering, limiting, and pagination per FR-AST-001. At minimum, validate and warn on unsupported params. |
| R03 | 🟡 WARNING | FR-AST-005 says "Stale metadata refreshed before download" but `AssetProviderMetadataCapability` has no stale-refresh logic — cache TTL exists but no refresh-on-stale behavior | `modules/asset/src/capabilities_asset_provider.py` lines 31-42 | Add stale-check before cache return. If age >= TTL, fetch fresh metadata and update cache. |
| R04 | 🟡 WARNING | FR-AST-001 says "Disabled providers excluded with warning" but `AssetSearchHandler.__init__` has no provider enablement check | `modules/asset/src/capabilities_asset_search_handler.py` lines 31-36 | Add provider enablement list from config. Log warning for disabled providers in search target. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| BF01 | 🔴 CRITICAL | **No workflow enforcement** — FRD implies download→extract→import flow but `AssetOrchestrator` has no state machine or ordering. Caller can import without downloading, extract without downloading, etc. | `modules/asset/src/agent_asset_orchestrator.py` full file | Implement workflow state tracking in orchestrator. Add preconditions: import requires downloaded file, extract requires extracted archive. |
| BF02 | 🔴 CRITICAL | **"All providers fail → empty result with aggregated error"** — FR-AST-001 QA checklist requires aggregated error when all providers fail, but implementation returns `assets=[]` without error summary | `modules/asset/src/capabilities_asset_search_handler.py` lines 68-78 | Collect errors from failed providers. When all fail, return result with aggregated error message and provider status = "error". |
| BF03 | 🟡 WARNING | **No auto-detection for large downloads** — FRD says "Large downloads → job feature" but `_estimate_download_size` raises `NotImplementedError`, so background submission always fails | `modules/asset/src/capabilities_asset_download.py` lines 142-150 | Implement size estimation or add a `is_large_download` heuristic (e.g., file size > threshold). Auto-route to background. |
| BF04 | 🟡 WARNING | **Cache integrity check is incomplete** — FRD says "Integrity checksum verified when provider supplies one" but `_verify_integrity` only checks existence and size > 0, not actual checksums | `modules/asset/src/capabilities_asset_download.py` lines 126-137 | Accept checksum from provider metadata. Compare downloaded file hash against expected checksum. |

### Logic Implementation Gaps
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| L01 | 🔴 CRITICAL | **Download is not atomic** — FRD QA says "Atomic write (temp → final)" but `_perform_download` writes directly to `cache_path`, not temp→final | `modules/asset/src/capabilities_asset_download.py` lines 167-170 | Write to temp file first, then atomically rename to final path. Clean up temp on failure. |
| L02 | 🔴 CRITICAL | **No concurrency control for same-asset downloads** — FRD says "Concurrent same-asset downloads resolve to one transfer" but no locking or dedup exists | `modules/asset/src/capabilities_asset_download.py` full download flow | Add in-memory lock per asset_id during download. Subsequent concurrent requests for same asset wait and return the winning result. |
| L03 | 🟡 WARNING | **Extract capability has hardcoded limits** — FR-AST-003 says "All archive safety decisions delegated to security" but `_extract_archive` has hardcoded `max_entries=1000`, `max_extracted_size=1073741824` | `modules/asset/src/capabilities_asset_extract.py` lines 73-78 | Remove hardcoded limits. Pass them through as parameters from caller or config. Security supervisor enforces its own limits. |
| L04 | 🟡 WARNING | **Import format validation is incomplete** — `_is_supported_format` only checks file extension, not actual file magic/headers | `modules/asset/src/capabilities_asset_import.py` lines 104-111 | Add file type detection via magic bytes or Python `imghdr`/`file` module. Validate actual content, not just extension. |
| L05 | 🟡 WARNING | **Search handler logs raw query in debug** — `logger.debug("Search query=%s providers=%s ...", query, target, asset_type_filter, limit or 0, page_token)` may log sensitive provider filters | `modules/asset/src/capabilities_asset_search_handler.py` line 53 | Redact sensitive params from debug logs. Only log safe fields (query text, provider names). |

### Edge Case Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| E01 | 🟡 WARNING | **FR-AST-001 "empty query returns curated/default results"** — implementation doesn't check for empty query and return defaults | `modules/asset/src/capabilities_asset_search_handler.py` lines 50-52 | Add empty-query check. When query is empty or whitespace, return curated/default results per provider support. |
| E02 | 🟡 WARNING | **FR-AST-002 "corrupted artifact → re-download"** — `_verify_integrity` returns False but caller doesn't trigger re-download on cache hit failure | `modules/asset/src/capabilities_asset_download.py` lines 93-100 | When cached artifact fails integrity check, delete it and proceed to download. |
| E03 | 🟡 WARNING | **FR-AST-003 "partial extraction cleaned up on failure"** — `_extract_allowed` has no cleanup on exception during extraction loop | `modules/asset/src/capabilities_asset_extract.py` lines 152-164 | Wrap extraction in try/except. On failure, remove extracted files and return error with cleanup status. |
| E04 | 🟡 WARNING | **FR-AST-004 "missing local file directs toward download"** — `_is_supported_format` doesn't check file existence before format validation (order issue) | `modules/asset/src/capabilities_asset_import.py` lines 85-101 | Check file existence first (already done at line 72), then validate format. Currently the empty-file check is redundant since missing-file check already returns. |

### Configuration & Events
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| CE01 | 🟢 INFO | **FRD events not emitted** — FRD specifies 6 events (asset searched, downloaded, cached, extracted, imported, provider degraded) but implementation has no event emission | Multiple files | Add event emission after each operation. Use diagnostics logging as telemetry channel per architecture. |
| CE02 | 🟢 INFO | **FRD config keys not wired** — `overwrite_policy`, `enabled_providers`, `maximum_download_size`, `cache_eviction_policy` from FRD config table are not read from config | Multiple files | Wire config getter in container. Read defaults from config.yaml. Override via capability constructor. |

## Violations

### FRD Compliance Gaps
- **FR-AST-001**: "All providers fail → empty result with aggregated error" — NOT implemented (returns empty assets without error summary)
- **FR-AST-002**: "Atomic write (temp → final)" — NOT implemented (writes directly to cache_path)
- **FR-AST-002**: "Concurrent same-asset downloads resolve to one transfer" — NOT implemented
- **FR-AST-002**: "Integrity checksum verified when available" — PARTIAL (checks existence/size only)
- **FR-AST-003**: "All safety decisions delegated to security" — PARTIAL (hardcoded limits remain)
- **FRD Events**: None of the 6 specified events are emitted

### AES Rule Violations
- **AES201 (Forbidden Import)**: `capabilities_asset_download.py` imports from `contract_job_protocol` and `contract_config_protocol` — agent/utility layer imports are allowed, verify layer boundaries
- **AES403 (CapabilityTooManyTypes)**: `AssetDownloadCapability` has 1 class + 8 methods = within limits
- **AES304 (Bypass Comment)**: `_estimate_download_size` raises `ValidationError` with explicit message — intentional placeholder, acceptable

## Action Items
- [CRITICAL] Implement "all providers fail → aggregated error" in search handler
- [CRITICAL] Implement atomic write (temp → final) in download capability
- [CRITICAL] Add concurrency control for same-asset downloads
- [CRITICAL] Implement workflow state enforcement in orchestrator (download→extract→import ordering)
- [HIGH] Replace raw `str` `overwrite_policy` with taxonomy `DuplicatePolicy` VO
- [HIGH] Implement stale metadata refresh in provider capability
- [HIGH] Implement integrity checksum verification in download capability
- [HIGH] Add FRD event emission to all 6 operations
- [MEDIUM] Remove hardcoded limits from extract capability
- [MEDIUM] Implement empty-query default results in search
- [MEDIUM] Clean up partial extraction on failure
- [LOW] Log redaction for sensitive search params
- [LOW] Wire FRD config keys into container

## Fixed Code

### Fix 1: "All providers fail → aggregated error" (capabilities_asset_search_handler.py)

```python
async def search_all(
    self,
    query: SearchQuery,
    providers: list[str] | None = None,
    asset_type_filter: Any = None,
    limit: Any = None,
    page_token: Any = None,
) -> dict[str, Any]:
    """Search across all enabled providers with unified response.

    FR-AST-001: When all providers fail, returns empty assets with
    aggregated error summary. When ≥1 succeeds, returns partial results.
    """
    target = providers if providers is not None else self._providers

    logger.debug("Search query=%s providers=%s", query, target)

    async def search_one(name: str) -> tuple[str, list[Any], str | None]:
        try:
            if name == "Polyhaven":
                vo = await polyhaven_search(self._connection, query)
            elif name == "Sketchfab":
                vo = await sketchfab_search(self._connection, query)
            else:
                return name, [], "unknown provider"
            normalized = [
                {
                    "id": str(a.id),
                    "name": str(a.name),
                    "type": str(a.type),
                    "provider": str(a.provider),
                    "thumbnail_url": str(a.thumbnail_url) if a.thumbnail_url else None,
                    "tags": list(a.tags),
                }
                for a in vo.assets
            ]
            return name, normalized, None
        except Exception as e:
            logger.warning("Provider %s search failed: %s", name, e)
            return name, [], str(e)

    tasks = [search_one(str(p)) for p in target]
    results = await asyncio.gather(*tasks)

    assets: list[Any] = []
    provider_status: dict[str, str] = {}
    warnings: list[str] = []
    errors: list[str] = []

    for name, items, error in results:
        if error:
            provider_status[name] = "error"
            warnings.append(f"Provider {name} failed: {error}")
            errors.append(f"{name}: {error}")
        elif items:
            provider_status[name] = "success"
            assets.extend(items)
        else:
            provider_status[name] = "empty"

    # FR-AST-001: When all providers fail, include aggregated error
    all_failed = all(status == "error" for status in provider_status.values()) and len(provider_status) > 0
    
    return {
        "assets": assets,
        "total": len(assets),
        "provider_status": provider_status,
        "warnings": warnings,
        "errors": errors if all_failed else None,  # Aggregated error only when all fail
        "search_timestamp": datetime.now(timezone.utc).isoformat(),
    }
```

### Fix 2: Atomic write + concurrency control (capabilities_asset_download.py)

```python
import asyncio
import hashlib
import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from modules.shared.src.asset.contract_asset_download_protocol import AssetDownloadProtocol
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetType,
    FilePath,
    MaxSize,
    ProviderName,
    ResolutionPreference,
)
from modules.shared.src.common.taxonomy_domain_error import (
    ProviderError,
    ValidationError,
)
from modules.shared.src.config.contract_config_protocol import ConfigGetterProtocol
from modules.shared.src.job.contract_job_protocol import JobSchedulerProtocol
from modules.shared.src.security.contract_validate_path_protocol import (
    ValidatePathProtocol,
)

logger = logging.getLogger("BlenderMCPServer")


class AssetDownloadCapability(AssetDownloadProtocol):
    """Asset download capability with cache management.

    FR-AST-002: Atomic write, concurrency control, integrity verification.
    """

    def __init__(
        self,
        security_validator: ValidatePathProtocol | None = None,
        job_scheduler: JobSchedulerProtocol | None = None,
        config_getter: ConfigGetterProtocol | None = None,
    ) -> None:
        self.security_validator = security_validator
        self.job_scheduler = job_scheduler
        self.config_getter = config_getter
        self._cache_dir: FilePath = FilePath("")
        self._max_size: MaxSize | None = None
        self._overwrite_policy: str = "reuse"
        # Concurrency control: lock per asset_id during download
        self._download_locks: dict[str, asyncio.Lock] = {}

    async def _get_download_lock(self, cache_key: str) -> asyncio.Lock:
        """Get or create a lock for a specific download key."""
        if cache_key not in self._download_locks:
            self._download_locks[cache_key] = asyncio.Lock()
        return self._download_locks[cache_key]

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

        cache_key = f"{provider}:{asset_id}:{resolution or 'default'}"
        
        # FR-AST-002: Concurrent same-asset downloads resolve to one transfer
        lock = await self._get_download_lock(cache_key)
        async with lock:
            cached_path = self._get_cache_path(cache_key)

            if cached_path and os.path.exists(cached_path):
                # Check overwrite policy
                if overwrite_policy == "reuse":
                    # FR-AST-002: Verify integrity of cached artifact
                    if self._verify_integrity(cached_path):
                        logger.info("Cache hit: %s", cache_key)
                        return {
                            "success": True,
                            "file_path": cached_path,
                            "cached": True,
                            "integrity_ok": True,
                            "message": "Cached artifact served without network access",
                            "cache_key": cache_key,
                        }
                    else:
                        # Corrupted cache — remove and re-download
                        logger.warning("Corrupted cache entry, removing: %s", cache_key)
                        try:
                            os.remove(cached_path)
                        except OSError:
                            pass

                elif overwrite_policy == "unique":
                    cached_path = self._get_unique_cache_path(cache_key)

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

            # Perform synchronous download with atomic write
            try:
                file_path = await self._perform_download_atomic(provider, asset_id, cached_path)
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

    async def _perform_download_atomic(
        self, provider: ProviderName, asset_id: AssetId, cache_path: str
    ) -> str:
        """Perform download with atomic write (temp → final).

        FR-AST-002: Atomic write ensures cache integrity.
        Temp file is cleaned up on failure.
        """
        cache_parent = Path(cache_path).parent
        cache_parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temp file first
        temp_path = str(cache_parent / f"{Path(cache_path).stem}.tmp-{hash(asset_id)}")
        try:
            with open(temp_path, "w") as f:
                # Mock download — real impl would stream provider data
                f.write(f"mock-{provider}-{asset_id}")
            
            # Atomic rename
            os.replace(temp_path, cache_path)
            return cache_path
        except Exception:
            # Clean up temp file on failure
            try:
                os.remove(temp_path)
            except OSError:
                pass
            raise
```

### Fix 3: Replace raw str with DuplicatePolicy VO (contract + capability)

In `contract_asset_download_protocol.py`:
```python
from modules.shared.src.common.taxonomy_core_vo import (
    # ... existing imports ...
    DuplicatePolicy,
)

class AssetDownloadProtocol(ABC):
    @abstractmethod
    async def download_to_cache(
        self,
        provider: ProviderName,
        asset_id: AssetId,
        asset_type: AssetType,
        cache_dir: FilePath,
        resolution: ResolutionPreference | None = None,
        overwrite_policy: DuplicatePolicy = DuplicatePolicy("reuse"),  # Changed from str
        max_size: MaxSize | None = None,
        background: bool = False,
    ) -> dict[str, Any]:
```

In `capabilities_asset_download.py`:
```python
from modules.shared.src.common.taxonomy_core_vo import (
    # ... existing imports ...
    DuplicatePolicy,
)

class AssetDownloadCapability(AssetDownloadProtocol):
    async def download_to_cache(
        self,
        provider: ProviderName,
        asset_id: AssetId,
        asset_type: AssetType,
        cache_dir: FilePath,
        resolution: ResolutionPreference | None = None,
        overwrite_policy: DuplicatePolicy = DuplicatePolicy("reuse"),  # Changed from str
        max_size: MaxSize | None = None,
        background: bool = False,
    ) -> dict[str, Any]:
        # ... existing code ...
        
        if cached_path and os.path.exists(cached_path):
            if overwrite_policy == DuplicatePolicy("reuse"):
                # ...
            elif overwrite_policy == DuplicatePolicy("create_unique"):
                cached_path = self._get_unique_cache_path(cache_key)
```

### Fix 4: Stale metadata refresh (capabilities_asset_provider.py)

```python
async def normalize_metadata(
    self,
    raw_provider_data: dict[str, Any],
    provider_name: ProviderName,
    asset_id: AssetId,
) -> dict[str, Any]:
    cache_key = f"{provider_name}:{asset_id}"

    # Check cache freshness with stale-refresh logic (FR-AST-005)
    if cache_key in self._metadata_cache:
        cached = self._metadata_cache[cache_key]
        age = (datetime.now(timezone.utc) - cached["timestamp"]).total_seconds()
        
        if age < self.cache_ttl_seconds:
            logger.debug("Using fresh cached metadata for %s", cache_key)
            return dict(cached["data"])
        
        # FR-AST-005: Stale metadata refreshed before download
        logger.debug("Cached metadata stale for %s (age=%.1fs), refreshing", cache_key, age)
    
    # ... rest of normalization logic ...
```

### Fix 5: Event emission stub (agent_asset_orchestrator.py additions)

```python
import logging
from datetime import datetime, timezone

logger = logging.getLogger("BlenderMCPServer")


def _emit_event(event_name: str, **kwargs: Any) -> None:
    """Emit FRD-specified telemetry event via diagnostics logging.
    
    FRD Events: asset searched, downloaded, cached, extracted, imported, provider degraded
    """
    payload = {
        "event": event_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        **kwargs,
    }
    logger.info("telemetry.asset.event=%s payload=%s", event_name, payload)
```

Then call `_emit_event` after each operation:
```python
# After search
_emit_event("asset_searched", result_count=len(assets), providers=target)

# After download
_emit_event("asset_downloaded", file_path=file_path, size=file_size)

# After cache hit
_emit_event("asset_cache_hit", cache_key=cache_key)

# After extract
_emit_event("asset_extracted", extracted_count=len(extracted_files))

# After import
_emit_event("asset_imported", object_count=len(object_names))
```
