# Review Plan: Asset — Tech Lead (Phase 3)

## Summary
The Asset module provides single authority for everything entering blender-arwaky from outside: search providers, download to local cache, extract archives under security supervision, and import into Blender. Overall code quality is good with solid AES architecture compliance and proper layer separation. Most structural concerns are well handled — capabilities delegate properly, orchestrator follows contract protocols, and DI wiring in the container is clean. The primary issues found are bypass comments (`# noqa: ARG002`) used to silence unused-parameter warnings for interface params that aren't yet consumed, and one flagged dummy import for `time` (which is actually used in `_get_unique_cache_path`). No critical security vulnerabilities — thumbnail URL validation rejects unsafe protocols and credentials.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | Thumbnail URL validation already rejects unsafe protocols (file://, javascript:, data:) and credential-embedded URLs | capabilities_asset_provider.py:120-134 | ✅ No fix needed — properly implemented |
| 2 | 🟢 INFO | Credentials never embedded in results/logs/events | All files | ✅ No fix needed — by design |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | Parallel provider search via asyncio.gather — efficient, no N+1 queries | capabilities_asset_search_handler.py:58-59 | ✅ No fix needed — already optimal |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | Per-provider error handling with partial results — failures logged and skipped | capabilities_asset_search_handler.py:47-56 | ✅ No fix needed — proper graceful degradation |
| 2 | 🟡 WARNING | Download capability returns dict instead of raising exceptions for errors | capabilities_asset_download.py:85-94,152-163 | Consider raising ProviderError instead of returning error dict (aligns with gateway pattern from commit 59561ed) |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | AssetOrchestrator has 5 dependency injections — exceeds 3 types limit? | agent_asset_orchestrator.py:47-52 | Check AES405 — orchestrator has 5 capability injections but all are dependencies (not type declarations), so compliant |
| 2 | 🟢 INFO | AssetContainer uses double-checked locking for thread-safe DI — appropriate for Python | root_asset_container.py:38-60 | ✅ No fix needed — intentional concurrency pattern |

### Code Quality
| # | Severity | Issue | Location (File:Line) | Recommendation | Status |
|---|----------|-------|----------------------|----------------|--------|
| 1 | 🔴 CRITICAL | 6 `# noqa: ARG002` bypass comments in 2 files — unused interface params | capabilities_asset_search_handler.py:37-39, capabilities_asset_download.py:64,214,222 | Replace with underscore prefix (`_asset_type`, `_limit`, etc.) to signal intentional unused params | Needs fix |
| 2 | 🟡 WARNING | `time` import flagged as dummy (AES204) | capabilities_asset_download.py:12 | False positive — `time` is used at line 198 in `_get_unique_cache_path`. Linter may need scope adjustment. | Verify |

## Action Items
- [ ] **CRITICAL** Replace `# noqa: ARG002` bypass comments with underscore-prefixed parameter names in capabilities_asset_search_handler.py (lines 37-39)
- [ ] **CRITICAL** Replace `# noqa: ARG002` bypass comments with underscore-prefixed parameter names in capabilities_asset_download.py (lines 64, 214, 222)
- [ ] **WARNING** Verify `time` import is genuinely used at line 198 — if linter flag is false positive, document; if unused, remove

## Fixed Code

### File: `modules/asset/src/capabilities_asset_search_handler.py`

Replace lines 37-39:
```python
        asset_type_filter: Any = None,  # noqa: ARG002
        limit: Any = None,  # noqa: ARG002
        page_token: Any = None,  # noqa: ARG002
```
With:
```python
        _asset_type_filter: Any = None,
        _limit: Any = None,
        _page_token: Any = None,
```

### File: `modules/asset/src/capabilities_asset_download.py`

Replace line 64:
```python
        asset_type: AssetType,  # noqa: ARG002
```
With:
```python
        _asset_type: AssetType,
```

Replace line 214:
```python
    async def _estimate_download_size(self, provider: ProviderName, asset_id: AssetId) -> int:  # noqa: ARG002
```
With:
```python
    async def _estimate_download_size(self, provider: ProviderName, _asset_id: AssetId) -> int:
```

Replace line 222:
```python
    async def _submit_background_download(self, provider: ProviderName, asset_id: AssetId, cache_path: str) -> str:  # noqa: ARG002
```
With:
```python
    async def _submit_background_download(self, provider: ProviderName, _asset_id: AssetId, cache_path: str) -> str:
```
