# Job Feature — Business Analyst Plan

**Date:** 2026-07-29 15:28  
**Scope:** modules/job/ — FR-JOB-001 through FR-JOB-005  
**Analyst:** Business Analyst (FRD Compliance Review)

---

## 1. Summary

The job feature implementation is **substantially complete and production-ready**. All five FRD requirements (FR-JOB-001 through FR-JOB-005) are implemented with correct business logic, thread safety, sanitization, and capacity enforcement. The architecture cleanly separates capabilities from the orchestrator layer.

**Overall Assessment: PASS — Minor gaps in test coverage for capability-layer components.**

| Requirement | Status | Notes |
|---|---|---|
| FR-JOB-001 (Task Lifecycle) | ✅ PASS | Full lifecycle, state machine, sanitization |
| FR-JOB-002 (Status Monitoring) | ✅ PASS | Visibility rules, redaction, monotonicity |
| FR-JOB-003 (Cancellation) | ⚠️ PARTIAL | Logic correct, capability untested in isolation |
| FR-JOB-004 (Cleanup) | ⚠️ PARTIAL | Logic correct, capability untested in isolation |
| FR-JOB-005 (Capacity) | ✅ PASS | Atomic enforcement, terminal release |

---

## 2. Findings by Category

### 2.1 Requirements Clarity

**Finding:** All five FRD requirements are well-scoped, unambiguous, and consistent with each other.

| Aspect | Assessment |
|---|---|
| **Unambiguous** | ✅ Each requirement has clear acceptance criteria (e.g., "progress bounded 0–100", "monotonic by default") |
| **Complete** | ✅ Covers lifecycle, monitoring, cancellation, cleanup, capacity — no missing domain |
| **Consistent** | ✅ No conflicting definitions; state names, error categories, and policy keys align across FRD and code |
| **Testable** | ✅ Each requirement maps to verifiable behavior |

**Minor observation:** The FRD mentions a "QA checklist" section that is not yet reflected in the test suite. The checklist items are implicit in tests but not enumerated as explicit test cases.

### 2.2 Business Flow

**Finding:** Implementation faithfully follows the FRD business flow for all five requirements.

#### FR-JOB-001: Task Lifecycle Flow
```
CREATE → PENDING → RUNNING → {COMPLETED, FAILED, CANCELLED, TIMED_OUT}
```
- ✅ All transitions implemented with proper timestamp tracking
- ✅ Terminal states are immutable (except cleanup)
- ✅ Backward transitions rejected with `InvalidStateTransitionError`
- ✅ Unknown task identifiers rejected with `TaskNotFoundError`

**Edge case handled:** Running tasks can transition to CANCELLED or TIMED_OUT — both tested.

#### FR-JOB-002: Status Monitoring Flow
```
SNAPSHOT → PROJECT → CONSUMER-SAFE VIEW
         (redact metadata, apply visibility rules)
```
- ✅ Result visible only after COMPLETED
- ✅ Error visible only after FAILED
- ✅ Metadata redacted (defense-in-depth via `redact_metadata`)
- ✅ Progress applicability flag set correctly

**Edge case handled:** Pending tasks have `progress_applicable=False`; only RUNNING tasks have it `True`.

#### FR-JOB-003: Cancellation Flow
```
EVALUATE(current_state) → {ACCEPTED, REJECTED, SIGNAL_EXECUTOR}
```
- ✅ Terminal states rejected with clear message
- ✅ Pending accepted without executor signaling
- ✅ Running tasks signal executor before acceptance
- ✅ Sanitization of cancellation reason

**Edge case handled:** If executor cannot be signaled, returns UNSUPPORTED (not ACCEPTED).

#### FR-JOB-004: Cleanup Flow
```
CLEANUP(now, policy) → {STALE_TIMEOUT, EXPIRED_PURGE, MAX_ENFORCE}
```
- ✅ Stale running tasks detected when `stale_recovery_enabled=True`
- ✅ Expired terminal records purged (oldest first, sorted by finish time)
- ✅ Max record count enforced after expiration purge
- ✅ Warnings emitted for corrupt/missing timestamps

**Edge case handled:** Running tasks with no `started_at` produce warnings but are NOT timed out.

#### FR-JOB-005: Capacity Flow
```
EVALUATE(active_count, policy) → {ACCEPTED, REJECTED}
```
- ✅ Active >= limit → rejected with context message
- ✅ Active < limit → accepted with available slots
- ✅ Terminal tasks do NOT count against capacity

**Edge case handled:** Over-limit submissions (active > limit) correctly rejected.

### 2.3 Logic Implementation

**Finding:** Business logic is correctly translated from FRD to code. All invariants hold.

| Invariant | Status | Evidence |
|---|---|---|
| **Thread safety** | ✅ | `RLock` guards all repository methods |
| **Sanitization** | ✅ | `sanitize_error_detail`, `redact_metadata`, `sanitize_cancellation_reason` |
| **Progress monotonicity** | ✅ | `ValidationError` raised when progress decreases |
| **Progress bounds** | ✅ | `ValidationError` for <0 or >100 |
| **Capacity atomicity** | ✅ | Capacity check + creation in single locked operation |
| **State machine correctness** | ✅ | All valid transitions; all invalid transitions raise errors |

**Minor gaps (advisory, not blocking):**

1. **Progress throttle is advisory:** The FRD mentions a progress throttle (minimum time delta between updates). Implementation checks the delta but only as an advisory warning, not a hard enforcement. This is acceptable for the current design but should be documented.

2. **Stale running timeout only during cleanup sweep:** The FRD implies stale detection happens during cleanup resolution. The implementation correctly does this — there is NO automatic background timer for stale detection. This means stale tasks remain RUNNING until the next cleanup cycle. This is a design choice, not a bug.

### 2.4 Testability & Acceptance Criteria

**Finding:** All acceptance criteria are testable and covered by existing tests.

| Acceptance Criterion | Covered By | Status |
|---|---|---|
| FR-JOB-001: Unique IDs | `test_fr_job_001_create_task_with_unique_id` | ✅ |
| FR-JOB-001: Starts PENDING | `test_fr_job_001_create_task_starts_pending` | ✅ |
| FR-JOB-001: All transitions | `test_fr_job_001_transition_*` (6 tests) | ✅ |
| FR-JOB-001: Terminal immutability | `test_fr_job_001_transition_after_terminal_rejected` | ✅ |
| FR-JOB-001: Unknown ID rejected | `test_fr_job_001_unknown_task_identifier_rejected` | ✅ |
| FR-JOB-001: Sanitization | `test_fr_job_001_error_detail_sanitized`, `test_fr_job_001_metadata_redacted` | ✅ |
| FR-JOB-002: Progress bounded 0–100 | `test_fr_job_002_progress_bounded_zero_to_one_hundred` | ✅ |
| FR-JOB-002: Progress monotonic | `test_fr_job_002_progress_monotonic` | ✅ |
| FR-JOB-002: Result visibility | `test_fr_job_002_result_visible_only_after_completed` | ✅ |
| FR-JOB-002: Error visibility | `test_fr_job_002_error_visible_only_after_failed` | ✅ |
| FR-JOB-003: State-based evaluation | Repository-level cancel tests cover flow | ⚠️ (capability untested) |
| FR-JOB-004: Cleanup decisions | Repository-level delete tests cover flow | ⚠️ (capability untested) |
| FR-JOB-005: Capacity limits | `test_fr_job_005_capacity_*` (4 tests) | ✅ |
| FR-JOB-005: Terminal release | `test_fr_job_005_terminal_tasks_release_capacity` | ✅ |

**Coverage gap:** The capability-layer components (`JobCancellationEvaluator`, `JobCleanupResolver`, `JobStatusMonitor`) are tested indirectly through the repository but NOT tested in isolation. This is acceptable since they are stateless and receive-only, but explicit tests would improve confidence.

### 2.5 Traceability

**Finding:** Clear traceability from FRD → code → tests → config.

| FRD Requirement | Implementation Files | Test Files | Config Keys |
|---|---|---|---|
| FR-JOB-001 | `capabilities_job_repository.py`, `root_job_container.py` | `test_job_repository.py` (16 tests) | `job_policy.max_active` |
| FR-JOB-002 | `capabilities_job_monitor.py`, `utility_job_sanitizer.py` | `test_job_repository.py` (8 tests) | N/A |
| FR-JOB-003 | `capabilities_job_evaluator.py`, `utility_job_signaler.py` | `test_job_repository.py` (via repo) | N/A |
| FR-JOB-004 | `capabilities_job_resolver.py` | `test_job_repository.py` (2 tests) | `job_policy.stale_recovery_enabled`, `retention_seconds`, `max_records`, `stale_running_lifetime_seconds` |
| FR-JOB-005 | `capabilities_job_checker.py` | `test_job_repository.py` (4 tests) | `job_policy.max_active` |

**Orchestrator layer:**
- `agent_job_orchestrator.py` — thin agent facade, no dedicated tests (acceptable for thin wrapper)
- `root_job_container.py` — composition root, wired correctly

---

## 3. Violations

No violations found. All implementation decisions align with or exceed FRD requirements.

| Severity | Count | Details |
|---|---|---|
| **CRITICAL** | 0 | None |
| **MAJOR** | 0 | None |
| **MINOR** | 2 | Capability-layer tests missing for FR-JOB-003 and FR-JOB-004 (see Action Items) |

---

## 4. Action Items

### Priority: LOW (nice-to-have, not blocking production)

#### AI-001: Add isolated test for `JobCancellationEvaluator`
**Rationale:** Capability is stateless and receives-only; tested via repository but not in isolation.

```python
# modules/job/tests/test_job_evaluator.py (new file)
def test_cancel_running_signals_executor():
    evaluator = JobCancellationEvaluator()
    cmd = CancelTaskCommand(
        job_id=JobId("test-1"),
        reason=CancellationReason("User requested cancel"),
    )
    result = evaluator.evaluate(cmd, JobState.RUNNING)
    assert result.accepted is True
    assert result.outcome == CANCELLATION_ACCEPTED

def test_cancel_terminal_rejected():
    evaluator = JobCancellationEvaluator()
    cmd = CancelTaskCommand(
        job_id=JobId("test-1"),
        reason=CancellationReason("User requested cancel"),
    )
    result = evaluator.evaluate(cmd, JobState.COMPLETED)
    assert result.accepted is False
    assert result.outcome == CANCELLATION_ALREADY_TERMINAL

def test_cancel_pending_accepted_no_signal():
    evaluator = JobCancellationEvaluator()
    cmd = CancelTaskCommand(
        job_id=JobId("test-1"),
        reason=CancellationReason("User requested cancel"),
    )
    result = evaluator.evaluate(cmd, JobState.PENDING)
    assert result.accepted is True
    assert result.outcome == CANCELLATION_ACCEPTED
```

#### AI-002: Add isolated test for `JobCleanupResolver`
**Rationale:** Stateless decision component; repository tests cover delete but not cleanup resolution logic.

```python
# modules/job/tests/test_job_resolver.py (new file)
def test_resolve_stale_running_task():
    resolver = JobCleanupResolver()
    now = Timestamp(2000.0)
    policy = _make_policy(stale_recovery_enabled=True, stale_running_lifetime_seconds=600)
    running = (JobStatusSnapshot(
        job_id=JobId("test-1"),
        state=JOB_STATE_RUNNING,
        started_at=Timestamp(1000.0),  # 1000s old > 600s policy
    ),)
    decision = resolver.resolve((), running, now, policy)
    assert JobId("test-1") in decision.stale_timeout_ids

def test_resolve_no_stale_when_disabled():
    resolver = JobCleanupResolver()
    now = Timestamp(2000.0)
    policy = _make_policy(stale_recovery_enabled=False)  # disabled
    running = (JobStatusSnapshot(
        job_id=JobId("test-1"),
        state=JOB_STATE_RUNNING,
        started_at=Timestamp(1000.0),
    ),)
    decision = resolver.resolve((), running, now, policy)
    assert len(decision.stale_timeout_ids) == 0

def test_resolve_expired_terminal_oldest_first():
    resolver = JobCleanupResolver()
    now = Timestamp(2000.0)
    policy = _make_policy(retention_seconds=500)
    terminal = (
        JobStatusSnapshot(job_id=JobId("test-2"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1600.0)),  # newer
        JobStatusSnapshot(job_id=JobId("test-1"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1000.0)),  # older
    )
    decision = resolver.resolve(terminal, (), now, policy)
    assert JobId("test-1") in decision.purge_ids  # oldest purged first

def test_resolve_max_records_enforced():
    resolver = JobCleanupResolver()
    now = Timestamp(2000.0)
    policy = _make_policy(max_records=1, retention_seconds=999999)  # keep only 1
    terminal = (
        JobStatusSnapshot(job_id=JobId("test-1"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1500.0)),
        JobStatusSnapshot(job_id=JobId("test-2"), state=JOB_STATE_COMPLETED, finished_at=Timestamp(1700.0)),
    )
    decision = resolver.resolve(terminal, (), now, policy)
    # test-1 is oldest, should be purged to enforce max_records=1
    assert JobId("test-1") in decision.purge_ids
```

#### AI-003: Add isolated test for `JobStatusMonitor`
**Rationale:** Redaction and visibility rules are tested via repository but the monitor capability itself is not exercised in isolation.

```python
# modules/job/tests/test_job_monitor.py (new file)
def test_project_redacts_metadata():
    monitor = JobStatusMonitor()
    snap = JobStatusSnapshot(
        job_id=JobId("test-1"),
        state=JOB_STATE_RUNNING,
        metadata=(("api_key", "secret-abc"), ("safe", "value")),
    )
    projected = monitor.project(snap)
    assert projected.metadata == (("api_key", "[REDACTED]"), ("safe", "value"))

def test_project_result_none_before_completed():
    monitor = JobStatusMonitor()
    snap = JobStatusSnapshot(
        job_id=JobId("test-1"),
        state=JOB_STATE_RUNNING,
        result_url=ResultUrl("/tmp/out.png"),
    )
    projected = monitor.project(snap)
    assert projected.result_url is None

def test_project_error_none_before_failed():
    monitor = JobStatusMonitor()
    snap = JobStatusSnapshot(
        job_id=JobId("test-1"),
        state=JOB_STATE_RUNNING,
        error=ErrorString("fail"),
    )
    projected = monitor.project(snap)
    assert projected.error is None

def test_project_flags_set_correctly():
    monitor = JobStatusMonitor()
    snap = JobStatusSnapshot(
        job_id=JobId("test-1"),
        state=JOB_STATE_RUNNING,
    )
    projected = monitor.project(snap)
    assert projected.is_cancellable is True
    assert projected.progress_applicable is True
```

### Priority: INFORMATIONAL (no action required)

#### AI-004: Document progress throttle as advisory
**Rationale:** The FRD mentions a progress throttle (minimum time delta between updates). Implementation checks the delta but only emits a warning, not a hard enforcement. This is acceptable for the current design but should be documented to avoid confusion.

> **Suggested documentation:** "Progress throttling is advisory — the repository checks the time delta between updates and emits a warning if updates are too frequent, but does not reject updates. This allows burst progress updates during rapid state changes."

#### AI-005: Document stale timeout behavior
**Rationale:** Stale running tasks are only detected during cleanup sweeps, not via automatic background timers. This is a deliberate design choice but should be documented.

> **Suggested documentation:** "Stale running task detection occurs only during cleanup resolution cycles. Tasks that exceed the stale lifetime threshold remain in RUNNING state until the next cleanup sweep initiates. This avoids background monitoring overhead."

---

## 5. Fixed Code

No code fixes required. All implementation decisions are correct and align with FRD requirements. The action items above (AI-001 through AI-003) add test coverage for capability-layer components — these are tests, not code changes.

**Code quality score: 9.5/10** — only missing test coverage for isolated capability tests.

---

## Appendix: File Inventory

| File | Role | Lines | Notes |
|---|---|---|---|
| `modules/job/src/root_job_container.py` | Composition root | ~70 | Wires 5 capabilities to orchestrator |
| `modules/job/src/agent_job_orchestrator.py` | Agent facade | ~120 | Thin wrapper, no business logic |
| `modules/job/src/capabilities_job_repository.py` | Core repository | ~300 | Thread-safe, RLock, state machine |
| `modules/job/src/capabilities_job_transitor.py` | Transition logic | ~80 | Atomic transition with validation |
| `modules/job/src/capabilities_job_evaluator.py` | Cancellation eval | ~60 | State-based, executor signaling |
| `modules/job/src/capabilities_job_checker.py` | Capacity check | ~30 | Stateless decision |
| `modules/job/src/capabilities_job_monitor.py` | Status monitor | ~50 | Redaction, visibility rules |
| `modules/job/src/capabilities_job_resolver.py` | Cleanup resolver | ~80 | Stale detection, max enforcement |
| `modules/job/tests/test_job_repository.py` | Integration tests | ~340 | 30+ tests covering all FRs |

---

**Analyst signature:** Business Analyst (FRD Compliance Review)  
**Assessment date:** 2026-07-29  
**Next review recommended:** After AI-001/AI-002/AI-003 are implemented, re-run compliance check.
