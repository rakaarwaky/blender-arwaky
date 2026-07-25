# FRD — job (Job Feature Module)

## System Overview

The job module tracks long-running operations — status updates, progress reporting, and result delivery. It provides the job status entity and state constants.

## Functional Requirements

### FR-JOB-001: Create Job

- **Description**: Create a new job tracker for a long-running operation
- **Input**: Job ID (auto-generated UUID)
- **Output**: JobStatus entity with PENDING state
- **Business Rules**: Job ID must be unique; initial state is PENDING
- **Edge Cases**: Duplicate job ID, invalid ID format
- **Error Handling**: ValidationError for invalid job IDs

### FR-JOB-002: Update Job State

- **Description**: Transition job through state machine (PENDING → RUNNING → COMPLETED/FAILED)
- **Input**: Job ID, target state
- **Output**: Updated JobStatus
- **Business Rules**: Valid state transitions only; no backward transitions
- **Edge Cases**: Invalid transition (e.g., PENDING → COMPLETED), job not found
- **Error Handling**: ValidationError for invalid transitions

### FR-JOB-003: Report Progress

- **Description**: Update job progress as percentage (0-100)
- **Input**: Job ID, progress value
- **Output**: Updated JobStatus with progress
- **Business Rules**: Progress must be 0-100; only valid for RUNNING jobs
- **Edge Cases**: Progress < 0 or > 100, progress on non-running job
- **Error Handling**: ValidationError for out-of-range progress

### FR-JOB-004: Complete Job with Result

- **Description**: Mark job as completed with result URL
- **Input**: Job ID, result URL
- **Output**: Updated JobStatus with COMPLETED state
- **Business Rules**: Only RUNNING jobs can be completed; result URL is optional
- **Edge Cases**: Completing already-completed job, invalid result URL
- **Error Handling**: ValidationError for invalid state transitions

### FR-JOB-005: Fail Job with Error

- **Description**: Mark job as failed with error message
- **Input**: Job ID, error message
- **Output**: Updated JobStatus with FAILED state
- **Business Rules**: Only RUNNING jobs can be failed; error message is required
- **Edge Cases**: Failing already-failed job, empty error message
- **Error Handling**: ValidationError for invalid state transitions

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `create_job_id` | None | JobId | Generate unique job ID |
| `create_progress` | int (0-100) | Progress | Create validated progress value |
| `JobStatus.mark_running` | None | None | Transition to RUNNING |
| `JobStatus.mark_completed` | result_url | None | Transition to COMPLETED |
| `JobStatus.mark_failed` | error | None | Transition to FAILED |

## Integration Points

- **Internal**: shared (taxonomy VOs, job constants)
- **External**: None (pure domain entity)

## Non-functional Requirements (Detailed)

- Performance: State transitions < 1ms
- Reliability: State machine enforced; no invalid transitions possible
- Thread Safety: JobStatus updates must be thread-safe

## Test Scenarios / QA Checklist

- [ ] Create job with auto-generated ID succeeds
- [ ] State transition PENDING → RUNNING succeeds
- [ ] State transition RUNNING → COMPLETED succeeds
- [ ] State transition RUNNING → FAILED succeeds
- [ ] Invalid transition PENDING → COMPLETED raises ValidationError
- [ ] Progress 0-100 accepted for RUNNING jobs
- [ ] Progress outside 0-100 raises ValidationError
- [ ] Duplicate job IDs are rejected

## Assumptions & Constraints

- Jobs are in-memory only (no persistence)
- State machine is strict (no cycles except PENDING → RUNNING → COMPLETED/FAILED)

## Glossary

- **JobStatus**: Entity tracking state and progress of a long-running operation
- **JobState**: Enum of valid job states (PENDING, RUNNING, COMPLETED, FAILED)
- **Progress**: Value object representing 0-100 percentage

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
