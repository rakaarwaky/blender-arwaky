# ARWAKY LOOP TODO

## Completed Actions

* [X]  **Baseline & Structural Audit** : Ran initial test sweep, audited module FRDs, replaced stubs, and aligned capability-protocol structures for asset, scene, telemetry, security, job, and MCP modules (Cycles 1–3, 5, 6, 7, 28).
* [X]  **Imports & Linter Fixes** : Resolved critical F821/F811/F401 crashes, missing imports, and applied ruff auto-fixes (Cycles 4, 8, 14b, 22, 24, 25b, 27, 29).
* [X]  **Orchestrator Aggregate Alignment** : Added aggregate inheritance and VO type compliance across scene, render, gateway, telemetry, and MCP orchestrators (Cycles 6, 7, 9, 10, 12).
* [X]  **Unused Arguments & Exception Chaining** : Cleaned up ARG001/ARG002/ARG005 unused parameters and resolved B904 exception chaining issues (Cycles 23, 27, 28).
* [X]  **FR Traceability** : Completed FR references across all 14 capability and surface modules (Cycles 14, 31, 32).
* [X]  **Orphan & Dead Code Cleanup** : Removed unreachable CLI agent layer (Cycle 25), MCP orchestrator (Cycle 26), redundant capabilities (Cycles 20, 28), and duplicate telemetry contract (Cycle 37).
* [X]  **Security & Logic Hardening** :
  * Added PEP 706 tar extraction filtering (Cycle 11).
  * Enforced job capacity limits `FR-JOB-005` (Cycle 30).
  * Hardened gateway reconnect logic `FR-GWY-002` (Cycle 36).
  * Fixed credential leaks in `SensitiveRedactor` and `AuditEmitter` for raw, JSON, and spaced secrets `FR-SEC-004` (Cycles 41–44).
* [X]  **Performance Sweep** : Resolved 7 HIGH/MEDIUM bottlenecks (O(n²) bytes concatenation, ThreadPoolExecutor per-call instantiation, N+1 Blender calls, recursive dict depth limit) (Cycle 45).
* [X]  **Stale-Barrel Import Remediation** : Fixed broken `modules.shared/src/job`/`asset` barrel exports (JobStatus→JobStatusSnapshot, removed dead create_job_id/create_progress factories, added missing AssetSearchVO) that broke 4 test collections; full barrel `__all__` sweep clean (Cycle 46).
* [X]  **AES201 Forbidden Import Fix** : Deleted dead/orphan files (`surface_cli_command.py` with CliCommandHandler, `root_cli_entry.py`) that imported from non-existent `modules.shared.src.common.agent_di_container`. AES201 violations reduced to 0. All 451 tests pass (Cycle 49).
* [X]  **AES202 False Positive Resolution** : ACCEPTED (Cycle 48) — barrel re-export files and GatewayOrchestrator flagged for missing taxonomy imports; adding taxonomy creates AES203 violations. Documented as intentional false positives (barrel pattern + GatewayOrchestrator design).
* [X]  **Broken Barrel Export Fix** : Fixed `modules/shared/src/job/__init__.py` and `modules/shared/src/__init__.py` importing from non-existent `taxonomy_job_state_constant.py`. Corrected to `taxonomy_job_constant.py`. Recovered 4 test collection errors. Total tests: 453 (Cycle 52).

## Deferred & Pending Actions

* [ ]  **Exception Naming (N818)** : Preserve existing `ConnectionError` naming hierarchy without adding forced `Error` suffixes.
* [ ]  **Design Pattern Checks (B017/B024/ARG004)** : Retain blind assertions, abstract base classes without abstract methods, and unused protocol parameters as intentional architectural patterns.
* [ ]  **Contract & Addon Linting (AES203/AES204/AES401/AES402)** : Retain primitive getters in contracts and defer out-of-scope addon linter rules.
* [ ]  **AES502 Contract Orphan Remediation** : 58 contract protocols defined but never implemented (abandoned requirements from concurrent multi-agent editing). Verified zero FRD match, zero implementations, zero consumers. Exported from shared/src/__init__.py (public API) so removal = breaking change. Requires explicit user decision on bulk remediation strategy. Priority: Maintainability risk (Quality #10).
* [ ]  **Bulk Lint-Arwaky Remediation** : Kept deferred pending explicit user decision to prevent cascading file rename collisions with sibling agents. Current violation summary: AES304 noqa bypass (435), AES502 contract orphan (58), AES202 mandatory import (13, accepted false positives), AES401 taxonomy primitive (24), AES402 unused import (19), AES102 naming suffix mismatch (16), AES204 unused import (14), AES305 noqa missing reason (9, false positive), AES501 orphan utility (5), AES505 orphan capability (7), AES504 orphan taxonomy (7), AES101 naming prefix mismatch (6), AES405/AES403 (3). Total: 636 violations.
