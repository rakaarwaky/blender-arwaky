## Summary

Execute the diagnostics business analyst plan, launcher improvements, CLI utility migration, dispatcher tech lead review, telemetry security fixes, and job feature refactoring.

## Changes

### Diagnostics
- Add `DiagnosticsConfigVO` dataclass with FRD config keys (health_probe_timeout, freshness_tolerance, audit_max_buffer_size, logging_max_buffer_size)
- Wire audit/logging buffer sizes to AuditEmitter and LoggingPolicy constructors in container
- Remove unused `source_tool` parameter from `IDiagnosticsAggregate.compose_health()`
- Move probe_timeout/freshness_tolerance from compose_health args to HealthComposer constructor

### Launcher
- Add symlink normalization (`os.path.realpath`) in `ExecutableLocator._validate()`
- Add `mark_launched()` call for uptime tracking in container wiring
- Add `threading.Lock` for concurrent safety in `StatePersistence`

### CLI
- Migrate `utility_runtime_registry` and `utility_blender_process` from shared/launcher/ to CLI layer
- Update all surface commands to import from modules/cli/src/ utilities
- Update CLI unit tests to reference new utility locations

### Dispatcher (Tech Lead Review)
- Add `__enter__/__exit__` context manager to SyncDispatchExecutor for ThreadPoolExecutor cleanup
- Improve job tracker warning level and interface documentation in BackgroundSubmitExecutor
- Fix CatalogRegistrationExecutor.__repr__ typo (Catal → Catalog)

### Telemetry (Security Fixes)
- **CRITICAL**: Remove PII fields (customer_uuid, error_message, prompt_text, tool_name) from TelemetryEvent VO — FRD hard rule violation
- **CRITICAL**: Fix Protocol/Port interface mismatches across recording, classification, session, enrichment contracts
- **CRITICAL**: Remove `context: ErrorMessage` from record_system_error — eliminates PII leak
- **HIGH**: Add file-based session persistence, rotation, and consent withdrawal to TelemetrySessionManager (FR-TLM-003)
- Fix import-in-function anti-patterns (time, os), remove dead code, standardize logger names

### Asset (Phase 2 Business Analyst Findings)
- **Atomic downloads** — temp file + `os.replace()` instead of direct write
- **Concurrency control** — per-asset async locks prevent duplicate transfers
- **Workflow enforcement** — orchestrator tracks download→extract→import state
- **Event emission** — telemetry events for all 6 FRD operations
- **Config wiring** — container reads FRD config keys, falls back to defaults
- Replaced raw `str` overwrite_policy with `DuplicatePolicy` taxonomy VO
- Added integrity checksum verification in download capability
- Added stale metadata refresh in provider capability
- Magic bytes format detection in import capability
- Partial extraction cleanup on failure
- Removed unused config variables from container (F841 violations)

### Job (Phase 2 Business Analyst)
- **AES201 compliance** — Extracted `JobStateTransitor` from capabilities layer to shared utility (`modules/shared/src/job/utility_job_transition.py`)
- **Stateless functions** — `validate_transition`, `create_record`, `transition_record`, `count_active` replace stateful class composition
- **Cross-capability import removed** — `capabilities_job_repository.py` no longer imports from `capabilities_job_transitor.py`
- **AES303 compliance** — Removed empty `__init__` methods from `JobCancellationEvaluator` and `JobStatusMonitor`
- **Deleted** `capabilities_job_transitor.py` (replaced by shared utility)

## Verification

- 41 telemetry tests passing — no regressions
- 59 dispatcher tests passing — no regressions
- 121 diagnostics tests passing — no regressions
- 85 asset tests passing — no regressions
- 110 job feature tests passing — no regressions
