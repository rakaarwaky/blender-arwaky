# Review Plan: asset (External Asset Feature) — Backend Developer

## Summary

Reviewed `modules/asset/src/` (5 capabilities + agent orchestrator + root container) against
`modules/asset/FRD.md`. The module is structurally AES-compliant (capabilities implement their
protocols, naming follows `capabilities_*`/`agent_*`/`root_*` prefixes). However, one **CRITICAL**
FRD-layer violation exists: the extraction capability implements its *own* archive path-traversal
protection (`_is_safe_path`, `_is_symlink_entry`, inline size/count/link checks) — which FR-AST-003
explicitly forbids — and simultaneously calls the real security supervisor with the wrong signature
(loose kwargs instead of `ArchiveExtractionVO`), so it would `TypeError` against the real
`ExtractArchiveProtocol`. Secondary WARNING-level issues: the search capability passes a fabricated
request object instead of `AssetSearchVO` and silently ignores filter/limit/pagination parameters;
the download capability hardcodes `integrity_ok=True` without verifying the downloaded artifact.
Architectural gaps (orchestrator only coordinates search; container never wires download/extract/
import or the security/job/gateway/config dependencies) are documented but not fixed this cycle
because they require shared-contract and cross-module wiring changes that exceed module scope.

## Findings by Category

### Architecture & Layer Compliance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| A1  | 🔴 CRITICAL | Extraction capability enforces its own path-traversal / symlink / size / count safety instead of delegating to security policy feature (FR-AST-003: "Asset feature must not implement its own path traversal protection"). | `capabilities_asset_extract.py` (`_is_safe_path`, `_is_symlink_entry`, inline per-entry checks in `_extract_zip`/`_extract_tar`) | Remove local safety logic; delegate all archive safety decisions to `security_supervisor.validate_extraction(ArchiveExtractionVO)`. |
| A2  | 🔴 CRITICAL | Wrong security-supervisor contract call: passes `artifact_path=`, `destination=`, `max_entries=`, `max_size=`, `allow_symlinks=` kwargs, but `ExtractArchiveProtocol.validate_extraction` takes a single `ArchiveExtractionVO`. Works only against the test mock; breaks against the real security feature. | `capabilities_asset_extract.py:71` | Build `ArchiveExtractionVO` (entries + options) and call `await security_supervisor.validate_extraction(vo)`. |
| A3  | 🟡 WARNING | Orchestrator (`agent_orchestrator.py`) only coordinates search and delegates `fetch_and_import` to the collector (`AssetSearchProtocol`); real `AssetSearchCapability` has no `fetch_and_import` → `AttributeError` at runtime. Also `search()` typed to return `list[AssetMetadata]` but capability returns `dict`. | `agent_orchestrator.py`, `root_asset_container.py` | Orchestrator must hold search+download+extract+import capabilities and compose them. Requires container wiring + shared contract for `fetch_and_import`. Deferred (cross-module/shared). |
| A4  | 🟡 WARNING | `root_asset_container.py` never instantiates `AssetDownloadCapability`, `AssetExtractCapability`, `AssetImportCapability`, `AssetProviderMetadataCapability`, and never wires `security_validator`/`job_scheduler`/`gateway_client`/`config_getter`. Feature cannot download/extract/import end-to-end. | `root_asset_container.py` | Wire all capabilities and their declared dependencies once those features expose entry points. Deferred (depends on other modules). |

### Security

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| S1  | 🔴 CRITICAL | Local traversal protection in asset feature duplicates security policy and can drift out of sync with the authoritative guard. Empty-query / no-supervisor path currently extracts with zero safety. | `capabilities_asset_extract.py` | Delegated (see A1/A2). Fail closed when no supervisor is present. |
| S2  | 🟢 INFO | Search result leakage of credentials already mitigated; no exposure found. Adapter-side `token=`/`signature=` redaction lives in metadata capability. OK. | `capabilities_asset_provider_metadata.py` | None. |

### Performance

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| P1  | 🟢 INFO | `_estimate_download_size` is a fixed 1 MB stub; size guard relies on it. Acceptable until real provider integration. | `capabilities_asset_download.py:208` | Replace with provider-supplied size once adapter wired. |

### Error Handling

| #   | Severity | Issue | Location | Recommendation |
| --- | -------- | ----- | -------- | -------------- |
| E1  | 🟡 WARNING | `search_all` constructs `type("Obj", (), {"query": query})()` instead of the protocol's `AssetSearchVO`, so the request type contract is violated and `asset_type_filter`/`limit`/`page_token` are never propagated. | `capabilities_asset_search.py:85` | Pass `AssetSearchVO(query=query)`. (Filter wiring blocked by shared `AssetSearchVO` lacking `asset_type`/`categories`/limit/`page_token` fields — see INFO I1.) |
| E2  | 🟡 WARNING | `download_to_cache` returns `integrity_ok: True` on synchronous success without verifying the artifact exists/non-empty (the stub `_perform_download` never writes a file). | `capabilities_asset_download.py:165` | Compute `integrity_ok` from `_verify_integrity(file_path)`; have the stub write a non-empty placeholder artifact so verification is meaningful. |
| E3  | 🟢 INFO | Download `max_size` comparison `estimated_size > max_size` compares int to `MaxSize` VO; currently works because `MaxSize` is an `int` `NewType`, but is fragile. | `capabilities_asset_download.py:136` | Compare against `int(max_size)` once a real estimate exists. |

## Violations

- AES201 (cross-layer import): none introduced. New extract imports (`modules.shared.src.security.taxonomy_security_vo`, `contract_extract_archive_protocol`) are taxonomy + contract(protocol) — permitted for the capabilities layer.
- AES304 (bypass comment): not introducing `noqa`/`type: ignore`/`unwrap`. Broad `except Exception` retained for provider orchestration (returns error dict) — acceptable per existing pattern.
- AES303 (mandatory definition): all files retain definitions.
- FR-AST-003 layer violation (A1/A2/S1) is the primary defect.

## Action Items

- [ ] CRITICAL Rewrite `capabilities_asset_extract.py` to delegate safety to `security_supervisor.validate_extraction(ArchiveExtractionVO)`; remove `_is_safe_path`/`_is_symlink_entry` and inline per-entry enforcement; fail closed when no supervisor.
- [ ] CRITICAL Update `tests/test_asset_extract.py` mock supervisor to the `ArchiveExtractionVO` contract and flip the "no local traversal protection" assertion.
- [ ] WARNING Fix `capabilities_asset_search.py` to pass `AssetSearchVO(query=query)`.
- [ ] WARNING Fix `capabilities_asset_download.py` `integrity_ok` to reflect real verification; stub writes a non-empty artifact.
- [ ] INFO Document A3/A4/I1 as deferred cross-module/shared findings (no code change this cycle).

## Fixed Code

### `capabilities_asset_extract.py` (extract delegation — key change)

```python
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveEntryVO,
    ArchiveExtractionOptionsVO,
    ArchiveExtractionVO,
)
from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
...
async def extract_archive(self, artifact_path, destination, max_entries=1000,
                          max_extracted_size=1073741824, allow_symlinks=False):
    if not Path(artifact_path).exists():
        return {"success": False, ..., "message": f"Archive file not found: {artifact_path}"}
    try:
        entries = self._list_entries(artifact_path)   # ArchiveEntryVO list
    except (zipfile.BadZipFile, tarfile.TarError) as e:
        return {"success": False, ..., "message": f"Invalid archive: {e}"}
    options = ArchiveExtractionOptionsVO(
        max_entry_count=max_entries,
        max_total_size=max_extracted_size,
        allow_symbolic_links=allow_symlinks,
    )
    vo = ArchiveExtractionVO(
        destination_directory=str(destination),
        entries=tuple(entries),
        options=options,
    )
    if self.security_supervisor is None:
        return {"success": False, ...,
                "message": "Archive extraction requires security supervision (FR-AST-003); "
                           "asset feature does not implement path traversal protection."}
    result = await self.security_supervisor.validate_extraction(vo)
    if not result.allowed:
        return {"success": False, "extracted_files": [],
                "rejected_entries": [r.entry_path for r in result.rejected_entries],
                "message": "Extraction rejected by security policy",
                "warnings": list(result.warnings)}
    dest = result.safe_destination or str(destination)
    os.makedirs(dest, exist_ok=True)
    rejected = {r.entry_path for r in result.rejected_entries}
    extracted = self._extract_allowed(artifact_path, dest, rejected)  # no local safety checks
    return {"success": True, "extracted_files": extracted,
            "rejected_entries": [r.entry_path for r in result.rejected_entries],
            "message": f"Extracted {len(extracted)} files, {len(rejected)} rejected",
            "extraction_timestamp": datetime.now(timezone.utc).isoformat()}
```

(Full implementation in `Fixed Code` file below.)
