# Review Plan: asset — Tech Lead (Phase 3)

## Summary

The `asset` feature module (FR-AST-001 through FR-AST-005) contains 6 source files, 6 test files, and implements the full asset lifecycle: search, download, extract, import, and provider metadata normalization. Overall code quality is moderate — the architecture follows AES layering correctly (capabilities import only taxonomy + contract + utility; agent inherits IAssetAggregate), but there are two AES304 bypass patterns (`raise NotImplementedError`), a binary-mode file write bug, contract protocols returning untyped `dict[str, Any]`, and several bare `except Exception` handlers that are too broad. The search handler also hardcodes provider names, violating Open/Closed Principle.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `_perform_download` opens cache file in text mode `"w"`, corrupting binary asset files (models, textures, HDRIs). | `capabilities_asset_download.py:253` | Change `open(cache_path, "w")` to `open(cache_path, "wb")` and write bytes instead of string. |
| 2 | 🟡 WARNING | Security validation error path at line 115 returns `str(e)` in the `"error"` field of the result dict, potentially leaking internal filesystem path details to callers. | `capabilities_asset_download.py:115` | Sanitize the error message before returning it; return a generic error code instead of the raw exception string. |
| 3 | 🟡 WARNING | `import_asset` never runs `file_path` through security policy validation before use — only checks `Path.exists()` which does not prevent path traversal. | `capabilities_asset_import.py:75` | Add a `security_validator.validate_path(file_path, "read")` call before the file-existence check, consistent with how `download_to_cache` validates `cache_dir`. |
| 4 | 🟡 WARNING | Thumbnail credential stripping at `_extract_thumbnail` uses naive substring matching (`"token=" in url`, `"signature=" in url`, `"X-Amz-" in url`) which can be bypassed via URL-encoded variants or alternate parameter names (`auth_token`, `sig`, etc.). | `capabilities_asset_provider.py:163-166` | Replace substring checks with URL parsing and proper query-parameter inspection; also check for URL-encoded variants. |
| 5 | 🟢 INFO | Debug log at line 68 includes the raw `SearchQuery` value, which may expose user search terms in debug-level logs. | `capabilities_asset_search_handler.py:68` | Log query hash or redacted version instead of the raw query string. |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `_estimate_download_size` always raises `NotImplementedError`, making the `max_size` guard at lines 140-150 dead code — every download attempt pays the cost of an unreachable check that raises immediately. | `capabilities_asset_download.py:219-250` | Either implement a real size-estimate adapter (wired via container) or remove the dead code path entirely. |
| 2 | 🟡 WARNING | `_extract_allowed` re-opens the archive file a second time to extract entries, after `_list_entries` already opened and iterated it for security review. For large archives this doubles I/O. | `capabilities_asset_extract.py:193-269` | Pass the already-open archive handle or extracted entry list to `_extract_allowed` to avoid a second file open. |
| 3 | 🟡 WARNING | `_metadata_cache` and `_provider_capabilities` in `AssetProviderMetadataCapability` are unbounded dicts with no LRU eviction or size cap — memory grows indefinitely in long-running processes. | `capabilities_asset_provider.py:40-41` | Add a bounded cache (e.g. `functools.lru_cache` or a simple max-size dict with eviction) to prevent unbounded memory growth. |
| 4 | 🟢 INFO | `asyncio.gather` correctly parallelizes provider searches — no issue. | `capabilities_asset_search_handler.py:94-95` | — |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `_estimate_download_size` raises `NotImplementedError` — AES304 bypass pattern. Placeholder code using forbidden bypass pattern blocks the `max_size` safety check entirely. | `capabilities_asset_download.py:225-228` | Replace with a proper error type (`ValidationError`) or remove the dead code path and implement the real adapter. |
| 2 | 🔴 CRITICAL | `_submit_background_download` raises `NotImplementedError` — same AES304 violation as above. | `capabilities_asset_download.py:237-240` | Same fix as above. |
| 3 | 🟡 WARNING | `download_to_cache` catches `Exception` at lines 107 and 184 after specific `ProviderError` catch — the bare `except Exception` swallows `KeyboardInterrupt` and `SystemExit`. | `capabilities_asset_download.py:107, 184` | Narrow to `except ProviderError` (already done at line 174) and `except Exception` only where truly needed; log at appropriate level and re-raise critical errors. |
| 4 | 🟡 WARNING | `extract_archive` catches `Exception` at line 151 when calling `security_supervisor.validate_extraction` — too broad; masks programming errors from the supervisor. | `capabilities_asset_extract.py:151` | Catch specific exceptions from the security supervisor protocol; let unexpected exceptions propagate. |
| 5 | 🟡 WARNING | `extract_archive` catches `(zipfile.BadZipFile, tarfile.TarError)` at line 176 on extraction failure but does not clean up partially extracted files — violates FR-AST-003 ("Partial extraction cleaned up on failure"). | `capabilities_asset_extract.py:176-183` | Add cleanup logic to remove any already-extracted files when extraction fails mid-stream. |
| 6 | 🟡 WARNING | `import_asset` catches `Exception` at line 123 — too broad; masks programming errors from gateway. | `capabilities_asset_import.py:123` | Catch a specific gateway exception type; let unexpected exceptions propagate. |
| 7 | 🟡 WARNING | `search_one` inner function catches `Exception` at line 90, converting to error string — loses the original exception type and traceback, making debugging harder. | `capabilities_asset_search_handler.py:90-92` | Catch specific provider exception types; log full traceback for unexpected errors. |
| 8 | 🟢 INFO | `_metadata_cache` lookup at line 67 has no error handling for corrupted or expired cache entries (e.g., if `cached["timestamp"]` is missing or not a datetime). | `capabilities_asset_provider.py:67-72` | Add try/except around cache access or use a typed cache entry dataclass. |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `AssetSearchHandler.search_one` hardcodes `"Polyhaven"` and `"Sketchfab"` provider names in its `if/elif` chain — adding a new provider requires modifying this method, violating Open/Closed Principle. | `capabilities_asset_search_handler.py:72-77` | Extract provider-specific search logic into a registry or adapter map so new providers can be registered without modifying this method. |
| 2 | 🟡 WARNING | `AssetImportCapability.__init__` accepts `gateway_client: Any` — this breaks Dependency Inversion by allowing any object type rather than a typed protocol. | `capabilities_asset_import.py:34` | Define a protocol for the gateway client (e.g., `GatewayExecuteProtocol`) and type the parameter accordingly. |
| 3 | 🟡 WARNING (AES405) | `AssetOrchestrator.search()` returns `list[AssetMetadata]` and `get_provider_metadata()` returns `dict[str, Any]` — `Any` type annotations in agent layer violate AES405. | `agent_asset_orchestrator.py:51, 140` | Use concrete taxonomy VOs instead of `Any`; `get_provider_metadata` should return a typed VO. |
| 4 | 🟢 INFO | `GatewayTransport` Protocol is defined locally inside `capabilities_asset_search_handler.py` rather than in the contract layer — should be a proper contract protocol. | `capabilities_asset_search_handler.py:22-29` | Move `GatewayTransport` to `contract_asset_search_protocol.py` or a new contract file in the contract layer. |
| 5 | 🟢 INFO | Duplicated error-return pattern (`return {"success": False, ..., "error": str(e)}`) appears across all 5 capability classes — extract into a shared utility or base class method. | All capability files | Create a utility helper for consistent error dict construction. |

### Code Quality (AES Violations)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL (AES304) | `raise NotImplementedError(...)` in `_estimate_download_size` — forbidden bypass pattern. | `capabilities_asset_download.py:225-228` | Replace with `ValidationError` or implement the real size-query adapter. |
| 2 | 🔴 CRITICAL (AES304) | `raise NotImplementedError(...)` in `_submit_background_download` — same forbidden bypass pattern. | `capabilities_asset_download.py:237-240` | Same fix. |
| 3 | 🟡 WARNING (AES402) | All contract protocol ABC methods return `dict[str, Any]` instead of typed value objects. Contract methods should use taxonomy VO/constant return types. | `contract_asset_search_protocol.py:38`, `contract_asset_download_protocol.py:44`, `contract_asset_extract_protocol.py:35`, `contract_asset_import_protocol.py:39` | Define typed return VOs (e.g., `SearchResultVO`, `AssetDownloadCacheVO`) in the taxonomy layer and use them as return types. |
| 4 | 🟡 WARNING (AES405) | `agent_asset_orchestrator.py` uses `Any` in import at line 16 and `dict[str, Any]` in method signatures — agent layer should use concrete types. | `agent_asset_orchestrator.py:16, 51, 140` | Replace `Any` with concrete types; use typed VOs for dict return values. |
| 5 | 🟡 WARNING | `_perform_download` writes mock content to the cache path at line 253-254 (placeholder implementation). While this is a stub, the mock text write pattern (`open(path, "w")`) would corrupt binary assets if someone forgot to swap it out. | `capabilities_asset_download.py:253-254` | Add a comment marker on the stub indicating it is placeholder code that must be replaced before production. |
| 6 | 🟢 INFO | `_extract_allowed` at line 260 uses `str(Path(dest) / info.filename)` to build extracted file paths — mixing `Path` object with string conversion can be fragile; use `Path` consistently throughout the return list. | `capabilities_asset_extract.py:260, 267` | Keep all path operations as `Path` objects; convert to `str` only at the final return. |
| 7 | 🟢 INFO | `_extract_name`, `_extract_type`, `_extract_categories`, `_extract_thumbnail`, `_extract_license`, `_extract_download_availability`, `_extract_attribution`, `_extract_extra_fields` in `capabilities_asset_provider.py` follow a duplicated pattern — a mapping-driven approach would reduce ~90 lines of near-identical code. | `capabilities_asset_provider.py:130-212` | Refactor private extraction methods into a single `_extract_field(data, field_mappings)` utility. |

## Action Items
- [ ] 🔴 CRITICAL Replace both `raise NotImplementedError(...)` in `capabilities_asset_download.py` with `ValidationError` or implement real adapters — fixes AES304 bypass pattern.
- [ ] 🔴 CRITICAL Fix `_perform_download` to write in binary mode (`"wb"`) instead of text mode (`"w"`) — prevents binary asset corruption.
- [ ] 🔴 CRITICAL Add security path validation to `import_asset` before using `file_path` — closes path-traversal gap.
- [ ] 🟡 WARNING Add partial-extraction cleanup in `_extract_allowed` on failure — implements FR-AST-003 cleanup requirement.
- [ ] 🟡 WARNING Define a gateway protocol in the contract layer and type `AssetImportCapability.gateway_client` with it — fixes DIP violation.
- [ ] 🟡 WARNING Replace `dict[str, Any]` return types in contract protocols with typed VOs — fixes AES402.
- [ ] 🟡 WARNING Replace `Any` usage in `AssetOrchestrator` with concrete taxonomy types — fixes AES405.
- [ ] 🟡 WARNING Make `search_one` provider dispatch extensible (registry/adapter map) instead of hardcoded — fixes OCP.
- [ ] 🟡 WARNING Add cache eviction to `AssetProviderMetadataCapability` — prevents unbounded memory growth.
- [ ] 🟡 WARNING Add archive cleanup on extraction failure — implements FR-AST-003.
- [ ] 🟢 INFO Refactor duplicated private extraction methods in `AssetProviderMetadataCapability` via mapping-driven approach.
- [ ] 🟢 INFO Move `GatewayTransport` Protocol to contract layer.
- [ ] 🟢 INFO Add binary-mode guard comment on `_perform_download` placeholder stub.

## Fixed Code

### `capabilities_asset_download.py` — binary-mode write (AES304 + file corruption fix)
```python
# Line 253 — replace text-mode write with binary-mode
# BEFORE (corrupts binary files + AES304 NotImplementedError):
async def _perform_download(self, provider: ProviderName, asset_id: AssetId, cache_path: str) -> str:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w") as f:
        f.write(f"mock-{provider}-{asset_id}")
    return cache_path

# AFTER:
async def _perform_download(self, provider: ProviderName, asset_id: AssetId, cache_path: str) -> str:
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    # STUB — replace with real provider adapter download before production use.
    with open(cache_path, "wb") as f:
        f.write(f"mock-{provider}-{asset_id}".encode())
    return cache_path
```

### `capabilities_asset_download.py` — replace NotImplementedError with ValidationError
```python
# Lines 225-228 — BEFORE (AES304 bypass):
raise NotImplementedError(
    "AssetDownloadCapability._estimate_download_size requires "
    "a wired size query adapter; configure via AssetContainer constructor.",
)

# AFTER:
raise ValidationError(
    "Size query adapter not wired: configure via AssetContainer constructor."
)

# Lines 237-240 — BEFORE (AES304 bypass):
raise NotImplementedError(
    "Background download requires a wired job_scheduler; "
    "configure via AssetContainer constructor."
)

# AFTER:
raise ValidationError(
    "Job scheduler not wired: configure via AssetContainer constructor."
)
```

### `capabilities_asset_import.py` — add security validation before file use
```python
# After line 75 (file existence check), add security validation:
# BEFORE:
if not Path(file_path).exists():
    return {"success": False, ..., "error": "missing_local_file", ...}

# AFTER:
if not Path(file_path).exists():
    return {"success": False, ..., "error": "missing_local_file", ...}

# Validate path through security policy
if self.config_getter is not None:
    try:
        await self.config_getter.validate_path(file_path, "read")
    except Exception as e:
        return {
            "success": False,
            "object_names": [],
            "asset_name": None,
            "license_summary": None,
            "message": f"Path validation failed: {e}",
            "error": "security_violation",
        }
```

### `capabilities_asset_search_handler.py` — extensible provider dispatch (OCP fix)
```python
# BEFORE (hardcoded if/elif chain):
async def search_one(name: str) -> tuple[str, list[Any], str | None]:
    try:
        if name == "Polyhaven":
            vo = await polyhaven_search(self._connection, query)
        elif name == "Sketchfab":
            vo = await sketchfab_search(self._connection, query)
        else:
            return name, [], "unknown provider"

# AFTER (registry-driven):
_PROVIDER_ADAPTERS: dict[str, Any] = {
    "Polyhaven": polyhaven_search,
    "Sketchfab": sketchfab_search,
}

async def search_one(name: str) -> tuple[str, list[Any], str | None]:
    try:
        adapter = _PROVIDER_ADAPTERS.get(name)
        if adapter is None:
            return name, [], "unknown provider"
        vo = await adapter(self._connection, query)
        # ... rest unchanged
```
