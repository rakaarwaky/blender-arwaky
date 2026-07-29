File: `.agents/issues/issue-job-architect-2026-07-30-120000.md`

```markdown
# Issue: job — Architectural Review & Refactoring

## Summary
The `job` feature has a mostly sound AES shape: shared contracts, taxonomy VOs/constants/errors, five capabilities, one aggregate orchestrator, and one composition root. However, the current implementation contains at least one critical layer-boundary violation (`utility_job_event_emitter.py` implements a contract and imports the contract layer), sanitization gaps where FRD-required safe storage is not enforced (`operation_type` and cancellation `reason`), agent-layer impurity/computation in `JobOrchestrator.cleanup_expired_tasks`, an orphaned/possibly missing contract export (`JobSchedulerProtocol`), and several dead-code/unused-import issues. There are also observability gaps against the FRD event catalog: `EVENT_CAPACITY_REJECTED` and `EVENT_CLEANUP_SWEEP` are defined but never emitted, and the default event emitter is not wired through diagnostics. These issues should be fixed before the job feature is considered architecturally stable for v1.7.x.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `utility_job_event_emitter.py` imports `contract_job_event_protocol.IJobEventPublisher` and implements it. Utility layer may depend only on Taxonomy and must not implement contracts. Violates AES201 and AES404. | `modules/job/src/utility_job_event_emitter.py:7-12` | Move this adapter to Capabilities as `capabilities_job_event_publisher.py`, or make it a stateless utility function without contract implementation. Prefer a Capability because it implements `IJobEventPublisher`. |
| 2 | 🔴 CRITICAL | `capabilities_job_repository.py` imports and instantiates concrete `JobEventEmitter` from a utility module. This couples a capability to a concrete event adapter and hides the dependency from the composition root. | `modules/job/src/capabilities_job_repository.py:54-72` | Require `IJobEventPublisher` via constructor injection. Wire the concrete publisher only in `root_job_container.py`. |
| 3 | 🟡 WARNING | `JobOrchestrator` imports and calls `time.time()` directly. Agent layer should orchestrate, not access system clock directly. This harms testability and violates agent purity expectations. | `modules/job/src/agent_job_orchestrator.py:cleanup_expired_tasks` | Inject a `Callable[[], Timestamp]` clock through the constructor, or move timestamp acquisition into a lower-layer service/capability. |
| 4 | 🟡 WARNING | `utility_job_transition.py` contains domain state-machine transition policy and mutates repository records. This is domain behavior, not low-level technical mechanics. | `modules/shared/src/job/utility_job_transition.py:transition_record` | Move transition policy into the lifecycle capability/repository or a dedicated domain service. Keep utility only for stateless technical helpers such as ID generation. |
| 5 | 🟢 INFO | Feature-local utility file exists under `modules/job/src/`, while the architecture recommends shared utilities live under `modules/shared/src/<domain>/`. | `modules/job/src/utility_job_event_emitter.py` | If the behavior remains an adapter, convert to Capability. If it becomes a pure helper, move to `modules/shared/src/job/`. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `utility_job_event_emitter.py` uses the `utility_` prefix but contains a stateful class implementing a contract. The name misclassifies the layer. | `modules/job/src/utility_job_event_emitter.py:12` | Rename to `capabilities_job_event_publisher.py` and class to `JobLoggingEventPublisher` or `JobEventPublisher`. |
| 2 | 🟡 WARNING | `modules/shared/src/job/__init__.py` exports `JobSchedulerProtocol`, which does not follow the contract naming convention `I<Name>Protocol`. The referenced file is also absent from the provided v1.7.0 source list. | `modules/shared/src/job/__init__.py:9` | Remove the export if unused/missing. If required, rename to `IJobSchedulerProtocol` and provide a valid contract file. |
| 3 | 🟢 INFO | `root_job_container.py` exposes `agent` and `create_job_feature()` as concrete `JobOrchestrator` instead of `IJobAggregate`. | `modules/job/src/root_job_container.py:JobContainer.agent`, `create_job_feature` | Return `IJobAggregate` to reinforce dependency inversion for consumers. |
| 4 | 🟢 INFO | `IJobEventPublisher` is not exported from `modules/shared/src/job/__init__.py`, although it is a public job-domain contract. | `modules/shared/src/job/__init__.py` | Add `IJobEventPublisher` to imports and `__all__`. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `JobSchedulerProtocol` is imported/exported by `modules/shared/src/job/__init__.py`, but `contract_job_protocol.py` is not present in the provided module source list and no implementation/caller appears in the job feature. This is either a broken import or an orphan contract. Violates AES502 if unused. | `modules/shared/src/job/__init__.py:9` | Remove the import/export unless the contract is required by an active FRD. If required, add the missing contract file and implementation. |
| 2 | 🟢 INFO | Unused import: `DeletedCount` in agent orchestrator. | `modules/job/src/agent_job_orchestrator.py:imports` | Remove `DeletedCount` from imports. |
| 3 | 🟢 INFO | Unused import: `DeletedCount` in taxonomy errors. | `modules/shared/src/job/taxonomy_job_error.py:imports` | Remove `DeletedCount` from imports. |
| 4 | 🟢 INFO | Unused import: `JOB_STATE_TIMED_OUT` in transition utility. | `modules/shared/src/job/utility_job_transition.py:imports` | Remove if not used. |
| 5 | 🟢 INFO | `capabilities_job_evaluator.py` creates a logger but never uses it. | `modules/job/src/capabilities_job_evaluator.py:logger` | Remove `logging` import and `logger` if unused. |
| 6 | 🟢 INFO | `RecordNotFoundError` and `RecordCountError` are defined but not used by the current job feature flows. | `modules/shared/src/job/taxonomy_job_error.py:RecordNotFoundError`, `RecordCountError` | Remove unless required by a documented future FRD item. |
| 7 | 🟢 INFO | `RecordCount` VO is defined but not used. | `modules/shared/src/job/taxonomy_job_vo.py:RecordCount` | Remove or use it in cleanup summary/count APIs. |
| 8 | 🟢 INFO | Constants `EVENT_CLEANUP_SWEEP` and `EVENT_CAPACITY_REJECTED` are defined but never emitted. | `modules/shared/src/job/taxonomy_job_constant.py:EVENT_CLEANUP_SWEEP`, `EVENT_CAPACITY_REJECTED` | Emit the events if required by FRD, otherwise remove the constants. FRD currently lists them, so implementation is preferred. |
| 9 | 🟢 INFO | `JobCapacityChecker.__init__` and `JobCleanupResolver.__init__` are empty `pass` constructors with no state. | `modules/job/src/capabilities_job_checker.py:__init__`, `modules/job/src/capabilities_job_resolver.py:__init__` | Remove unnecessary constructors. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | `InMemoryJobLifecycleRepository` combines persistence, transition enforcement, progress throttling, capacity counting, sanitization, and event emission. This is too many responsibilities for one capability. | `modules/job/src/capabilities_job_repository.py:InMemoryJobLifecycleRepository` | Split responsibilities: persistence adapter, transition policy, progress throttle policy, capacity counter, and event publisher. Keep repository focused on record storage and atomic mutation. |
| 2 | 🟡 WARNING | `utility_job_signaler.signal_executor()` is a placeholder that only logs. FRD requires signaling a registered execution-layer hook. There is no extension point for real executors. | `modules/shared/src/job/utility_job_signaler.py:signal_executor` | Introduce a protocol such as `IJobExecutorSignal` and implement it in a capability. Allow executor hooks to be registered through the composition root. |
| 3 | 🟡 WARNING | `JobContainer` does not wire an explicit `IJobEventPublisher`. The repository falls back to a local logging emitter. This prevents integration with diagnostics or an external event bus. | `modules/job/src/root_job_container.py:wire` | Construct and inject a diagnostics-backed or logging-backed `IJobEventPublisher` from the root. |
| 4 | 🟡 WARNING | FRD states the job feature depends on diagnostics for lifecycle event delivery, but no diagnostics integration is visible in the job module wiring. | `modules/job/src/root_job_container.py`, `modules/job/src/utility_job_event_emitter.py` | Add a diagnostics event publisher adapter and wire it as the default `IJobEventPublisher` when diagnostics is available. |
| 5 | 🟢 INFO | `JobPolicy` uses raw `int`/`float` fields. This is not necessarily an AES violation for `_vo.py`, but branded VOs would improve domain clarity. | `modules/shared/src/job/taxonomy_job_vo.py:JobPolicy` | Consider using branded VOs such as `MaxActiveTasks`, `RetentionSeconds`, `MaxRecordCount`, `StaleLifetimeSeconds`, and `ProgressThrottleSeconds`. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `create_task()` sanitizes `operation_type` into a local variable but then stores the raw unsanitized `str(command.operation_type)` via `create_record()`. This bypasses FRD-required sanitization before storage. | `modules/job/src/capabilities_job_repository.py:create_task` | Pass the sanitized `operation` value to `create_record()`. |
| 2 | 🔴 CRITICAL | Cancellation reason is sanitized only inside `JobCancellationEvaluator._evaluate_running()` for signaling, but the original `command.reason` is later stored by `InMemoryJobLifecycleRepository.apply_cancel()`. FRD requires reason sanitization before storage. | `modules/job/src/agent_job_orchestrator.py:cancel_task`, `modules/job/src/capabilities_job_repository.py:apply_cancel` | Sanitize `reason` inside `apply_cancel()` or before calling `apply_cancel()`. Prefer repository-side sanitization so storage is always safe. |
| 3 | 🟡 WARNING | `JobOrchestrator.cleanup_expired_tasks()` performs arithmetic totals and silently swallows `TaskNotFoundError` / `InvalidStateTransitionError` with `pass`. Agent layer should not compute summary metrics or silently discard errors. | `modules/job/src/agent_job_orchestrator.py:cleanup_expired_tasks` | Collect warnings for skipped stale-timeout operations and delegate summary construction to a VO factory or capability. Do not use bare `pass`. |
| 4 | 🟡 WARNING | FRD events `capacity rejected` and `cleanup sweep` are not emitted. `submit_task()` raises `CapacityError` without emitting `EVENT_CAPACITY_REJECTED`; `cleanup_expired_tasks()` does not emit `EVENT_CLEANUP_SWEEP`. | `modules/job/src/agent_job_orchestrator.py:submit_task`, `cleanup_expired_tasks` | Emit the required events through `IJobEventPublisher`, or route them through a diagnostics/event capability. Extend event taxonomy if sweep/capacity events cannot be represented by the current `JobEvent` shape. |
| 5 | 🟢 INFO | `JobEvent` requires `job_id`, but sweep and capacity-rejection events are not tied to a single job record. The current event VO may be too narrow for the FRD event catalog. | `modules/shared/src/job/taxonomy_job_event.py:JobEvent` | Introduce optional `job_id`, a separate `JobSystemEvent` VO, or a discriminated event model for aggregate/system-level events. |
| 6 | 🟢 INFO | `JobEvent` does not carry sanitized error category or cancellation reason, while FRD event payloads mention sanitized reason/category. | `modules/shared/src/job/taxonomy_job_event.py:JobEvent`, `modules/job/src/capabilities_job_repository.py:_emit` | Add optional sanitized payload fields and populate them where applicable. |

## Violations
- AES201 — CRITICAL: `modules/job/src/utility_job_event_emitter.py` imports contract-layer `IJobEventPublisher` from a utility layer.
- AES404 — MEDIUM/HIGH: `modules/job/src/utility_job_event_emitter.py` contains a stateful class and implements a contract, which is forbidden for Utility.
- AES405 — MEDIUM: `JobOrchestrator.cleanup_expired_tasks()` uses direct system time, computes summary totals, and silently discards errors.
- AES203 — MEDIUM: unused imports detected in `agent_job_orchestrator.py`, `taxonomy_job_error.py`, `utility_job_transition.py`, and `capabilities_job_evaluator.py`.
- AES502 — MEDIUM: `JobSchedulerProtocol` appears orphaned or missing; no implementation/caller is visible in the provided v1.7.0 source.
- AES501 — LOW: unused taxonomy error types and count VO candidates: `RecordNotFoundError`, `RecordCountError`, `RecordCount`.
- FRD compliance risk: sanitization before storage is not consistently enforced for `operation_type` and cancellation `reason`.
- FRD compliance risk: required lifecycle events `capacity rejected` and `cleanup sweep` are defined but not emitted.

## Action Items (For Developer)
- [ ] P0 Remove `utility_job_event_emitter.py` and replace it with a Capability-level `IJobEventPublisher` implementation.
- [ ] P0 Make `InMemoryJobLifecycleRepository` require an injected `IJobEventPublisher`; remove concrete emitter import/default.
- [ ] P0 Fix `create_task()` to store the sanitized `operation_type`.
- [ ] P0 Fix `apply_cancel()` to sanitize cancellation reason before storage.
- [ ] P1 Remove or restore `JobSchedulerProtocol` correctly. If kept, rename to `IJobSchedulerProtocol` and provide contract file plus implementation/callers.
- [ ] P1 Remove agent-layer direct `time.time()` usage by injecting a clock or moving time acquisition out of the agent.
- [ ] P1 Move cleanup summary arithmetic out of the agent, preferably into a `CleanupSummary` factory or capability-level summary builder.
- [ ] P1 Replace silent `except: pass` in cleanup with warning collection.
- [ ] P1 Emit FRD-required `EVENT_CAPACITY_REJECTED` and `EVENT_CLEANUP_SWEEP` events, or create an explicit follow-up issue if event taxonomy must be redesigned.
- [ ] P2 Wire a diagnostics-backed `IJobEventPublisher` in `JobContainer`.
- [ ] P2 Remove unused imports and unused taxonomy error/count types.
- [ ] P2 Return `IJobAggregate` from root factory/property instead of concrete `JobOrchestrator`.
- [ ] P2 Evaluate moving `utility_job_transition.py` domain transition logic into the lifecycle capability/repository.
- [ ] P3 Introduce a real executor-signaling extension point instead of the logging-only `signal_executor()` placeholder.

## Proposed Fixes / Reference Code

### 1. Replace utility event emitter with a Capability

Delete:

```text
modules/job/src/utility_job_event_emitter.py
```

Add:

```python
# modules/job/src/capabilities_job_event_publisher.py
"""Capability: Job event publisher (logging adapter).

Implements IJobEventPublisher. This is an external-adaptation capability,
not a utility, because it implements a contract and performs I/O via logging.
"""

from __future__ import annotations

import logging

from modules.shared.src.job.contract_job_event_protocol import IJobEventPublisher
from modules.shared.src.job.taxonomy_job_event import JobEvent


class JobLoggingEventPublisher(IJobEventPublisher):
    """Publishes job events through structured logging."""

    def __init__(self, logger_name: str = "BlenderMCPServer") -> None:
        self._logger = logging.getLogger(logger_name)

    def emit(self, event: JobEvent) -> None:
        self._logger.info(
            "Job event: %s job=%s state=%s op=%s",
            event.event_type,
            event.job_id,
            event.state_after,
            event.operation_type,
        )

    def __repr__(self) -> str:
        return "<JobLoggingEventPublisher>"
```

### 2. Update repository to require event publisher and fix sanitization

```python
# modules/job/src/capabilities_job_repository.py
from modules.shared.src.job.utility_job_sanitizer import (
    redact_metadata,
    sanitize_cancellation_reason,
    sanitize_error,
    sanitize_error_category,
    sanitize_operation_type,
    sanitize_progress_message,
)

# Remove:
# from modules.job.src.utility_job_event_emitter import JobEventEmitter


class InMemoryJobLifecycleRepository(IJobLifecycle):
    def __init__(
        self,
        policy: JobPolicy,
        clock: Callable[[], Timestamp],
        event_publisher: IJobEventPublisher,
        id_generator: Callable[[], JobId] | None = None,
    ) -> None:
        self._policy = policy
        self._clock = clock
        self._lock = threading.RLock()
        self._records: dict[str, JobRecord] = {}
        self._active_count: int = 0
        self._event_publisher = event_publisher

    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        operation = sanitize_operation_type(str(command.operation_type))
        if not str(operation).strip():
            raise ValidationError(ErrorString("operation_type is required"))

        metadata = redact_metadata(command.metadata)

        with self._lock:
            job_id, snapshot = create_record(
                self._records,
                str(operation),  # FIX: store sanitized operation type
                str(command.correlation_id) if command.correlation_id else None,
                metadata if metadata else {},
                self._clock,
            )
            if self._counts_toward_capacity(snapshot.state):
                self._active_count += 1

        self._emit(EVENT_TASK_CREATED, snapshot)
        return snapshot

    def apply_cancel(
        self,
        job_id: JobId,
        reason: CancellationReason | None,
    ) -> JobStatusSnapshot:
        safe_reason = sanitize_cancellation_reason(reason)  # FIX: sanitize before storage
        snapshot = self._transition(
            job_id,
            JOB_STATE_CANCELLED,
            cancellation_reason=safe_reason,
        )
        self._emit(EVENT_TASK_CANCELLED, snapshot)
        return snapshot
```

### 3. Wire event publisher from the composition root

```python
# modules/job/src/root_job_container.py
from .capabilities_job_event_publisher import JobLoggingEventPublisher


class JobContainer:
    def wire(self) -> None:
        if self._wired:
            return

        logger.info("Wiring job feature module")

        clock = self._clock or (lambda: Timestamp(time.time()))
        event_publisher = JobLoggingEventPublisher()

        lifecycle = InMemoryJobLifecycleRepository(
            policy=self._policy,
            clock=clock,
            event_publisher=event_publisher,
        )
        monitor = JobStatusMonitor()
        cancellation = JobCancellationEvaluator()
        cleanup = JobCleanupResolver()
        capacity = JobCapacityChecker()

        self._orchestrator = JobOrchestrator(
            lifecycle=lifecycle,
            monitor=monitor,
            cancellation=cancellation,
            cleanup=cleanup,
            capacity=capacity,
            policy=self._policy,
        )
        self._wired = True
```

Optional stronger typing:

```python
from modules.shared.src.job.contract_job_aggregate import IJobAggregate


class JobContainer:
    @property
    def agent(self) -> IJobAggregate:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("JobContainer not wired — call wire() first")
        return self._orchestrator


def create_job_feature(
    policy: JobPolicy | None = None,
    clock: Callable[[], Timestamp] | None = None,
) -> IJobAggregate:
    container = JobContainer(policy=policy, clock=clock)
    container.wire()
    return container.agent
```

### 4. Remove direct time import from agent and improve cleanup error handling

Minimal direction:

```python
# modules/job/src/agent_job_orchestrator.py
from collections.abc import Callable

from modules.shared.src.common.taxonomy_core_vo import JobId, Timestamp


class JobOrchestrator(IJobAggregate):
    def __init__(
        self,
        lifecycle: IJobLifecycle,
        monitor: IJobMonitor,
        cancellation: IJobCancellation,
        cleanup: IJobCleanup,
        capacity: IJobCapacity,
        policy: JobPolicy,
        clock: Callable[[], Timestamp],
    ) -> None:
        self._lifecycle = lifecycle
        self._monitor = monitor
        self._cancellation = cancellation
        self._cleanup = cleanup
        self._capacity = capacity
        self._policy = policy
        self._clock = clock

    def cleanup_expired_tasks(self) -> CleanupSummary:
        now = self._clock()
        terminal = self._lifecycle.list_terminal()
        running = self._lifecycle.list_running()

        decision = self._cleanup.resolve(terminal, running, now, self._policy)
        warnings = list(decision.warnings)

        reclaimed = 0
        for job_id in decision.stale_timeout_ids:
            try:
                self._lifecycle.apply_timeout(job_id)
                reclaimed += 1
            except (TaskNotFoundError, InvalidStateTransitionError) as exc:
                warnings.append(f"Skipped stale timeout for {job_id}: {exc}")

        purged = self._lifecycle.delete_records(decision.purge_ids)

        return CleanupSummary(
            purged=int(purged),
            retained=max(0, len(terminal) - int(purged) + int(self._lifecycle.active_count())),
            reclaimed_capacity=reclaimed,
            warnings=tuple(warnings),
        )
```

Preferred direction: move the retained-count arithmetic into a `CleanupSummary.from_counts(...)` factory or a capability-level summary builder so the agent only orchestrates.

### 5. Remove orphaned or unused contract export

```python
# modules/shared/src/job/__init__.py

# Remove:
# from .contract_job_protocol import JobSchedulerProtocol

# Remove from __all__:
# "JobSchedulerProtocol",

# Add missing public contract export:
from .contract_job_event_protocol import IJobEventPublisher

__all__ = [
    "IJobAggregate",
    "IJobCancellation",
    "IJobCapacity",
    "IJobCleanup",
    "IJobEventPublisher",
    "IJobLifecycle",
    "IJobMonitor",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_TIMED_OUT",
    "JobEvent",
]
```

### 6. Remove unused imports

```python
# modules/job/src/agent_job_orchestrator.py
# Remove DeletedCount from taxonomy_job_vo imports if unused.

# modules/shared/src/job/taxonomy_job_error.py
# Remove DeletedCount from imports if unused.

# modules/shared/src/job/utility_job_transition.py
# Remove JOB_STATE_TIMED_OUT from imports if unused.

# modules/job/src/capabilities_job_evaluator.py
# Remove logging import and logger variable if unused.
```

### 7. Remove empty constructors where unnecessary

```python
# modules/job/src/capabilities_job_checker.py
class JobCapacityChecker(IJobCapacity):
    # Remove:
    # def __init__(self) -> None:
    #     pass

    def evaluate(self, active_count: ActiveCount, policy: JobPolicy) -> CapacityDecision: ...
```

```python
# modules/job/src/capabilities_job_resolver.py
class JobCleanupResolver(IJobCleanup):
    # Remove:
    # def __init__(self) -> None:
    #     pass

    def resolve(...):
        ...
```

```

```
