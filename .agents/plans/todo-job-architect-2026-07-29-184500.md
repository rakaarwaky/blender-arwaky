# Review Plan: job — Architect (Phase 1)

## Summary
Analysis of the `job` feature module against FRD requirements and AES 7-layer constraints. The job module implements a background task tracking system with a clean 5-capability architecture wired through an orchestrator and container. Five CRITICAL/WARNING issues found: primitive types in contract protocols (AES 402), primitives in error constructors (AES 401), `object` type annotations in capability layer, and monolithic repository class exceeding single-responsibility boundaries. All files pass linter scan otherwise.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| J1 | 🟡 WARNING | `IJobCapacity.evaluate()` uses primitive `int` for `active_count` parameter instead of branded type | `contract_job_capacity_protocol.py:11` | Define `ActiveCount` NewType in taxonomy; use `ActiveCount` instead of `int` |
| J2 | 🟡 WARNING | `IJobLifecycle.delete_records()` returns primitive `int` instead of branded type | `contract_job_lifecycle_protocol.py:41` | Define `DeletedCount` NewType; return `DeletedCount` instead of `int` |
| J3 | 🟡 WARNING | `InMemoryJobLifecycleRepository._transition()` uses `object | None` for `result_url` and `progress_message` parameters | `capabilities_job_repository.py:217-218` | Use proper domain types (`ResultUrl | None`, `ProgressMessage | None`) instead of `object | None` |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| N1 | 🟢 INFO | `JobStatusMonitor.__init__()` has empty body with `pass` — violates AES303 sub-check 2 (dead definition) | `capabilities_job_monitor.py:17-18` | Remove empty `__init__` or add meaningful initialization |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| O1 | 🟢 INFO | `JobEvent` taxonomy event defined in `taxonomy_job_event.py` but never imported by any capability, agent, or surface file | `taxonomy_job_event.py` | Either wire into lifecycle `_emit` method or mark as deferred for future telemetry integration |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| S1 | 🟡 WARNING | `InMemoryJobLifecycleRepository` is monolithic — handles 12 protocol methods across create/start/progress/complete/fail/cancel/timeout/get/list/delete/count operations | `capabilities_job_repository.py` | Consider splitting into separate repositories: `ITaskCreationRepository`, `ITaskStateRepository`, `ITaskQueryRepository` |
| S2 | 🟢 INFO | `JobCapacityChecker` and `JobCleanupResolver` are stateless single-method classes — could be utility functions instead of capabilities | `capabilities_job_checker.py`, `capabilities_job_resolver.py` | Extract to utility layer if they don't need protocol abstraction for mocking |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| D1 | 🟢 INFO | `_emit()` in repository writes directly to logger instead of emitting through a dedicated event bus protocol | `capabilities_job_repository.py:237` | Wire an event bus capability and delegate emission through it for decoupling |

## Violations
1. **AES 402 HIGH** — `IJobCapacity.evaluate()` uses primitive `int` for `active_count` instead of branded type
2. **AES 402 HIGH** — `IJobLifecycle.delete_records()` returns primitive `int` instead of branded type
3. **AES 402 HIGH** — `IJobLifecycle.active_count()` returns primitive `int` instead of branded type
4. **AES 401 HIGH** — `CapacityError.__init__()` uses `int` params (max_active, current_active) instead of branded types
5. **AES 401 HIGH** — `TaskNotFoundError.__init__()` uses `str` param (task_id) instead of `JobId` type
6. **AES 401 HIGH** — `InvalidStateTransitionError.__init__()` uses `str` params (from_state, to_state) instead of `JobState` type

## Action Items
- ✅ P0 FIX AES 402: Define `ActiveCount`, `DeletedCount`, `RecordCount` NewTypes in taxonomy_job_vo.py; update contract protocols (completed, 95 tests pass)
- ✅ P0 FIX AES 401: Replace primitive params in error constructors with branded types (JobId, JobState)
- ✅ P1 FIX S1: Split `InMemoryJobLifecycleRepository` — extracted `JobStateTransitor` for state transition logic (95 tests pass)
- ✅ P1 FIX J3: Replace `object | None` annotations in `_transition()` with proper domain types (completed during P0)
- ✅ P2 FIX N1: Remove empty `__init__` from `JobStatusMonitor`
- ✅ P3 FIX O1: Wire `JobEvent` into lifecycle emission through event bus protocol (created IJobEventPublisher protocol + JobEventEmitter default impl)
- ⏸️ P3 FIX S2: Deferred — evaluation below. Both classes are stateless single-method implementations of protocol interfaces. Keeping as capabilities preserves mocking capability and layer boundaries. Moving to utilities would simplify usage but reduce test isolation. Recommendation: keep current structure; extract private helpers (`_resolve_stale`, `_resolve_expired`, `_enforce_max`) to utility functions if needed.

## Fixed Code

### File: `modules/shared/src/job/taxonomy_job_vo.py` — Add branded count types

After existing NewType definitions, add:
```python
# ─── Count Types ──────────────────────────────────────────────────────────────
ActiveCount = NewType("ActiveCount", int)
DeletedCount = NewType("DeletedCount", int)
RecordCount = NewType("RecordCount", int)
```

### File: `modules/shared/src/job/contract_job_capacity_protocol.py` — Fix AES 402

```python
class IJobCapacity(ABC):
    @abstractmethod
    def evaluate(self, active_count: ActiveCount, policy: JobPolicy) -> CapacityDecision: ...
```

### File: `modules/shared/src/job/contract_job_lifecycle_protocol.py` — Fix AES 402

```python
class IJobLifecycle(ABC):
    @abstractmethod
    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def start_task(self, job_id: JobId) -> JobStatusSnapshot: ...
    @abstractmethod
    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot: ...
    @abstractmethod
    def apply_cancel(self, job_id: JobId, reason: CancellationReason | None) -> JobStatusSnapshot: ...
    @abstractmethod
    def apply_timeout(self, job_id: JobId) -> JobStatusSnapshot: ...
    @abstractmethod
    def get_record(self, job_id: JobId) -> JobStatusSnapshot: ...
    @abstractmethod
    def list_terminal(self) -> tuple[JobStatusSnapshot, ...]: ...
    @abstractmethod
    def list_running(self) -> tuple[JobStatusSnapshot, ...]: ...
    @abstractmethod
    def delete_records(self, job_ids: tuple[JobId, ...]) -> DeletedCount: ...
    @abstractmethod
    def active_count(self) -> ActiveCount: ...
```

### File: `modules/shared/src/job/taxonomy_job_error.py` — Fix AES 401

```python
class CapacityError(JobError):
    """Raised when background capacity is exceeded."""

    def __init__(self, max_active: ActiveCount, current_active: ActiveCount) -> None:
        message = ErrorString(
            f"Background capacity exceeded: {current_active}/{max_active} active tasks"
        )
        super().__init__(message)
        self.max_active = max_active
        self.current_active = current_active


class TaskNotFoundError(JobError):
    """Raised when a requested task ID is not found."""

    def __init__(self, task_id: JobId) -> None:
        message = ErrorString(f"Task {task_id} not found")
        super().__init__(message)
        self.task_id = task_id


class InvalidStateTransitionError(JobError):
    """Raised when a state transition is not allowed."""

    def __init__(self, from_state: JobState, to_state: JobState) -> None:
        message = ErrorString(f"Invalid state transition: {from_state} -> {to_state}")
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state
```

### File: `modules/job/src/capabilities_job_repository.py` — Fix object annotations in _transition

Replace:
```python
def _transition(
    self,
    job_id: JobId,
    target: JobState,
    *,
    result_url: object | None = None,
    error: ErrorString | None = None,
    error_category: ErrorCategory | None = None,
    cancellation_reason: CancellationReason | None = None,
    progress_message: object | None = None,
) -> JobStatusSnapshot:
```

With:
```python
def _transition(
    self,
    job_id: JobId,
    target: JobState,
    *,
    result_url: ResultUrl | None = None,
    error: ErrorString | None = None,
    error_category: ErrorCategory | None = None,
    cancellation_reason: CancellationReason | None = None,
    progress_message: ProgressMessage | None = None,
) -> JobStatusSnapshot:
```

And add import:
```python
from modules.shared.src.job.taxonomy_job_vo import (
    ...
    ProgressMessage,
    ResultUrl,
    ...
)
```

### File: `modules/job/src/capabilities_job_monitor.py` — Remove empty __init__

Remove lines 17-18:
```python
    def __init__(self) -> None:
        pass
```
