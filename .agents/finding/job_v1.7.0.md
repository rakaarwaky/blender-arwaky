# Module: job (v1.7.0)

This document contains the source code for module `job` along with related and imported definitions from the `shared` module.

## File List

- [ARCHITECTURE.md](<ARCHITECTURE.md>)
- [modules/job/FRD.md](<modules/job/FRD.md>)
- [modules/job/pyproject.toml](<modules/job/pyproject.toml>)
- [modules/job/src/__init__.py](<modules/job/src/__init__.py>)
- [modules/job/src/agent_job_orchestrator.py](<modules/job/src/agent_job_orchestrator.py>)
- [modules/job/src/root_job_container.py](<modules/job/src/root_job_container.py>)
- [modules/shared/src/common/__init__.py](<modules/shared/src/common/__init__.py>)
- [modules/shared/src/common/taxonomy_core_vo.py](<modules/shared/src/common/taxonomy_core_vo.py>)
- [modules/shared/src/job/__init__.py](<modules/shared/src/job/__init__.py>)
- [modules/shared/src/job/contract_job_aggregate.py](<modules/shared/src/job/contract_job_aggregate.py>)
- [modules/shared/src/job/taxonomy_job_error.py](<modules/shared/src/job/taxonomy_job_error.py>)
- [modules/shared/src/job/taxonomy_job_state_constant.py](<modules/shared/src/job/taxonomy_job_state_constant.py>)
- [modules/shared/src/job/taxonomy_job_status_entity.py](<modules/shared/src/job/taxonomy_job_status_entity.py>)
- [pyproject.toml](<pyproject.toml>)
- [README.md](<README.md>)

---

## File: ARCHITECTURE.md

````markdown
# Agentic Engineering System Architecture

## 1. Purpose

The Agentic Engineering System is a layered, AI-native architecture pattern. It keeps domain models stable, business logic readable, technical detail isolated, and layer boundaries explicit enough for both humans and AI agents to modify the system safely.

---

## 2. Workspace Organization

The architecture supports multi-language workspaces.

| Term               | Meaning                                                           |
| ------------------ | ----------------------------------------------------------------- |
| Project Workspaces | Project root containing all configuration and language members    |
| Workspace Member   | One self-contained crate, package, or module inside the workspace |
| Crates directory   | Rust workspace members                                            |
| Packages directory | TypeScript or JavaScript packages                                 |
| Modules directory  | Python modules or sub-projects                                    |

---

## 3. Naming Convention

File names must communicate three parts:

1. Layer as prefix
2. Concern as middle name
3. Role as suffix

The parts are joined by underscores, followed by the normal file extension for the language.

`layer_concern_role.rs/py/ts`

---

## 4. Vertical Slicing Folder Structure

The recommended folder structure follows this order:

#### Features member

_Example feature crate `crates|packages|modules/<name-features>/`_

```text
surface_<concern>_<role>.rs/py/ts                ← surface layer
capabilities_<concern>_<role>.rs/py/ts           ← capabilities layer
agent_<concern>_orchestrator.rs/py/ts            ← agent layer
```

Exceptions: `main.rs`, `lib.rs`, `mod.rs`, `__init__.py`, `index.ts`, `index.js`.

#### Shared member

`crates|packages|modules/shared/<common>or<domain-folder>`

```text
contract_<concern>_protocol.rs/py/ts             ← contract layer
contract_<concern>_aggregate.rs/py/ts            ← contract layer
taxonomy_<concern>_vo.rs/py/ts                   ← taxonomy layer
taxonomy_<concern>_event.rs/py/ts                ← taxonomy layer
taxonomy_<concern>_entity.rs/py/ts               ← taxonomy layer
taxonomy_<concern>_constant.rs/py/ts             ← taxonomy layer
utility_<concern>_<role>.rs/py/ts                ← utility layer
```

`shared` folder groups by domain. Use `shared/common/` for generic files.

---

## 5. Taxonomy Layer

### Purpose

Taxonomy is the domain foundation layer. It defines the stable language of the domain and must remain free from technical or behavioral concerns.

### Components

| Role         | Meaning                               |
| ------------ | ------------------------------------- |
| Value object | Immutable data concept                |
| Entity       | Stateful domain concept with identity |
| Event        | Immutable domain fact                 |
| Error        | Domain-level error                    |
| Constant     | Compile-time literal value            |

### Dependencies

Taxonomy depends on nothing.

### Special Rules

- Value objects and Constants may use all primitive types.
- Entities, Events, and Errors must use Value objects/Constants instead of primitive types (bool/str is an exception).
- Constants must be compile-time values.
- Taxonomy must not contain business rules, infrastructure, or imports from other layers.

---

## 6. Contract Layer

### Purpose

Contract defines the public behavior of the system without exposing implementation. It allows callers to depend on stable interfaces instead of concrete logic.

### Components

| Role      | Meaning                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------- |
| Protocol  | Interface defining inbound behavior. It is implemented by Capabilities and consumed by the Agent. |
| Aggregate | Facade definition implemented by Agent, used by Surface to access feature behavior.               |

### Dependencies

Contract may depend on Taxonomy only.

### Special Rules

- Protocol defines behavior only without implementation.
- Aggregate hides Capabilities from Surface.

---

## 7. Utility Layer

### Purpose

Utility contains low-level technical mechanics. It exists so that Capabilities can remain clean and expressive.

### Role Naming

Utility role suffixes are unlimited. The role name is chosen based on demand and must describe the technical responsibility and concern of the file.

parser
splitter
trimmer
slugifier
sanitizer
normalizer
extractor
replacer
converter
counter
resolver
detector
builder
joiner
serializer
deserializer
encoder
decoder
hasher
generator
formatter
comparator
differ
matcher
checker
calculator
mapper
merger
grouper
sorter
deduplicator
printer

### Dependencies

Utility may depend only on Taxonomy.

### Technical Concern Examples

| Concern                 | Responsibility                                      |
| ----------------------- | --------------------------------------------------- |
| File discovery          | Walk directories, detect files, apply ignore        |
| External tool execution | Run linters, compilers, formatters, analyzers       |
| Parsing and matching    | Parse text, match patterns, extract structured data |
| Path normalization      | Normalize paths across platforms                    |
| System operations       | Handle process or environment mechanics             |

### Special Rules

- Utility must use stateless standalone functions only.
- Utility must not contain stateful objects, behavior definitions, or contract implementations.
- Utility must not make business decisions.
- Utility may perform technical operations if needed.
- Utility must not implement any contract.
- Utility role names may expand freely, but the layer must remain technical and standalone.
- Utility must use stateless standalone functions only.

---

## 8. Capabilities Layer

### Purpose

Capabilities contain the concrete implementation of the system's behavior. This layer encapsulates both **pure business logic** (computations, validations) and **external adaptations** (database access, third-party API calls, infrastructure mechanics). By hiding these implementations behind Contracts, the system keeps its behavior modular, swappable, and fully isolated from orchestration.

### Role Naming

#### Internal Examples

validator
assessor
calculator
resolver
classifier
selector
mapper
transformer
policy
enricher
evaluator
analyzer
scorer
grader
ranker
filter
checker
reviewer
approver
rejector

#### External Examples

repository
gateway
client
provider
fetcher
reader
writer
scanner
executor
publisher
subscriber
adapter
connector
uploader
downloader
sender
receiver
dispatcher
watcher
monitor

### Dependencies

- Capabilities may depend on Taxonomy, Contract, and Utility.
- Capabilities must not depend on or import other Capabilities.

### Concern Examples

Capabilities generally handle two types of concerns:

| Category                | Concern        | Responsibility                                 |
| ----------------------- | -------------- | ---------------------------------------------- |
| **Business Logic**      | Validation     | Check domain conditions or input correctness   |
|                         | Computation    | Calculate scores, totals, or derived values    |
|                         | Transformation | Map, filter, reduce, or reshape data           |
|                         | Resolution     | Apply rules and decide outcomes                |
|                         | Assessment     | Judge severity, compliance, grade, or quality  |
| **External Adaptation** | Repository     | Fetch or persist domain entities to a database |
|                         | Integration    | Communicate with third-party services or APIs  |
|                         | Provider       | Generate data from external systems            |

### Special Rules

- **No Inter-Capability Dependency:** Capabilities must never import or call other Capabilities directly. They are standalone execution units.
- **Pipeline Aggregation:** Multiple Capabilities (e.g., Capability A for data fetching, Capability B for business calculation) are designed to be composed into a sequential pipeline by the **Agent Layer**, not by themselves.
- **Shared Logic Extraction (DRY):** If multiple Capabilities require the same technical mechanics or functions, that logic must be extracted into a reusable standalone function in the **Utility Layer**. Capabilities must not duplicate technical code (Don't Repeat Yourself).
- **Contract Implementation:** Capabilities must implement the `protocol_` defined in the Contract Layer.
- **State Ownership:** Capabilities are the owners of business and technical state within their execution scope.
- **Utility Delegation:** Capabilities must call Utility standalone functions when low-level technical operations are required, passing their state/data as arguments.
- **No Orchestration:** Capabilities must not contain flow control (looping across capabilities, branching between capabilities, or error escalation policy). They execute their single responsibility and return a result.
- **No Domain Definition:** Capabilities must not define domain models (Entities, Value Objects); they only consume and produce Taxonomy.

---

## 9. Agent Layer

### Purpose

Agent coordinates multiple capabilities into executable flows. It controls sequence and movement, not business calculation.

### Allowed Role

The only Agent role is orchestrator.

### Dependencies

Agent may depend only on Taxonomy, Contract, and Utility.

### Allowed Flow Control

| Flow Type               | Purpose                                |
| ----------------------- | -------------------------------------- |
| Sequential execution    | Run steps in order                     |
| Looping                 | Process multiple items or events       |
| Branching               | Choose path based on result            |
| Error handling          | Recover, abort, continue, or escalate  |
| Timeout or cancellation | Stop long-running or asynchronous work |

### Special Rules

- Agent must depend on Contract, not concrete implementations.
- Agent must not use and must be completely ignorant of Capabilities implementations.
- Agent must not calculate business results.
- Agent must not define domain models.

---

## 10. Surface Layer

### Purpose

Surface is the outer boundary of the system. It handles user-facing or external-facing interaction and translates it into architectural actions.

### Allowed Roles

Surface roles include:

- command
- controller
- page
- view
- component
- router
- layout
- hook
- store
- action
- screen

### Surface Groups

| Group            | Roles                             | Dependencies                          | Rule                                            |
| ---------------- | --------------------------------- | ------------------------------------- | ----------------------------------------------- |
| Smart surfaces   | command, controller, page, router | Taxonomy, Contract Aggregate, Utility | May initiate feature behavior through aggregate |
| Utility surfaces | hook, store, action, screen       | Taxonomy, Contract Aggregate, Utility | Support smart surfaces but must not import smart surfaces |
| Passive surfaces | component, view, layout           | Taxonomy only                         | Presentation-only, no logic or orchestration    |

### Special Rules

- Smart surfaces must consume Contract Aggregates.
- Surfaces must not import Capabilities, Utility, or Agent directly.
- Surfaces must not contain business calculation or orchestration.

---

## 11. Root Layer

### Purpose

Root is the composition layer. It assembles the system by connecting concrete implementations to contracts and starting the application.

### Components

| Role      | Meaning                                                                           |
| --------- | --------------------------------------------------------------------------------- |
| Container | Wires one feature by connecting Capabilities to Contract protocols and aggregates |
| Entry     | Bootstraps the application and composes feature containers                        |

### Dependencies

Root may depend on all layers.

### Special Rules

- Root may instantiate and wire components.
- Root must not contain business logic.
- Root must not contain orchestration policy.
- Root must not contain technical parsing or user interface behavior.
````

---

## File: modules/job/FRD.md

```markdown
# FRD — Background Job Tracking Feature

## Purpose

Tracks the lifecycle of background tasks for **blender-arwaky**. Single owner of all background task state.

This feature is the only authority for background task records. Domain features may execute long-running work, but they must register that work through the job feature, update it through the job feature, and expose its outcome through the job feature. Task identifiers, state transitions, progress, cancellation, retention, and capacity are all governed here.

The result is one consistent, pollable, auditable view of every long-running operation in the system, regardless of which domain feature performs the actual work.

## Scope

- Task creation with collision-resistant unique task identifier
- Task state machine and terminal state enforcement
- Progress reporting with bounded percentage values
- Cancellation request and execution layer signaling
- Final result reference delivery
- Error state capture with sanitized detail
- Retention and automatic cleanup of task records
- Capacity limit enforcement for concurrent background work
- Real-time status snapshots for polling consumers
- Correlation with request tracking identifiers
- Stale running task detection
- Lifecycle observability events

## Out of Scope

- Execution logic
- Download logic
- Render logic
- Code execution logic
- Connection state
- Metrics storage, owned by diagnostics feature
- Persistence of task records beyond application memory
- Storage of result artifacts
- Client push notification or streaming updates
- Retry or resubmission policy for failed tasks

## Depends On

- config feature for capacity, retention, cleanup interval, and staleness settings
- diagnostics feature for lifecycle event delivery

## Provides To

- dispatcher feature
- asset feature
- render feature
- gateway feature
- any domain feature executing long-running work that must be tracked

## Functional Requirements

### FR-JOB-001: Track and Update Task Lifecycle

Job creates task with unique ID. Job updates task state through lifecycle: pending -> running -> completed/failed/cancelled.

- **Description**: Create background task records and move them through a strictly enforced state machine until a terminal state is reached
- **Input**: Task creation concept containing operation type, optional correlation identifier, optional non-sensitive metadata; state update concept containing task identifier, target state, optional result reference, optional error detail, optional transition reason
- **Output**: Task record concept containing task identifier, current state, timestamps, and terminal outcome when finished
- **Business Rules**:
  - Every background task must be registered through the job feature before execution begins
  - Task identifier must be unique and generated using a collision-resistant strategy
  - Initial state must be pending with creation timestamp recorded
  - Valid state transitions are:
    - pending to running
    - running to completed
    - running to failed
    - pending to cancelled
    - running to cancelled
  - Extended transition running to timed out may be enabled by configuration for stale task recovery
  - No backward transitions are allowed under any circumstance
  - Terminal states are immutable except for record cleanup
  - Every transition must update the last-updated timestamp
  - Transition to running must record started timestamp
  - Transition to terminal state must record finished timestamp
  - Transition to completed may carry optional result reference
  - Transition to failed must carry error message and may carry error category
  - Error detail must be sanitized before storage, excluding secrets and raw code
  - Metadata must not contain secrets, credentials, tokens, or sensitive paths
  - All transitions must be atomic and thread-safe
  - State update for unknown task identifier must fail with task not found error
  - Correlation identifier must link task to originating request where provided
- **Edge Cases**: Duplicate task identifier, concurrent transition attempts, transition after terminal state, invalid target state, unknown task identifier, missing error message on failure, sensitive content in metadata or error detail, clock skew affecting timestamps, creation during cleanup sweep
- **Error Handling**: State error for invalid or out-of-order transitions; task not found error for unknown task identifier; validation error for malformed metadata or missing required error detail; concurrency conflict resolved atomically with first valid transition winning

### FR-JOB-002: Monitor Task Status

Job provides real-time task status. Job exposes progress percentage where applicable.

- **Description**: Expose consistent, read-only status snapshots for polling consumers, including progress where the executing feature reports it
- **Input**: Task identifier
- **Output**: Task status snapshot concept containing state, progress percentage, progress message, timestamps, result reference, error detail, operation type, and correlation identifier
- **Business Rules**:
  - Status retrieval must be read-only and must not mutate task state
  - Status retrieval must return consistent snapshot even during concurrent updates
  - Progress percentage must be bounded between zero and one hundred inclusive
  - Progress updates must be atomic and monotonic by default
  - Progress message may accompany progress value and must be sanitized
  - Progress reporting is optional per operation type; snapshot must indicate when progress is not applicable
  - Snapshot must clearly distinguish active states from terminal states
  - Snapshot must include result reference only after completed state
  - Snapshot must include error detail only after failed state
  - Sensitive metadata must be redacted before snapshot emission
  - Snapshot should expose whether task is cancellable in its current state
  - Status retrieval must be lightweight enough to support frequent polling
  - Progress update frequency may be throttled to reduce state churn
- **Edge Cases**: Polling unknown task identifier, polling purged task after retention expiry, concurrent update during snapshot read, progress not applicable for operation type, non-monotonic progress report, oversized progress message, sensitive metadata present, polling during state transition, excessive polling frequency
- **Error Handling**: Task not found error for unknown or purged task identifier; out-of-range or malformed progress rejected with validation error; redaction applied before emission rather than failing the snapshot

### FR-JOB-003: Cancel a Task

Job supports cancellation request. Job signals execution layer to stop. Job marks task as cancelled.

- **Description**: Accept cancellation requests, signal the executing feature, and record cancellation outcome atomically
- **Input**: Task identifier, optional cancellation reason
- **Output**: Cancellation result concept distinguishing accepted, already terminal, unsupported, and not found outcomes
- **Business Rules**:
  - Cancellation may be requested only for pending or running tasks
  - Cancellation of terminal task must be rejected with state error
  - Pending task may transition directly to cancelled without execution layer signaling
  - Running task cancellation must signal the registered execution layer hook
  - Cancellation of running task is best-effort; final state depends on executor acknowledgment
  - Task is marked cancelled only when cancellation transition is applied atomically
  - Race between cancellation and completion resolves to whichever valid transition applies first; the losing request receives already-terminal outcome rather than error
  - Cancellation result must distinguish between:
    - cancellation accepted
    - cancellation acknowledged and confirmed
    - task already terminal
    - cancellation unsupported by executor
    - task not found
  - Cancellation reason must be sanitized before storage
  - Cancellation must not delete the task record; record remains pollable until retention cleanup
  - Duplicate cancellation requests are idempotent and return current cancellation state
  - Cancellation event must be emitted when transition applies
- **Edge Cases**: Cancelling missing task, cancelling completed task, cancelling failed task, duplicate cancellation request, executor without cancellation support, executor unresponsive after signal, concurrent cancellation and completion race, sensitive content in cancellation reason, cancellation during cleanup sweep
- **Error Handling**: Task not found error for unknown task identifier; state error for cancellation of terminal task; unsupported outcome when executor cannot be signaled; race outcome reported as already terminal rather than failure

### FR-JOB-004: Automatic Task Record Cleanup

Job retains completed tasks for configured duration. Job automatically purges old records. Job enforces capacity limit.

- **Description**: Automatically remove expired and excess terminal task records while protecting active tasks and preserving system stability
- **Input**: Retention policy derived from configuration, including retention duration, cleanup interval, and maximum record count
- **Output**: Cleanup summary concept containing purged record count, retained record count, reclaimed capacity count, and warnings
- **Business Rules**:
  - Terminal task records must be retained for configured retention duration after finishing
  - Cleanup sweep runs at configured interval and must be lightweight enough not to degrade normal task operations
  - Purge order must remove oldest terminal records first
  - Active tasks in pending or running state must never be purged by normal retention sweep
  - Running task exceeding configured maximum lifetime may be marked timed out when stale recovery policy is enabled, after which normal retention applies
  - Capacity pressure may trigger early eviction of oldest terminal records outside scheduled sweep
  - Purged task identifier becomes unknown; subsequent polling returns task not found error
  - Cleanup must be safe against concurrent state transitions and status reads
  - Corrupt or unreadable records must be dropped with warning rather than crashing the sweep
  - Cleanup summary must be observable without exposing sensitive task metadata
  - Clock skew must not cause premature purging of recently finished tasks
- **Edge Cases**: Retention duration exceeded, maximum record count exceeded, sweep concurrent with state transition, sweep concurrent with status read, stale running task occupying capacity, clock skew, empty registry, corrupt record, retention configuration changed between sweeps, cleanup interval shorter than sweep duration
- **Error Handling**: Cleanup warnings for corrupt records and partial sweeps; stale running task reconciled through timed out transition when policy enabled; sweep failure must not block task creation or updates

### FR-JOB-005: Enforce Background Capacity

Job enforces max concurrent background tasks. New tasks rejected with CapacityError when limit reached. Domain features must not bypass capacity check.

- **Description**: Limit the number of concurrently active background tasks and make the job feature the only path to background execution
- **Input**: Task creation request against current capacity state
- **Output**: Capacity decision concept containing accepted indicator or capacity error, plus current active count
- **Business Rules**:
  - Maximum concurrent background task count must be enforced from configuration
  - Capacity check must count active tasks, meaning pending and running records, according to configured counting policy
  - Capacity check must be atomic with task creation so concurrent submissions cannot exceed the limit
  - New task submission must be rejected with capacity error when limit is reached
  - Terminal task records must not count against capacity
  - Capacity must be reclaimed automatically as tasks reach terminal states
  - Domain features must not create, track, or run background tasks outside the job feature
  - Background work submitted without job registration should be detectable through missing correlation and flagged for diagnostics
  - Capacity status should be observable, including active count, limit, and available slots
  - Capacity rejection must not create partial or orphan task records
  - Capacity error should include current active count to support caller retry decisions
  - Stale running tasks recovered through timed out transition must release their capacity slot
- **Edge Cases**: Limit reached at submission time, two submissions racing for final slot, capacity freed during submission, terminal task failing to release capacity, stale running task occupying slot indefinitely, miscount after application restart with in-memory records, capacity configuration changed at runtime, burst of submissions after capacity release
- **Error Handling**: Capacity error when limit reached, including active count context; rejected submission leaves no partial record; capacity leak suspected when active count exceeds configured limit triggers diagnostic warning

## Error Categories

- task not found error — task identifier not found, including purged records after retention
- capacity error — background capacity exceeded at submission time
- state error — invalid state transition or cancellation of terminal task
- validation error — malformed metadata, out-of-range progress, or missing required error detail
- concurrency conflict outcome — competing transition lost an atomic race, reported as already terminal rather than failure

## Events

- task created event — task registered with unique identifier and pending state
- task started event — task transitioned to running with started timestamp
- task progress updated event — progress percentage updated, emitted in throttled manner
- task completed event — task reached completed state with result reference indicator
- task failed event — task reached failed state with sanitized error category
- task cancelled event — task reached cancelled state with cancellation outcome
- task timed out event — stale running task recovered through timed out transition
- task cleanup sweep event — retention sweep completed with purged and retained counts
- capacity rejected event — task submission rejected because capacity limit reached

Event payloads should include:

- event category
- task identifier
- operation type
- state before and after transition
- progress percentage where applicable
- correlation identifier when available
- duration metadata
- sanitized reason summary

Event payloads must avoid:

- secrets and credentials
- raw code content
- sensitive filesystem paths
- full result payloads
- unsanitized error detail

## Configuration Keys


| Configuration Concept               | Description                                                          | Typical Default                                |
| ------------------------------------- | ---------------------------------------------------------------------- | ------------------------------------------------ |
| Maximum concurrent background tasks | Upper bound for active background task count                         | Conservative concurrent limit                  |
| Capacity counting policy            | Whether pending tasks count against capacity alongside running tasks | Pending and running both counted               |
| Retention duration                  | How long terminal task records remain pollable after finishing       | Limited retention window measured in hours     |
| Cleanup sweep interval              | Frequency of automatic retention sweeps                              | Periodic interval measured in minutes          |
| Maximum record count                | Upper bound for total retained task records before early eviction    | Conservative record limit                      |
| Stale running lifetime              | Maximum running duration before stale recovery marks task timed out  | Bounded multiple of typical operation duration |
| Stale recovery enabled              | Whether stale running tasks are automatically timed out              | Enabled                                        |
| Progress update throttle            | Minimum interval between stored progress updates                     | Short throttle window                          |

## QA Checklist

- [ ]  Task created with unique collision-resistant identifier
- [ ]  Task created in pending state with creation timestamp
- [ ]  State transition pending to running succeeds with started timestamp
- [ ]  State transition running to completed succeeds with finished timestamp
- [ ]  State transition running to failed succeeds with required error message
- [ ]  State transition pending to cancelled succeeds
- [ ]  State transition running to cancelled succeeds when executor acknowledges
- [ ]  Backward transition rejected with state error
- [ ]  Transition after terminal state rejected with state error
- [ ]  Concurrent transitions resolved atomically with first valid transition winning
- [ ]  Unknown task identifier rejected with task not found error
- [ ]  Status and progress exposed in real-time as consistent snapshot
- [ ]  Status retrieval does not mutate task state
- [ ]  Progress bounded between zero and one hundred
- [ ]  Progress monotonic by default
- [ ]  Progress on non-running task rejected
- [ ]  Result reference visible only after completed state
- [ ]  Error detail visible only after failed state and sanitized
- [ ]  Sensitive metadata redacted from status snapshot
- [ ]  Cancellation signals execution layer for running task
- [ ]  Cancellation of pending task applies immediately
- [ ]  Cancellation of terminal task rejected with state error
- [ ]  Duplicate cancellation request is idempotent
- [ ]  Cancellation and completion race reports already terminal outcome to loser
- [ ]  Cancellation reason sanitized before storage
- [ ]  Capacity limit enforced — no bypass
- [ ]  Capacity check atomic with task creation under concurrent submissions
- [ ]  Capacity error includes active count context
- [ ]  Rejected submission leaves no partial or orphan record
- [ ]  Terminal tasks release capacity automatically
- [ ]  Stale running task timed out and capacity slot reclaimed when policy enabled
- [ ]  Domain features cannot run background tasks without job tracking
- [ ]  Unregistered background work flagged through missing correlation
- [ ]  Completed tasks cleaned up automatically after retention duration
- [ ]  Cleanup purges oldest terminal records first
- [ ]  Active tasks never purged by normal retention sweep
- [ ]  Purged task identifier returns task not found on polling
- [ ]  Cleanup sweep safe against concurrent transitions and reads
- [ ]  Corrupt record dropped with warning without crashing sweep
- [ ]  Clock skew does not cause premature purge
- [ ]  Lifecycle events emitted for creation, start, progress, completion, failure, cancellation, timeout, sweep, and capacity rejection
```

---

## File: modules/job/pyproject.toml

```toml
[project]
name = "blender-arwaky-job"
version = "1.6.5"
description = "BlenderArwaky job feature module"
requires-python = ">=3.10"
license = {text = "MIT"}

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["."]
```

---

## File: modules/job/src/__init__.py

```python
"""Job feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/job/)      → VOs, Entities, Events, Errors, Constants
  - Contract (shared/src/job/)      → aggregate (IJobAggregate)
  - Agent                           → JobOrchestrator (implements IJobAggregate facade)
  - Root                            → JobContainer (DI wiring)

The JobOrchestrator is self-contained: it owns task state directly and
implements every FR-JOB requirement (track / monitor / cancel / cleanup /
capacity) without delegating to a separate capabilities layer. The
per-FR capability files (cancel / capacity / cleanup / monitor / tracker)
were redundant duplicates of the orchestrator's logic and were removed
(see AUDIT.md, cycle 27).

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from .agent_job_orchestrator import JobOrchestrator

__all__ = [
    "JobOrchestrator",
]
```

---

## File: modules/job/src/agent_job_orchestrator.py

```python
"""Agent: Job feature orchestrator.

Coordinates job state tracking, monitoring, cancellation, and cleanup.
Wires capabilities together per FR-JOB requirements.
"""

import logging

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    Progress,
    ResultUrl,
)
from modules.shared.src.job.contract_job_aggregate import IJobAggregate
from modules.shared.src.job.taxonomy_job_error import CapacityError
from modules.shared.src.job.taxonomy_job_status_entity import JobStatus

logger = logging.getLogger("BlenderMCPServer")


class JobOrchestrator(IJobAggregate):
    """Orchestrates job lifecycle operations via capabilities layer."""

    def __init__(self, max_active: int = 100):
        self._jobs: dict[str, JobStatus] = {}
        self._max_active = max_active

    # FR-JOB-001: Track and Update Task Lifecycle

    def track_new_task(self, operation_type: str, _metadata: dict | None = None) -> tuple[JobId, JobStatus]:
        """Register a new background task. Returns unique tracking ID."""
        import uuid

        job_id = JobId(str(uuid.uuid4()))

        # FR-JOB-005: Enforce Background Capacity
        running = sum(1 for j in self._jobs.values() if j.status.value in ("RUNNING", "PENDING"))
        if running >= self._max_active:
            raise CapacityError(max_active=self._max_active, current_active=running)

        status = JobStatus(job_id=job_id)
        self._jobs[str(job_id)] = status
        logger.info("New task tracked: %s (type=%s)", job_id, operation_type)
        return job_id, status

    def update_progress(self, job_id: JobId, progress: float, _message: str = "") -> JobStatus:
        """Update progress of a running task (0-100%)."""
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]
        if progress < 0 or progress > 100:
            raise ValueError(f"Invalid progress value: {progress} (must be 0-100)")
        if status.status.value not in ("RUNNING", "PENDING"):
            raise RuntimeError(f"Cannot update progress on task in {status.status.value} state")

        status.progress = Progress(progress)
        return status

    def finalize_task_success(
        self, job_id: JobId, result_url: ResultUrl | None = None, _summary: str = ""
    ) -> JobStatus:
        """Mark a task as successfully completed."""
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]
        if status.status.value in ("COMPLETED", "FAILED", "CANCELLED"):
            raise RuntimeError(f"Cannot finalize task already in {status.status.value} state")

        status.mark_completed(result_url)
        logger.info("Task completed: %s", job_id)
        return status

    def finalize_task_failure(self, job_id: JobId, error_message: ErrorString, error_category: str = "") -> JobStatus:
        """Mark a task as failed with error details."""
        if job_id not in self._jobs:
            raise KeyError(f"Task {job_id} not found")

        status = self._jobs[str(job_id)]
        if status.status.value in ("COMPLETED", "FAILED", "CANCELLED"):
            raise RuntimeError(f"Cannot finalize task already in {status.status.value} state")

        status.mark_failed(error_message)
        logger.info("Task failed: %s (%s)", job_id, error_category)
        return status

    # FR-JOB-002: Monitor Task Status

    def get_task_status(self, job_id: JobId) -> JobStatus | None:
        """Retrieve current state snapshot of a task (read-only)."""
        import copy

        status = self._jobs.get(str(job_id))
        if status is None:
            return None
        return copy.deepcopy(status)

    # FR-JOB-003: Cancel a Task

    def cancel_task(self, job_id: JobId, reason: ErrorString = "") -> tuple[bool, str]:
        """Request cancellation of a waiting or running task."""
        status = self._jobs.get(str(job_id))
        if status is None:
            return False, f"Task {job_id} not found"

        state = status.status.value
        if state in ("COMPLETED", "FAILED", "CANCELLED"):
            return False, f"Cannot cancel task already in {state} state"

        status.mark_cancelled(ErrorString(f"Cancelled: {reason}") if reason else ErrorString("Cancelled"))
        logger.info("Task cancelled: %s (reason=%s)", job_id, reason)
        return True, f"Task {job_id} cancellation accepted"

    # FR-JOB-004: Automatic Task Record Cleanup

    def cleanup_expired_tasks(self, max_retained: int = 100) -> dict[str, int]:
        """Remove old, finished task records."""
        terminal_states = {"COMPLETED", "FAILED", "CANCELLED", "TIMED_OUT"}

        terminal = [jid for jid, s in self._jobs.items() if s.status.value in terminal_states]
        to_remove = terminal[max_retained:] if len(terminal) > max_retained else []

        for jid in to_remove:
            del self._jobs[jid]

        return {
            "removed": len(to_remove),
            "retained": len(self._jobs) - len(to_remove),
        }
```

---

## File: modules/job/src/root_job_container.py

```python
"""Root: Job feature composition container.

Wires the job orchestrator (self-contained lifecycle state machine) and
bootstraps the job module. The JobOrchestrator owns task state directly and
delegates to no external capabilities.

This file is the composition root for the job feature.
"""

from __future__ import annotations

import logging

from .agent_job_orchestrator import JobOrchestrator

logger = logging.getLogger("BlenderMCPServer")


class JobContainer:
    """Dependency injection container for the job feature module."""

    def __init__(self, max_active: int = 100) -> None:
        self._max_active = max_active
        self._orchestrator: JobOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the job orchestrator."""
        if self._wired:
            return

        logger.info("Wiring job feature module")

        self._orchestrator = JobOrchestrator(max_active=self._max_active)

        self._wired = True
        logger.info("Job feature module wired successfully")

    @property
    def agent(self) -> JobOrchestrator:
        """Return the assembled job orchestrator facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("JobContainer not wired — call wire() first")
        return self._orchestrator


def create_job_feature(max_active: int = 100) -> JobOrchestrator:
    """Factory function to create and wire the job feature module."""
    container = JobContainer(max_active=max_active)
    container.wire()
    return container.agent
```

---

## File: modules/shared/src/common/__init__.py

```python
"""Common domain — taxonomy types and contracts (cross-cutting).

Note: Contract modules are imported by the main src/__init__.py to avoid
circular dependencies between domain folders.
"""

from . import (
    taxonomy_app_config_vo,
    taxonomy_bounding_box_vo,
    taxonomy_command_catalog_constant,
    taxonomy_core_vo,
    taxonomy_domain_error,
    taxonomy_vector3d_vo,
)

__all__ = [
    "taxonomy_app_config_vo",
    "taxonomy_bounding_box_vo",
    "taxonomy_command_catalog_constant",
    "taxonomy_core_vo",
    "taxonomy_domain_error",
    "taxonomy_vector3d_vo",
]
```

---

## File: modules/shared/src/common/taxonomy_core_vo.py

```python
"""Core branded primitive types (NewType aliases) — taxonomy value objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, NewType
from uuid import UUID

# ============================================================
# ID TYPES
# ============================================================

UserId = NewType("UserId", str)
SceneId = NewType("SceneId", str)
AssetId = NewType("AssetId", str)
JobId = NewType("JobId", str)
HdriId = NewType("HdriId", str)
ObjectId = NewType("ObjectId", UUID)
ParentId = NewType("ParentId", str)

# ============================================================
# NAME TYPES
# ============================================================

ObjectName = NewType("ObjectName", str)
AssetName = NewType("AssetName", str)
ProviderName = NewType("ProviderName", str)
MaterialName = NewType("MaterialName", str)
ModifierName = NewType("ModifierName", str)
ActionName = NewType("ActionName", str)
WorkflowName = NewType("WorkflowName", str)
RuleName = NewType("RuleName", str)
SceneRuleSetName = NewType("SceneRuleSetName", str)

# ============================================================
# TYPE & ENUM TYPES
# ============================================================

ObjectType = NewType("ObjectType", str)
AssetType = NewType("AssetType", str)
RenderEngine = NewType("RenderEngine", str)
ImageFormat = NewType("ImageFormat", str)
PrimitiveType = NewType("PrimitiveType", str)
ExportFormat = NewType("ExportFormat", str)
JobState = NewType("JobState", str)
CleanupMode = NewType("CleanupMode", str)
AssetTypeFilter = NewType("AssetTypeFilter", str)

# ============================================================
# TEXT, URLS & MESSAGES
# ============================================================

Prompt = NewType("Prompt", str)
ErrorString = NewType("ErrorString", str)
SearchQuery = NewType("SearchQuery", str)
NextPageToken = NewType("NextPageToken", str)
ResultUrl = NewType("ResultUrl", str)
ThumbnailUrl = NewType("ThumbnailUrl", str)

# ============================================================
# NUMERIC LIMITS & METRICS
# ============================================================

MaxSize = NewType("MaxSize", int)
IterationCount = NewType("IterationCount", int)
PortNumber = NewType("PortNumber", int)
Host = NewType("Host", str)
SampleCount = NewType("SampleCount", int)
ResolutionX = NewType("ResolutionX", int)
ResolutionY = NewType("ResolutionY", int)
ObjectCount = NewType("ObjectCount", int)
AssetCount = NewType("AssetCount", int)
RenderSamples = NewType("RenderSamples", int)
MaxImageSize = NewType("MaxImageSize", int)
ResultLimit = NewType("ResultLimit", int)
LightStrength = NewType("LightStrength", float)
RenderTime = NewType("RenderTime", float)
Progress = NewType("Progress", float)

# ============================================================
# FLAGS
# ============================================================

EnabledFlag = NewType("EnabledFlag", bool)
SuccessFlag = NewType("SuccessFlag", bool)
UseDenoising = NewType("UseDenoising", bool)

# ============================================================
# COLLECTIONS & VECTORS
# ============================================================

StringList = NewType("StringList", list[str])
TagList = NewType("TagList", list[str])
AssetIdList = NewType("AssetIdList", list[str])
CoordinateList = NewType("CoordinateList", list[float])
ScaleVector = NewType("ScaleVector", list[float])
RotationVector = NewType("RotationVector", list[float])
ObjectIdList = NewType("ObjectIdList", list[UUID])
ChildrenIds = NewType("ChildrenIds", list[str])

# Surface-typed primitives (for handler param annotations)
SkillName = NewType("SkillName", str)
SectionRef = NewType("SectionRef", str)
ServerName = NewType("ServerName", str)
DomainRef = NewType("DomainRef", str)
FormatRef = NewType("FormatRef", str)
CapabilityRef = NewType("CapabilityRef", str)

# Exit code for CLI main() return codes
ExitCode = NewType("ExitCode", int)

# Pathing
FilePath = NewType("FilePath", str)
DirectoryPath = NewType("DirectoryPath", str)

# Config types (no raw primitives in contracts)
ConfigPath = NewType("ConfigPath", str)

# Additional VOs for AES006 compliance
CustomerUuid = NewType("CustomerUuid", str)
SessionId = NewType("SessionId", str)
Timestamp = NewType("Timestamp", float)
VersionString = NewType("VersionString", str)
PlatformName = NewType("PlatformName", str)
ToolName = NewType("ToolName", str)
DurationMs = NewType("DurationMs", float)
BlenderVersion = NewType("BlenderVersion", str)
StatusString = NewType("StatusString", str)
PythonCode = NewType("PythonCode", str)
TaskUuid = NewType("TaskUuid", str)
ScaleFactor = NewType("ScaleFactor", float)
ImageBytes = NewType("ImageBytes", bytes)
BBoxIntegers = NewType("BBoxIntegers", list[int])

# Server-specific VOs for request correlation
RequestId = NewType("RequestId", str)
QueueWaitMs = NewType("QueueWaitMs", float)
ProtocolVersion = NewType("ProtocolVersion", str)
AuthToken = NewType("AuthToken", str)

# Job retention types
MaxTasksCount = NewType("MaxTasksCount", int)

# Details type alias (used in error handling)
Details = dict[str, Any]

# ErrorMessage is an alias for ErrorString, used by capability layers
ErrorMessage = ErrorString

# BlenderObjectList placeholder (resolved at runtime)
BlenderObjectList = NewType("BlenderObjectList", list[Any])

# ============================================================
# CONFIGURATION METADATA (FR-CFG-001, FR-CFG-005)
# ============================================================

SourceLocation = NewType("SourceLocation", str | None)
ParseWarning = NewType("ParseWarning", str)
ValidationWarning = NewType("ValidationWarning", str)
OverrideCount = NewType("OverrideCount", int)


@dataclass(frozen=True)
class ConfigMetadata:
    """Immutable metadata about configuration loading (FR-CFG-001, FR-CFG-005).

    Frozen (hashable). Carries structural counts + source path only —
    never raw settings values or secrets.
    """

    source: SourceLocation | None = None
    exists: bool = False
    overrides: OverrideCount = 0
    parse_warnings: tuple[ParseWarning, ...] = field(default_factory=tuple)
    validation_warnings: tuple[ValidationWarning, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # Normalize list inputs to immutable tuples.
        if isinstance(self.parse_warnings, list):
            object.__setattr__(self, "parse_warnings", tuple(self.parse_warnings))
        if isinstance(self.validation_warnings, list):
            object.__setattr__(self, "validation_warnings", tuple(self.validation_warnings))

    def to_dict(self) -> dict[str, Any]:
        """Serialize metadata for diagnostics (secrets excluded)."""
        return {
            "source": self.source,
            "exists": self.exists,
            "overrides": self.overrides,
            "parse_warnings": list(self.parse_warnings),
            "validation_warnings": list(self.validation_warnings),
        }
```

---

## File: modules/shared/src/job/__init__.py

```python
"""Job domain — contracts, taxonomy, and shared types."""

from .contract_job_aggregate import IJobAggregate
from .taxonomy_job_state_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
)
from .taxonomy_job_status_entity import JobStatus

__all__ = [
    "IJobAggregate",
    "JOB_STATE_CANCELLED",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_TIMED_OUT",
    "JobStatus",
]
```

---

## File: modules/shared/src/job/contract_job_aggregate.py

```python
"""Job domain contract: job aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for job lifecycle operations: track, update, finalize, cancel, cleanup.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import ErrorString, JobId, ResultUrl
from .taxonomy_job_status_entity import JobStatus


class IJobAggregate(ABC):
    @abstractmethod
    def track_new_task(
        self,
        operation_type: str,
        metadata: dict[str, Any] | None = None,
    ) -> tuple[JobId, JobStatus]: ...

    @abstractmethod
    def update_progress(
        self,
        job_id: JobId,
        progress: float,
        message: str = "",
    ) -> JobStatus: ...

    @abstractmethod
    def finalize_task_success(
        self,
        job_id: JobId,
        result_url: ResultUrl | None = None,
        summary: str = "",
    ) -> JobStatus: ...

    @abstractmethod
    def finalize_task_failure(
        self,
        job_id: JobId,
        error_message: ErrorString,
        error_category: str = "",
    ) -> JobStatus: ...

    @abstractmethod
    def get_task_status(self, job_id: JobId) -> JobStatus | None: ...

    @abstractmethod
    def cancel_task(
        self,
        job_id: JobId,
        reason: ErrorString = "",
    ) -> tuple[bool, str]: ...

    @abstractmethod
    def cleanup_expired_tasks(self, max_retained: int = 100) -> dict[str, Any]: ...
```

---

## File: modules/shared/src/job/taxonomy_job_error.py

```python
"""Job domain error types."""

from __future__ import annotations

from ..common.taxonomy_core_vo import ErrorString


class JobError(Exception):
    """Base error for job domain operations."""

    def __init__(self, message: ErrorString | None = None) -> None:
        message = message or ErrorString("Job error")
        super().__init__(message)


class CapacityError(JobError):
    """Raised when background capacity limit is reached (FR-JOB-005)."""

    def __init__(self, max_active: int = 100, current_active: int = 100) -> None:
        message = ErrorString(f"Background capacity exceeded: {current_active}/{max_active} active tasks")
        super().__init__(message)
        self.max_active = max_active
        self.current_active = current_active


class TaskNotFoundError(JobError):
    """Raised when a requested task does not exist."""

    def __init__(self, task_id: str) -> None:
        message = ErrorString(f"Task {task_id} not found")
        super().__init__(message)
        self.task_id = task_id


class InvalidStateTransitionError(JobError):
    """Raised when an invalid state transition is requested."""

    def __init__(self, from_state: str, to_state: str) -> None:
        message = ErrorString(f"Invalid state transition: {from_state} -> {to_state}")
        super().__init__(message)
        self.from_state = from_state
        self.to_state = to_state
```

---

## File: modules/shared/src/job/taxonomy_job_state_constant.py

```python
"""Job state constants."""

from __future__ import annotations

from typing import Final

from ..common.taxonomy_core_vo import JobState

# ============================================================
# JOB STATE CONSTANTS
# ============================================================

JOB_STATE_PENDING: Final[JobState] = JobState("PENDING")
JOB_STATE_RUNNING: Final[JobState] = JobState("RUNNING")
JOB_STATE_COMPLETED: Final[JobState] = JobState("COMPLETED")
JOB_STATE_FAILED: Final[JobState] = JobState("FAILED")
JOB_STATE_CANCELLED: Final[JobState] = JobState("CANCELLED")
JOB_STATE_TIMED_OUT: Final[JobState] = JobState("TIMED_OUT")
```

---

## File: modules/shared/src/job/taxonomy_job_status_entity.py

```python
"""Mutable job status tracking entity."""

from __future__ import annotations

from ..common.taxonomy_core_vo import ErrorString, JobId, JobState, Progress, ResultUrl
from .taxonomy_job_state_constant import (
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
)


class JobStatus:
    """Mutable tracking of an async background job."""

    def __init__(
        self,
        job_id: JobId,
        status: JobState = JOB_STATE_PENDING,
        progress: Progress | None = None,
        result_url: ResultUrl | None = None,
        error: ErrorString | None = None,
    ) -> None:
        self.job_id = job_id
        self.status: JobState = status
        self.progress: Progress = progress if progress is not None else Progress(0.0)
        self.result_url: ResultUrl | None = result_url
        self.error: ErrorString | None = error

    def mark_running(self) -> None:
        """Transition to running state."""
        self.status = JOB_STATE_RUNNING
        self.progress = Progress(0.0)

    def mark_completed(self, result_url: ResultUrl | None = None) -> None:
        """Transition to completed state."""
        self.status = JOB_STATE_COMPLETED
        self.progress = Progress(100.0)
        self.result_url = result_url

    def mark_failed(self, error: ErrorString) -> None:
        """Transition to failed state."""
        self.status = JOB_STATE_FAILED
        self.error = error

    def mark_cancelled(self, reason: ErrorString | None = None) -> None:
        """Transition to cancelled state."""
        self.status = JOB_STATE_CANCELLED
        if reason:
            self.error = reason

    def mark_timed_out(self) -> None:
        """Transition to timed out state."""
        self.status = JOB_STATE_TIMED_OUT


def create_job_id(raw: str) -> JobId:
    """Factory helper to create a JobId from a raw string."""
    return JobId(raw)


def create_progress(raw: float) -> Progress:
    """Factory helper to create a validated Progress value."""
    if raw < 0.0 or raw > 100.0:
        raise ValueError("progress must be between 0.0 and 100.0")
    return Progress(raw)
```

---

## File: pyproject.toml

```toml
[project]
name = "blender-arwaky"
version = "1.7.0"
description = "Blender integration through the Model Context Protocol"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    {name = "rakaarwaky", email = "arwaky90@gmail.com"}
]
license = {text = "MIT"}
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "mcp[cli]>=1.3.0",
    "tomli>=2.0.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.3",
    "pillow>=12.2.0",
]

[project.optional-dependencies]
test = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=7.1.0",
    "pytest-mock>=3.15.1",
    "requests>=2.31.0",  # Used by blender_mcp_addon modules (bundled with Blender at runtime)
]
lint = [
    "ruff>=0.11.0",
    "mypy>=1.15.0",
    "bandit>=1.8.0",
]
dev = [
    "blender-arwaky[test]",
    "blender-arwaky[lint]",
]

[dependency-groups]
test = ["blender-arwaky[test]"]
lint = ["blender-arwaky[lint]"]
dev = ["blender-arwaky[dev]"]

[project.scripts]
blender-arwaky = "modules.cli.src.surface_cli_main:main"
blender-mcp = "modules.root_mcp_entry:main"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["modules*", "blender_mcp_addon*"]
exclude = ["*.tests", "tests*", "log*", "plugin*"]

[project.urls]
"Homepage" = "https://github.com/rakaarwaky/blender-arwaky"
"Bug Tracker" = "https://github.com/rakaarwaky/blender-arwaky/issues"

[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM", "ARG", "RUF100"]
ignore = ["E501"]

# Blender API contracts: class names (N801), argument names (N803/ARG001/ARG002),
# and Hunyuan API field names (N806) are dictated by external APIs.
[tool.ruff.lint.per-file-ignores]
"blender_mcp_addon/__init__.py"   = ["N801"]  # bl_info keys
"blender_mcp_addon/operators.py"  = ["N801"]  # Operator.bl_idname convention
"blender_mcp_addon/ui.py"         = ["N801", "ARG002"]  # Panel/AddonPreferences + context arg required by bpy
"blender_mcp_addon/polyhaven.py"  = ["B007"]  # `dirs` is required by os.walk contract
"blender_mcp_addon/sketchfab.py"  = ["B007"]  # `dirs` is required by os.walk contract
"blender_mcp_addon/properties.py" = []  # noqa already used inline

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

# ─── Pytest configuration ───────────────────────────────────────────────────
[tool.pytest.ini_options]
minversion = "9.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--cov=src",
    "--cov=modules",
    "--cov=blender_mcp_addon",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml:coverage.xml",
]
markers = [
    "unit: Pure logic tests, no external dependencies",
    "integration: Layer interaction tests with real DI, mocked I/O",
    "functional: End-to-end command flows within project boundaries",
    "addon: Blender addon tests using bpy mock (tests/addon/)",
    "slow: Tests that take >1s to run",
    "asyncio: Async test marker (pytest-asyncio)",
]
asyncio_mode = "auto"

# ─── Coverage configuration ────────────────────────────────────────────────
[tool.coverage.run]
source = ["src", "modules", "blender_mcp_addon"]
branch = true
parallel = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/.*",
    "*/dist/*",
    "*/build/*",
    # Exclude external-API clients from global threshold.
    # They require recorded HTTP fixtures (vcrpy) to test meaningfully.
    "blender_mcp_addon/polyhaven.py",
    "blender_mcp_addon/sketchfab.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
# Realistic current threshold — increase as tests mature.
# Excludes external-API modules (polyhaven, sketchfab)
# that require live network mocking to test.
fail_under = 60
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "\\.\\.\\.",
    "pass",
]
exclude_also = [
    "raise ImportError",
    "except ImportError",
    "@overload",
    "@abstractmethod",
]

```

---

## File: README.md

````markdown
# BlenderArwaky

> Connect Blender to AI agents through the Model Context Protocol.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Blender 3.0+](https://img.shields.io/badge/Blender-3.0%2B-orange.svg)](https://www.blender.org/)

BlenderArwaky bridges [Blender 3D](https://www.blender.org/) with any MCP-compatible client — Claude Desktop, Cursor, Continue.dev, or custom agents. Control scenes, import assets, render, and execute Blender Python through 4 universal MCP tools.

## Prerequisites

- **Blender 3.0+** (tested on 5.1)
- **Python 3.10+**

## Quick Start

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync
```

### Install Blender Addon

1. Blender → Edit → Preferences → Add-ons
2. Install `blender_mcp_addon/` directory
3. Enable **"Interface: Blender Arwaky"**

### Start MCP Server

```bash
uv run blender-mcp
```

### Configure MCP Client

```json
{
  "mcpServers": {
    "blender-arwaky": {
      "command": "uv",
      "args": ["--directory", "/path/to/blender-arwaky", "run", "blender-mcp"]
    }
  }
}
```

## Architecture

AES 7-layer architecture with full dependency inversion:

```
taxonomy → contract → capabilities → agent → surface → entry
                ↑
            infrastructure
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for full specification.

## Project Structure

```
modules/
├── shared/         ← Taxonomy + Contracts (FRD: modules/shared/FRD.md)
├── object/         ← Object operations (FRD: modules/object/FRD.md)
├── scene/          ← Scene management (FRD: modules/scene/FRD.md)
├── render/         ← Rendering + assets (FRD: modules/render/FRD.md)
├── telemetry/      ← Usage analytics (FRD: modules/telemetry/FRD.md)
├── job/            ← Job tracking (FRD: modules/job/FRD.md)
├── cli/            ← Standalone CLI (FRD: modules/cli/FRD.md)
├── root_mcp_entry.py
└── root_cli_entry.py
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `uv run blender-mcp` | Start MCP server |
| `uv run blender-arwaky` | Run standalone CLI |
| `uv run pytest` | Run tests (455+) |
| `uv run pytest -m unit` | Unit tests only |
| `uv run ruff check .` | Lint code |
| `lint-arwaky-cli scan .` | AES architecture compliance |

## Configuration

```yaml
blender:
  executable_path: "/path/to/blender"
  host: "localhost"
  port: 9876

server:
  transport: "stdio"
  log_dir: "log"
```

| Env Var | Description |
|---------|-------------|
| `BLENDERMCP_CONFIG_PATH` | Override config.yaml path |
| `BLENDERMCP_BLENDER.HOST` | Override Blender host |
| `BLENDERMCP_BLENDER.PORT` | Override Blender port |
| `BLENDERMCP_STRICT` | Enable v1.7.0 new enforcement (schema validation, 1 MiB size limit, `\` path escaping, strict ConfigTypeError, runtime overrides). Default OFF; flips ON in v1.8.0. |

## Testing

```bash
uv run pytest              # Full suite
uv run pytest -m unit      # Unit tests
uv run pytest -m integration  # Integration tests
```

## Documentation

- [PRD.md](PRD.md) — Product requirements (stakeholders)
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [SKILL.md](SKILL.md) — Agent usage reference
- [AGENT.md](AGENT.md) — Developer reference
- [TEST.md](TEST.md) — Testing guide
- [modules/\*/FRD.md](modules/shared/FRD.md) — Feature specs (engineers)

## License

[MIT License](LICENSE) — Originally by Siddharth Ahuja, extended by Raka Arwaky.
````

---

---
name: create-capabilities-python
description: "Create and validate Python capabilities layer files following AES rules: concrete implementation of behavior (business logic + external adaptation), 3-block structure, max 3 types per file, protocol ABC contracts, DI for service dependencies, and shared VOs for domain data."
metadata:
  tags:
    [
      python,
      aes,
      capability,
      protocol,
      structure,
      3-block-structure,
      di,
      vo,
      role-naming,
    ]
  triggers:
    - "create capability python"
    - "add capability python"
    - "fix capability structure python"
    - "create protocol python"
    - "capability missing protocol python"
    - "check capabilities python"
    - "audit capabilities python"
  dependencies: []
  related:
    - create-agent-python
    - create-contract-python
    - create-taxonomy-python
---
# create-capabilities-python

## Purpose

Create and validate Python **capabilities layer** files following AES rules.

A capabilities file contains the **concrete implementation** of the system's behavior. This layer encapsulates both:

- **Business logic**: computations, validations, transformations, assessments
- **External adaptation**: database access, third-party API calls, file system access

Capabilities hide these implementations behind Contracts, keeping behavior modular, swappable, and fully isolated from orchestration.

A capabilities file must:

- implement at least one domain protocol ABC (via class inheritance),
- follow strict 3-block structure,
- use dependency injection for service collaborators,
- use shared VOs for domain data,
- use Utility standalone functions for low-level technical operations.

## Role Naming (ARCHITECTURE §8)

Capabilities use role suffixes describing their concern. Two families:

**Internal (business logic):**

validator, assessor, calculator, resolver, classifier, selector, mapper, transformer, policy, enricher, evaluator, analyzer, scorer, grader, ranker, filter, checker, reviewer, approver, rejector

**External (adaptation):**

repository, gateway, client, provider, fetcher, reader, writer, scanner, executor, publisher, subscriber, adapter, connector, uploader, downloader, sender, receiver, dispatcher, watcher, monitor

File: `capabilities_<domain>_<role>.py`

## Dependencies (ARCHITECTURE §8)

- **May depend on:** Taxonomy, Contract, Utility.
- **Must NOT depend on / import:** other Capabilities, Agent.

Note: use the Utility layer for I/O, network, and database access.

## Special Rules (ARCHITECTURE §8)

- **No Inter-Capability Dependency:** a capability never imports or calls another capability. They are standalone execution units.
- **Pipeline Aggregation:** multiple capabilities are composed into a sequential pipeline by the **Agent layer**, not by themselves.
- **Shared Logic Extraction (DRY):** if several capabilities need the same technical mechanics, extract it into a reusable standalone function in the **Utility layer**. Capabilities must not duplicate technical code.
- **Contract Implementation:** the capability inherits the protocol ABC defined in the Contract layer. The file MUST import from `_protocol` module only. Example: `from shared.role_rules.contract_<name>_protocol import I<Name>`
- **State Ownership:** the capability owns business and technical state within its execution scope.
- **Utility Delegation:** low-level technical operations call Utility standalone functions, passing state/data as arguments.
- **No Orchestration:** no flow control across capabilities (looping/branching between capabilities) and no error-escalation policy. Execute one responsibility, return a result.
- **No Domain Definition:** do not define domain models (Entities, Value Objects); only consume and produce Taxonomy.
- **Constant Extraction:** extract reusable constants (magic strings, numbers, patterns) into `taxonomy_<domain>_constant.py` in shared. Capabilities must not contain magic constants.

## AES403 — Capability Composition Rules

See `references/capabilities-roles.md` for the full AES403 rules: Rule 1 (internal helpers allowed), Rule 2 (at least one implementor required), Rule 3 (max 3 types per file), detection patterns, and guard check.

## Definition of Done

1. At least one class inherits a protocol ABC in Block 2 (Rule 2).
2. Block 2 contains ONLY domain protocol method implementations.
3. Dunder methods, factory classmethods, private helpers in Block 3.
4. No locally defined domain models — Entities/Value Objects are consumed from Taxonomy, not defined here.
5. Service dependencies use DI via protocol interfaces.
6. Value/configuration fields use shared VOs.
7. No inter-capability dependencies (capabilities must not import other capabilities or Agent).
8. Low-level technical operations delegate to Utility standalone functions.
9. Reusable constants extracted to `taxonomy_<domain>_constant.py` in shared.
10. Total class count ≤ 3 (Rule 3).
11. File imports from `_protocol` module only.
12. `python -c "import <module>"` passes.

## References

Read these files for detailed rules:


| File                                | Content                                                      |
| ------------------------------------- | -------------------------------------------------------------- |
| `references/layer-boundaries.md`    | Allowed/Forbidden imports and dependencies                   |
| `references/3-block-structure.md`   | Block 1/2/3 definitions, method placement rules              |
| `references/helper-vs-utility.md`   | Helper vs utility decision, I/O Blocker, decision tree       |
| `references/primitive-vo-policy.md` | Primitive policy table, VO construction rules                |
| `references/error-handling.md`      | Error handling rules with examples                           |
| `references/examples.md`            | All BAD/GOOD code examples                                   |
| `references/commands.md`            | Quick heuristic check commands                               |
| `references/checklist.md`           | Verification checklist                                       |
| `references/capabilities-roles.md`  | AES403 capabilities roles (helpers, implementor, type count) |

## Templates

Use these templates when creating new files:


| File                                  | Purpose                              |
| --------------------------------------- | -------------------------------------- |
| `templates/capabilities_name.py`      | New capabilities implementation file |
| `templates/contract_name_protocol.py` | New protocol ABC definition          |

## Workflow

### Step 1: Analyze File Responsibility

Read the file and ask: **"Does this implement protocol behavior?"**

If yes → keep as capabilities. If no → check if it's orchestration (→ agent), domain data (→ taxonomy), or pure technical mechanics (→ utility).

### Step 2: Check Protocol Import (AES403 Guard)

The file MUST import from a `_protocol` module. If missing → flag `CapabilityNoProtocol`.

```python
from shared.role_rules.contract_<name>_protocol import I<Name>
```

### Step 3: Create Protocol File if Missing

Create `contract_<name>_protocol.py` in the appropriate shared domain folder.

### Step 4: Enforce 3-Block Structure

Reorganize: class definition + `__init__` → protocol methods → dunders/factories/helpers.

### Step 5: Verify AES403 Compliance

- **Rule 1:** Internal helper classes without ABC inheritance are ALLOWED (never flagged).
- **Rule 2:** At least one class must inherit a protocol ABC (`class Name(Protocol):`).
- **Rule 3:** Total class count ≤ 3.

### Step 6: Verify Type Discipline

At least one class inherits a protocol ABC, max 3 total classes, DI via protocol interfaces, shared VOs.

### Step 7: Verify Helper vs Utility Boundary

See `references/helper-vs-utility.md` for the decision tree.

### Step 8: Verify Layer Compliance

No forbidden imports (Agent, other capabilities), no inter-capability dependencies, no business logic leakage, no domain model definition.

### Step 9: Verify Error Handling, VO, and Constants

See `references/error-handling.md` and `references/primitive-vo-policy.md`.

### Step 10: Verify Compilation

```bash
python -c "import <module>"
```

## Quick Commands

```bash
# Check forbidden imports (no agent, no other capabilities)
grep -n "^\s*from.*capabilities_\|from.*agent_\|from.*surface_" modules/*/src/capabilities_*.py

# List protocol ABC implementations
grep -n "class.*I[A-Za-z0-9_]*Protocol" modules/*/src/capabilities_*.py

# Check _protocol import (guard)
grep -n "from.*capabilities_\|from.*agent_\|from.*surface_" modules/*/src/capabilities_*.py
```

## Common Mistakes

- Importing other capabilities or Agent directly.
- Defining domain models (Entities, Value Objects) in capabilities files.
- Using concrete service types as constructor fields.
- Putting private helpers in the protocol ABC.
- Putting constructors in the protocol ABC.
- Placing dunder methods before the domain protocol methods.
- Mixing Block 2 and Block 3 responsibilities.
- Flow control across capabilities / error-escalation policy (orchestration).
- Silent error swallowing with `or ""` or `or 0`.
- Magic constants in capabilities logic (extract to `taxonomy_<domain>_constant.py`).
- Not delegating low-level technical operations to Utility.
- Importing from the wrong module instead of `_protocol`.
- Having no class that inherits a protocol ABC (Rule 2 violation).
- Exceeding 3 total classes in a file (Rule 3 violation).

---
name: create-agent-python
description: "Create and validate Python agent layer files following AES rules: orchestration-only, zero I/O, zero business logic, zero domain computation, 3-block structure, max 3 types per file, aggregate ABC contracts, DI for service dependencies, and shared VOs for domain data."
metadata:
  tags:
    [
      python,
      aes,
      agent,
      aggregate,
      structure,
      3-block-structure,
      di,
      orchestration,
      vo,
    ]
  triggers:
    - "create agent python"
    - "add agent python"
    - "fix agent structure python"
    - "create aggregate python"
    - "agent missing aggregate python"
    - "validate agent logic python"
    - "check agent python"
    - "audit agent python"
  dependencies: []
  related:
    - create-capabilities-python
    - create-taxonomy-python
    - create-contract-python
---
# create-agent-python

## Purpose

Create and validate Python **agent layer** files following AES rules.

An agent file contains **orchestration / pipeline execution only**.

Agents coordinate capabilities into executable flows. They control sequence and movement, not business calculation.

Agents MUST NOT contain I/O, business logic, domain rules, domain computation, or domain data definitions.

Agents depend ONLY on Taxonomy, Contract, and Utility layers. They must be completely ignorant of Capabilities implementations.

## Definition of Done

1. At least one class inherits an aggregate ABC in Block 2 (AES405 Rule 2).
2. Block 2 contains ONLY aggregate ABC method implementations.
3. Dunder methods, factory classmethods, private helpers in Block 3.
4. Zero I/O, zero business logic, zero domain computation.
5. No locally defined domain data structures.
6. Service dependencies use DI via aggregate/protocol interfaces.
7. Value/configuration fields use shared VOs.
8. Aggregate signatures use shared VOs for domain data.
9. Total class count ≤ 3 (AES405 Rule 3).
10. `python -c "import <module>"` passes.

## References


| File                                  | Content                                                |
| --------------------------------------- | -------------------------------------------------------- |
| `references/layer-boundaries.md`      | Allowed/Forbidden imports and dependencies             |
| `references/3-block-structure.md`     | Block 1/2/3 definitions, method placement rules        |
| `references/helper-vs-utility.md`     | Helper vs utility decision, I/O Blocker, decision tree |
| `references/computation-detection.md` | Computation detection rules                            |
| `references/error-handling.md`        | Error handling rules                                   |
| `references/primitive-vo-policy.md`   | Primitive policy table, VO rules                       |
| `references/examples.md`              | All BAD/GOOD code examples                             |
| `references/commands.md`              | Quick heuristic check commands                         |
| `references/checklist.md`             | Verification checklist                                 |

## Templates


| File                                   | Purpose                       |
| ---------------------------------------- | ------------------------------- |
| `templates/agent_name.py`              | New agent implementation file |
| `templates/contract_name_aggregate.py` | New aggregate ABC definition  |

## Workflow

### Step 1: Analyze File

Read the file and ask: **"Is this orchestration only?"**

If yes → keep as agent. If it contains computation → capabilities, domain data → taxonomy.

### Step 2: Check for Missing Aggregate

Does the agent class inherit an aggregate ABC? If no → create one.

### Step 3: Create Aggregate File if Missing

Create `contract_<name>_aggregate.py` in the appropriate shared domain folder.

### Step 4: Enforce 3-Block Structure

Reorganize: class definition + `__init__` → aggregate methods → dunders/factories/helpers.

### Step 5: Verify Type Discipline

At least one class inherits an aggregate ABC, max 3 total classes, DI via protocol interfaces, shared VOs.

### Step 6: Verify Helper vs Utility Boundary

See `references/helper-vs-utility.md` for the decision tree.

### Step 7: Verify Layer Compliance

No forbidden imports, no I/O, no business logic, no domain computation.

### Step 8: Verify Error Handling, VO, and Constants

See `references/error-handling.md` and `references/primitive-vo-policy.md`.

### Step 9: Verify Compilation

```bash
python -c "import <module>"
```

## Quick Commands

```bash
# List aggregate ABC implementations
grep -n "class.*I[A-Za-z0-9_]*Aggregate" modules/*/src/agent_*.py

# Check computation patterns
grep -n "sum(\|len(\|\.iter\(\)\|\.map(" modules/*/src/agent_*.py

# Check forbidden imports (agent must only depend on taxonomy + contract + utility)
grep -n "^\s*from.*capabilities_\|from.*agent_\|from.*surface_" modules/*/src/agent_*.py
```

## Common Mistakes

- Putting domain computation in agents.
- Putting business logic in agents.
- Putting I/O in agents.
- Defining domain data classes in agent files.
- Using concrete service types as constructor fields.
- Putting private helpers in the aggregate ABC.
- Placing dunder methods before the aggregate ABC methods.
- Mixing Block 2 and Block 3 responsibilities.
- Silent error swallowing with `or ""` or `or 0`.
- Magic constants in agent logic.