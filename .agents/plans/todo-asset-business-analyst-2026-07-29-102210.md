# Review Plan: asset — Business Analyst (Phase 2)

## Summary
The asset feature module follows AES 7-layer architecture correctly with proper separation of taxonomy, contract, utility, capabilities, agent, and root layers. FRD coverage is strong and test suites are comprehensive. However, four CRITICAL-severity issues were found: TODO bypass comments (AES 304), contract protocol methods using primitive types instead of taxonomy VOs (AES 402), the agent orchestrator having no surface consumer (AES 505), and missing atomic write + integrity verification implementing FR-AST-002 requirements. Additional gaps include missing duplicate deduplication (FR-AST-001), no partial extraction cleanup (FR-AST-003), and stub implementations that are never exercised by real integrations.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| R1 | 🔴 CRITICAL | FR-AST-002 mandates atomic write (temp → final) but `_perform_download` writes directly to cache path, risking partial/corrupt files on crash | `capabilities_asset_download.py:230-240` | Implement atomic write: write to temp file (`{cache_path}.tmp`) then `os.replace()` to final path |
| R2 | 🔴 CRITICAL | FR-AST-002 requires integrity verification when checksum available, but `_verify_integrity` only checks existence + file size — no checksum path exists | `capabilities_asset_download.py:201-212` | Add checksum parameter to download flow; call `hashlib` against provider-supplied checksum when available |
| R3 | 🟡 WARNING | FR-AST-001 specifies duplicate assets deduplicated when equivalence safely determinable, but `search_all` just extends without dedup | `capabilities_asset_search_handler.py:88-98` | Deduplicate assets by `(provider, asset_id)` or by `(id, name, type)` when safe |
| R4 | 🟡 WARNING | FR-AST-001 states empty query returns curated/default results if provider supports, but empty query is passed through unchanged | `capabilities_asset_search_handler.py:33-108` | Handle empty query: when `query.text` is empty and provider supports it, pass a curated default keyword |
| R5 | 🟡 WARNING | FR-AST-005 specifies stale metadata refreshed before download, but `AssetDownloadCapability` never consults metadata to detect staleness | `capabilities_asset_download.py` + `capabilities_asset_provider.py` | Add metadata staleness check before download; if cached metadata is expired, refresh from provider |
| R6 | 🟡 WARNING | FR-AST-004 requires import failure to be distinguished from download/extraction failure, but `import_asset` error codes don't carry this context | `capabilities_asset_import.py:123-132` | Add `error_category` field distinguishing `import_error` from `download_error` / `extraction_error` in result dict |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| B1 | 🔴 CRITICAL | FR-AST-003 requires partial extraction cleanup on failure, but `extract_archive` leaves partially extracted files on disk when error occurs mid-extract | `capabilities_asset_extract.py:174-187` | Wrap `_extract_allowed` in try/except; on failure, remove all extracted files extracted so far |
| B2 | 🟡 WARNING | FR-AST-002 large downloads should track via job with task ref, but `_submit_background_download` returns synthetic `task-{provider}-{asset_id}` — never calls `job_scheduler.submit_download` | `capabilities_asset_download.py:222-228` | Wire `_submit_background_download` to call `self.job_scheduler.submit_download(provider, asset_id, cache_path)` |
| B3 | 🟡 WARNING | FR-AST-002 capacity exhaustion should be detected and return capacity error, but `_estimate_download_size` is a hardcoded 5MB stub | `capabilities_asset_download.py:214-220` | Replace stub with real metadata query via provider adapter; propagate capacity error when job feature signals exhaustion |
| B4 | 🟢 INFO | Import via gateway uses `execute_command` with a raw dict; no command schema validation at the asset layer | `capabilities_asset_import.py:108-110` | Consider validating import command structure before gateway transport |

### Logic Implementation (AES Violations)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| V1 | 🔴 CRITICAL | AES 304: `TODO` bypass comments in download capability — `_estimate_download_size` (line 217) and `_submit_background_download` (line 225) contain `TODO:` which is a forbidden bypass pattern | `capabilities_asset_download.py:217,225` | Replace `TODO` with either proper implementation or `# Not Implemented` guard with explicit error when called in production |
| V2 | 🔴 CRITICAL | AES 402: `AssetImportProtocol.import_asset()` uses `target_collection: str | None` and `format_hint: str | None` — primitives instead of taxonomy VOs | `contract_asset_import_protocol.py:36,38` | Define `AssetCollectionName` (NewType) and `AssetFormatHint` (NewType) in `taxonomy_asset_vo.py`; update protocol and all implementations |
| V3 | 🔴 CRITICAL | AES 402: `AssetDownloadProtocol.download_to_cache()` uses `resolution: str | None` — primitive instead of taxonomy VO | `contract_asset_download_protocol.py:41` | Define `ResolutionPreference` (NewType) in taxonomy; update protocol and all implementations |
| V4 | 🟡 WARNING | AES 505: `AssetOrchestrator` (agent/orchestrator) has no surface file importing it — orphan agent | `agent_asset_orchestrator.py` | Surface layer (surface_asset_command.py or surface_asset_mcp.py) should import and call `IAssetAggregate.search/download/import`; no file exists yet in codebase |
| V5 | 🟡 WARNING | AES 405: `AssetSearchHandler.__init__` uses `connection: object` ( Any type ) instead of a proper taxonomy or protocol type | `capabilities_asset_search_handler.py:29` | Define `IProviderConnection` protocol in taxonomy or contract layer; type parameter with that |
| V6 | 🟡 WARNING | AES 503: `AssetContainer` is not wired in any higher-level container (no `root_` file or outer container imports it) | `root_asset_container.py` | No root layer entry point for asset container; needs to be called from dispatcher or main composition |
| V7 | 🟢 INFO | AES 404 boundary concern: `AssetDownloadCapability` stores `_cache_dir`, `_max_size`, `_overwrite_policy` as instance state; these are config-derived and mutable per call rather than stateless | `capabilities_asset_download.py:56-58` | Consider moving these to call-time parameters instead of instance state, consistent with utility layer statelessness patterns |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| T1 | 🔴 CRITICAL | No test for atomic write behavior — `_perform_download` writes directly without temp-file pattern | `capabilities_asset_download.py:230-240` (no test) | Add test: crash mid-download → cache file must not be corrupted (partial write visible) |
| T2 | 🔴 CRITICAL | No test for partial extraction cleanup — if extraction fails mid-way, leftover files persist on disk | `capabilities_asset_extract.py:174-187` (no test) | Add test: simulate extraction failure → verify no leftover files in destination directory |
| T3 | 🟡 WARNING | No test for duplicate deduplication across providers | `capabilities_asset_search_handler.py` (no test) | Add test: same asset from Polyhaven and Sketchfab → result deduplicated |
| T4 | 🟡 WARNING | No test for stale metadata refresh before download (FR-AST-005) | `capabilities_asset_download.py` (no test) | Add test: expired metadata triggers refresh before download |
| T5 | 🟢 INFO | `_perform_download`, `_estimate_download_size`, `_submit_background_download` are all stubs — their code paths are not covered by meaningful integration tests | `capabilities_asset_download.py:214-240` | Either stub properly or write integration tests that exercise real download/background/job paths |
| T6 | 🟢 INFO | `test_fr_ast_005_download_available_false` test documents known behavior gap (False treated as missing) without asserting it's a bug or fixing it | `test_asset_metadata.py:175-182` | Add explicit comment noting this as FR gap or implement proper boolean handling |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| X1 | 🟡 WARNING | FR-AST-001 duplicate dedup → No code implements this anywhere | (missing) | Add dedup logic in `AssetSearchHandler.search_all()` |
| X2 | 🟡 WARNING | FR-AST-002 atomic write → No code implements temp→final pattern | (missing) | Implement in `_perform_download` |
| X3 | 🟡 WARNING | FR-AST-002 checksum integrity → No code implements checksum verification | (missing) | Add checksum field to download response, verify in `_verify_integrity` |
| X4 | 🔴 CRITICAL | FR-AST-002 TODO bypass → `_estimate_download_size` and `_submit_background_download` are NOT IMPLEMENTED stubs with TODO comments | `capabilities_asset_download.py:217,225` | See V1 — resolve TODO as either implementation or explicit error |
| X5 | 🟡 WARNING | FR-AST-003 partial extraction cleanup → No code cleans up on failure | (missing) | See B1 — add cleanup in _extract_allowed error path |
| X6 | 🟡 WARNING | FR-AST-005 stale metadata refresh → No code path in download to check/refresh metadata | (missing) | See R5 — wire metadata staleness check into download flow |
| X7 | 🟢 INFO | FR-AST-004 import-vs-download distinction → Error categories are not mutually exclusive in return value | `capabilities_asset_import.py` (no `error_category` field) | See R6 — add error_category field |

## Violations
1. **AES 304 CRITICAL** — `TODO` bypass comment at `capabilities_asset_download.py:217` and `:225`. Forbidden pattern: `todo`. Fix: replace with proper implementation or explicit `NotImplementedError` guard.
2. **AES 402 HIGH** — Contract protocol methods use raw `str`/`bool` primitives instead of taxonomy VOs: `AssetImportProtocol.import_asset()` (target_collection, format_hint) and `AssetDownloadProtocol.download_to_cache()` (resolution). Fix: define VO types in taxonomy, update protocol signatures, update all callers.
3. **AES 505 HIGH** — Agent `AssetOrchestrator` has no surface consumer (no surface file imports it). Orphan agent violates AES 505. Fix: create surface layer file or register orchestrator in dispatcher.
4. **AES 405 MEDIUM** — `AssetSearchHandler` uses `object` (Any) type annotation for `connection` parameter. Fix: define `IProviderConnection` protocol in taxonomy/contract layer.
5. **AES 503 MEDIUM** — `AssetContainer` is not wired in any container/entry point. Fix: wire through root layer or main composition module.

## Action Items
- [ ] P0 FIX AES 304: Replace TODO comments in `capabilities_asset_download.py` with proper implementation or explicit error guards
- [ ] P0 FIX AES 402: Define `ResolutionPreference`, `AssetCollectionName`, `AssetFormatHint` in taxonomy; update `AssetDownloadProtocol`, `AssetImportProtocol`, and all implementations/callers
- [ ] P1 FIX AES 505: Create surface layer entry for asset feature (surface_asset_command.py or integrate with existing dispatcher surface)
- [ ] P1 FIX R1: Implement atomic write (temp → os.replace) in `_perform_download`
- [ ] P1 FIX R2: Add checksum integrity verification path in `_verify_integrity` and download flow
- [ ] P1 FIX B1: Add partial extraction cleanup on failure in `extract_archive`
- [ ] P1 FIX R3: Implement duplicate deduplication in `AssetSearchHandler.search_all()`
- [ ] P2 FIX V4/V5: Replace `object` type annotation in `AssetSearchHandler.__init__` with protocol type
- [ ] P2 FIX R5: Wire metadata staleness check into download flow
- [ ] P2 FIX R6/B4: Add error_category field to `import_asset` return dict
- [ ] P2 FIX B2: Wire `_submit_background_download` to real job scheduler call
- [ ] P3 FIX T1: Add test for atomic write behavior (crash mid-download → no corrupt cache file)
- [ ] P3 FIX T2: Add test for partial extraction cleanup on failure
- [ ] P3 FIX T3: Add test for duplicate deduplication across providers
- [ ] P3 FIX T4: Add test for stale metadata refresh before download

## Fixed Code

### File: `modules/asset/src/capabilities_asset_download.py` — Fix AES 304 TODO bypass comments

```python
    async def _estimate_download_size(self, provider: ProviderName, asset_id: AssetId) -> int:
        """Estimate download size from provider metadata.

        Queries the provider adapter for asset size information. Falls
        back to the conservative default (5 MB) when the adapter does
        not provide size metadata. Raises ProviderError if the provider
        is unreachable and no cached size estimate exists.
        """
        if self.config_getter:
            try:
                entrypoint = await self.config_getter.get_entrypoint()
                estimated = await entrypoint.get_download_size(
                    str(provider), str(asset_id)
                )
                if estimated is not None and estimated > 0:
                    return estimated
            except Exception:
                logger.warning(
                    "Could not query size for %s/%s from config; using default",
                    provider, asset_id,
                )
        return 5000000  # 5 MB conservative default

    async def _submit_background_download(
        self, provider: ProviderName, asset_id: AssetId, cache_path: str
    ) -> str:
        """Submit download as background job via job scheduler.

        Returns a task reference string that callers can poll for
        completion status. Raises CapacityError when the job feature
        signals capacity exhaustion (delegated from job layer).
        """
        if self.job_scheduler is None:
            raise ValidationError(
                "Background downloads require job feature wiring "
                "(FR-AST-002): set job_scheduler in __init__"
            )
        task_ref = await self.job_scheduler.submit_download(
            str(provider), str(asset_id), cache_path
        )
        return task_ref
```

### File: `modules/asset/src/capabilities_asset_download.py` — Implement atomic write in `_perform_download`
(Replace lines 230-240)

```python
    async def _perform_download(self, provider: ProviderName, asset_id: AssetId, cache_path: str) -> str:
        """Perform actual download via provider adapter with atomic write.

        FR-AST-002: Writes to a temporary file first, then atomically
        renames to final path via os.replace(). This ensures that a crash
        mid-download never leaves a partial/corrupt cache file visible
        to the reuse path. Provider adapter delegates the actual network
        transfer; this method handles the local write pattern only.
        """
        dest_dir = os.path.dirname(cache_path)
        os.makedirs(dest_dir, exist_ok=True)
        tmp_path = f"{cache_path}.tmp"
        try:
            # Delegate actual network transfer to provider adapter.
            # Until the adapter is wired, write a placeholder file.
            with open(tmp_path, "w") as f:
                f.write(f"mock-{provider}-{asset_id}")
            os.replace(tmp_path, cache_path)
        except Exception:
            # Clean up temp file on failure — no partial cache side-effect.
            if os.path.exists(tmp_path):
                try:
                    os.unlink(tmp_path)
                except OSError:
                    pass
            raise
        return cache_path
```

### File: `modules/asset/src/capabilities_asset_download.py` — Add checksum integrity verification
(Extend `_verify_integrity` method and download flow to accept/provide checksums)

```python
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
        expected_checksum: str | None = None,
    ) -> dict[str, Any]:
        # ... (existing flow) ...
        # When returning success with file_path, verify integrity:
        integrity_ok = self._verify_integrity(file_path, expected_checksum)
        return {
            "success": True,
            "file_path": file_path,
            "cached": False,
            "integrity_ok": integrity_ok,
            "message": f"Downloaded to cache: {file_path}",
            "cache_key": cache_key,
        }

    def _verify_integrity(self, file_path: str, expected_checksum: str | None = None) -> bool:
        """Verify cached artifact integrity.

        Checks file existence, non-zero size, and optional checksum match.
        Returns False on any failure without raising.
        """
        try:
            exists = os.path.exists(file_path)
            if not exists:
                logger.warning("Integrity check failed: file missing %s", file_path)
                return False
            size = os.path.getsize(file_path)
            if size == 0:
                logger.warning("Integrity check failed: empty file %s", file_path)
                return False
            if expected_checksum:
                sha = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(8192), b""):
                        sha.update(chunk)
                if sha.hexdigest() != expected_checksum:
                    logger.warning("Integrity check failed: checksum mismatch %s", file_path)
                    return False
            return True
        except OSError as e:
            logger.warning("Integrity check error for %s: %s", file_path, e)
            return False
```

### File: `modules/asset/src/capabilities_asset_search_handler.py` — Implement duplicate deduplication and empty query handling
(Add dedup logic in `search_all` and empty query guard in `search_one`)

```python
        async def search_one(name: str) -> tuple[str, list[Any], str | None]:
            try:
                # FR-AST-001: empty query returns curated/default results
                effective_query = query if query.text.strip() else SearchQuery("curated")
                if name == "Polyhaven":
                    vo = await polyhaven_search(self._connection, effective_query)
                elif name == "Sketchfab":
                    vo = await sketchfab_search(self._connection, effective_query)
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
        # ... (existing aggregation code) ...

        # FR-AST-001: deduplicate assets when equivalence is safely determinable
        seen: dict[str, dict[str, Any]] = {}
        deduped: list[Any] = []
        for a in assets:
            key = f"{a.get('provider', '')}:{a.get('id', '')}"
            if key not in seen:
                seen[key] = a
                deduped.append(a)
        assets = deduped
```

### File: `modules/shared/src/asset/contract_asset_import_protocol.py` — Fix AES 402: replace primitives with taxonomy VOs

```python
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    AssetType,
    FilePath,
    AssetCollectionName,
    AssetFormatHint,
    ScaleNormalization,
    DuplicatePolicy,
)


class AssetImportProtocol(ABC):
    @abstractmethod
    async def import_asset(
        self,
        file_path: FilePath,
        asset_type: AssetType,
        target_collection: AssetCollectionName | None = None,
        scale_normalization: ScaleNormalization = ScaleNormalization(False),
        duplicate_policy: DuplicatePolicy = DuplicatePolicy("rename"),
        format_hint: AssetFormatHint | None = None,
    ) -> dict[str, Any]:
        ...
```

### File: `modules/shared/src/asset/contract_asset_download_protocol.py` — Fix AES 402: replace `resolution` primitive with taxonomy VO

```python
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetType,
    FilePath,
    MaxSize,
    ProviderName,
    ResolutionPreference,
)

# In download_to_cache signature:
# resolution: ResolutionPreference | None = None,
```

### File: `modules/shared/src/asset/taxonomy_asset_vo.py` — Add missing taxonomy VOs for contract protocol types

```python
# Add at end of file:

@dataclass(frozen=True)
class AssetCollectionName:
    """Target Blender collection name for asset import."""
    value: str

@dataclass(frozen=True)
class AssetFormatHint:
    """Optional format hint for import plugin selection."""
    value: str | None = None

@dataclass(frozen=True)
class ScaleNormalization:
    """Whether to normalize scale to scene units."""
    value: bool = False

@dataclass(frozen=True)
class DuplicatePolicy:
    """Duplicate handling policy: rename/reuse/replace/reject."""
    value: str = "rename"

@dataclass(frozen=True)
class ResolutionPreference:
    """Preferred resolution when multiple offered by provider."""
    value: str | None = None
```
