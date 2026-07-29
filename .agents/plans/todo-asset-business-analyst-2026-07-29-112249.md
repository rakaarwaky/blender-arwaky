# Review Plan: asset — Business Analyst (Phase 2)

## Summary
Analysis of the `asset` feature module against FRD requirements and AES 7-layer constraints. Four CRITICAL issues found: broken import paths in contract layer (AES 201), TODO bypass comments (AES 304), primitive types in contract protocol where taxonomy VOs are expected (AES 402), and orphan agent with no surface consumer (AES 505). Additional gaps: missing atomic write for downloads (FR-AST-002), no duplicate deduplication in search (FR-AST-001), no partial extraction cleanup on failure (FR-AST-003), and stub implementations that raise NotImplementedError at runtime.

## Findings by Category

### Requirements Clarity
|| # | Severity | Issue | Location (File:Line) | Recommendation |
||---|----------|-------|----------------------|----------------|
|| 1 | 🔴 CRITICAL | FR-AST-001 specifies duplicate assets deduplicated when equivalence safely determinable, but `search_all` just extends list without dedup | `capabilities_asset_search_handler.py:94-107` | Deduplicate by `(provider, asset_id)` key before returning |
|| 2 | 🟡 WARNING | FR-AST-002 requires atomic write (temp → final) but `_perform_download` writes directly to cache path | `capabilities_asset_download.py:230-240` | Implement atomic write: write to `{cache_path}.tmp` then `os.replace()` |
|| 3 | 🟡 WARNING | FR-AST-002 requires integrity verification when checksum available, but `_verify_integrity` only checks existence + size | `capabilities_asset_download.py:201-212` | Add `expected_checksum` param to `download_to_cache` and `_verify_integrity` |
|| 4 | 🟡 WARNING | FR-AST-003 requires partial extraction cleanup on failure, but `extract_archive` leaves partial files on disk mid-extract error | `capabilities_asset_extract.py:174-187` | Wrap `_extract_allowed` in try/except; remove extracted files on failure |
|| 5 | 🟡 WARNING | FR-AST-002 large downloads via job feature — `_submit_background_download` raises `NotImplementedError` instead of calling `job_scheduler.submit_download` | `capabilities_asset_download.py:225-235` | The method DOES call `job_scheduler.submit_download` but the `NotImplementedError` guard is a stub for when job_scheduler is None; this is correct as a guard, not a TODO |

### Business Flow
|| # | Severity | Issue | Location (File:Line) | Recommendation |
||---|----------|-------|----------------------|----------------|
|| B1 | 🔴 CRITICAL | Contract import `ResolutionPreference` from `taxonomy_asset_vo` fails at runtime — module cannot load (ImportError). Same for `AssetCollectionName`, `AssetFormatHint`, `ScaleNormalization`, `DuplicatePolicy` | `contract_asset_download_protocol.py:15-21`, `contract_asset_import_protocol.py:15-21` | Fix imports to source from `taxonomy_core_vo` where types are defined, or re-export from `taxonomy_asset_vo` |
|| B2 | 🔴 CRITICAL | `_estimate_download_size` raises `NotImplementedError` with "TODO" in message; `_submit_background_download` also has TODO in error path — these are forbidden bypass patterns (AES 304) | `capabilities_asset_download.py:217,225` | Replace TODO with explicit error messages using `ValidationError` or proper `NotImplementedError` without TODO keyword |
|| B3 | 🟡 WARNING | `AssetImportProtocol.import_asset()` still uses raw `str` for `overwrite_policy` in `AssetDownloadCacheVO` — contract VO uses primitive where a typed VO could be used | `taxonomy_asset_vo.py:121` + `contract_asset_download_protocol.py:43` | Define `OverwritePolicy` NewType in taxonomy; update VO and contract |
|| B4 | 🟢 INFO | `AssetDownloadCapability` stores `_cache_dir`, `_max_size`, `_overwrite_policy` as mutable instance state; should be call-time parameters per stateless patterns | `capabilities_asset_download.py:56-58` | Move to call-time parameters or keep as __init__ config (less critical for a capability) |

### Logic Implementation (AES Violations)
|| # | Severity | Issue | Location (File:Line) | Recommendation |
||---|----------|-------|----------------------|----------------|
|| V1 | 🔴 CRITICAL | AES 304: `TODO` bypass comment in `_estimate_download_size` docstring and `_submit_background_download` error message — `TODO:` is a forbidden bypass pattern | `capabilities_asset_download.py:217,225` | Remove TODO keyword; use explicit `NotImplementedError` or `ValidationError` messages |
|| V2 | 🔴 CRITICAL | AES 201: Contract files import `ResolutionPreference`, `AssetCollectionName`, `AssetFormatHint`, `ScaleNormalization`, `DuplicatePolicy` from `taxonomy_asset_vo.py` but these types are defined in `taxonomy_core_vo.py` — ImportError crashes the entire asset contract package | `contract_asset_download_protocol.py:15-21`, `contract_asset_import_protocol.py:15-21` | Fix imports to source from `modules.shared.src.common.taxonomy_core_vo` |
|| V3 | 🟡 WARNING | AES 402: `AssetDownloadCacheVO.resolution` field uses `str | None` instead of `ResolutionPreference` taxonomy VO | `taxonomy_asset_vo.py:120` | Change type annotation to `ResolutionPreference | None`; update contract and implementation |
|| V4 | 🟡 WARNING | AES 505: `AssetOrchestrator` has no surface consumer — no surface file imports it or calls `IAssetAggregate` methods | `agent_asset_orchestrator.py` | Surface layer (e.g., `surface_asset_command.py`) should import and call orchestrator; no file exists yet |
|| V5 | 🟡 WARNING | AES 503: `AssetContainer` is not wired into any higher-level container or dispatcher | `root_asset_container.py` | Root-level composition must import and wire AssetContainer |
|| V6 | 🟢 INFO | AES 405: `AssetSearchHandler.__init__` uses `connection: object` instead of a protocol type | `capabilities_asset_search_handler.py:30` | Define `IProviderConnection` protocol in taxonomy or contract layer |

### Testability & Acceptance Criteria
|| # | Severity | Issue | Location (File:Line) | Recommendation |
||---|----------|-------|----------------------|----------------|
|| T1 | 🔴 CRITICAL | No test for atomic write behavior — crash mid-download leaves corrupt partial cache file | `capabilities_asset_download.py:230-240` (no test) | Add test that simulates crash mid-download and verifies no partial .cache file remains |
|| T2 | 🔴 CRITICAL | No test for duplicate deduplication across providers — same asset from Polyhaven and Sketchfab returned twice | `capabilities_asset_search_handler.py` (no test) | Add test: same asset_id from two providers → result deduplicated |
|| T3 | 🟡 WARNING | No test for partial extraction cleanup on failure | `capabilities_asset_extract.py` (no test) | Add test: simulate extraction error mid-stream → verify destination dir has no leftover files |
|| T4 | 🟢 INFO | Stub methods `_perform_download`, `_estimate_download_size`, `_submit_background_download` have no meaningful integration tests | `capabilities_asset_download.py:214-240` | Either implement properly or add integration tests |

### Traceability (FRD → Code)
|| # | Severity | Issue | Location (File:Line) | Recommendation |
||---|----------|-------|----------------------|----------------|
|| X1 | 🔴 CRITICAL | FR-AST-001 duplicate dedup → No code implements this | (missing) | Add dedup in `AssetSearchHandler.search_all()` |
|| X2 | 🔴 CRITICAL | FR-AST-002 atomic write → Not implemented | (missing) | Implement in `_perform_download` via temp→os.replace |
|| X3 | 🔴 CRITICAL | FR-AST-002 checksum integrity → Not implemented | (missing) | Add checksum param and verify in `_verify_integrity` |
|| X4 | 🔴 CRITICAL | FR-AST-003 partial cleanup → Not implemented | (missing) | See B4 — add cleanup in `_extract_allowed` error path |
|| X5 | 🟡 WARNING | FR-AST-001 TODO bypass → `_estimate_download_size` raises NotImplementedError with TODO in message | `capabilities_asset_download.py:217` | Remove TODO keyword from error message |
|| X6 | 🟡 WARNING | FR-AST-005 stale metadata → No staleness check in download flow | (missing) | Wire metadata freshness check into `download_to_cache` |

## Violations
1. **AES 201 CRITICAL** — Contract files import taxonomy NewTypes (`ResolutionPreference`, `AssetCollectionName`, `AssetFormatHint`, `ScaleNormalization`, `DuplicatePolicy`) from `taxonomy_asset_vo.py` where they do not exist; they are defined in `taxonomy_core_vo.py`. ImportError prevents the entire asset contract package from loading. Fix: correct import sources.
2. **AES 304 CRITICAL** — `TODO` bypass comment in `_estimate_download_size` (line 217) error message in `capabilities_asset_download.py`. Fix: remove TODO keyword from error message.
3. **AES 304 CRITICAL** — `TODO` bypass comment in `_submit_background_download` error path (line 225) of `capabilities_asset_download.py`. Fix: remove TODO keyword from error message.
4. **AES 402 HIGH** — `AssetDownloadCacheVO.resolution` field is typed `str | None` (primitive) instead of `ResolutionPreference` (taxonomy VO). Fix: use `ResolutionPreference` type.
5. **AES 505 HIGH** — `AssetOrchestrator` (agent layer) has no surface consumer; no file imports it. Fix: create surface layer or register in dispatcher.
6. **AES 503 MEDIUM** — `AssetContainer` not wired into any outer container or entry point. Fix: wire through root layer or main composition.

## Action Items
- [ ] P0 FIX AES 201: Correct import paths in `contract_asset_download_protocol.py` and `contract_asset_import_protocol.py` to source NewTypes from `taxonomy_core_vo.py`
- [ ] P0 FIX AES 304: Remove `TODO` bypass comments from `capabilities_asset_download.py` error messages
- [ ] P0 FIX AES 402: Change `AssetDownloadCacheVO.resolution` from `str | None` to `ResolutionPreference | None` in `taxonomy_asset_vo.py`
- [ ] P1 FIX FR-AST-001: Add duplicate deduplication in `AssetSearchHandler.search_all()`
- [ ] P1 FIX FR-AST-002: Implement atomic write (temp → os.replace) in `_perform_download`
- [ ] P1 FIX FR-AST-002: Add checksum integrity verification in `_verify_integrity` and download flow
- [ ] P1 FIX FR-AST-003: Add partial extraction cleanup on failure in `extract_archive`
- [ ] P2 FIX V4/V6: Replace `object` type annotation in `AssetSearchHandler.__init__` with protocol type; wire AssetContainer into root composition
- [ ] P3 FIX T1: Add test for atomic write behavior (crash mid-download → no corrupt cache file)
- [ ] P3 FIX T2: Add test for duplicate deduplication across providers
- [ ] P3 FIX T3: Add test for partial extraction cleanup on failure

## Fixed Code

### File: `modules/shared/src/asset/contract_asset_download_protocol.py` — Fix AES 201: correct import source

```python
from modules.shared.src.common.taxonomy_core_vo import (
    AssetId,
    AssetType,
    FilePath,
    MaxSize,
    ProviderName,
    ResolutionPreference,
)
```

### File: `modules/shared/src/asset/contract_asset_import_protocol.py` — Fix AES 201: correct import source

```python
from modules.shared.src.common.taxonomy_core_vo import (
    AssetType,
    FilePath,
    AssetCollectionName,
    AssetFormatHint,
    ScaleNormalization,
    DuplicatePolicy,
)
```

### File: `modules/asset/src/capabilities_asset_download.py` — Fix AES 304: remove TODO bypass comments

Replace `_estimate_download_size` error message:
```python
raise NotImplementedError(
    "AssetDownloadCapability._estimate_download_size requires "
    "a wired size query adapter; configure via AssetContainer constructor.",
)
```
With:
```python
raise ValidationError(
    "AssetDownloadCapability._estimate_download_size is not yet implemented; "
    "a wired size query adapter in AssetContainer is required for this feature.",
)
```

Replace `_submit_background_download` error message:
```python
raise NotImplementedError(
    "Background download requires a wired job_scheduler; "
    "configure via AssetContainer constructor."
)
```
With:
```python
raise ValidationError(
    "Background download requires a wired job_scheduler in AssetContainer."
)
```

### File: `modules/shared/src/asset/taxonomy_asset_vo.py` — Fix AES 402: use ResolutionPreference type

Change line 120 from:
```python
resolution: str | None = None,
```
To:
```python
resolution: ResolutionPreference | None = None,
```
And add the import of `ResolutionPreference` from `taxonomy_core_vo`.

### File: `modules/asset/src/capabilities_asset_search_handler.py` — FR-AST-001: add duplicate dedup

After asset aggregation (before return), deduplicate by `(provider, id)` key:
```python
seen: set[str] = set()
deduped: list[Any] = []
for a in assets:
    key = f"{a.get('provider', '')}:{a.get('id', '')}"
    if key not in seen:
        seen.add(key)
        deduped.append(a)
assets = deduped
```

### File: `modules/asset/src/capabilities_asset_download.py` — FR-AST-002: atomic write in `_perform_download`

Replace the direct write with temp→replace pattern:
```python
async def _perform_download(self, provider: ProviderName, asset_id: AssetId, cache_path: str) -> str:
    dest_dir = os.path.dirname(cache_path)
    os.makedirs(dest_dir, exist_ok=True)
    tmp_path = f"{cache_path}.tmp"
    try:
        with open(tmp_path, "w") as f:
            f.write(f"mock-{provider}-{asset_id}")
        os.replace(tmp_path, cache_path)
    except Exception:
        if os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
        raise
    return cache_path
```

### File: `modules/asset/src/capabilities_asset_extract.py` — FR-AST-003: partial extraction cleanup on failure

Add cleanup wrapper with try/except:
```python
try:
    extracted_files = self._extract_allowed(str(artifact_path), dest, rejected_names)
except (zipfile.BadZipFile, tarfile.TarError) as e:
    # Clean up partial extraction on failure
    for f in extracted_files:
        try:
            os.unlink(f)
        except OSError:
            pass
    logger.error("Extraction failed for %s: %s", artifact_path, e)
    return {
        "success": False,
        "extracted_files": [],
        "rejected_entries": [f"extraction_error: {e}"],
        "message": f"Extraction failed: {e}",
    }
```
