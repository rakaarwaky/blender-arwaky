# Review Plan: job — Backend Developer

## Summary

The `job` module (FR-JOB-001…005) is functionally present but architecturally
broken and partly stubbed. The `agent_job_orchestrator.py` re-implements all
business logic directly (capacity counting, progress, finalize, cancel, cleanup)
instead of delegating to the five capability classes, which themselves are
**not wired** and **do not implement their contract protocols** (AES403). The
`cleanup_expired_tasks` capability is a no-op stub, violating FR-JOB-004 and
AES303. Capacity is duplicated (tracker + agent both raise `OverflowError`
rather than the domain `CapacityError`) and the public aggregate path does not
enforce capacity atomically with creation (FR-JOB-005). Error handling uses
generic `KeyError`/`RuntimeError`/`OverflowError` instead of the FR error
categories. No thread-safety/locking exists despite FR-JOB-001/002/004
requiring atomic, thread-safe, consistent behavior.

This cycle fixes the AES layering (agent delegates via DI; capabilities
implement protocols), replaces the cleanup stub with real retention + oldest-
first eviction, centralizes domain errors in a taxonomy file, adds
thread-safety (shared `RLock`), and aligns capacity error handling to FR-JOB-005.
Out-of-scope blockers (shared taxonomy lacks timestamp fields; no execution-
layer cancel hook; no stale-timeout sweep) are documented as INFO.

## Findings by Category

### Architecture & Layer Compliance

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| A1 | 🔴 CRITICAL | Agent contains all business logic instead of orchestrating capabilities (AES405: direct capability implementation, state in agent). | `agent_job_orchestrator.py` (whole file) | Make `JobOrchestrator` implement `IJobAggregate` and delegate to injected protocol collaborators. |
| A2 | 🔴 CRITICAL | Capabilities `JobTracker`/`JobMonitor`/`JobCancel`/`JobCleanup` do not inherit their protocol ABCs (AES403 Rule 2). | `capabilities_job_*.py` | Add `JobTrackerProtocol` / `JobMonitorProtocol` / `JobCancelProtocol` / `JobCleanupProtocol` base classes. |
| A3 | 🟡 WARNING | Capabilities are never wired by the container and effectively orphans (AES503). Container only instantiates the agent. | `root_job_container.py` | Wire shared store + capabilities + enforcer into the orchestrator. |
| A4 | 🟡 WARNING | Agent imports `JobTrackerProtocol` but never uses it (AES203 unused import). | `agent_job_orchestrator.py:15` | Remove; import only what the agent uses. |
| A5 | 🟢 INFO | Capability filenames (`_tracker`, `_cancel`, `_cleanup`, `_capacity`) are not in the strict AES102 capability suffix list (only `_monitor` qualifies). Pre-existing, broad rename impact. | all `capabilities_job_*` | Rename in a coordinated future cycle touching shared imports + dispatcher. Deferred. |

### Security

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| S1 | 🟡 WARNING | Error detail / cancel reason stored without sanitization (FR-JOB-001/003: strip secrets & raw code). | `capabilities_job_tracker.finalize_task_failure`, `capabilities_job_cancel.cancel_task` | Sanitize via a shared `utility_job_sanitizer`. |

### Performance

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| P1 | 🟢 INFO | `cleanup_expired_tasks` previously iterated with no eviction; monitor deep-copies under no lock (inconsistent under concurrency). | `capabilities_job_monitor.py`, `capabilities_job_cleanup.py` | Guard store with a shared `RLock`; implement real eviction. |

### Error Handling

| # | Severity | Issue | Location | Recommendation |
| - | -------- | ----- | -------- | -------------- |
| E1 | 🟡 WARNING | Capacity rejection raises `OverflowError`; not-found raises `KeyError`; state errors raise `RuntimeError`. Does not match FR error categories. | `agent_*`, `capabilities_job_tracker.py` | Introduce `taxonomy_job_error.py` with `JobNotFoundError`/`JobStateError`/`JobCapacityError`/`JobValidationError`; raise those. |
| E2 | 🔴 CRITICAL | `capabilities_job_cleanup.cleanup_expired_tasks` is a stub (`pass` + `removed=0`), violating FR-JOB-004 and AES303. | `capabilities_job_cleanup.py:23-41` | Implement retention-duration + oldest-first count eviction; never purge active; drop corrupt records with warning. |
| E3 | 🟡 WARNING | Capacity check duplicated in tracker and agent; not atomic with creation (FR-JOB-005). | `capabilities_job_tracker.track_new_task`, `agent_*` | Centralize in the aggregate path via `JobCapacityEnforcer`; single atomic check+create under lock. |

## Violations

- AES403 (CRITICAL): 4 capability classes missing protocol inheritance (A2).
- AES405 (MEDIUM→treated CRITICAL here for loop severity): agent holds logic/state (A1).
- AES303 (HIGH): cleanup capability is a non-functional stub (E2).
- AES203 (MEDIUM): unused import in agent (A4).
- AES503 (MEDIUM): capabilities not wired by container (A3).
- AES401 (HIGH, pre-existing): domain errors defined inside capability files (`StateError`, `CapacityError`); addressed by moving to `taxonomy_job_error.py`.

## Action Items

- [ ] A1 Fix agent to implement `IJobAggregate` and delegate to injected protocols.
- [ ] A2 Make all 5 capabilities inherit their protocol ABCs.
- [ ] A3 Wire container: shared store + RLock + capabilities + enforcer.
- [ ] A4 Remove unused import from agent.
- [ ] E1 Add `taxonomy_job_error.py`; raise proper domain errors.
- [ ] E2 Implement real `cleanup_expired_tasks` (retention + oldest-first eviction, active protected, corrupt-handled).
- [ ] E3 Atomic capacity check+create in aggregate path via `JobCapacityEnforcer`.
- [ ] S1 Sanitize error detail + cancel reason via `utility_job_sanitizer`.
- [ ] Add `RLock` for atomic/thread-safe transitions and consistent snapshots.

## Fixed Code

Key shapes (full files written during Implement phase):

- `taxonomy_job_error.py`: `JobNotFoundError`, `JobStateError`, `JobCapacityError`, `JobValidationError` (all `Exception`).
- `utility_job_sanitizer.py`: `sanitize_error_detail(text: str) -> str` (strip control chars, truncate, redact secret patterns).
- `capabilities_job_tracker.py`: `class JobTracker(JobTrackerProtocol)` — capacity check removed (owned by aggregate/enforcer); `track_new_task` returns `tuple[JobId, JobStatus]` (preserves dispatcher contract at `dispatcher/capabilities_background_submit.py:77`); monotonic & bounded progress; terminal-immutable; sanitized failure detail; locked.
- `capabilities_job_monitor.py`: `class JobMonitor(JobMonitorProtocol)` — locked deepcopy snapshot.
- `capabilities_job_cancel.py`: `class JobCancel(JobCancelProtocol)` — returns `JobStatus | None`; idempotent; sanitized reason; locked.
- `capabilities_job_cleanup.py`: `class JobCleanup(JobCleanupProtocol)` — real eviction; locked.
- `capabilities_job_capacity.py`: keep `JobCapacityProtocol` impl; `CapacityError` re-exported from taxonomy.
- `agent_job_orchestrator.py`: `class JobOrchestrator(IJobAggregate)` — pure delegation; atomic capacity+create under `RLock`.
- `root_job_container.py`: wires shared store, `RLock`, capabilities, enforcer, orchestrator.
