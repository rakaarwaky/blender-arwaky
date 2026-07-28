# ARWAKY LOOP TODO

Next concrete actions (filled by the loop):

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

## Deferred & Pending Actions

* [ ]  **Exception Naming (N818)** : Preserve existing `ConnectionError` naming hierarchy without adding forced `Error` suffixes.
* [ ]  **Design Pattern Checks (B017/B024/ARG004)** : Retain blind assertions, abstract base classes without abstract methods, and unused protocol parameters as intentional architectural patterns.
* [ ]  **Contract & Addon Linting (AES203/AES204/AES401/AES402)** : Retain primitive getters in contracts and defer out-of-scope addon linter rules.
* [ ]  **Bulk Lint-Arwaky Remediation** : Kept deferred pending explicit user decision to prevent cascading file rename collisions with sibling agents.
