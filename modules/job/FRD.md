# FRD — JOB Tracking Feature

## System Overview

The background task tracking feature manages the lifecycle of long-running operations (such as rendering, large asset imports, or complex calculations) that execute outside the main application flow. It provides a reliable way to monitor progress, check status, cancel operations, and automatically clean up old records.

The feature ensures that background tasks are tracked predictably without interfering with the main application's responsiveness. It enforces a strict, logical lifecycle for tasks and guarantees that users and AI clients can always get a consistent, up-to-date view of what a background task is doing, while automatically managing system resources by clearing old records.

## Functional Requirements

### FR-JOB-001: Track and Update Task Lifecycle

- **Use Case:** The system needs to register a new long-running background task and continuously update its progress and final outcome as it executes.
- **User Action:** (Implicit) The system creates a task record when a background operation starts, updates its progress, and marks it as completed or failed.
- **System Response:** Maintain a reliable, up-to-date record of the task's lifecycle, current progress percentage, and final result or error.
- **Business Rules:**
  - Every task must be assigned a unique, unguessable tracking identifier.
  - Tasks must follow a strict, forward-only lifecycle: Waiting (Pending) → Running → Completed / Failed / Cancelled.
  - Backward transitions (e.g., moving from Completed back to Running) are strictly forbidden.
  - Progress must be a percentage between 0 and 100. Progress should generally increase monotonically (never go backward) unless explicitly reset.
  - When a task completes, it can optionally store a reference to its output (e.g., a file path or object reference).
  - When a task fails, it must store a clear, sanitized error message and category.
  - The system must prevent duplicate tracking identifiers.
  - The system must enforce a maximum limit on the number of active tasks to prevent resource exhaustion.
- **Edge Cases:** Duplicate identifiers, invalid progress values (e.g., 110% or negative numbers), attempting to update a task that has already finished, exceeding the maximum active task limit.
- **Error Handling:** Return `ValidationError` for invalid progress or state changes; return `CapacityError` if the active task limit is reached; return `StateError` if trying to update a finished task.

### FR-JOB-002: Monitor Task Status

- **Use Case:** A user or AI client needs to check the current state, progress, or final result of a background task.
- **User Action:** Request the status of a specific task using its tracking identifier.
- **System Response:** Return a complete, read-only snapshot of the task's current state, progress, timestamps, and any final results or errors.
- **Business Rules:**
  - The operation must be strictly read-only and never alter the task's state.
  - The returned snapshot must be consistent and reflect the exact state at the moment of the request.
  - The response must include: current state, progress percentage, creation time, start time, completion time (if finished), result reference (if completed), and error details (if failed).
  - Any sensitive information in the task's metadata or result references must be automatically hidden (redacted) in the response.
  - If the task identifier is not found or has already been cleaned up, the system must return a clear "Not Found" response.
- **Edge Cases:** Task identifier not found, task already cleaned up, sensitive data present in metadata, multiple simultaneous status checks.
- **Error Handling:** Return `NotFoundError` for missing or expired tasks. Automatically redact sensitive data instead of throwing an error.

### FR-JOB-003: Cancel a Task

- **Use Case:** A user or AI client needs to stop a background task that is either waiting to start or currently running.
- **User Action:** Request the cancellation of a specific task using its tracking identifier, optionally providing a reason.
- **System Response:** Attempt to stop the task and update its status to "Cancelled", or report if cancellation is not possible.
- **Business Rules:**
  - Cancellation is only allowed for tasks in the "Waiting" or "Running" states. Finished tasks cannot be cancelled.
  - If the underlying operation cannot be stopped immediately (e.g., it's in an uninterruptible phase), the system must accept the cancellation request, but the task may remain "Running" until it naturally finishes or safely aborts.
  - The cancellation reason must be stored for troubleshooting but must not contain sensitive information.
  - The system must clearly distinguish between: cancellation accepted, task already finished, cancellation not supported for this specific task type, and task not found.
  - Requesting cancellation must not immediately delete the task record; it should follow the standard lifecycle to "Cancelled".
- **Edge Cases:** Cancelling an already finished task, cancelling a task that doesn't support cancellation, cancelling a missing task, simultaneous cancellation and completion requests.
- **Error Handling:** Return `StateError` if the task is already finished; return `NotFoundError` if the task doesn't exist; return `UnsupportedError` if the specific task type cannot be cancelled.

### FR-JOB-004: Automatic Task Record Cleanup

- **Use Case:** The system needs to automatically free up resources by removing old, finished task records that are no longer needed.
- **User Action:** (Implicit) The system periodically checks for and removes expired task records based on configured retention rules.
- **System Response:** Safely remove old records and provide a summary of the cleanup action.
- **Business Rules:**
  - Only tasks in a final state (Completed, Failed, Cancelled, Timed Out) are eligible for cleanup. Running or Waiting tasks must never be removed automatically.
  - Records are removed based on a configured retention period (e.g., keep results for 10 minutes after completion).
  - If the maximum number of active tasks is reached, the system may automatically remove the oldest finished records to make room for new ones.
  - The cleanup process must be lightweight and never block or delay the tracking of active tasks.
  - The system must prioritize removing the oldest finished records first.
  - The cleanup summary must report how many records were removed and retained, without exposing sensitive task details.
- **Edge Cases:** Cleanup triggered while a task is finishing, maximum task limit exceeded, empty task registry, system clock changes.
- **Error Handling:** Silently retry or log warnings for partial cleanup failures. Never remove active tasks to resolve capacity issues unless explicitly configured to abandon them.

## System Capabilities (User-Facing Operations)


| Operation               | User Action (Input)                    | System Response (Output)         | Description                              |
| ------------------------- | ---------------------------------------- | ---------------------------------- | ------------------------------------------ |
| `track_new_task`        | Operation type, optional metadata      | Task Tracking ID, Initial Status | Register a new background task           |
| `update_task_progress`  | Task ID, progress percentage, message  | Updated Task Status              | Update the progress of a running task    |
| `finalize_task_success` | Task ID, result reference, summary     | Completed Task Status            | Mark a task as successfully completed    |
| `finalize_task_failure` | Task ID, error message, error category | Failed Task Status               | Mark a task as failed with error details |
| `get_task_status`       | Task ID                                | Task Status Snapshot             | Retrieve the current state of a task     |
| `cancel_task`           | Task ID, optional cancellation reason  | Cancellation Result              | Request the cancellation of a task       |
| `cleanup_expired_tasks` | Retention policy limits                | Cleanup Summary                  | Remove old, finished task records        |

**Additional Capability Behaviors:**

- All operations return a structured result containing a success indicator, a human-readable message, and an error category if failed.
- All state-changing operations strictly validate the current task state before applying changes.
- Read operations (like `get_task_status`) always return a safe, consistent snapshot without altering the task.
- Final states (Completed, Failed, Cancelled) are immutable and cannot be changed, only read or cleaned up.

## System Boundaries

- **External Consumers:**
  - Internal application components that initiate long-running operations (e.g., rendering, asset downloading).
  - AI Clients and User Interfaces that need to poll task status or cancel tasks.
- **Target Environment:**
  - The local application runtime environment.
- **External Dependencies:**
  - System Clock: For calculating retention periods and timestamps.

## Non-functional Requirements

- **Performance:**
  - Task state updates and progress reporting must be extremely fast and never delay the underlying background operation.
  - Status retrieval must be instantaneous.
  - The automatic cleanup process must run in the background without impacting the performance of active task tracking.
- **Reliability:**
  - The task lifecycle rules must be strictly enforced; invalid state changes must be impossible.
  - Finished tasks must remain immutable and cannot be accidentally altered.
  - The system must handle simultaneous updates gracefully without corrupting the task record.
- **Security & Privacy:**
  - Task identifiers must be unguessable to prevent unauthorized status polling.
  - Result references and error messages must be sanitized to ensure no secrets or sensitive file paths are exposed in logs or status responses.
  - Task metadata must not contain sensitive information by default.
- **Observability:**
  - The system must log task creation, state transitions, and cleanup summaries.
  - Progress updates should be logged in a controlled manner to avoid flooding the logs.
  - Logs must include the task identifier, operation type, state, and duration, but must exclude sensitive result data.

## Test Scenarios / QA Checklist

**Task Lifecycle & Progress:**

- [ ]  Create a new task with an auto-generated identifier succeeds and sets state to "Waiting".
- [ ]  Create a task with a duplicate identifier is rejected.
- [ ]  Transition a task from "Waiting" to "Running" succeeds.
- [ ]  Update progress to 50% on a "Running" task succeeds.
- [ ]  Update progress with an invalid value (e.g., -10 or 110) returns `ValidationError`.
- [ ]  Update progress on a "Waiting" or "Finished" task returns `StateError`.
- [ ]  Finalize a task as "Completed" with a result reference succeeds.
- [ ]  Finalize a task as "Failed" with an error message succeeds.
- [ ]  Attempting to update a task that is already "Completed" or "Failed" returns `StateError`.
- [ ]  Creating a task when the maximum active limit is reached returns `CapacityError`.

**Monitoring & Cancellation:**

- [ ]  Retrieve task status returns a consistent, read-only snapshot.
- [ ]  Retrieve status for a missing or expired task returns `NotFoundError`.
- [ ]  Retrieve status automatically redacts sensitive metadata.
- [ ]  Cancel a "Waiting" or "Running" task succeeds and changes state to "Cancelled".
- [ ]  Cancel an already "Completed" or "Failed" task returns `StateError`.
- [ ]  Cancel a missing task returns `NotFoundError`.
- [ ]  Cancel a task type that does not support cancellation returns `UnsupportedError`.

**Cleanup & Stability:**

- [ ]  Expired "Completed" or "Failed" tasks are removed after the retention period.
- [ ]  "Running" or "Waiting" tasks are never removed during normal cleanup.
- [ ]  Cleanup removes the oldest finished tasks first when the maximum count is exceeded.
- [ ]  Cleanup summary correctly reports removed and retained task counts.
- [ ]  Simultaneous task updates and status checks do not corrupt data or cause errors.

## Assumptions & Constraints

- Task records are managed locally by the application and do not persist across application restarts unless explicitly extended.
- The lifecycle is strictly forward-only; tasks cannot revert to previous states.
- The actual execution of the background work is handled by other components; this feature only tracks the lifecycle.
- The effectiveness of task cancellation depends on the underlying operation's ability to be interrupted.
- Progress reporting depends on the underlying operation providing updates.
- The retention policy must be configured to prevent unbounded memory growth over long sessions.

## Glossary

- **Background Task:** A long-running operation that executes outside the main application flow, tracked via a unique identifier.
- **Task Lifecycle:** The strict sequence of states a task goes through: Waiting → Running → Completed / Failed / Cancelled.
- **Tracking Identifier:** A unique, unguessable reference used to locate and monitor a specific background task.
- **Result Reference:** An optional pointer to the final output of a completed task (e.g., a rendered image file path).
- **Terminal State:** A final task state (Completed, Failed, Cancelled) that cannot transition to any other active state.
- **Retention Period:** The duration that finished task records remain available for status checking before being automatically cleaned up.
