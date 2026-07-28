# Module: job (v1.7.0)

This document contains the source code for module `job` along with related and imported definitions from the `shared` module.

## File List

- [ARCHITECTURE.md](<ARCHITECTURE.md>)
- [modules/job/FRD.md](<modules/job/FRD.md>)
- [modules/job/pyproject.toml](<modules/job/pyproject.toml>)
- [modules/job/src/__init__.py](<modules/job/src/__init__.py>)
- [modules/job/src/agent_job_orchestrator.py](<modules/job/src/agent_job_orchestrator.py>)
- [modules/job/src/capabilities_job_registry.py](<modules/job/src/capabilities_job_registry.py>)
- [modules/job/src/root_job_container.py](<modules/job/src/root_job_container.py>)
- [modules/shared/src/common/__init__.py](<modules/shared/src/common/__init__.py>)
- [modules/shared/src/common/taxonomy_core_vo.py](<modules/shared/src/common/taxonomy_core_vo.py>)
- [modules/shared/src/common/taxonomy_domain_error.py](<modules/shared/src/common/taxonomy_domain_error.py>)
- [modules/shared/src/gateway/taxonomy_gateway_error.py](<modules/shared/src/gateway/taxonomy_gateway_error.py>)
- [modules/shared/src/job/__init__.py](<modules/shared/src/job/__init__.py>)
- [modules/shared/src/job/contract_job_aggregate.py](<modules/shared/src/job/contract_job_aggregate.py>)
- [modules/shared/src/job/contract_job_protocol.py](<modules/shared/src/job/contract_job_protocol.py>)
- [modules/shared/src/job/taxonomy_job_error.py](<modules/shared/src/job/taxonomy_job_error.py>)
- [modules/shared/src/job/taxonomy_job_state_constant.py](<modules/shared/src/job/taxonomy_job_state_constant.py>)
- [modules/shared/src/job/taxonomy_job_status_entity.py](<modules/shared/src/job/taxonomy_job_status_entity.py>)
- [modules/shared/src/job/taxonomy_job_vo.py](<modules/shared/src/job/taxonomy_job_vo.py>)
- [modules/shared/src/job/utility_job_sanitizer.py](<modules/shared/src/job/utility_job_sanitizer.py>)
- [modules/shared/src/security/__init__.py](<modules/shared/src/security/__init__.py>)
- [modules/shared/src/security/taxonomy_security_error.py](<modules/shared/src/security/taxonomy_security_error.py>)
- [modules/shared/src/security/taxonomy_security_vo.py](<modules/shared/src/security/taxonomy_security_vo.py>)
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
# modules/job/src/agent_job_orchestrator.py
from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import JobId
from modules.shared.src.job.contract_job_aggregate import IJobAggregate
from modules.shared.src.job.contract_job_protocol import IJobRegistry
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationResult,
    CancelTaskCommand,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    FailTaskCommand,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


class JobOrchestrator(IJobAggregate):
    """
    Thin agent facade.

    This orchestrator delegates to capability contracts and does not
    contain business logic or state.
    """

    def __init__(self, registry: IJobRegistry) -> None:
        self._registry = registry

    def submit_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        return self._registry.create_task(command)

    def start_task(self, job_id: JobId) -> JobStatusSnapshot:
        return self._registry.start_task(job_id)

    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot:
        return self._registry.update_progress(command)

    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot:
        return self._registry.complete_task(command)

    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot:
        return self._registry.fail_task(command)

    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult:
        return self._registry.cancel_task(command)

    def get_task_status(self, job_id: JobId) -> JobStatusSnapshot:
        return self._registry.get_snapshot(job_id)

    def cleanup_expired_tasks(self) -> CleanupSummary:
        return self._registry.cleanup_expired()

    def get_capacity_status(self) -> CapacityStatus:
        return self._registry.capacity_status()
```

---

## File: modules/job/src/capabilities_job_registry.py

```python
# modules/job/src/capabilities_job_registry.py
from __future__ import annotations

import logging
import threading
import uuid
from collections.abc import Callable
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    Timestamp,
)
from modules.shared.src.job.contract_job_protocol import (
    ICancellationSignaler,
    IJobEventPublisher,
    IJobRegistry,
)
from modules.shared.src.job.taxonomy_job_error import (
    CapacityError,
    InvalidStateTransitionError,
    JobError,
    TaskNotFoundError,
    ValidationError,
)
from modules.shared.src.job.taxonomy_job_state_constant import (
    CANCELLATION_OUTCOME_ACCEPTED,
    CANCELLATION_OUTCOME_ALREADY_TERMINAL,
    CANCELLATION_OUTCOME_NOT_FOUND,
    CANCELLATION_OUTCOME_UNSUPPORTED,
    JOB_STATE_CANCELLED,
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    JOB_STATE_TIMED_OUT,
    TERMINAL_JOB_STATES,
    VALID_JOB_TRANSITIONS,
)
from modules.shared.src.job.taxonomy_job_status_entity import JobRecord
from modules.shared.src.job.taxonomy_job_vo import (
    CancellationReason,
    CancellationResult,
    CancelTaskCommand,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    ErrorCategory,
    FailTaskCommand,
    JobPolicy,
    JobStatusSnapshot,
    OperationType,
    ProgressUpdateCommand,
)
from modules.shared.src.job.utility_job_sanitizer import (
    redact_metadata,
    sanitize_cancellation_reason,
    sanitize_error,
    sanitize_progress_message,
    sanitize_text,
)

logger = logging.getLogger("BlenderMCPServer")


class InMemoryJobRegistry(IJobRegistry):
    """
    Thread-safe in-memory job registry capability.

    This capability owns job state and enforces:
    - state machine transitions
    - capacity limits
    - progress rules
    - cancellation outcomes
    - retention cleanup
    - stale running recovery
    """

    def __init__(
        self,
        policy: JobPolicy,
        clock: Callable[[], Timestamp],
        cancellation_signaler: ICancellationSignaler | None = None,
        event_publisher: IJobEventPublisher | None = None,
        id_generator: Callable[[], JobId] | None = None,
    ) -> None:
        if policy.max_active < 0:
            raise ValueError("policy.max_active must be >= 0")
        if policy.retention_seconds < 0:
            raise ValueError("policy.retention_seconds must be >= 0")
        if policy.max_records < 0:
            raise ValueError("policy.max_records must be >= 0")
        if policy.stale_running_lifetime_seconds < 0:
            raise ValueError("policy.stale_running_lifetime_seconds must be >= 0")
        if policy.progress_throttle_seconds < 0:
            raise ValueError("policy.progress_throttle_seconds must be >= 0")

        self._policy = policy
        self._clock = clock
        self._cancellation_signaler = cancellation_signaler
        self._event_publisher = event_publisher
        self._new_id = id_generator or (lambda: JobId(str(uuid.uuid4())))

        self._lock = threading.RLock()
        self._records: dict[str, JobRecord] = {}
        self._active_count = 0

    # ============================================================
    # PUBLIC API
    # ============================================================

    def create_task(self, command: CreateTaskCommand) -> JobStatusSnapshot:
        now = self._now()

        operation = sanitize_text(str(command.operation_type), 100)
        if not operation:
            raise ValidationError(ErrorString("operation_type is required"))

        metadata = redact_metadata(command.metadata)

        with self._lock:
            if self._active_count >= self._policy.max_active:
                raise CapacityError(
                    max_active=self._policy.max_active,
                    current_active=self._active_count,
                )

            job_id = self._new_id()
            record = JobRecord(
                job_id=job_id,
                operation_type=OperationType(operation),
                correlation_id=command.correlation_id,
                metadata=metadata,
                created_at=now,
                updated_at=now,
            )

            self._records[str(job_id)] = record

            if self._counts_toward_capacity(record.state):
                self._active_count += 1

            snapshot = record.to_snapshot()

        self._publish_snapshot("job.task.created", snapshot)
        return snapshot

    def start_task(self, job_id: JobId) -> JobStatusSnapshot:
        snapshot = self._transition(job_id, JOB_STATE_RUNNING, event="job.task.started")
        return snapshot

    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot:
        now = self._now()
        progress_value = float(command.progress)

        if progress_value < 0.0 or progress_value > 100.0:
            raise ValidationError(ErrorString("progress must be between 0 and 100"))

        message = sanitize_progress_message(command.message)

        with self._lock:
            record = self._records.get(str(command.job_id))
            if record is None:
                raise TaskNotFoundError(str(command.job_id))

            if record.state != JOB_STATE_RUNNING:
                raise InvalidStateTransitionError(str(record.state), "PROGRESS")

            if progress_value < float(record.progress):
                raise ValidationError(ErrorString("progress must be monotonic"))

            # Throttle non-final progress updates.
            if (
                record.last_progress_at is not None
                and (float(now) - float(record.last_progress_at)) < self._policy.progress_throttle_seconds
                and progress_value < 100.0
            ):
                return record.to_snapshot()

            record.progress = Progress(progress_value)
            record.progress_message = message
            record.updated_at = now
            record.last_progress_at = now

            snapshot = record.to_snapshot()

        self._publish_snapshot("job.task.progress_updated", snapshot)
        return snapshot

    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot:
        summary = sanitize_progress_message(command.summary)
        snapshot = self._transition(
            command.job_id,
            JOB_STATE_COMPLETED,
            result_url=command.result_url,
            progress_message=summary,
            event="job.task.completed",
        )
        return snapshot

    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot:
        error = sanitize_error(command.error_message)
        if not str(error).strip():
            raise ValidationError(ErrorString("error_message is required"))

        category: ErrorCategory | None = None
        if command.error_category:
            raw_category = sanitize_text(str(command.error_category), 100)
            category = ErrorCategory(raw_category) if raw_category else None

        snapshot = self._transition(
            command.job_id,
            JOB_STATE_FAILED,
            error=error,
            error_category=category,
            event="job.task.failed",
        )
        return snapshot

    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult:
        reason = sanitize_cancellation_reason(command.reason)

        with self._lock:
            record = self._records.get(str(command.job_id))
            if record is None:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_NOT_FOUND,
                    message="Task not found",
                )

            if record.state in TERMINAL_JOB_STATES:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_ALREADY_TERMINAL,
                    message=f"Task already in terminal state {record.state}",
                )

            current_state = record.state

        # Pending tasks cancel immediately.
        if current_state == JOB_STATE_RUNNING:
            if self._cancellation_signaler is None:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_UNSUPPORTED,
                    message="Executor does not support cancellation",
                )

            try:
                signaled = self._cancellation_signaler.signal(command.job_id, reason)
            except Exception:
                logger.exception("Cancellation signaler failed for job %s", command.job_id)
                signaled = False

            if not signaled:
                return CancellationResult(
                    job_id=command.job_id,
                    accepted=False,
                    outcome=CANCELLATION_OUTCOME_UNSUPPORTED,
                    message="Executor could not be signaled",
                )

        try:
            self._transition(
                command.job_id,
                JOB_STATE_CANCELLED,
                cancellation_reason=reason,
                event="job.task.cancelled",
            )
        except TaskNotFoundError:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_OUTCOME_NOT_FOUND,
                message="Task not found",
            )
        except InvalidStateTransitionError:
            return CancellationResult(
                job_id=command.job_id,
                accepted=False,
                outcome=CANCELLATION_OUTCOME_ALREADY_TERMINAL,
                message="Task reached terminal state before cancellation applied",
            )

        return CancellationResult(
            job_id=command.job_id,
            accepted=True,
            outcome=CANCELLATION_OUTCOME_ACCEPTED,
            message="Cancellation accepted",
        )

    def get_snapshot(self, job_id: JobId) -> JobStatusSnapshot:
        with self._lock:
            record = self._records.get(str(job_id))
            if record is None:
                raise TaskNotFoundError(str(job_id))
            return record.to_snapshot()

    def cleanup_expired(self) -> CleanupSummary:
        now = self._now()
        warnings: list[str] = []
        events: list[tuple[str, JobStatusSnapshot]] = []

        with self._lock:
            reclaimed_capacity = 0

            # 1) Stale running recovery.
            if self._policy.stale_recovery_enabled:
                for record in list(self._records.values()):
                    if record.state != JOB_STATE_RUNNING:
                        continue
                    if record.started_at is None:
                        continue

                    age = float(now) - float(record.started_at)
                    if age <= self._policy.stale_running_lifetime_seconds:
                        continue

                    try:
                        snapshot = self._apply_transition_locked(
                            record,
                            JOB_STATE_TIMED_OUT,
                            now,
                            error=ErrorString("Task exceeded maximum running lifetime"),
                            error_category=ErrorCategory("TIMEOUT"),
                        )
                        reclaimed_capacity += 1
                        events.append(("job.task.timed_out", snapshot))
                    except JobError as exc:
                        warnings.append(f"stale_transition_failed: {exc}")

            # 2) Retention purge, oldest terminal first.
            terminal = [r for r in self._records.values() if r.state in TERMINAL_JOB_STATES]
            terminal.sort(key=lambda r: float(r.finished_at if r.finished_at is not None else r.updated_at))

            purge_ids: set[str] = set()

            for record in terminal:
                finished = float(record.finished_at if record.finished_at is not None else record.updated_at)
                if float(now) - finished >= self._policy.retention_seconds:
                    purge_ids.add(str(record.job_id))

            remaining_terminal = [r for r in terminal if str(r.job_id) not in purge_ids]

            # 3) Max retained terminal records.
            if len(remaining_terminal) > self._policy.max_records:
                excess = len(remaining_terminal) - self._policy.max_records
                for record in remaining_terminal[:excess]:
                    purge_ids.add(str(record.job_id))

            for job_id in purge_ids:
                self._records.pop(job_id, None)

            retained = len(self._records)

            summary = CleanupSummary(
                purged=len(purge_ids),
                retained=retained,
                reclaimed_capacity=reclaimed_capacity,
                warnings=tuple(warnings),
            )

        for event_name, snapshot in events:
            self._publish_snapshot(event_name, snapshot)

        self._publish_raw(
            "job.task.cleanup_sweep",
            {
                "purged": summary.purged,
                "retained": summary.retained,
                "reclaimed_capacity": summary.reclaimed_capacity,
                "warnings": list(summary.warnings),
            },
        )

        return summary

    def capacity_status(self) -> CapacityStatus:
        with self._lock:
            active = self._active_count
            limit = self._policy.max_active
            available = max(0, limit - active)
            return CapacityStatus(active=active, limit=limit, available=available)

    # ============================================================
    # INTERNAL HELPERS
    # ============================================================

    def _now(self) -> Timestamp:
        return Timestamp(float(self._clock()))

    def _counts_toward_capacity(self, state: JobState) -> bool:
        if state == JOB_STATE_RUNNING:
            return True
        if state == JOB_STATE_PENDING:
            return self._policy.count_pending_toward_capacity
        return False

    def _assert_transition(self, current: JobState, target: JobState) -> None:
        allowed = VALID_JOB_TRANSITIONS.get(current, frozenset())
        if target not in allowed:
            raise InvalidStateTransitionError(str(current), str(target))

    def _transition(
        self,
        job_id: JobId,
        target: JobState,
        *,
        result_url: Any | None = None,
        error: ErrorString | None = None,
        error_category: ErrorCategory | None = None,
        cancellation_reason: CancellationReason | None = None,
        progress_message: Any | None = None,
        event: str | None = None,
    ) -> JobStatusSnapshot:
        now = self._now()

        with self._lock:
            record = self._records.get(str(job_id))
            if record is None:
                raise TaskNotFoundError(str(job_id))

            snapshot = self._apply_transition_locked(
                record,
                target,
                now,
                result_url=result_url,
                error=error,
                error_category=error_category,
                cancellation_reason=cancellation_reason,
                progress_message=progress_message,
            )

        event_name = event or f"job.task.{str(target).lower()}"
        self._publish_snapshot(event_name, snapshot)
        return snapshot

    def _apply_transition_locked(
        self,
        record: JobRecord,
        target: JobState,
        now: Timestamp,
        *,
        result_url: Any | None = None,
        error: ErrorString | None = None,
        error_category: ErrorCategory | None = None,
        cancellation_reason: CancellationReason | None = None,
        progress_message: Any | None = None,
    ) -> JobStatusSnapshot:
        self._assert_transition(record.state, target)

        was_active = self._counts_toward_capacity(record.state)

        record.state = target
        record.updated_at = now

        if target == JOB_STATE_RUNNING:
            record.started_at = now
            record.progress = Progress(0.0)
            record.progress_message = None
            record.last_progress_at = None

        if target in TERMINAL_JOB_STATES:
            record.finished_at = now

        if target == JOB_STATE_COMPLETED:
            record.progress = Progress(100.0)
            record.result_url = result_url
            if progress_message is not None:
                record.progress_message = progress_message

        if target == JOB_STATE_FAILED:
            record.error = error or ErrorString("Unknown error")
            record.error_category = error_category

        if target == JOB_STATE_CANCELLED:
            record.cancellation_reason = cancellation_reason

        now_active = self._counts_toward_capacity(target)
        delta = (1 if now_active else 0) - (1 if was_active else 0)
        self._active_count += delta

        if self._active_count < 0:
            logger.warning("Active job count became negative; resetting to zero")
            self._active_count = 0

        return record.to_snapshot()

    def _publish_snapshot(self, event: str, snapshot: JobStatusSnapshot) -> None:
        if self._event_publisher is None:
            return

        payload = {
            "job_id": str(snapshot.job_id),
            "state": str(snapshot.state),
            "operation_type": str(snapshot.operation_type),
            "progress": float(snapshot.progress),
            "correlation_id": str(snapshot.correlation_id) if snapshot.correlation_id else None,
            "is_terminal": snapshot.is_terminal,
            "created_at": float(snapshot.created_at),
            "updated_at": float(snapshot.updated_at),
            "started_at": float(snapshot.started_at) if snapshot.started_at is not None else None,
            "finished_at": float(snapshot.finished_at) if snapshot.finished_at is not None else None,
        }

        self._publish_raw(event, payload)

    def _publish_raw(self, event: str, payload: dict[str, Any]) -> None:
        if self._event_publisher is None:
            return

        try:
            self._event_publisher.publish(event, payload)
        except Exception:
            logger.exception("Failed publishing job event: %s", event)
```

---

## File: modules/job/src/root_job_container.py

```python
# modules/job/src/root_job_container.py
from __future__ import annotations

import logging
import time
from collections.abc import Callable

from modules.shared.src.common.taxonomy_core_vo import Timestamp
from modules.shared.src.job.contract_job_protocol import (
    ICancellationSignaler,
    IJobEventPublisher,
)
from modules.shared.src.job.taxonomy_job_vo import JobPolicy

from .agent_job_orchestrator import JobOrchestrator
from .capabilities_job_registry import InMemoryJobRegistry

logger = logging.getLogger("BlenderMCPServer")


class JobContainer:
    """Dependency injection container for the job feature module."""

    def __init__(
        self,
        policy: JobPolicy | None = None,
        cancellation_signaler: ICancellationSignaler | None = None,
        event_publisher: IJobEventPublisher | None = None,
        clock: Callable[[], Timestamp] | None = None,
    ) -> None:
        self._policy = policy or JobPolicy()
        self._cancellation_signaler = cancellation_signaler
        self._event_publisher = event_publisher
        self._clock = clock

        self._orchestrator: JobOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        if self._wired:
            return

        logger.info("Wiring job feature module")

        clock = self._clock or (lambda: Timestamp(time.time()))

        registry = InMemoryJobRegistry(
            policy=self._policy,
            clock=clock,
            cancellation_signaler=self._cancellation_signaler,
            event_publisher=self._event_publisher,
        )

        self._orchestrator = JobOrchestrator(registry)
        self._wired = True

        logger.info("Job feature module wired successfully")

    @property
    def agent(self) -> JobOrchestrator:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("JobContainer not wired — call wire() first")
        return self._orchestrator


def create_job_feature(
    policy: JobPolicy | None = None,
    cancellation_signaler: ICancellationSignaler | None = None,
    event_publisher: IJobEventPublisher | None = None,
    clock: Callable[[], Timestamp] | None = None,
) -> JobOrchestrator:
    container = JobContainer(
        policy=policy,
        cancellation_signaler=cancellation_signaler,
        event_publisher=event_publisher,
        clock=clock,
    )
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

## File: modules/shared/src/common/taxonomy_domain_error.py

```python
"""Domain error types for the BlenderMCP system."""

from __future__ import annotations

from typing import Any

from .taxonomy_core_vo import AssetId, Details, ErrorString, ProviderName


class BlenderMCPError(Exception):
    """Base error for all BlenderMCP exceptions."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        message = message or ErrorString("")
        super().__init__(message)
        self.details = details or {}
        self._error_message: ErrorString = ErrorString(str(message))

    def to_mcp_format(self) -> Any:
        """Serialize error for MCP response."""
        return {
            "code": self.__class__.__name__,
            "message": str(ErrorString(str(self))),
            "details": getattr(self, "details", None),
        }


class DomainError(BlenderMCPError):
    """Base for domain-specific errors in the BlenderMCP system."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        message = message or ErrorString("Domain error")
        super().__init__(message)
        self.details = details or {}
        self._error_message: ErrorString = ErrorString(str(message))

    def to_mcp_format(self) -> Any:
        """Serialize error for MCP response."""
        return {
            "code": self.__class__.__name__,
            "message": str(ErrorString(str(self))),
            "details": getattr(self, "details", None),
        }


class SceneValidationError(DomainError):
    """Raised when a scene invariant is violated or validation fails."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Scene validation failed"))


class AssetNotFoundError(DomainError):
    """Raised when an asset is not found in a provider's database."""

    def __init__(self, asset_id: AssetId, provider: ProviderName):
        super().__init__(ErrorString(f"Asset {asset_id} not found in provider {provider}"))
        self.asset_id = asset_id
        self.provider = provider


class ValidationError(DomainError):
    """Raised when input parameters fail domain validation rules or constraints."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Input validation failed"))


class ConnectionError(DomainError):
    """Raised when a persistent connection to an external service or socket fails."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Connection failed"))


class ProviderError(DomainError):
    """Raised when an external asset provider returns an error."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Provider error"))


class ExecutionError(DomainError):
    """Raised when a command execution in Blender fails or returns a runtime error."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Execution failed"))


class BlenderConnectionFailure(ConnectionError):  # noqa: N818
    """Raised when the specific socket connection to the Blender instance is lost."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Blender connection lost"))


class InvalidCommandError(DomainError):
    """Raised when a command string is not recognized by the internal dispatcher."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Invalid command"))
```

---

## File: modules/shared/src/gateway/taxonomy_gateway_error.py

```python
"""Taxonomy error types for gateway and server domains.

Gateway errors (lines 8-56): simple exceptions for transport/connection failures.
Server errors (lines 57+): MCP-serializable errors with code/message/details.
All errors use explicit typed classes — no bare strings.
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import ErrorMessage, ErrorString


class GatewayError(Exception):
    """Base error for all gateway domain exceptions."""


class ConnectionError(GatewayError):
    """Connection failed, refused, or lost."""


class TimeoutError(GatewayError):
    """Transport timeout, execution timeout, or queue wait timeout exceeded."""


class ProtocolVersionMismatchError(GatewayError):
    """Protocol version incompatible between application and Blender bridge."""


class ChannelConflictError(GatewayError):
    """Queue conflict, queue depth limit reached, or serialization contention."""


class TransportParseError(GatewayError):
    """Malformed frame or unparseable response content."""


class PayloadLimitError(GatewayError):
    """Request or response exceeded configured payload size."""


class ServerError(Exception):
    """Base error for all server-domain exceptions.

    Provides structured error info with code/message/details for
    MCP error serialization and observability.
    """

    def __init__(self, code: ErrorString, message: ErrorMessage, _details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = _details or {}  # type: ignore[dict-item]
        super().__init__(f"[{code}] {message}")

    def to_mcp_format(self) -> dict:  # noqa: ANN004
        """Serialize error for MCP response."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ─── Security Errors ──────────────────────────────────────────────


class SecurityViolationError(ServerError):
    """Raised when user-provided code contains blocked patterns or violates sandbox policy."""

    def __init__(self, message: str = "Security violation", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("security_violation", message, _details)


# ─── Execution Errors ──────────────────────────────────────────────


class ExecutionTimeoutError(ServerError):
    """Raised when code execution exceeds the configured timeout."""

    def __init__(self, timeout_ms: float = 30_000.0, _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("execution_timeout", f"Execution exceeded {timeout_ms}ms", {"timeout_ms": timeout_ms})


class CommandTimeoutError(ServerError):
    """Raised when a command response exceeds the configured timeout."""

    def __init__(self, action: str = "", timeout_ms: float = 5_000.0, _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__(
            "command_timeout",
            f"Command '{action}' timed out after {timeout_ms}ms",
            {"action": action, "timeout_ms": timeout_ms},
        )


# ─── Queue Errors (renamed v2.0.0) ──────────────────────────────


class TooManyPendingOperationsError(ServerError):
    """Raised when the serialized execution queue has reached maximum depth.

    Renamed from QueueFullError in v2.0.0.
    Error code: 'too_many_pending_operations'
    """

    def __init__(self, max_depth: int = 50, request_id: str | None = None, _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__(
            "too_many_pending_operations",
            f"Queue full (depth={max_depth})",
            {"max_depth": max_depth, "request_id": request_id, **(_details or {})},
        )


class OperationWaitTimeoutError(ServerError):
    """Raised when a queued operation exceeds the configured wait timeout.

    Renamed from QueueTimeoutError in v2.0.0.
    Error code: 'operation_wait_timeout'
    """

    def __init__(self, request_id: str = "", timeout_ms: float = 10_000.0, _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__(
            "operation_wait_timeout",
            f"Operation wait timeout for {request_id}",
            {"request_id": request_id, "timeout_ms": timeout_ms},
        )


# ─── Task Errors ────────────────────────────────────────────────


class TaskNotFoundError(ServerError):
    """Raised when polling an unknown or expired async task."""

    def __init__(self, task_id: str = "", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("task_not_found", f"Task not found: {task_id}", {"task_id": task_id})


# ─── Connection Errors ──────────────────────────────────────────


class ConnectionConfigError(ServerError):
    """Raised when connection factory receives invalid configuration."""

    def __init__(self, message: str = "Connection config error", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_config_error", message, _details)


class AuthenticationError(ServerError):
    """Raised when connection authentication fails."""

    def __init__(self, message: str = "Authentication failed", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("authentication_failed", message, _details)


class VersionMismatchError(ServerError):
    """Raised when server and Blender addon protocol versions are incompatible.

    Renamed from ProtocolVersionMismatchError in v2.0.0.
    Error code: 'version_mismatch'
    """

    def __init__(self, expected: str = "", actual: str = "", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__(
            "version_mismatch",
            f"Expected major version {expected}, got {actual}",
            {"expected": expected, "actual": actual},
        )


class ConnectionClosedError(ServerError):
    """Raised when an operation is rejected after graceful disconnect."""

    def __init__(self, _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_closed", "Connection already closed", _details)


class BlenderConnectionExhausted(ServerError):  # noqa: N818
    """Raised after all reconnect attempts have been exhausted."""

    def __init__(self, attempts: int = 3, _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__(
            "connection_retries_exhausted", f"All {attempts} reconnect attempts failed", {"attempts": attempts}
        )


class BlenderConnectionFailure(ServerError):  # noqa: N818
    """Raised when connection is lost or unavailable."""

    def __init__(self, message: str = "Blender connection failure", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("blender_connection_failure", message, _details)


# ─── Validation Errors ──────────────────────────────────────────


class ValidationError(ServerError):
    """Raised for unknown commands, invalid parameters, or syntax errors."""

    def __init__(
        self, message: str = "Validation error", code: str = "validation_error", _details: dict | None = None
    ) -> None:  # noqa: ANN004
        super().__init__(code, message, _details)


# ─── Adapter / Surface Errors ────────────────────────────────────


class ProviderError(ServerError):
    """Raised when Blender addon returns a command-specific failure."""

    def __init__(self, message: str = "Provider error", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("provider_error", message, _details)


class ExecutionError(ServerError):
    """Raised when Blender code execution returns a runtime failure."""

    def __init__(self, message: str = "Execution error", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("execution_error", message, _details)


class AdapterSurfaceError(ServerError):
    """Raised when an unexpected adapter surface failure occurs."""

    def __init__(self, message: str = "Adapter surface error", _details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("adapter_surface_error", message, _details)
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
# modules/shared/src/job/contract_job_aggregate.py
from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import JobId
from .taxonomy_job_vo import (
    CancellationResult,
    CancelTaskCommand,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    FailTaskCommand,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


class IJobAggregate(ABC):
    @abstractmethod
    def submit_task(self, command: CreateTaskCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def start_task(self, job_id: JobId) -> JobStatusSnapshot: ...

    @abstractmethod
    def update_progress(self, command: ProgressUpdateCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def complete_task(self, command: CompleteTaskCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def fail_task(self, command: FailTaskCommand) -> JobStatusSnapshot: ...

    @abstractmethod
    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult: ...

    @abstractmethod
    def get_task_status(self, job_id: JobId) -> JobStatusSnapshot: ...

    @abstractmethod
    def cleanup_expired_tasks(self) -> CleanupSummary: ...

    @abstractmethod
    def get_capacity_status(self) -> CapacityStatus: ...
```

---

## File: modules/shared/src/job/contract_job_protocol.py

```python
# modules/shared/src/job/contract_job_protocol.py
from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import JobId
from .taxonomy_job_vo import (
    CancellationReason,
    CancellationResult,
    CancelTaskCommand,
    CapacityStatus,
    CleanupSummary,
    CompleteTaskCommand,
    CreateTaskCommand,
    FailTaskCommand,
    JobStatusSnapshot,
    ProgressUpdateCommand,
)


class IJobRegistry(ABC):
    """Protocol contract for job state management capability."""

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
    def cancel_task(self, command: CancelTaskCommand) -> CancellationResult: ...

    @abstractmethod
    def get_snapshot(self, job_id: JobId) -> JobStatusSnapshot: ...

    @abstractmethod
    def cleanup_expired(self) -> CleanupSummary: ...

    @abstractmethod
    def capacity_status(self) -> CapacityStatus: ...


class ICancellationSignaler(ABC):
    """Protocol contract for signaling job cancellation to the executor."""

    @abstractmethod
    def signal(self, job_id: JobId, reason: CancellationReason | None) -> bool: ...


class IJobEventPublisher(ABC):
    """Protocol contract for publishing job lifecycle events."""

    @abstractmethod
    def publish(self, event: str, payload: Mapping[str, Any]) -> None: ...
```

---

## File: modules/shared/src/job/taxonomy_job_error.py

```python
# modules/shared/src/job/taxonomy_job_error.py
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


class ValidationError(JobError):
    """Raised when input validation fails."""

    def __init__(self, message: ErrorString) -> None:
        super().__init__(message)
```

---

## File: modules/shared/src/job/taxonomy_job_state_constant.py

```python
# modules/shared/src/job/taxonomy_job_state_constant.py
from __future__ import annotations

from collections.abc import Mapping
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

# ============================================================
# STATE SETS
# ============================================================
ACTIVE_JOB_STATES: Final[frozenset[JobState]] = frozenset(
    {
        JOB_STATE_PENDING,
        JOB_STATE_RUNNING,
    }
)

TERMINAL_JOB_STATES: Final[frozenset[JobState]] = frozenset(
    {
        JOB_STATE_COMPLETED,
        JOB_STATE_FAILED,
        JOB_STATE_CANCELLED,
        JOB_STATE_TIMED_OUT,
    }
)

# ============================================================
# VALID TRANSITIONS
# ============================================================
VALID_JOB_TRANSITIONS: Final[Mapping[JobState, frozenset[JobState]]] = {
    JOB_STATE_PENDING: frozenset(
        {
            JOB_STATE_RUNNING,
            JOB_STATE_CANCELLED,
        }
    ),
    JOB_STATE_RUNNING: frozenset(
        {
            JOB_STATE_COMPLETED,
            JOB_STATE_FAILED,
            JOB_STATE_CANCELLED,
            JOB_STATE_TIMED_OUT,
        }
    ),
    JOB_STATE_COMPLETED: frozenset(),
    JOB_STATE_FAILED: frozenset(),
    JOB_STATE_CANCELLED: frozenset(),
    JOB_STATE_TIMED_OUT: frozenset(),
}

# ============================================================
# CANCELLATION OUTCOMES
# ============================================================
CANCELLATION_OUTCOME_ACCEPTED: Final[str] = "ACCEPTED"
CANCELLATION_OUTCOME_ALREADY_TERMINAL: Final[str] = "ALREADY_TERMINAL"
CANCELLATION_OUTCOME_NOT_FOUND: Final[str] = "NOT_FOUND"
CANCELLATION_OUTCOME_UNSUPPORTED: Final[str] = "UNSUPPORTED"
```

---

## File: modules/shared/src/job/taxonomy_job_status_entity.py

```python
# modules/shared/src/job/taxonomy_job_status_entity.py
from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    ResultUrl,
    Timestamp,
)
from .taxonomy_job_state_constant import (
    ACTIVE_JOB_STATES,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
    TERMINAL_JOB_STATES,
)
from .taxonomy_job_vo import (
    CancellationReason,
    CorrelationId,
    ErrorCategory,
    JobStatusSnapshot,
    OperationType,
    ProgressMessage,
)


@dataclass
class JobRecord:
    """
    Mutable internal job record.

    This is an internal state holder, not a public read model.
    Business rules should be applied by capabilities, not by direct mutation.
    """

    job_id: JobId
    operation_type: OperationType
    created_at: Timestamp
    updated_at: Timestamp

    correlation_id: CorrelationId | None = None
    metadata: dict[str, str] = field(default_factory=dict)

    state: JobState = JOB_STATE_PENDING
    progress: Progress = Progress(0.0)
    progress_message: ProgressMessage | None = None

    result_url: ResultUrl | None = None
    error: ErrorString | None = None
    error_category: ErrorCategory | None = None
    cancellation_reason: CancellationReason | None = None

    started_at: Timestamp | None = None
    finished_at: Timestamp | None = None
    last_progress_at: Timestamp | None = None

    def to_snapshot(self) -> JobStatusSnapshot:
        return JobStatusSnapshot(
            job_id=self.job_id,
            state=self.state,
            operation_type=self.operation_type,
            created_at=self.created_at,
            updated_at=self.updated_at,
            progress=self.progress,
            progress_message=self.progress_message,
            result_url=self.result_url,
            error=self.error,
            error_category=self.error_category,
            correlation_id=self.correlation_id,
            started_at=self.started_at,
            finished_at=self.finished_at,
            metadata=tuple(sorted(self.metadata.items())),
            is_terminal=self.state in TERMINAL_JOB_STATES,
            is_cancellable=self.state in ACTIVE_JOB_STATES,
            progress_applicable=self.state == JOB_STATE_RUNNING,
        )
```

---

## File: modules/shared/src/job/taxonomy_job_vo.py

```python
# modules/shared/src/job/taxonomy_job_vo.py
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import NewType

from ..common.taxonomy_core_vo import (
    ErrorString,
    JobId,
    JobState,
    Progress,
    ResultUrl,
    Timestamp,
)

# ============================================================
# JOB-SPECIFIC VOs
# ============================================================
OperationType = NewType("OperationType", str)
CorrelationId = NewType("CorrelationId", str)
ProgressMessage = NewType("ProgressMessage", str)
CancellationReason = NewType("CancellationReason", str)
ErrorCategory = NewType("ErrorCategory", str)
TaskMetadata = NewType("TaskMetadata", Mapping[str, str])


# ============================================================
# POLICY / CONFIG VO
# ============================================================
@dataclass(frozen=True)
class JobPolicy:
    """Runtime policy for job tracking, capacity, retention, and recovery."""

    max_active: int = 100
    retention_seconds: float = 3600.0
    max_records: int = 1000
    stale_recovery_enabled: bool = True
    stale_running_lifetime_seconds: float = 1800.0
    progress_throttle_seconds: float = 0.5
    count_pending_toward_capacity: bool = True


# ============================================================
# COMMANDS
# ============================================================
@dataclass(frozen=True)
class CreateTaskCommand:
    operation_type: OperationType
    correlation_id: CorrelationId | None = None
    metadata: TaskMetadata | None = None


@dataclass(frozen=True)
class ProgressUpdateCommand:
    job_id: JobId
    progress: Progress
    message: ProgressMessage | None = None


@dataclass(frozen=True)
class CompleteTaskCommand:
    job_id: JobId
    result_url: ResultUrl | None = None
    summary: ProgressMessage | None = None


@dataclass(frozen=True)
class FailTaskCommand:
    job_id: JobId
    error_message: ErrorString
    error_category: ErrorCategory | None = None


@dataclass(frozen=True)
class CancelTaskCommand:
    job_id: JobId
    reason: CancellationReason | None = None


# ============================================================
# READ MODELS / RESULTS
# ============================================================
@dataclass(frozen=True)
class JobStatusSnapshot:
    job_id: JobId
    state: JobState
    operation_type: OperationType
    created_at: Timestamp
    updated_at: Timestamp

    progress: Progress = Progress(0.0)
    progress_message: ProgressMessage | None = None
    result_url: ResultUrl | None = None
    error: ErrorString | None = None
    error_category: ErrorCategory | None = None
    correlation_id: CorrelationId | None = None

    started_at: Timestamp | None = None
    finished_at: Timestamp | None = None

    metadata: tuple[tuple[str, str], ...] = field(default_factory=tuple)

    is_terminal: bool = False
    is_cancellable: bool = False
    progress_applicable: bool = False


@dataclass(frozen=True)
class CancellationResult:
    job_id: JobId
    accepted: bool
    outcome: str
    message: str


@dataclass(frozen=True)
class CleanupSummary:
    purged: int
    retained: int
    reclaimed_capacity: int
    warnings: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True)
class CapacityStatus:
    active: int
    limit: int
    available: int
```

---

## File: modules/shared/src/job/utility_job_sanitizer.py

```python
# modules/shared/src/job/utility_job_sanitizer.py
from __future__ import annotations

import re
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import ErrorString
from .taxonomy_job_vo import CancellationReason

_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_SENSITIVE_KEYS = frozenset({"password", "token", "secret", "api_key", "auth"})


def sanitize_text(value: str, max_length: int) -> str:
    """Strip control characters and truncate to max_length."""
    cleaned = _CONTROL_CHARS.sub("", value).strip()
    return cleaned[:max_length]


def sanitize_error(value: ErrorString) -> ErrorString:
    """Sanitize an error string, preserving type."""
    return ErrorString(sanitize_text(str(value), 500))


def sanitize_progress_message(value: Any | None) -> str | None:
    """Sanitize an optional progress message string."""
    if value is None:
        return None
    cleaned = sanitize_text(str(value), 500)
    return cleaned if cleaned else None


def sanitize_cancellation_reason(value: CancellationReason | None) -> CancellationReason | None:
    """Sanitize an optional cancellation reason."""
    if value is None:
        return None
    cleaned = sanitize_text(str(value), 500)
    return CancellationReason(cleaned) if cleaned else None


def redact_metadata(metadata: Mapping[str, Any] | None) -> dict[str, Any]:
    """Shallow-copy metadata, redacting values for known sensitive keys."""
    if not metadata:
        return {}
    return {
        k: ("***" if k.lower() in _SENSITIVE_KEYS else v)
        for k, v in metadata.items()
    }
```

---

## File: modules/shared/src/security/__init__.py

```python
"""Security domain — taxonomy types and contracts.

Provides Value Objects, Entities, Events, Errors, Constants,
5 individual Protocol interfaces, and Aggregate facade for all 5 security operations per the Security FRD.
"""

from . import (
    taxonomy_security_constant,
    taxonomy_security_error,
    taxonomy_security_event,
    taxonomy_security_vo,
)
from .contract_emit_audit_protocol import EmitAuditProtocol
from .contract_extract_archive_protocol import ExtractArchiveProtocol
from .contract_redact_sensitive_protocol import RedactSensitiveProtocol
from .contract_security_operate_aggregate import ISecurityOperateAggregate
from .contract_validate_code_protocol import ValidateCodeProtocol
from .contract_validate_path_protocol import ValidatePathProtocol

__all__ = [
    "EmitAuditProtocol",
    "ExtractArchiveProtocol",
    "RedactSensitiveProtocol",
    "ISecurityOperateAggregate",
    "ValidateCodeProtocol",
    "ValidatePathProtocol",
    "taxonomy_security_constant",
    "taxonomy_security_error",
    "taxonomy_security_event",
    "taxonomy_security_vo",
]
```

---

## File: modules/shared/src/security/taxonomy_security_error.py

```python
"""Security domain — Error types for path, archive, code, redaction, and audit failures.

All errors subclass SecurityError with explicit error codes.
"""

from __future__ import annotations

from modules.shared.src.common.taxonomy_core_vo import ErrorMessage
from modules.shared.src.security.taxonomy_security_vo import (
    ErrorCategory,
    FilePath,
    FileSize,
    MetadataMap,
)

# ─── Default Message Constants ──────────────────────────────────

_DEFAULT_ARCHIVE_SAFETY_MESSAGE: ErrorMessage = ErrorMessage("Archive safety violation")
_DEFAULT_ARCHIVE_BOMB_MESSAGE: ErrorMessage = ErrorMessage("Archive bomb detected")
_DEFAULT_CODE_VALIDATION_MESSAGE: ErrorMessage = ErrorMessage("Code validation failed")
_DEFAULT_REDACTION_MESSAGE: ErrorMessage = ErrorMessage("Redaction failed")
_DEFAULT_AUDIT_EMISSION_MESSAGE: ErrorMessage = ErrorMessage("Audit emission failed")
_DEFAULT_VALIDATION_MESSAGE: ErrorMessage = ErrorMessage("Validation error")

# ─── Default Path Constants ─────────────────────────────────────

_EMPTY_PATH: FilePath = FilePath("")

# ─── Default FileSize Constants ─────────────────────────────────

_DEFAULT_FILE_SIZE_ZERO: FileSize = FileSize(0)


class SecurityError(Exception):
    """Base error for all security-domain exceptions."""

    def __init__(self, code: ErrorCategory, message: str, details: MetadataMap | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ─── Path Validation Errors ─────────────────────────────────────


class PathTraversalError(SecurityError):
    """Raised when a path traversal attempt is detected."""

    def __init__(self, path: FilePath = _EMPTY_PATH, details: MetadataMap | None = None) -> None:
        super().__init__(
            ErrorCategory("path_traversal"),
            f"Path traversal detected: {path}",
            {"path": path, **(details or {})},
        )


class UnauthorizedAccessError(SecurityError):
    """Raised when a path is outside allowed directories."""

    def __init__(self, path: FilePath = _EMPTY_PATH, details: MetadataMap | None = None) -> None:
        super().__init__(
            ErrorCategory("unauthorized_access"),
            f"Access denied: {path}",
            {"path": path, **(details or {})},
        )


class SymlinkEscapeError(SecurityError):
    """Raised when a symbolic link escapes allowed directories."""

    def __init__(self, path: FilePath = _EMPTY_PATH, details: MetadataMap | None = None) -> None:
        super().__init__(
            ErrorCategory("symlink_escape"),
            f"Symbolic link escape: {path}",
            {"path": path, **(details or {})},
        )


# ─── Archive Safety Errors ──────────────────────────────────────


class ArchiveSafetyError(SecurityError):
    """Raised when archive extraction violates safety policy."""

    def __init__(self, message: ErrorMessage | None = None, details: MetadataMap | None = None) -> None:
        super().__init__(ErrorCategory("archive_safety"), message or _DEFAULT_ARCHIVE_SAFETY_MESSAGE, details)


class ArchiveBombError(SecurityError):
    """Raised when an archive bomb pattern is detected."""

    def __init__(self, message: ErrorMessage | None = None, details: MetadataMap | None = None) -> None:
        super().__init__(ErrorCategory("archive_bomb"), message or _DEFAULT_ARCHIVE_BOMB_MESSAGE, details)


# ─── Code Validation Errors ─────────────────────────────────────


class CodeValidationError(SecurityError):
    """Raised when untrusted code fails validation."""

    def __init__(self, message: ErrorMessage | None = None, details: MetadataMap | None = None) -> None:
        super().__init__(ErrorCategory("code_validation"), message or _DEFAULT_CODE_VALIDATION_MESSAGE, details)


class CodeOversizedError(SecurityError):
    """Raised when code exceeds maximum allowed size."""

    def __init__(
        self,
        size: FileSize = _DEFAULT_FILE_SIZE_ZERO,
        max_size: FileSize = _DEFAULT_FILE_SIZE_ZERO,
        details: MetadataMap | None = None,
    ) -> None:
        super().__init__(
            ErrorCategory("code_oversized"),
            ErrorMessage(f"Code payload too large: {size} bytes (max: {max_size})"),
            {"size": size, "max_size": max_size, **(details or {})},
        )


# ─── Redaction Errors ───────────────────────────────────────────


class RedactionError(SecurityError):
    """Raised when sensitive value redaction fails."""

    def __init__(self, message: ErrorMessage | None = None, details: MetadataMap | None = None) -> None:
        super().__init__(ErrorCategory("redaction_error"), message or _DEFAULT_REDACTION_MESSAGE, details)


# ─── Audit Errors ───────────────────────────────────────────────


class AuditEmissionError(SecurityError):
    """Raised when audit event delivery fails."""

    def __init__(self, message: ErrorMessage | None = None, details: MetadataMap | None = None) -> None:
        super().__init__(ErrorCategory("audit_emission"), message or _DEFAULT_AUDIT_EMISSION_MESSAGE, details)


# ─── Policy Errors ──────────────────────────────────────────────


class ValidationError(SecurityError):
    """Raised for malformed request or invalid security policy input."""

    def __init__(self, message: ErrorMessage | None = None, details: MetadataMap | None = None) -> None:
        super().__init__(ErrorCategory("validation_error"), message or _DEFAULT_VALIDATION_MESSAGE, details)
```

---

## File: modules/shared/src/security/taxonomy_security_vo.py

```python
"""Security domain — Value Objects for path validation, archive safety, code validation, redaction, and audit.

Frozen dataclasses with explicit types. All VOs are immutable.
Input and output fields live in a single VO per concept.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from enum import Enum
from typing import Any, NewType

# ============================================================
# Access Mode
# ============================================================


class AccessMode(str, Enum):
    """File access mode for path validation."""

    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    EXTRACT = "extract"


# ============================================================
# Path Validation (FR-SEC-001)
# ============================================================


@dataclass(frozen=True)
class PathValidationVO:
    """Unified path validation — input and output in one VO.

    Caller sets target_path, access_mode, base_directory, operation_context.
    Callee sets allowed, canonical_path, denial_reason, audit_metadata.
    """

    # Input
    target_path: str = ""
    access_mode: AccessMode = AccessMode.READ
    base_directory: str | None = None
    operation_context: str | None = None
    # Output
    allowed: bool = False
    canonical_path: str | None = None
    denial_reason: str | None = None
    audit_metadata: dict = dc_field(default_factory=dict)


# ============================================================
# Archive Extraction (FR-SEC-002)
# ============================================================


@dataclass(frozen=True)
class ArchiveEntryVO:
    """Metadata for a single archive entry."""

    entry_path: str
    is_directory: bool = False
    is_symbolic_link: bool = False
    is_hard_link: bool = False
    compressed_size: int = 0
    uncompressed_size: int = 0


@dataclass(frozen=True)
class ArchiveExtractionOptionsVO:
    """Options controlling archive extraction safety."""

    max_depth: int = 5
    max_total_size: int = 104_857_600  # 100 MB
    max_entry_size: int = 10_485_760  # 10 MB
    max_entry_count: int = 1_000
    allow_symbolic_links: bool = False
    allow_hard_links: bool = False


@dataclass(frozen=True)
class RejectedEntryVO:
    """A rejected archive entry with reason."""

    entry_path: str
    reason: str


@dataclass(frozen=True)
class ArchiveExtractionVO:
    """Unified archive extraction — input and output in one VO.

    Caller sets destination_directory, entries, options.
    Callee sets allowed, safe_destination, rejected_entries, warnings, audit_metadata.
    """

    # Input
    destination_directory: str = ""
    entries: tuple[ArchiveEntryVO, ...] = dc_field(default_factory=tuple)
    options: ArchiveExtractionOptionsVO = dc_field(default_factory=ArchiveExtractionOptionsVO)
    # Output
    allowed: bool = False
    safe_destination: str | None = None
    rejected_entries: tuple[RejectedEntryVO, ...] = dc_field(default_factory=tuple)
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    audit_metadata: dict = dc_field(default_factory=dict)


# ============================================================
# Code Validation (FR-SEC-003)
# ============================================================


@dataclass(frozen=True)
class CodeViolationVO:
    """A single code validation violation."""

    category: str
    description: str
    location_hint: str | None = None


@dataclass(frozen=True)
class CodeValidationVO:
    """Unified code validation — input and output in one VO.

    Caller sets code_text, max_code_size, strict_mode, execution_context.
    Callee sets allowed, violations, redacted_metadata, audit_metadata.
    """

    # Input
    code_text: str = ""
    max_code_size: int = 1_048_576  # 1 MB
    strict_mode: bool = True
    execution_context: str | None = None
    # Output
    allowed: bool = False
    violations: tuple[CodeViolationVO, ...] = dc_field(default_factory=tuple)
    redacted_metadata: dict = dc_field(default_factory=dict)
    audit_metadata: dict = dc_field(default_factory=dict)


# ============================================================
# Redaction (FR-SEC-004)
# ============================================================


class SensitivityLevel(str, Enum):
    """Sensitivity level for redaction."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RedactionVO:
    """Unified redaction — input and output in one VO.

    Caller provides ``text`` (the value to redact) as input.
    Callee returns ``text`` as the redacted (safe) output and also populates
    ``redacted_text``, ``redacted_count``, ``failed``, ``failure_reason``.
    The returned RedactionVO never contains the original secret (FR-SEC-004):
    on success ``text`` is the redacted value; on failure it is masked.
    """

    # Input
    text: str = ""
    sensitivity_level: SensitivityLevel = SensitivityLevel.HIGH
    patterns: tuple[str, ...] = dc_field(default_factory=tuple)
    key_names: tuple[str, ...] = dc_field(default_factory=tuple)
    # Output
    redacted_text: str = ""
    redacted_count: int = 0
    failed: bool = False
    failure_reason: str | None = None


# ============================================================
# Audit Events (FR-SEC-005)
# ============================================================


class AuditSeverity(str, Enum):
    """Audit event severity level."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ViolationCategory(str, Enum):
    """Security violation category."""

    PATH_TRAVERSAL = "path_traversal"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    UNSAFE_ARCHIVE_ENTRY = "unsafe_archive_entry"
    CODE_VIOLATION = "code_violation"
    REDACTION_FAILURE = "redaction_failure"
    PERMISSION_DENIED = "permission_denied"
    POLICY_OVERRIDE = "policy_override"


@dataclass(frozen=True)
class SecurityAuditEventVO:
    """Unified security audit event — input context and emitted event in one VO.

    Caller sets violation_category, operation_type, source_feature, severity, etc.
    Callee sets event_id, timestamp, policy_mode.
    """

    # Input (context)
    violation_category: ViolationCategory = ViolationCategory.PATH_TRAVERSAL
    operation_type: str = ""
    source_feature: str = ""
    target_metadata: dict = dc_field(default_factory=dict)
    severity: AuditSeverity = AuditSeverity.WARNING
    correlation_id: str | None = None
    redacted_reason: str | None = None
    # Output (emitted event)
    event_id: str = ""
    timestamp: float = 0.0
    policy_mode: str = "strict"


# ============================================================
# Security Policy Config
# ============================================================


@dataclass(frozen=True)
class SecurityPolicyVO:
    """Security policy configuration."""

    allowed_directories: tuple[str, ...] = ()
    archive_max_depth: int = 5
    archive_max_total_size: int = 104_857_600
    archive_max_entry_count: int = 1_000
    archive_allow_symbolic_links: bool = False
    code_validation_enabled: bool = True
    blocked_code_constructs: tuple[str, ...] = dc_field(default_factory=tuple)
    max_code_size: int = 1_048_576
    redaction_patterns: tuple[str, ...] = dc_field(default_factory=tuple)
    redaction_debug_mode: bool = False
    security_policy_mode: str = "strict"


# ============================================================
# Error Domain Types
# ============================================================

ErrorCategory = NewType("ErrorCategory", str)
FilePath = NewType("FilePath", str)
FileSize = NewType("FileSize", int)

# ============================================================
# Metadata Type
# ============================================================

MetadataMap = dict[str, Any]
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

