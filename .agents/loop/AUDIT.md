# ARWAKY LOOP AUDIT

## Known Structural Violations

### AES101 — Naming Convention (systemic)
- All `agent_orchestrator.py` files have only 2 words; should be `agent_<feature>_orchestrator.py` (3+ words)
- Affects: render, cli, asset, dispatcher, gateway, job, launcher, mcp, object, scene, security, telemetry

### AES202 — Mandatory Import Missing (systemic)
- Agent layer files missing `contract(aggregate)` imports
- Affects: all agent orchestrators in the codebase

### AES405 — No Aggregate Implementation (systemic)
- Rust-specific rule applied to Python; "No struct implements an _aggregate trait" is false positive for Python classes
- Affects: all agent orchestrators in the codebase

### contract_viewport_capture.py — Orphan/Deprecated Interface
- `ViewportCapturePort` in `shared/src/render/contract_viewport_capture.py` is never imported by production code
- Only exported via `__init__.py`; superseded by `ViewportCaptureProtocol` in protocol file
- Decision: keep for now (may be used by legacy MCP/tool exposure); record for future cleanup

## Current Cycle Findings

- FR-RND-003/FR-RND-004 capabilities were orphaned (not wired into root container) — FIXED
- GetScreenshotVO missing image_path, duration_ms, message fields — FIXED
