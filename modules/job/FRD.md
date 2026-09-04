# FRD — Background Job Tracking Feature

## System Overview
The Job module is the single authority for background task records. Domain features register long-running work through it, update progress, and expose outcomes. It provides a consistent, pollable, auditable view of every long-running operation regardless of the executing feature.

## Functional Requirements

### FR-001: Track and Monitor Task Lifecycle
- **Description**: Create background task records, enforce state machine transitions, and expose status snapshots.
- **Input**: Task creation (operation type, correlation ID, metadata), Task ID (for status).
- **Output**: Task record (ID, state, timestamps, progress %, result ref).
- **Business Rules**: State machine: pending → running → completed/failed/cancelled. No backward transitions. Progress % bounded 0–100. Terminal states immutable. Shared JSON-backed store with atomic temp-file replacement.
- **Edge Cases**: Duplicate ID; concurrent transitions; transition after terminal; sensitive content in metadata.
- **Error Handling**: `state_error` for invalid transitions; `task_not_found` for unknown ID; `validation_error` for malformed metadata.

### FR-002: Cancel Tasks and Enforce Capacity
- **Description**: Accept cancellation requests, signal executing features, and limit concurrent active tasks.
- **Input**: Task ID, cancellation reason, capacity check.
- **Output**: Cancellation result, Capacity decision.
- **Business Rules**: Only pending/running tasks can be cancelled. Running tasks signal registered execution layer hook. Max concurrent count from config. Limit reached triggers `capacity_error`.
- **Edge Cases**: Terminal task cancellation; executor unresponsive; two submissions racing for final slot; stale running occupying capacity.
- **Error Handling**: `state_error` for terminal cancellation; `capacity_error` with active count context; `unsupported` if executor lacks cancellation hook.

### FR-003: Automatic Cleanup and Public Submission
- **Description**: Remove expired terminal records and expose aggregate task creation via canonical action.
- **Input**: Retention policy, operation type, metadata.
- **Output**: Cleanup summary, canonical pending task snapshot.
- **Business Rules**: Terminal records retained for configured duration. Purge order: oldest first. Active tasks never purged. Submission evaluates capacity before record creation.
- **Edge Cases**: Retention exceeded; sweep concurrent with transition; corrupt record; clock skew.
- **Error Handling**: Warnings for corrupt records; `task_not_found` for purged IDs.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `submit_task` | `operation_type`, `metadata` | `TaskRecord` | Create background task record after capacity check; raises `capacity_error` with active count context, `validation_error` for malformed metadata |
| `list_tasks` | None | `TaskRecord[]` | List pending, running, and terminal tasks |
| `get_capacity_status` | None | `CapacityStatus` | Read active count and configured limits |
| `get_task_status` | `task_id` | `TaskStatus` | Query task progress and state; raises `task_not_found` for unknown or purged ID |
| `cancel_task` | `task_id` | `task_cancelled` | Cancel running/pending task via executor hook; raises `state_error` for terminal tasks, `unsupported` if executor lacks cancellation hook |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `config` (capacity/retention settings), `diagnostics` (lifecycle events), `dispatcher` (public submission).

## Non-functional Requirements (Detailed)

- **Performance**: Status snapshots are lightweight for frequent polling. Progress updates throttled.
- **Security**: Sensitive metadata redacted before storage and emission. No secrets/raw code in task records.
- **Scalability**: Capacity limits prevent system exhaustion. Automatic cleanup reclaims slots from terminal/stale tasks.

## Test Scenarios / QA Checklist

- [ ] Verify state machine rejects backward transitions (e.g., completed → running).
- [ ] Verify concurrent transitions resolve atomically (first valid wins).
- [ ] Verify capacity limit triggers `capacity_error` without creating orphan records.
- [ ] Verify retention sweep purges oldest terminal records first and never purges active tasks.
- [ ] Verify stale running tasks are timed out and release capacity slots.

## Assumptions & Constraints

- Domain features must not create or track background tasks outside the Job module.
- The Job module does not execute the work itself; it only tracks the lifecycle.

## Glossary

- **Task State Machine**: Strict lifecycle: pending → running → completed/failed/cancelled.
- **Correlation ID**: Links a background task back to the originating request `TrackingID`.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: `config`, `diagnostics`
