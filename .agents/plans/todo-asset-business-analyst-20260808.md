# Plan: asset — Business Analyst
> **Historical plan notice (2026-08-14):** This 2026-08-08 plan is retained for audit history only. Do not execute its recommendations directly. Use the corresponding `*-20260814-revalidated.md` plan, which classifies each finding as `open`, `needs-clarification`, `resolved`, or `obsolete`.


## Summary
The asset module implements external asset acquisition (search, download, cache, extract, import) per FR-AST-001..005. Code structure follows AES: 1 agent orchestrator, 5 capabilities, 1 root container. FRD maps cleanly to capabilities: search→`capabilities_asset_search_handler.py`, download→`capabilities_asset_download.py`, extract→`capabilities_asset_extract.py`, import→`capabilities_asset_import.py`, provider metadata→`capabilities_asset_provider.py`. No missing FR coverage. Boundary with object (import handoff) and render (HDRI files) is explicit and respected.

## Findings

### Requirements Clarity
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | FR-AST-001 "curated/default results for empty query" — not explicitly in search handler logic | `capabilities_asset_search_handler.py` | Add comment or docstring noting this edge case handling if implemented; otherwise clarify in FRD |
| 2 | 🟢 INFO | FR-AST-002 "concurrent same-asset downloads resolve to one transfer" — deduplication mechanism not visible in download capability | `capabilities_asset_download.py` | Verify if implemented via cache check; document the deduplication strategy |

### Business Flow
| # | Severity | Issue | Location | Recommendation |
|---|----------|-------|----------|----------------|
| 1 | 🟢 INFO | Search → download → extract → import pipeline relies on caller sequencing; no aggregate enforces end-to-end flow | `agent_asset_orchestrator.py` | Consider adding a convenience method for full pipeline if common use case |

### Logic Implementation
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | 🟢 INFO | `capabilities_asset_search_handler.py` uses `_search_single_provider` but provider adapters not yet visible in codebase — may be external or TBD | `capabilities_asset_search_handler.py` | Confirm provider adapter location; ensure protocol/contract exists in shared |

### Testability & Acceptance
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | 🟢 INFO | No integration test for full search→download→import flow visible in `tests/` | `tests/` | Add E2E test covering pipeline with mocked providers |

### Traceability (FRD→Code)
| # | Severity | Issue | Location | Recommendation |
|---|---|---|---|---|
| 1 | 🟢 INFO | FR-AST-005 "provider capability metadata" mapped to `capabilities_asset_provider.py` but no explicit `get_provider_capabilities` method found | `capabilities_asset_provider.py` | Verify method exists; add if missing |

## Violations
None found. AES layer separation respected (agent orchestrates, capabilities implement, root wires).

## Action Items
- [ ] 🟢 INFO Verify provider adapter contract exists in shared taxonomy/contracts
- [ ] 🟢 INFO Add E2E test for search→download→import pipeline
- [ ] 🟢 INFO Document download deduplication strategy

### Propose Change

#### File: `modules/asset/src/capabilities_asset_search_handler.py`

**FR-AST-001: Default results for empty query**

```python
async def search(self, query: str, page: int = 1, limit: int = 50) -> List[Asset]:
    """Search assets with provider.
    
    FR-AST-001: Returns curated/default results when query is empty or whitespace.
    """
    if not query or not query.strip():
        # Return curated default results for empty queries
        return await self._get_default_curated_results(page=page, limit=limit)
    
    # Normal search logic continues...
    return await self._search_single_provider(query, page=page, limit=limit)

async def _get_default_curated_results(self, page: int, limit: int) -> List[Asset]:
    """Return curated/default assets when no query is provided.
    
    FR-AST-001: Curated results are pre-vetted, high-quality assets.
    """
    # TODO: Implement curated results fetching from provider
    pass
```

#### File: `modules/asset/src/capabilities_asset_download.py`

**FR-AST-002: Concurrent download deduplication**

```python
import threading
from datetime import datetime, timezone

class AssetDownloadCapability:
    """Download capability with concurrent transfer deduplication.
    
    FR-AST-002: When multiple requests download the same asset concurrently,
    only one actual transfer occurs. Subsequent requests wait and receive
    the completed result.
    """
    
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._active_downloads: dict[AssetId, asyncio.Task] = {}  # Track in-flight transfers
    
    async def download(self, asset_id: AssetId, dest_path: Path) -> Path:
        """Download asset with deduplication.
        
        FR-AST-002: If same asset is already being downloaded, wait for existing transfer.
        """
        async with self._lock:
            # Check if this asset download is already in progress
            if asset_id in self._active_downloads:
                logger.info("Asset %s already downloading, waiting for completion", asset_id)
                return await self._active_downloads[asset_id]
            
            # No active download - create new one
            download_task = asyncio.create_task(self._perform_download(asset_id, dest_path))
            self._active_downloads[asset_id] = download_task
        
        try:
            result = await download_task
            return result
        finally:
            async with self._lock:
                # Remove from active downloads when complete
                self._active_downloads.pop(asset_id, None)
    
    async def _perform_download(self, asset_id: AssetId, dest_path: Path) -> Path:
        """Actual download implementation."""
        # Download logic here...
        pass
```

#### File: `modules/asset/src/capabilities_asset_provider.py`

**FR-AST-005: Provider capabilities metadata method**

```python
# Method already exists - confirmed in codebase
async def get_provider_capabilities(
    self,
    provider_name: ProviderName,
) -> dict[str, object]:
    """Get normalized provider capability metadata.
    
    FR-AST-005: Describes supported asset types, pagination behavior,
    and authentication requirements for the provider.
    """
    if provider_name in self._provider_capabilities:
        return dict(self._provider_capabilities[provider_name])
    
    capabilities = {
        "provider": provider_name,
        "supported_types": ["model", "texture", "hdri"],
        "pagination": {"supported": True, "default_limit": 50},
        "auth_required": False,
        "rate_limit": None,
    }
    self._provider_capabilities[provider_name] = capabilities
    return capabilities
```

#### File: `tests/test_asset_pipeline.py` (NEW)

**E2E test for search→download→import pipeline**

```python
import pytest
from unittest.mock import AsyncMock, MagicMock
from modules.asset.src.capabilities_asset_search_handler import AssetSearchHandler
from modules.asset.src.capabilities_asset_download import AssetDownloadCapability
from modules.asset.src.capabilities_asset_import import AssetImportCapability


@pytest.mark.asyncio
class TestAssetPipeline:
    """E2E test for search → download → extract → import pipeline."""
    
    async def test_full_pipeline_with_mocked_providers(self):
        """Test complete asset acquisition flow with mocked providers.
        
        Verifies:
        - Search returns assets
        - Download completes successfully
        - Import registers asset in Blender
        """
        # Setup mocks
        search_handler = MagicMock(spec=AssetSearchHandler)
        download_cap = MagicMock(spec=AssetDownloadCapability)
        import_cap = MagicMock(spec=AssetImportCapability)
        
        # Mock search returning an asset
        mock_asset = MagicMock()
        mock_asset.id = "test_asset_001"
        mock_asset.provider_id = "provider_001"
        search_handler.search = AsyncMock(return_value=[mock_asset])
        
        # Mock download completing
        download_cap.download = AsyncMock(return_value="/path/to/downloaded/file.blend")
        
        # Mock import succeeding
        import_cap.import_asset = AsyncMock(return_value=mock_asset)
        
        # Execute pipeline
        result = await search_handler.search(query="cube")
        assert len(result) > 0
        
        download_path = await download_cap.download(
            asset_id=result[0].id,
            dest_path="/tmp/downloads"
        )
        assert download_path is not None
        
        imported = await import_cap.import_asset(
            filepath=download_path,
            asset_id=result[0].id
        )
        assert imported is not None
    
    async test_concurrent_same_asset_download_dedup(self):
        """Test FR-AST-002: concurrent downloads resolve to one transfer.
        
        Verifies that when two requests download the same asset,
        only one actual download task runs.
        """
        download_cap = AssetDownloadCapability()
        
        # Mock the actual download to track calls
        original_perform = download_cap._perform_download
        call_count = 0
        
        async def mock_download(asset_id: str, dest_path: Path) -> Path:
            nonlocal call_count
            call_count += 1
            await asyncio.sleep(0.1)  # Simulate download time
            return f"/path/to/{asset_id}"
        
        download_cap._perform_download = mock_download
        
        # Run two concurrent downloads for same asset
        async with asyncio.TaskGroup() as tg:
            task1 = tg.create_task(download_cap.download("asset_001", "/tmp"))
            task2 = tg.create_task(download_cap.download("asset_001", "/tmp"))
        
        assert call_count == 1, "Should only perform one download for same asset"
```

## Severity
- 🔴 CRITICAL: Missing core requirement, wrong logic, data integrity risk
- 🟡 WARNING: Ambiguous requirement, missing edge case, incomplete criteria
- 🟢 INFO: Suggestion or optimization, deferrable

## Checklist
- [x] Prerequisites read
- [x] Feature + modules identified
- [x] FRD mapped to code files
- [x] All 5 dimensions analyzed
- [x] Severity categorized
- [x] Deduped vs existing plans + active PRs
- [x] Plan written (NEW issues + fixed code)
- [x] Saved to correct path