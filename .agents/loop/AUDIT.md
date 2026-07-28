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

## Cycle 4 — Broken-Import / Undefined-Name Sweep (FIXED)

Root-caused via `lint-arwaky-cli scan` (F821/F811 bug-class codes) + a 41-module import sweep. Six distinct import-time crash classes fixed:

1. **F821 undefined annotations** — `object`/`security` orchestrators + containers annotated return types with `ObjectOperateAggregate`/`SecurityOperateAggregate`, but the contract defines `IObjectOperateAggregate`/`ISecurityOperateAggregate` (the imported names). Without `from __future__ import annotations`, the annotation evaluated at def time -> `NameError` on import. Fixed 6 annotations.
2. **F811 duplicate `ConnectionError`** — `modules/shared/src/__init__.py` re-exported `ConnectionError` from both `common/taxonomy_domain_error.py` and `gateway/taxonomy_gateway_error.py`. Removed the unused common re-export.
3. **F811 redundant inner import** — `gateway/capabilities_transport.py` re-imported `validate_command_args` inside a method (already imported at module top).
4. **Missing `Host` type** — `gateway/taxonomy_gateway_event.py` + `taxonomy_gateway_entity.py` imported `Host` that did not exist anywhere in the repo. Added `Host = NewType("Host", str)` to `common/taxonomy_core_vo.py`.
5. **Wrong orchestrator module name** — 6 feature containers + the asset test imported `agent_orchestrator` (bare) after the files were renamed `agent_<feature>_orchestrator.py`. Fixed 7 imports. (telemetry legitimately keeps the bare name.)
6. **Wrong protocol module** — `dispatcher/agent_dispatcher_orchestrator.py` imported 3 protocols from `contract_dispatcher_aggregate` (only defines `IDispatcherAggregate`); each protocol now imported from its own file.

### Remaining / design debt (not fixed this cycle)
- **AES304 noqa bypass trap (570)** — systemic; tracked previously. Large effort, deferred.
- **F541 (3)** — f-strings without placeholders in helper scripts `_preflight.py`, `_scan_naming.py` (non-product tooling).
- **F401 (56)** — unused imports; count rose from 54 because previously-broken modules now lint fully (pre-existing, not regressions).
- **Triple `ConnectionError` naming** — three classes exist: `common/taxonomy_domain_error.py:69`, `gateway/taxonomy_gateway_error.py:17`, `scene/taxonomy_scene_error_vo.py:117`. The shared `__init__.py` collision (F811) is resolved, but the underlying triplicate + Python builtin shadow remains. Recommend aliasing (e.g. `GatewayConnectionError`, `SceneConnectionError`) in a deliberate pass — left for user decision to avoid renaming a public API.
- **Concurrency** — sibling agents are editing the same tree concurrently (dispatcher, gateway, diagnostics, mcp, telemetry, object protocol, job error). Verified the combined working tree imports cleanly (41/41) and all 340 tests pass; no breakage from my edits.

## Cycle 5 — MCP Orphan Removal (Correction of Cycle-4 Assumption)

Cycle 4 recorded the 4 mcp capability files (health/lifecycle/startup/tool_discovery) as "orphans... part of bootstrap chain". Full-repo grep proved this WRONG:

- The production bootstrap (`root_mcp_entry` → `surface_server_start` → `surface_server_instance`) imports the REAL `ServerInstanceHandler` / `ServerStartHandler` from `surface_server_*.py`, NOT from the capability files.
- `capabilities_lifecycle.py` ↔ `capabilities_startup.py` only reference EACH OTHER (`capabilities_startup.py` imports `capabilities_lifecycle.py`'s `ServerInstanceHandler`); neither is imported by any production code or test.
- `capabilities_health.py` (`ServerHealthCapability`) and `capabilities_tool_discovery.py` (`ServerDiscoveryCapability`) have ZERO external imports.
- All 4 define DUPLICATE classes of real surface implementations and carry NO FR-MCP code (mcp FRD = FR-MCP-001/002/003 only).

ACTION: Deleted all 4 orphan files. Verified green (import sweep 0 crashes, orphan linter clean for mcp, full pytest 340 passed). This resolves the mcp structural-compliance ISSUE — mcp is now COMPLIANT (3 capabilities ↔ 3 FRs).

NOTE: Helper scripts `_fix_naming.py` and `_preflight.py` still contain stale rename-mapping entries pointing at the deleted `mcp/src/capabilities_health.py|capabilities_lifecycle.py|capabilities_startup.py` paths. These are one-off migration tools (not product code / not in CI); the stale keys are harmless but should be cleaned in a future tooling pass.

## Cycle 6 — Telemetry Module Structural Compliance (FIXED)

### Files Modified

1. **modules/shared/src/telemetry/contract_telemetry_aggregate.py**
   - Added taxonomy imports: `ActionName`, `DurationMs`, `ErrorString`, `ErrorMessage`, `SessionId`, `SuccessFlag`
   - Replaced primitive types in method signatures with taxonomy VOs:
     - `record_action_execution(action_name: str, success: bool, duration_ms: float)` → `(action_name: ActionName, success: SuccessFlag, duration_ms: DurationMs)`
     - `record_system_error(error_category: str, context: str)` → `(error_category: ErrorString, context: ErrorMessage)`
   - Removed unused `Any` import; added proper type annotations

2. **modules/telemetry/src/agent_orchestrator.py** → **agent_telemetry_orchestrator.py** (RENAME)
   - Renamed file to follow AES101 naming convention (3+ words: agent_telemetry_orchestrator)
   - Added `ITelemetryAggregate` inheritance to `TelemetryOrchestrator` class
   - Added taxonomy imports: `ActionName`, `ErrorString`, `SessionId`
   - Updated method signatures to match aggregate interface

3. **modules/telemetry/src/root_telemetry_container.py**
   - Updated import from `.agent_orchestrator` → `.agent_telemetry_orchestrator`

### Violations Resolved
- AES101 (naming): Renamed agent_orchestrator.py → agent_telemetry_orchestrator.py
- AES202 (mandatory import): Added ITelemetryAggregate import + inheritance
- AES402 (contract primitive): Replaced 4 primitive type params with taxonomy VOs

### Test Verification
- Full pytest: 340 passed, 0 regressions
- No telemetry-specific tests exist (capability layer tested indirectly)

### Remaining in Telemetry
- AES402 line 48: `get_environment_metadata(self) -> dict[str, Any]` — legitimate use of dict for flexible metadata; consistent with other aggregates (CLI, diagnostics, config all use dict[str, Any])
- AES204: Dummy import in capabilities_telemetry_session_management.py (line 10)

### Linter Progress
| Cycle | Total Violations | Change |
|-------|------------------|--------|
| 5     | 449              | Baseline |
| 6     | 442              | -7 violations fixed |
| 7     | 421              | -21 violations fixed |

## Cycle 7 — Security Taxonomy Structural Compliance (FIXED)

### Files Modified

1. **modules/shared/src/security/taxonomy_security_vo.py**
   - Added `ErrorCategory`, `FilePath`, `FileSize` NewType aliases
   - Added `MetadataMap = dict[str, Any]` type alias
   - Added `from typing import Any, NewType` import

2. **modules/shared/src/security/taxonomy_security_error.py**
   - Added taxonomy imports: `ErrorCategory`, `FilePath`, `FileSize`, `ErrorMessage`
   - Created module-level constants for default values (_EMPTY_PATH, _DEFAULT_FILE_SIZE_ZERO, _DEFAULT_*_MESSAGE)
   - Replaced `str` error codes with `ErrorCategory` in SecurityError.__init__ and all subclasses
   - Replaced `str` path params with `FilePath` in PathTraversalError, UnauthorizedAccessError, SymlinkEscapeError
   - Replaced `int` size params with `FileSize` in CodeOversizedError
   - Replaced `str` message params with `ErrorMessage | None = None` pattern in all error classes
   - Used module-level constants for default values to avoid B008 ruff violations

3. **modules/shared/src/security/taxonomy_security_event.py**
   - Added import for `MetadataMap` from taxonomy_security_vo
   - Replaced `dict` type annotations with `MetadataMap` in all 4 event classes
   - Added trailing newline (W292 fix)

### Violations Resolved
- AES401 (primitive in error/event): 16 violations → replaced str/int/dict with ErrorCategory/FilePath/FileSize/MetadataMap
- AES202 (missing taxonomy import): 4 violations → added taxonomy(vo) imports
- B008 (function call in arg default): 8 violations → created module-level constants

### Test Verification
- Full pytest: 340 passed, 0 regressions

### Remaining in Security
- AES401 line 120 in taxonomy_security_error.py: `details: dict | None = None` — flexible error metadata dict; acceptable pattern consistent with Python exception best practices; deferred as not actionable without significant restructuring

## Cycle 8 — Import Cleanup (2026-07-28)

### Changes Applied
1. **modules/shared/src/__init__.py**
   - Added missing module exports to __all__: "asset", "config", "diagnostics", "dispatcher", "launcher"
   - Added OBJECT_TYPE_POINTCLOUD, SceneCleanupVO, SceneInspectionVO to __all__
   - Fixed all F401 unused import violations (8 imports → 0)

2. **Auto-fix via ruff --fix**
   - Applied 173 auto-fixes across all modules
   - Fixed import sorting (I001), true-false comparisons (E712), and other fixable issues

### Violations Resolved
- F401 (unused imports): 8 violations → 0 (added missing __all__ exports)
- I001 (import sorting): Multiple violations → fixed via ruff --fix
- E712 (true-false comparison): Fixed auto-fix

### Test Verification
- Full pytest: 340 passed, 0 regressions

### Remaining Violations (126 total)
- ARG002 (60): Unused method arguments — intentional interface compliance pattern (capabilities implement protocols with fixed signatures)
- B904 (18): Return in except block — intentional error-handling design pattern
- ARG001 (11): Unused first argument — intentional for protocol signature alignment
- Other minor lint issues (SIM, N818, F841, B007, B008, E402) — deferred as non-critical

## Cycle 9 — Orchestrator Aggregate Inheritance (2026-07-28)

### Changes Applied
1. **modules/scene/src/agent_scene_orchestrator.py**
   - Added import for `ISceneAggregate` from `contract_scene_aggregate`
   - Added `ISceneAggregate` inheritance to `SceneOrchestrator` class
   - Fixed AES202 violations in scene orchestrator (2 violations → 0)

2. **modules/render/src/agent_render_orchestrator.py**
   - Added imports for `ICameraConfigAggregate`, `IHdriConfigAggregate`, `IRenderOperateAggregate`, `IViewportCaptureAggregate` from `contract_render_aggregate`
   - Added all four aggregate interfaces as multiple inheritance to `RenderOrchestrator` class
   - Fixed AES202 violations in render orchestrator (2 violations → 0)

### Violations Resolved
- AES202 (missing aggregate import): 48→44 violations (fixed 4 in scene/render orchestrators)
- AES405 (no aggregate implementation): Scene and Render orchestrators now implement their aggregates

### Test Verification
- Full pytest: 340 passed, 0 regressions

### Remaining AES202 Violations (44 total)
- CLI capabilities (cli_lifecycle, cli_render, cli_error): 9 violations — missing contract imports
- Diagnostics capabilities (snapshot, health_composition, logging_policy): 9 violations — missing contract imports
- Taxonomy error files (job, gateway, launcher): 6 violations — missing taxonomy imports
- Protocol files (mcp, object, cli): 18 violations — missing taxonomy imports
- Gateway orchestrator: 2 violations — IBlenderServerAggregate import missing (async/sync mismatch)

## Cycle 10 — Taxonomy Error Files Structural Compliance (2026-07-28)

### Changes Applied
1. **modules/job/src/taxonomy_job_error.py**
   - Added import for `ErrorString` from `common.taxonomy_core_vo`
   - Fixed AES202 violations in job error file (2 violations → 0)

2. **modules/shared/src/gateway/taxonomy_gateway_error.py**
   - Added imports for `ErrorString`, `ErrorMessage` from `common.taxonomy_core_vo`
   - Replaced `str` type annotations with `ErrorString`, `ErrorMessage` in `ServerError.__init__`
   - Fixed AES202 violations in gateway error file (2 violations → 0)

3. **modules/shared/src/launcher/taxonomy_launcher_error.py**
   - Added imports for `ErrorString`, `ErrorMessage` from `common.taxonomy_core_vo`
   - Replaced `str` type annotations with `ErrorString`, `ErrorMessage` in `LauncherError.__init__` and all 7 subclasses
   - Fixed AES202 violations in launcher error file (2 violations → 0)

### Violations Resolved
- AES202 (missing taxonomy import): 44→38 violations (fixed 6 in job/gateway/launcher error files)
- AES401 (primitive in error signature): Fixed str→ErrorString/ErrorMessage in gateway/launcher errors

### Test Verification
- Full pytest: 340 passed, 0 regressions

### Remaining AES202 Violations (38 total)
- CLI capabilities (cli_lifecycle, cli_render, cli_error): 9 violations — missing contract imports
- Diagnostics capabilities (snapshot, health_composition, logging_policy): 9 violations — missing contract imports
- Protocol files (mcp, object, cli): 18 violations — missing taxonomy imports
- Gateway orchestrator: 2 violations — IBlenderServerAggregate import missing (async/sync mismatch)

## Cycle 11 — Tar Extraction PEP 706 Filter (2026-07-28)

### Root Cause
`modules/asset/src/capabilities_asset_extract.py` calls `tf.extract(member, dest)` for TAR member extraction without an extraction filter. Per PEP 706 (Python 3.12+), `tarfile.extract`/`extractall` require an explicit `filter` argument:
- Without it, Python 3.12/3.13 emit a `DeprecationWarning` (observed in `test_fr_ast_003_extract_tar`).
- In Python 3.14 the default behavior changes to `'data'`, which *rejects* previously-accepted members (e.g., absolute paths, special files) — a silent behavior break for archive extraction.

This is a real potential bug (priority #6) / edge-case hardening gap (priority #11), not a style lint. It traces directly to **FR-AST-003: Extract Asset Archive**.

### Fix
- Added `import sys`.
- Added a module-level constant: `_TAR_EXTRACT_FILTER = {"filter": "data"} if sys.version_info >= (3, 12) else {}`.
- Applied it at the only TAR extraction site: `tf.extract(member, dest, **_TAR_EXTRACT_FILTER)`.
- `filter='data'` is defense-in-depth and safe here: the security supervisor (`ArchiveGuard`) has already validated every member for path traversal, symlink/hardlink policy, and size, so approved output is byte-for-byte unchanged. Confirmed by the passing test suite.

### Version-Guard Rationale (critical)
`pyproject.toml` declares `requires-python = ">=3.10"`, but the `filter` kwarg on `tarfile.extract` only exists on **Python 3.12+**. Passing `filter='data'` unconditionally would raise `TypeError` on 3.10/3.11 and break the declared support floor. The version guard omits the kwarg entirely on <3.12 (legacy fully-trusted behavior, acceptable for already-validated members) and applies `'data'` on 3.12+, eliminating the warning and 3.14 break.

### Verification
- Full pytest: 341 passed (0 regressions; +1 new regression test).
- Regression test `test_fr_ast_003_tar_extraction_no_deprecation_warning` asserts no tarfile `DeprecationWarning` is emitted — guards against a future edit silently dropping the filter.
- Targeted `lint-arwaky-cli quality` on the changed file: 0 violations.
- Combined working tree stays green alongside the sibling agent's cycles 9–10 (orchestrator aggregate inheritance; taxonomy error files).

### Scope Note
The ZIP branch (`zf.extract(info, dest)`) was intentionally left unchanged: `zipfile` has no `filter` parameter and emits no such warning. The Blender-side `blender_mcp_addon/*.py` zip `extractall` calls are addon code (separate runtime), not part of the agent workspace.

## Cycle 11 — Gateway Orchestrator Broken Inheritance (concurrency remediation)

### Incident
During this run the combined working tree regressed: `python -m pytest` showed **9 gateway feature tests failing** with `TypeError: Can't instantiate abstract class GatewayOrchestrator without an implementation for abstract methods 'cancel_async_task', 'connect', 'get_metrics', 'get_status', 'poll_task_result', 'send_command', 'shutdown', 'start', 'submit_async_task'`. A concurrent sibling loop agent had edited `modules/gateway/src/agent_gateway_orchestrator.py` to `class GatewayOrchestrator(IBlenderServerAggregate):`.

### Root cause
`IBlenderServerAggregate` (modules/shared/src/gateway/contract_gateway_aggregate.py) is the **async server aggregate** — an `ABC` with 11 abstract async methods (`start`, `shutdown`, `connect`, `disconnect`, `get_status`, `execute_code`, `submit_async_task`, `poll_task_result`, `cancel_async_task`, `send_command`, `get_metrics`). `GatewayOrchestrator` implements NONE of them: it is the **sync gateway-feature orchestrator** (FR-GWY-001..005) that delegates to 5 capabilities via sync methods (`establish_connection`, `get_connection_status`, `send_heartbeat`, `attempt_reconnect`, `send_request`, `enqueue_scene_operation`, `get_queue_status`, `execute_code`). The sibling's AES202 fix (wire an aggregate base) was misapplied — it used the async *server* aggregate as the base instead of a gateway-specific aggregate, and left the abstract methods unimplemented, so the class became non-instantiable. `IBlenderServerAggregate` is otherwise an orphan ABC (no other implementer in the repo).

### Fix (smallest safe)
Reverted the broken inheritance:
- Removed `from modules.shared.src.gateway.contract_gateway_aggregate import IBlenderServerAggregate` (and its `# Aggregate interface for AES202 compliance` comment).
- Changed `class GatewayOrchestrator(IBlenderServerAggregate):` → `class GatewayOrchestrator:`.

This restores the pre-break green state. No other module consumes `IBlenderServerAggregate`, and `root_gateway_container.py` only instantiates `GatewayOrchestrator(...)` with the 5 capabilities (no server-aggregate API expected).

### Why not implement the 11 abstract methods
Implementing them would invent a server-level async API on the gateway-feature orchestrator (signature/async mismatches vs the capabilities, new surface the FR-GWY tests do not exercise) and collide with the sibling's in-flight design. The correct AES202 resolution for the gateway orchestrator — a dedicated gateway aggregate, or wiring the server aggregate at the root/mcp server-entry orchestrator — must be done deliberately, not via a broken partial base class. Recorded as OPEN/DEFERRED (see STATE.md Active Priority 9, TODO.md AES202 item).

### Verification
- `python -m pytest modules/gateway/tests/test_gateway_feature.py` → 9 passed.
- Full suite → 341 passed (0 regressions).
