# ARWAKY LOOP ASSUMPTIONS

Key architectural assumptions, corrections, and linter behavior decisions maintained across loop cycles:

## Architecture & Workflows

* **Concurrency & Commits** : Multiple agents edit the repository concurrently. Local changes must be verified against the combined working tree without forcing auto-commits.
* **Gateway Orchestration** : `GatewayOrchestrator` must NOT inherit `IBlenderServerAggregate` (a server-level aggregate); it remains a synchronous feature orchestrator for `FR-GWY-001..005`.
* **CLI & MCP Agent Layers** : The legacy agent/capability layers for CLI and MCP were verified dead and removed (Cycles 25, 26, 28). Runtime traffic routes directly via surface handlers (`surface_*`) and the DI container (`core_agent_orchestrator`).
* **Reconnect Hardening (FR-GWY-002)** : `MaintenanceExecutor.attempt_reconnect` delegates to `ConnectionExecutor.establish_connection` to reach `FAILED` state upon retry exhaustion (Cycle 36).

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
