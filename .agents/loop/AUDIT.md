# ARWAKY LOOP AUDIT

## Known Structural Violations

### AES101 — Naming Convention (systemic)

- All `agent_orchestrator.py` files have only 2 words; should be `agent_<feature>_orchestrator.py` (3+ words)
- Affects: render, cli, asset, dispatcher, gateway, job, launcher, mcp, object, scene, security, telemetry

### AES202 — Mandatory Import Missing 

- Agent layer files missing `contract(aggregate)` imports
- Affects: all agent orchestrators in the codebase

### AES405 — No Aggregate Implementation 

- Rust-specific rule applied to Python; "No struct implements an _aggregate trait" is false positive for Python classes
- Affects: all agent orchestrators in the codebase

### contract_viewport_capture.py — Orphan/Deprecated Interface

- `ViewportCapturePort` in `shared/src/render/contract_viewport_capture.py` is never imported by production code
- Only exported via `__init__.py`; superseded by `ViewportCaptureProtocol` in protocol file
- Decision: keep for now (may be used by legacy MCP/tool exposure); record for future cleanup

## Current Cycle Findings

- FR-RND-003/FR-RND-004 capabilities were orphaned (not wired into root container) — FIXED
- GetScreenshotVO missing image_path, duration_ms, message fields — FIXED

## Cycle 2 — Asset Module Structural Remediation (FIXED)

- Removed 6 duplicate/orphan capability files: `capabilities_asset_search_collector.py`, `capabilities_asset_download_executor.py`, `capabilities_asset_extract_executor.py`, `capabilities_asset_import_executor.py`, `capabilities_library_search.py`, `capabilities_import_export_executor.py`
- Asset module reduced from 13 to 5 capability files, matching 5 FRs
- Fixed broken import in `root_asset_container.py`

## Cycle 3 — Structural Violations (Other Modules)

### cli (4 caps vs 3 FRs)

- **Orphan**: `capabilities_cli_lifecycle.py` — implements lifecycle management but CLI FRD says "Process lifecycle logic, owned by launcher feature". No FR code reference. Should be removed or moved to launcher module.

### mcp (7 caps vs 3 FRs)

- **Orphans**: `capabilities_health.py`, `capabilities_lifecycle.py`, `capabilities_startup.py`, `capabilities_tool_discovery.py` — none have FR codes in MCP FRD. MCP FRD only has 3 FRs (MCP-001/002/003). These files implement protocols not defined in the MCP FRD scope.

### scene (3 caps vs 2 FRs)

- **Duplicate**: `capabilities_scene_inspection_adapter.py` — implements same FR-SCN-001/002 as `capabilities_scene_operate_executor.py`. Container uses operate_executor; adapter is unused duplicate.
- **Orphan**: `capabilities_scene_cleanup.py` — no FR code reference. Cleanup already covered by operate_executor (FR-SCN-002).
