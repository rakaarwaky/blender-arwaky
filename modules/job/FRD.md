# FRD — Background Job Tracking Feature

## Purpose

Single authority for background task records. Domain features register long-running work through the job feature, update through it, and expose outcomes through it. One consistent, pollable, auditable view of every long-running operation regardless of which feature performs the work.

## Scope

- Task creation with collision-resistant unique ID
- Task state machine and terminal state enforcement
- Progress reporting with bounded percentage
- Cancellation request + execution layer signaling
- Final result reference delivery
- Error state capture with sanitized detail
- Retention and automatic cleanup
- Capacity limit enforcement for concurrent background work
- Real-time status snapshots for polling consumers
- Correlation with request tracking IDs
- Stale running task detection
- Lifecycle observability events

## Out of Scope

Execution logic, download logic, render logic, code execution logic, connection state, metrics storage (diagnostics), persistence beyond application memory, result artifact storage, push notification/streaming, retry/resubmission policy.

## Depends On

config (capacity, retention, cleanup interval, staleness), diagnostics (lifecycle event delivery).

## Provides To

dispatcher, asset, render, gateway — any feature executing long-running tracked work.

## Functional Requirements

### FR-JOB-001: Track and Update Task Lifecycle

- **Description**: Create background task records and move through strictly enforced state machine until terminal state
- **Input**: Task creation (operation type, optional correlation ID, optional non-sensitive metadata); State update (task ID, target state, optional result ref, optional error detail, optional transition reason)
- **Output**: Task record (ID, state, timestamps, terminal outcome)
- **Rules**: Every background task registered through job before execution. Task ID unique and collision-resistant. Initial state: pending with creation timestamp. Valid transitions: pending→running, running→completed/failed, pending→cancelled, running→cancelled. Extended: running→timed out (optional, for stale recovery). No backward transitions. Terminal states immutable (except cleanup). Every transition updates last-updated timestamp. Running→record started timestamp. Terminal→record finished timestamp. Completed→may carry result ref. Failed→must carry error message + may carry category. Error detail sanitized before storage (no secrets/raw code). Metadata never contains secrets/credentials/tokens/paths. All transitions atomic + thread-safe. Unknown task ID → task not found error. Correlation ID links to originating request. The default repository is a shared JSON-backed store with atomic temp-file replacement; a new process refreshes records before status lookup or mutation, so CLI status/cancel works across process boundaries. Corrupt or partial stores are ignored safely rather than treated as successful task state.
- **Edge Cases**: Duplicate ID, concurrent transitions, transition after terminal, invalid target state, unknown ID, missing error message on failure, sensitive content in metadata/error, clock skew, creation during cleanup
- **Error Handling**: State error for invalid/out-of-order transitions; task not found error; validation error for malformed metadata; concurrency resolved atomically (first valid transition wins)

### FR-JOB-002: Monitor Task Status

- **Description**: Expose consistent read-only status snapshots for polling consumers, including progress where reported
- **Input**: Task ID
- **Output**: Task status snapshot (state, progress %, progress message, timestamps, result ref, error detail, operation type, correlation ID)
- **Rules**: Read-only, never mutates state. Consistent snapshot even during concurrent updates. Progress % bounded 0–100. Progress updates atomic + monotonic by default. Progress message sanitized. Progress optional per operation type → snapshot indicates N/A. Active vs terminal states clearly distinguished. Result ref only after completed state. Error detail only after failed state. Sensitive metadata redacted before emission. Snapshot exposes cancellability in current state. Lightweight for frequent polling. Progress update frequency may be throttled.
- **Edge Cases**: Unknown/purged task ID, concurrent update during read, progress N/A for operation, non-monotonic progress, oversized progress message, sensitive metadata, polling during transition, excessive frequency
- **Error Handling**: Task not found error; out-of-range/malformed progress → validation error; redaction before emission, never fail snapshot

### FR-JOB-003: Cancel a Task

- **Description**: Accept cancellation requests, signal executing feature, record cancellation atomically
- **Input**: Task ID, optional cancellation reason
- **Output**: Cancellation result (accepted/acknowledged+confirmed/already terminal/unsupported/not found)
- **Rules**: Only for pending or running tasks. Terminal → state error. Pending → cancelled directly without signaling. Running → signal registered execution layer hook (best-effort; final state depends on executor acknowledgment). Task marked cancelled only when transition applied atomically. Race with completion → whichever valid transition applies first; loser gets already-terminal outcome. Reason sanitized before storage. Record remains pollable until retention cleanup. Duplicate → idempotent, returns current state. Emits event when transition applies. The CLI `cancel-task` route is confirmation-protected and uses the same shared store as task producers.
- **Edge Cases**: Missing task, completed/failed task, duplicate request, executor without cancellation support, executor unresponsive after signal, concurrent cancellation+completion race, sensitive content in reason, during cleanup
- **Error Handling**: Task not found error; state error for terminal; unsupported outcome when executor can't be signaled; race → already terminal, not failure

### FR-JOB-004: Automatic Task Record Cleanup

- **Description**: Remove expired + excess terminal task records, protect active tasks
- **Input**: Retention policy from config (duration, interval, max record count)
- **Output**: Cleanup summary (purged count, retained count, reclaimed capacity, warnings)
- **Rules**: Terminal records retained for configured duration. Cleanup sweep at configured interval, lightweight. Purge order: oldest terminal first. Active (pending/running) never purged. Running exceeding max lifetime → timed out (if stale recovery enabled), then normal retention. Capacity pressure → early eviction of oldest terminal outside scheduled sweep. Purged ID → task not found on polling. Safe against concurrent transitions/reads. Corrupt/unreadable records dropped with warning. Summary observable without sensitive metadata. Clock skew must not cause premature purge.
- **Edge Cases**: Retention exceeded, max records exceeded, sweep concurrent with transition/read, stale running occupying capacity, clock skew, empty registry, corrupt record, config change between sweeps, interval shorter than duration
- **Error Handling**: Warnings for corrupt records/partial sweeps; stale running → timed out if policy enabled; sweep failure never blocks task creation/updates

### FR-JOB-005: Enforce Background Capacity

- **Description**: Limit concurrent active background tasks; job feature = only path to background execution
- **Input**: Task creation request against current capacity
- **Output**: Capacity decision (accepted or capacity error + active count)
- **Rules**: Max concurrent count from config. Capacity counts active (pending + running) per configured policy. Atomic with task creation (no race past limit). Limit reached → capacity error. Terminal tasks don't count. Capacity reclaimed automatically on terminal. Domain features must not create/track/run background tasks outside job. Capacity status observable (active count, limit, available slots). Rejection never creates partial/orphan records. Error includes active count for caller retry. Stale running → timed out → releases capacity slot.
- **Edge Cases**: Limit at submission, two submissions racing for final slot, capacity freed during submission, terminal failing to release capacity, stale running occupying indefinitely, miscount after restart with persisted records, runtime config change, burst after release
- **Error Handling**: Capacity error with active count context; rejected submission no partial record; capacity leak suspect → diagnostic warning

### FR-JOB-006: Submit Task Through Public Action

- **Description**: Expose the existing aggregate task creation flow through the canonical dispatcher action.
- **Input**: Required operation type, optional correlation ID, and optional non-sensitive metadata object.
- **Output**: Canonical pending task snapshot.
- **Rules**: Submission must call `JobOrchestrator.submit_task`; capacity is evaluated before record creation. Metadata is normalized to string values and sanitized by the repository. The action registers a task only; it does not pretend to execute the operation. Actual executors must start/update/complete/fail the task through the same aggregate.

### FR-JOB-007: List Task Snapshots

- **Description**: Return pending, running, and retained terminal task snapshots from the shared repository.
- **Input**: No parameters in Wave 1.
- **Output**: Bounded task array and count.
- **Rules**: Read-only. Pending, running, and terminal records are combined with stable ID deduplication. The action never creates, transitions, or purges records. Sensitive metadata remains sanitized by the job repository.

### FR-JOB-008: Read Capacity Status

- **Description**: Return active count, configured limit, and available background slots.
- **Input**: No parameters.
- **Output**: Capacity status read model.
- **Rules**: Read-only and derived from the same lifecycle repository used by submit_task. It must not reserve a slot or mutate task state.

## Error Categories

- task not found — ID not found (including purged)
- capacity error — limit reached at submission
- state error — invalid transition or cancellation of terminal
- validation error — malformed metadata, out-of-range progress, missing required error detail
- concurrency conflict — race loser, reported as already terminal

## Events

- task created (pending, unique ID)
- task started (running + started timestamp)
- task progress updated (throttled)
- task completed (result ref indicator)
- task failed (sanitized error category)
- task cancelled (cancellation outcome)
- task timed out (stale recovery)
- task cleanup sweep (purged + retained counts)
- capacity rejected (limit reached)

Payloads: category, task ID, operation type, state before/after, progress %, correlation ID, duration, sanitized reason. Never: secrets, raw code, sensitive paths, full result payloads, unsanitized error.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| max_concurrent_background_tasks | Active task upper bound | Conservative |
| capacity_counting_policy | pending+running or running only | pending+running |
| retention_duration | Terminal record pollable window | Bounded (hours) |
| cleanup_sweep_interval | Sweep frequency | Periodic (minutes) |
| max_record_count | Total retained limit before early eviction | Conservative |
| stale_running_lifetime | Max running before timed out | Bounded multiple of typical duration |
| stale_recovery_enabled | Auto-timeout stale running | Enabled |
| progress_update_throttle | Min interval between stored updates | Short |

## QA Checklist

- [ ] Task created with unique collision-resistant ID in pending state
- [ ] Transitions: pending→running, running→completed/failed, pending/running→cancelled
- [ ] No backward transitions; terminal immutable
- [ ] Concurrent transitions → first valid wins
- [ ] Unknown ID → task not found error
- [ ] Public submit_task action uses capacity check before record creation and returns pending snapshot
- [ ] list_tasks includes pending, running, and terminal records without duplicate IDs
- [ ] get_capacity_status is read-only and reflects shared repository capacity
- [ ] Status snapshot consistent, read-only, never mutates
- [ ] Progress 0–100, monotonic default
- [ ] Result ref only after completed; error detail only after failed + sanitized
- [ ] Sensitive metadata redacted from snapshot
- [ ] Cancellation signals executor for running; pending → immediate
- [ ] Terminal cancellation → state error
- [ ] Duplicate → idempotent; race → already terminal
- [ ] Capacity limit atomic with creation; terminal releases slot
- [ ] No bypass: domain features cannot run background tasks outside job
- [ ] Capacity error includes active count; no orphan records
- [ ] Stale running → timed out → slot reclaimed (if enabled)
- [ ] Retention sweep: oldest terminal first, active never purged
- [ ] Purged ID → task not found
- [ ] Cleanup safe against concurrent transitions/reads
- [ ] Corrupt record → dropped with warning; clock skew no premature purge
- [ ] All lifecycle events emitted
