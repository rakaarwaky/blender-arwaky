# ARWAKY LOOP ASSUMPTIONS

Key architectural assumptions, corrections, and linter behavior decisions maintained across loop cycles:

## Architecture & Workflows

* **Concurrency & Commits** : Multiple agents edit the repository concurrently. Local changes must be verified against the combined working tree without forcing auto-commits.
* **Gateway Orchestration** : `GatewayOrchestrator` must NOT inherit `IBlenderServerAggregate` (a server-level aggregate); it remains a synchronous feature orchestrator for `FR-GWY-001..005`.
* **CLI & MCP Agent Layers** : The legacy agent/capability layers for CLI and MCP were verified dead and removed (Cycles 25, 26, 28). Runtime traffic routes directly via surface handlers (`surface_*`) and the DI container (`core_agent_orchestrator`).
* **Reconnect Hardening (FR-GWY-002)** : `MaintenanceExecutor.attempt_reconnect` delegates to `ConnectionExecutor.establish_connection` to reach `FAILED` state upon retry exhaustion (Cycle 36).
* **Reconnect Counter Reset (FR-GWY-002, Cycle 54)** : `_reconnect_attempts` resets to 0 at the start of each new reconnect session (prior state CONNECTED, or prior session already exhausted at `max_retries`). It must NOT accumulate across drops — a stale inflated count or premature "exhaustion" on a later drop is a real bug, fixed this cycle.
* **MCP Surface Routing (Cycle 60)** : `ToolRegistryHandler.register_tools()` was broken by importing non-existent module-level names; fixed to call handler-class `register_*` static methods. The four tool handlers route to `core_agent_orchestrator` (DispatcherOrchestrator), which only exposes `execute_action` (sync) — `list_commands`/`read_skill_context`/`health_check` are NOT on it, and `execute_command` wrongly `await`s the sync `execute_action`. Left as OPEN design question (QUESTIONS.md) — not fixed autonomously to avoid changing the orchestrator's public contract during concurrent sibling edits.
* **MCP Test Naming (Cycle 60)** : pytest's `python_files = ["test_*.py"]` (pyproject.toml) means the AES skill's `contract_*`/`unit_*` test prefixes are NOT auto-collected. Prior mcp test files used those prefixes and were dead (0 collected) — renamed to `test_*` this cycle. New test files must use the `test_` prefix.

## Taxonomy & Types

* **Host Type** : Defined as `NewType("Host", str)` in common core VOs to resolve undefined type crashes in gateway taxonomy (Cycle 4).
* **ConnectionError Hierarchy** : Gateway's `ConnectionError` is kept as the single top-level re-export to resolve F811 collisions without renaming public APIs (Cycle 4).
* **Job Status Model** : `JobStatusSnapshot` is the canonical read-model; deprecated `JobStatus` factories were intentionally removed (Cycle 46).
* **Tar Extraction (FR-AST-003)** : `filter='data'` is version-guarded (`sys.version_info >= (3, 12)`) to prevent `TypeError` on Python 3.10/3.11 (Cycle 11).

## Security & Redaction (FR-SEC-004)

* **Audit Metadata** : `AuditEmitter.emit_audit` performs self-contained recursive redaction on `target_metadata` and `redacted_reason` to prevent secret leaks in log sinks (Cycle 42).
* **JSON Text Redaction** : `SensitiveRedactor` uses quoted-key regex matching (`"key": "value"`) to redact JSON payloads without duplicating `config` module dictionary rules (Cycle 43).

## Linter Behavior & False Positives

* **Orphan Flags (AES501/AES504)** : `lint-arwaky-cli` orphan flags are UNRELIABLE because cross-module imports are missed. All orphan deletion candidates MUST be verified via full-repo grep (Cycles 38, 39).
* **Barrel Re-exports (AES202)** : Barrel files intentionally aggregate protocol exports without direct taxonomy usage. Do NOT force dummy taxonomy imports as they trigger AES203/204 violations (Cycles 48, 50).
* **Linter Bugs** : Flags for AES305 (noqa missing reason on clean files) and AES302/AES403 on `capabilities_job_monitor.py` are known linter bugs; do NOT refactor clean code to satisfy them (Cycles 51, 53).
* **Signature Bypasses (AES304)** : `type: ignore` comments on protocol ABC signatures are intentional to accommodate type inheritance mismatches.
* **Full-Scan Per-File AES304 Attribution (Cycle 60)** : `lint-arwaky-cli scan .` reports per-file AES304 counts that DO NOT match a targeted `lint-arwaky-cli scan <file>`. Example: full scan attributed 15 AES304 to `capabilities_health_composition.py`, but the targeted scan reported 0 AES304 (only AES202×3 + AES403). Trust the targeted scan for per-file remediation; the full scan's per-file breakdown is unreliable (use it only for totals/category mix). The Cycle 55 "surgical AES304 widening" decision should be driven by targeted scans, not the full-scan per-file tallies.

## Cycle 55 Linter Shifts

* **W292 No Newline at EOF (Cycle 55→56)** : Increased from 8→25 violations (+17) in cycle 55, caused by sibling agent's InMemoryJobRegistry deletion leaving files without trailing newlines. FIXED in cycle 56 — added missing trailing newlines to 26 Python files (17 in modules/, 9 in blender_mcp_addon/). W292 violations reduced from 25→0.
* **AES203/AES204 Shifts (Cycle 55)** : AES203 increased 1→15 (+14), AES204 3→14 (+11). These are barrel re-export files getting re-scanned differently due to concurrent sibling agent changes. ACCEPTED as transient shifts from multi-agent editing; defer to bulk remediation strategy.
