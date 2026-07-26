# FRD — Background Job Tracking Feature

## Purpose

Tracks lifecycle of background tasks. Single owner of all background task state.

## Scope

- Task creation
- Task ID
- Task state
- Progress
- Cancellation request
- Final result reference
- Error state
- Retention/cleanup
- Capacity limit

## Out of Scope

- Execution logic
- Download logic
- Render logic
- Code execution logic
- Connection state
- Metrics storage (owner: `diagnostics`)

## Depends On

- `config`
- `diagnostics` (events)

## Provides To

- `dispatcher`
- `asset`
- `render`
- `gateway`

## Functional Requirements

### FR-JOB-001: Track and Update Task Lifecycle

Job creates task with unique ID. Job updates task state through lifecycle: pending -> running -> completed/failed/cancelled.

### FR-JOB-002: Monitor Task Status

Job provides real-time task status. Job exposes progress percentage where applicable.

### FR-JOB-003: Cancel a Task

Job supports cancellation request. Job signals execution layer to stop. Job marks task as cancelled.

### FR-JOB-004: Automatic Task Record Cleanup

Job retains completed tasks for configured duration. Job automatically purges old records. Job enforces capacity limit.

### FR-JOB-005: Enforce Background Capacity

Job enforces max concurrent background tasks. New tasks rejected with CapacityError when limit reached. Domain features must not bypass capacity check.

## Error Categories

- `TaskNotFoundError` — task ID not found
- `CapacityError` — background capacity exceeded
- `StateError` — invalid state transition

## Events

- `job.created` — task created
- `job.started` — task execution started
- `job.progress` — task progress updated
- `job.completed` — task completed
- `job.failed` — task failed
- `job.cancelled` — task cancelled

## Configuration Keys

- `job.max_concurrent` — max concurrent background tasks
- `job.retention_hours` — hours to retain completed tasks
- `job.cleanup_interval` — cleanup sweep interval

## QA Checklist

- [ ] Task created with unique ID
- [ ] State transitions valid (pending->running->completed/failed/cancelled)
- [ ] Status and progress exposed in real-time
- [ ] Cancellation signals execution layer
- [ ] Capacity limit enforced — no bypass
- [ ] Completed tasks cleaned up automatically
- [ ] Domain features cannot run background tasks without job tracking
