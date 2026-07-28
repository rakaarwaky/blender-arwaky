# ARWAKY LOOP AUDIT

Recent Cycle Audit Records

Cycle 62 — CodeValidator Non-Strict SyntaxError Crash (FR-SEC-003)

Issue: In CodeValidator.validate_code, when ast.parse raised SyntaxError and strict_mode was False, the except branch appended a syntax_error violation but did not return. Control fell through to `for node in ast.walk(tree)` where `tree` was never bound (the parse failed), raising UnboundLocalError: cannot access local variable 'tree' where it is not associated with a value. This crashed every non-strict validation of unparseable code; the test masked it via pytest.skip.

Fix: In the non-strict SyntaxError branch, return a CodeValidationVO with the syntax_error violation (allowed=False) instead of falling through. An unparseable tree cannot be walked, so walking is skipped.

Verification: isolated import harness + full security suite — 238 passed, 0 regressions. ruff clean; lint-arwaky quality 0 on source.

Blocker (not fixed this cycle): The full project test suite cannot run because a concurrent sibling agent's in-flight scene refactor (untracked contract_scene_protocol.py; modified contract_scene_aggregate.py) imports a non-existent taxonomy_scene_vo module and uses protocol class names (ISceneInspectionProtocol/ISceneCleanupProtocol) that no longer match the aggregate's import (SceneInspectionProtocol/SceneCleanupProtocol). This breaks the modules.shared.src import chain for all consumers. Left untouched: out of scope and actively edited by a sibling; fixing risks conflicting with the sibling's completion. Recorded in QUESTIONS.md/TODO.md as an OPEN blocker.

Cycle 63 — Render Module Import Chain + Stale Tests (Quality Priority #1 broken functionality / #12 failing tests)

Issue: After the sibling's render feature commit, the full suite could not even collect — 3 render test files import non-existent classes (`CameraConfigCapability`, `HdriConfigCapability`, `RenderOperateExecutor`) and the render package's `taxonomy_constant_vo.py` was misnamed while every consumer imports `taxonomy_render_constant`. The 5 render `src` files also referenced `common.contract_code_execution_protocol` (non-existent); a concurrent sibling commit `bbc5322` already corrected those to `gateway.contract_code_execution_protocol`.

Fix: Renamed `taxonomy_constant_vo.py`→`taxonomy_render_constant.py` (its content is constants; scene convention is `taxonomy_scene_constant.py`; all 6 consumers already import `taxonomy_render_constant`) and updated 2 internal references. Rewrote the 3 stale render test files against the real executors (`RenderCameraConfigExecutor`, `RenderHdriConfigExecutor`, `RenderViewportCaptureExecutor`, `RenderSceneImageExecutor`) over a duck-typed `ICodeExecutionProtocol` mock, covering FR-RND-001..004 validation/code-gen/success/failure.

Verification: `lint-arwaky-cli quality/import` = 0 violations on render src; full suite **886 passed, 0 failures, 0 collection errors** (was 850 collected + 3 errors). The Cycle-62 scene import blocker is now auto-resolved (the sibling's committed scene refactor exposes `taxonomy_scene_vo` and matching protocol names).

Cycle 54 — FR-GWY-002 Reconnect Attempt-Counter Fix

Issue: MaintenanceExecutor shared an un-reset _reconnect_attempts counter across all reconnect sessions, causing premature exhaustion logs and inflated attempt counts on second-drop reconnects.

Fix: Added a per-session counter reset when starting a new session (prior state CONNECTED or already exhausted).

Verification: +2 regression tests (pytest modules/gateway/tests/ passed 18/18); 453 total tests passed.

Cycle 56 — W292 Trailing Newline Fix

Issue: 26 Python files left without trailing newline at EOF by sibling agent's InMemoryJobRegistry deletion, causing W292 lint violations (25 in modules/, 0 in addon initially).

Fix: Added missing trailing newlines to all 26 files (17 in modules/job/ and modules/shared/src/job/, 9 in blender_mcp_addon/).

Verification: W292 violations reduced from 25→0. Total violations: 634 (down by 25 from 659). All 453 tests pass, 0 regressions.

Cycle 60 — MCP Tool-Registry ImportError Fix (FR-MCP-001 / FR-MCP-002)

Issue: `ToolRegistryHandler.register_tools()` in `modules/mcp/src/surface_tool_registry.py` executed `from .surface_command_execute import register_execute_command` (and three similar imports). Those names are static methods on the handler classes (`CommandExecuteHandler.register_execute_command`, etc.), NOT module-level symbols — so the import raised `ImportError` at call time. `register_tools` is invoked by `surface_server_instance.get_mcp_instance()`, meaning the MCP server could never register ANY tools; the entire AI entry point was dead on startup.

Fix: Imported the handler classes and called their `register_*` static methods (`CommandExecuteHandler.register_execute_command(mcp)`, etc.).

Verification: 13 new MCP tests (tool-exposure contract + routing parity) pass; full suite 561 passed, 0 failures (also cleared Cycle 59's 3 pre-existing MCP failures). `lint-arwaky-cli quality` + `import` on the changed file: 0 violations.

Known follow-on defect (OPEN, not fixed this cycle): The four tool handlers delegate to `core_agent_orchestrator` (DispatcherOrchestrator), but that aggregate only implements `execute_action` (sync) — it does NOT expose `list_commands`, `read_skill_context`, or `health_check`. So `list_commands`/`read_skill_context`/`health_check` tools would raise `AttributeError`, and `execute_command`'s `await orchestrator.execute_action(...)` would raise `TypeError` (await on a sync method) at tool-call time. Fixing this requires a design decision on what aggregate each tool should route to (FR-MCP-002 = 1:1 parity with CLI). Recorded in QUESTIONS.md.

Cycle 53 — Job Monitor Linter Analysis (AES302/AES403)

Analysis: capabilities_job_monitor.py was flagged for missing docstrings and un-implemented protocol traits.

Finding: False positive caused by linter ABC inheritance tracking limits; methods and ABC inheritance are fully intact. Kept code untouched.

Cycle 52 — Stale Job Barrel Export Fix

Issue: modules/shared/src/job/__init__.py and modules/shared/src/__init__.py imported from non-existent taxonomy_job_state_constant.py.

Fix: Repointed imports to taxonomy_job_constant.py. Restored 4 test collection errors; 453 tests passed.

Cycle 50 — AES502 Contract Orphan Analysis

Analysis: 58 contract protocols defined in shared/src/* have no capability implementations (e.g., ExecuteActionProtocol, WorkflowProtocol, ViewportCaptureProtocol).

Finding: Confirmed as abandoned requirements not in any FRD.

Decision: DEFERRED — exported via public API shared/src/__init__.py; deletion requires explicit user strategy.

Cycle 49 — AES201 Broken Import Cleanup

Issue: Legacy dead files (surface_cli_command.py, root_cli_entry.py) imported from non-existent agent_di_container.

Fix: Deleted both unused legacy monolith files. AES201 violations reduced to 0; 451 tests passed.

Cycle 46 — Job Barrel Realignment & Linter Baseline

Issue: Sibling refactor removed JobStatus entity, breaking shared barrels and 4 test collection paths.

Fix: Realigned barrels to canonical JobStatusSnapshot read-model and removed dead create_* factories. 451 tests passed.

Scan: Established 641 total linter baseline (439 AES304 bypass comments, 58 AES502 orphans).

Cycles 41–44 — Security Redaction & Leak Fixes (FR-SEC-004)

Cycle 41: Fixed raw secret leaks in SensitiveRedactor.redact VO text field on success/failure paths.

Cycle 42: Added recursive secret masking for target_metadata and redacted_reason in AuditEmitter.emit_audit.

Cycle 43: Expanded key-based regex pattern to match JSON-quoted secret forms ("key": "value").

Cycle 44: Fixed capture-group collision in _KV_VALUE regex to ensure quoted secrets with internal spaces ("password": "my secret") are fully masked.

Known Structural Violations & Design Debt

AES101 (Naming Conventions): Orchestrators using 2-word filenames instead of agent_<feature></feature>_orchestrator.py (systemic across render, asset, gateway, etc.).

AES202 / AES405 (Aggregate & Mandatory Imports): Agent orchestrators missing explicit contract(aggregate) imports or trigger Rust-specific trait checks in Python.

AES304 (Noqa Bypass Trap): ~439 noqa / type: ignore suppressions across codebase; deferred due to large effort required.

AES401 / AES402 (Taxonomy & Contract Primitives): Direct primitive types (str, int, dict) used in exception signatures and contracts where VOs are expected.

Orphan Interfaces / Capabilities: Legacy artifacts like ViewportCapturePort and SceneCleanupProtocol retained in shared barrels to prevent breaking public exports.
