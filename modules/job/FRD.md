
---

# FRD — job (Job Feature Module)

## System Overview

The job module tracks long-running operations for **blender-arwaky** — status updates, progress reporting, cancellation awareness, result delivery, and failure reporting. It provides a job status concept, a strict state machine, progress validation, and terminal result handling.

This module is responsible for representing the lifecycle of asynchronous or long-running operations in a deterministic and thread-safe way. It is used by operations such as rendering, asset download, large import, and other processes that may exceed standard request timeout limits.

The module covers:

- creating job tracking entries
- transitioning job state through a controlled state machine
- reporting progress percentage
- completing jobs with optional result reference
- failing jobs with descriptive error information
- retrieving job status snapshots
- cancelling jobs before or during execution where supported
- expiring and cleaning up in-memory job records

The module does not handle:

- actual execution of long-running operations
- persistence of job records beyond application memory unless explicitly extended
- transport of job updates to clients, which belongs to server or API layer
- storage of result artifacts, which belongs to render, asset, or file handling modules

## Functional Requirements

### FR-JOB-001: Create Job

- **Description**: Create a new job tracker for a long-running operation
- **Input**: Optional operation type, optional correlation identifier, optional metadata; job identifier is auto-generated when not provided
- **Output**: Job status concept with pending state
- **Business Rules**:
  - Job identifier must be unique within active job registry
  - Job identifier should be generated using a collision-resistant unique identifier strategy
  - Initial job state must be pending
  - Initial progress must be zero
  - Creation timestamp must be recorded
  - Last update timestamp must be initialized
  - Optional operation type may describe the kind of long-running operation being tracked
  - Optional correlation identifier may link job to originating request or workflow
  - Optional metadata may include non-sensitive contextual information
  - Job metadata must not include secrets, credentials, tokens, or sensitive payload by default
  - Job registry must reject duplicate job identifiers
  - Job registry may enforce maximum active job limit
  - When maximum active job limit is reached, creation may fail or evict expired terminal jobs based on configuration
- **Edge Cases**: Duplicate job identifier, invalid identifier format, maximum active job limit reached, missing creation timestamp source, invalid metadata, registry unavailable, clock skew
- **Error Handling**: Validation error for invalid job identifiers or invalid metadata; capacity error when maximum active job limit is reached and eviction is not allowed

### FR-JOB-002: Update Job State

- **Description**: Transition job through state machine
- **Input**: Job identifier, target state, optional state transition reason
- **Output**: Updated job status concept
- **Business Rules**:
  - Supported core states include:
    - pending
    - running
    - completed
    - failed
  - Extended states may be supported when enabled by configuration:
    - cancelled
    - timed out
    - expired
  - Valid core state transitions include:
    - pending to running
    - running to completed
    - running to failed
  - Extended valid transitions may include:
    - pending to cancelled
    - running to cancelled
    - running to timed out
    - pending to failed when startup failure is allowed by policy
  - No backward transitions are allowed
  - Terminal states are immutable except for cleanup or expiration handling
  - State transition must update last update timestamp
  - State transition to running should record started timestamp
  - State transition to terminal state should record finished timestamp
  - State transition must be atomic
  - State transition must fail if job identifier is not found
  - State transition may include human-readable reason for observability
  - State transition reason must not include sensitive information
- **Edge Cases**: Invalid transition, job not found, concurrent state transition attempt, transition after terminal state, missing timestamp source, invalid target state, stale job reference
- **Error Handling**: Validation error for invalid transitions; not found error for missing job identifier; concurrency conflict error when atomic transition cannot be applied

### FR-JOB-003: Report Progress

- **Description**: Update job progress as percentage
- **Input**: Job identifier, progress value, optional progress message
- **Output**: Updated job status concept with progress information
- **Business Rules**:
  - Progress value must be numeric percentage between zero and one hundred inclusive
  - Progress updates are valid only for running jobs by default
  - Progress update must not change job state except updating last update timestamp
  - Progress update may include optional progress message
  - Progress message must not include sensitive information
  - Progress updates should be monotonic by default
  - Non-monotonic progress may be allowed only when explicit reset policy is enabled
  - Progress update must be atomic
  - Progress update frequency may be throttled to avoid excessive state churn
  - Final progress may be set to one hundred before completion, but completion transition remains authoritative
  - Progress update on terminal job must be rejected
- **Edge Cases**: Progress below zero, progress above one hundred, non-numeric progress, progress on non-running job, progress on missing job, progress reset attempt, excessive progress updates, stale progress value, concurrent progress updates
- **Error Handling**: Validation error for out-of-range or non-numeric progress; not found error for missing job identifier; state error for progress update on non-running or terminal job

### FR-JOB-004: Complete Job with Result

- **Description**: Mark job as completed with optional result reference
- **Input**: Job identifier, optional result reference, optional completion summary
- **Output**: Updated job status concept with completed state
- **Business Rules**:
  - Only running jobs can be completed by default
  - Result reference is optional
  - Result reference may point to artifact location, rendered output, imported object reference, or structured result metadata
  - Result reference must be valid according to configured reference format when provided
  - Result reference must not expose secrets or sensitive tokens in logs
  - Completion summary may include human-readable result description
  - Completion transition must record finished timestamp
  - Completion transition must set final progress to one hundred when progress tracking is enabled
  - Completion transition must be atomic and terminal
  - Completing already completed job must be rejected
  - Completing failed, cancelled, timed out, or expired job must be rejected
- **Edge Cases**: Completing already completed job, completing non-running job, invalid result reference, oversized completion summary, missing job identifier, concurrent completion attempt, result reference pointing to unavailable artifact
- **Error Handling**: Validation error for invalid state transition or invalid result reference; not found error for missing job identifier; concurrency conflict error when terminal transition cannot be applied

### FR-JOB-005: Fail Job with Error

- **Description**: Mark job as failed with error message
- **Input**: Job identifier, error message, optional error category, optional error details
- **Output**: Updated job status concept with failed state
- **Business Rules**:
  - Only running jobs can be failed by default
  - Error message is required
  - Error category may be provided to classify failure
  - Error details may include non-sensitive diagnostic information
  - Error message and error details must not include secrets, credentials, tokens, or sensitive user data
  - Failure transition must record finished timestamp
  - Failure transition must be atomic and terminal
  - Failing already failed job must be rejected
  - Failing completed, cancelled, timed out, or expired job must be rejected
  - Failure reason should be preserved for polling and diagnostics
- **Edge Cases**: Failing already failed job, failing non-running job, empty error message, oversized error details, missing job identifier, concurrent failure attempt, sensitive data in error payload
- **Error Handling**: Validation error for invalid state transition or empty error message; not found error for missing job identifier; concurrency conflict error when terminal transition cannot be applied

### FR-JOB-006: Retrieve Job Status

- **Description**: Retrieve current job status snapshot
- **Input**: Job identifier
- **Output**: Job status snapshot containing state, progress, timestamps, result reference, error information, and metadata
- **Business Rules**:
  - Retrieval operation is read-only
  - Retrieval operation must return consistent snapshot of job state
  - Retrieval operation must not mutate job state
  - Retrieval operation should include:
    - job identifier
    - current state
    - progress value
    - progress message when available
    - creation timestamp
    - last update timestamp
    - started timestamp when available
    - finished timestamp when available
    - result reference when completed
    - error message and error category when failed
    - operation type when available
    - correlation identifier when available
  - Retrieval of missing job returns not found result
  - Retrieval may expose whether job is terminal
  - Retrieval should redact sensitive metadata before returning result
  - Retrieval may be used for polling by higher-level API or client layer
- **Edge Cases**: Job not found, expired job removed before retrieval, stale identifier, concurrent state transition during retrieval, oversized metadata, sensitive metadata present
- **Error Handling**: Not found error for missing job identifier; redaction applied for sensitive metadata; delegated error when underlying registry is unavailable

### FR-JOB-007: Cancel Job

- **Description**: Request cancellation of a long-running operation
- **Input**: Job identifier, optional cancellation reason
- **Output**: Updated job status concept with cancelled state when cancellation is accepted
- **Business Rules**:
  - Cancellation is supported only when job is pending or running and cancellation policy allows
  - Cancellation of terminal job must be rejected
  - Cancellation request may be synchronous or best-effort depending on operation executor
  - Cancellation transition must be atomic
  - Cancellation transition should record finished timestamp when job moves to terminal cancelled state
  - Cancellation reason may be stored for observability
  - Cancellation reason must not include sensitive information
  - If underlying operation cannot be interrupted immediately, job may remain running until executor reports cancellation completion
  - Cancellation request should not delete job record immediately
  - Cancellation result should distinguish between:
    - cancellation accepted
    - cancellation already completed
    - cancellation not supported
    - job not found
- **Edge Cases**: Cancel missing job, cancel completed job, cancel failed job, cancel already cancelled job, cancellation not supported by executor, long-running operation stuck, concurrent cancellation and completion, sensitive cancellation reason
- **Error Handling**: Validation error for invalid cancellation request; not found error for missing job identifier; state error when job cannot be cancelled; concurrency conflict error when cancellation races with terminal transition

### FR-JOB-008: Retention and Cleanup

- **Description**: Expire and remove job records according to retention policy
- **Input**: Retention policy, optional maximum age, optional maximum job count
- **Output**: Cleanup summary containing removed job count, retained job count, and warnings
- **Business Rules**:
  - Jobs are in-memory only by default
  - Terminal jobs may be retained for configurable retention period
  - Default retention period should be limited to prevent unbounded memory growth
  - Expired terminal jobs may be removed automatically by cleanup process
  - Non-terminal jobs should not be removed unless explicitly marked abandoned or timed out by policy
  - Maximum active job count may be enforced
  - Cleanup process should prefer removing oldest terminal jobs first
  - Cleanup process must not remove running jobs unless abandonment policy explicitly allows
  - Cleanup process should be non-blocking or lightweight enough not to degrade normal job operations
  - Cleanup summary should be observable but should not expose sensitive job metadata
  - Removed job identifiers may be logged at debug level without sensitive details
- **Edge Cases**: Retention period exceeded, maximum job count exceeded, cleanup during active state transition, cleanup during retrieval, clock skew, abandoned running job, registry empty, registry corrupted
- **Error Handling**: Cleanup warnings for partially removed records; capacity error when maximum job count enforcement fails; delegated error when registry unavailable

## API Contract


| Operation                       | Input                                                       | Output                                    | Description                                 |
| --------------------------------- | ------------------------------------------------------------- | ------------------------------------------- | --------------------------------------------- |
| Generate job identifier         | None                                                        | Unique job identifier                     | Generate collision-resistant job identifier |
| Create validated progress value | Numeric percentage                                          | Progress value concept                    | Create validated progress value             |
| Transition job to running       | Job identifier, optional reason                             | Updated job status                        | Move job from pending to running            |
| Transition job to completed     | Job identifier, optional result reference, optional summary | Updated job status                        | Move running job to completed               |
| Transition job to failed        | Job identifier, error message, optional error category      | Updated job status                        | Move running job to failed                  |
| Retrieve job status             | Job identifier                                              | Job status snapshot                       | Read current job state                      |
| Cancel job                      | Job identifier, optional reason                             | Updated job status or cancellation result | Request cancellation                        |
| Remove expired jobs             | Retention policy                                            | Cleanup summary                           | Clean up expired terminal jobs              |

Common contract behavior:

- All operations return structured result containing success indicator, human-readable message, and error category when failed
- All state-changing operations must be atomic
- All state-changing operations must validate current state before applying transition
- Read operations must return immutable or safe snapshot of job state
- Terminal states are immutable except for cleanup removal
- Progress updates do not change state but update job status snapshot
- Result reference and error details must be redacted in logs when sensitive
- Job identifier should be treated as opaque reference by callers
- Polling behavior is handled by higher-level API or client layer

## Integration Points

- **Internal**:
  - shared module: taxonomy concepts for job state, progress value, job identifier, result reference, error category, and result envelope
  - configuration module: retention period, maximum active job count, cancellation policy, progress throttling, and cleanup interval
  - server module or operation executor: reports state transitions, progress, completion, failure, and cancellation outcome for long-running operations
  - render module: long-running render job tracking
  - asset module: long-running download or import job tracking
  - logging module: transition events, progress throttling, redaction, and cleanup summaries
- **External**:
  - None by default for pure domain job tracking
  - Optional system clock or time source for timestamp handling
  - Optional in-memory registry implementation provided by application runtime

## Non-functional Requirements (Detailed)

- **Performance**:

  - State transitions should complete within one millisecond under normal in-memory conditions
  - Progress updates should complete within one millisecond under normal in-memory conditions
  - Job status retrieval should complete within one millisecond for active job records
  - Cleanup process should not block normal job operations for significant duration
- **Reliability**:

  - State machine must be strictly enforced
  - No invalid transitions should be possible through public contract
  - Terminal states must be immutable except cleanup removal
  - Concurrent updates must not corrupt job state
  - Failed cleanup should not remove active non-terminal jobs unless policy explicitly allows
- **Thread Safety**:

  - Job status updates must be thread-safe
  - State transitions must be atomic
  - Progress updates must be atomic
  - Reads must return consistent snapshot even during concurrent updates
  - Job registry access must be safe under concurrent creation, retrieval, update, and cleanup
- **Observability**:

  - Log job creation, state transitions, terminal states, and cleanup summaries
  - Log progress updates in throttled manner to avoid excessive noise
  - Include job identifier, operation type, state, progress, and duration in logs
  - Avoid logging sensitive result references, error details, or metadata
  - Expose job state metrics such as active job count, terminal job count, failed job count, and expired job count when supported
- **Security**:

  - Job identifiers should be collision-resistant and hard to guess
  - Result references must not expose secrets or authenticated locations in logs
  - Error messages must be sanitized before storage or exposure
  - Metadata must not contain sensitive information by default
  - Access to job status may be restricted by higher-level API or security policy
- **Retention**:

  - Jobs are in-memory only unless persistence is explicitly added
  - Terminal jobs expire after configured retention period
  - Maximum active job count should prevent unbounded memory growth
  - Cleanup should favor oldest terminal jobs first

## Test Scenarios / QA Checklist

- [ ]  Create job with auto-generated identifier succeeds
- [ ]  Create job with initial pending state succeeds
- [ ]  Create job with duplicate identifier is rejected
- [ ]  Create job with invalid identifier format returns validation error
- [ ]  Create job with invalid metadata returns validation error
- [ ]  Create job when maximum active job limit reached returns capacity error or triggers eviction based on configuration
- [ ]  State transition pending to running succeeds
- [ ]  State transition running to completed succeeds
- [ ]  State transition running to failed succeeds
- [ ]  State transition pending to cancelled succeeds when cancellation policy enabled
- [ ]  State transition running to cancelled succeeds when cancellation policy enabled
- [ ]  State transition running to timed out succeeds when timeout policy enabled
- [ ]  Invalid transition pending to completed raises validation error
- [ ]  Invalid transition completed to running raises validation error
- [ ]  Invalid transition failed to completed raises validation error
- [ ]  State transition on missing job returns not found error
- [ ]  Concurrent state transitions preserve terminal state consistency
- [ ]  Progress zero accepted for running job
- [ ]  Progress one hundred accepted for running job
- [ ]  Progress below zero raises validation error
- [ ]  Progress above one hundred raises validation error
- [ ]  Progress on pending job raises state error
- [ ]  Progress on completed job raises state error
- [ ]  Progress on failed job raises state error
- [ ]  Progress on missing job returns not found error
- [ ]  Non-monotonic progress is rejected unless reset policy enabled
- [ ]  Complete job with optional result reference succeeds
- [ ]  Complete job without result reference succeeds
- [ ]  Complete job with invalid result reference returns validation error
- [ ]  Complete already completed job raises validation error
- [ ]  Complete non-running job raises validation error
- [ ]  Fail job with required error message succeeds
- [ ]  Fail job with empty error message raises validation error
- [ ]  Fail already failed job raises validation error
- [ ]  Fail non-running job raises validation error
- [ ]  Fail job with optional error category stores category safely
- [ ]  Retrieve job status returns consistent snapshot
- [ ]  Retrieve missing job returns not found error
- [ ]  Retrieve job status does not mutate job state
- [ ]  Retrieve job status redacts sensitive metadata
- [ ]  Cancel pending job succeeds when cancellation enabled
- [ ]  Cancel running job returns accepted or best-effort status
- [ ]  Cancel completed job returns state error
- [ ]  Cancel missing job returns not found error
- [ ]  Cancellation reason is sanitized before storage
- [ ]  Expired terminal jobs are removed after retention period
- [ ]  Running jobs are not removed during normal cleanup
- [ ]  Cleanup removes oldest terminal jobs first when maximum count exceeded
- [ ]  Cleanup summary reports removed and retained job counts
- [ ]  Job operations remain thread-safe under concurrent access

## Assumptions & Constraints

- Jobs are in-memory only by default, with no persistence
- State machine is strict for core lifecycle: pending, running, completed, failed
- Optional extended states may be enabled for cancellation, timeout, and expiration
- No backward state transitions are allowed
- Terminal states are immutable except cleanup removal
- Job execution is handled by other modules or operation executors
- Job module only tracks lifecycle and does not perform actual long-running work
- Cancellation effectiveness depends on underlying operation executor
- Progress reporting depends on underlying operation providing progress updates
- Retention policy must prevent unbounded memory growth
- Timestamps depend on available system time source

## Glossary

- **Job status concept**: Concept tracking state, progress, timestamps, result reference, and error information of a long-running operation
- **Job state concept**: Valid lifecycle state of a job, such as pending, running, completed, failed, cancelled, timed out, or expired
- **Progress value concept**: Value representing percentage completion from zero to one hundred
- **Job identifier**: Unique opaque reference for a job record
- **Result reference**: Optional reference to final artifact, output location, or structured result metadata
- **Terminal state**: Final job state that cannot transition to another active state
- **Retention period**: Duration that terminal job records remain available before cleanup
- **Cancellation policy**: Rule describing whether and how jobs may be cancelled
- **Cleanup summary**: Result of expired or excess job removal process
- **Correlation identifier**: Optional identifier linking job to originating request or workflow

## Reference

- Product Requirements Document for blender-arwaky
- Shared feature requirements documentation
- Server feature requirements documentation
