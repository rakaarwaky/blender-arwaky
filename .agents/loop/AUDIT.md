# ARWAKY LOOP AUDIT

Skeptical findings from each cycle:

## Cycle 1

- **Import violation (FIXED)**: `gateway/src/root_gateway_container.py` imported non-existent `.root_security_container` from same package. File actually lives in `modules/security/src/`. Fixed by importing `CodeValidator` from `modules.security.src.capabilities_code_validator` directly.
- **Stub found (FIXED)**: `render/src/capabilities_render_operate_executor.py` — `get_viewport_screenshot()` raised `NotImplementedError` with message "Viewport capture requires socket adapter; not available through code executor". Replaced with real implementation following same code-generation pattern as other render methods.
- **Test coverage gap**: 7 of 14 modules have no tests: asset, cli, dispatcher, object, render, telemetry, mcp. Only config, gateway, job, launcher, scene, and security have test suites.

## Cycle 2 — Structural Violations (Asset Module)

- **Duplicate capability files for same FR** (NOT FIXED):
  - FR-AST-001: `capabilities_asset_search.py` + `capabilities_asset_search_collector.py` (both implement AssetSearchProtocol)
  - FR-AST-002: `capabilities_asset_download.py` + `capabilities_asset_download_executor.py` (both implement AssetDownloadProtocol)
  - FR-AST-003: `capabilities_asset_extract.py` + `capabilities_asset_extract_executor.py` (both implement AssetExtractProtocol)
  - FR-AST-004: `capabilities_asset_import.py` + `capabilities_asset_import_executor.py` (both implement AssetImportProtocol)
- **Orphan capability files with no FR traceability** (NOT FIXED):
  - `capabilities_library_search.py` — claims "FR-AST-003" but this is NOT in the asset FRD (wrong FR code)
  - `capabilities_import_export_executor.py` — implements ImportExportProtocol (FR-IMP-001/IMP-002), not defined in asset FRD at all
- **Violation of one-FR-one-capability rule**: Asset module has 13 capability files but only 5 FRs. Should have exactly 5.
