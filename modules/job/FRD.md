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
