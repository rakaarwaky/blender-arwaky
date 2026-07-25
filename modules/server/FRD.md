# FRD — Server Feature

## System Overview

The server feature manages the secure communication channel between external AI clients and the Blender application. It handles connection stability, safe custom code execution, and standard Blender operations.

The feature treats all user-provided code as potentially unsafe. It applies strict safety checks before execution and enforces runtime boundaries to protect the user's system from unauthorized access or destructive actions. Because the Blender application can only safely process one operation at a time, the feature ensures that all concurrent requests are handled sequentially to maintain application stability.

The feature defines connection stability handling, liveness monitoring, compatibility checks, authentication, data size limits, background task management, system observability, and error classification from a user-facing perspective.

## Functional Requirements

### FR-001: Establish and Maintain Connection

- **Use Case:** An AI client or user needs to connect to a running Blender instance and ensure the connection remains active during use.
- **User Action:** Provide connection settings (target address, port, timeout limits, authentication token, and compatibility version).
- **System Response:** Establish a secure connection and provide the current connection status.
- **Business Rules:**
  - The system must automatically attempt to reconnect if the connection is lost, up to a maximum of 3 attempts with increasing wait times.
  - Connection establishment must fail if it takes longer than 30 seconds.
  - The system must send periodic "liveness" checks (heartbeats) every 10 seconds to detect if the connection has gone stale.
  - The connection is only considered stale after a configurable number of consecutive failed liveness checks (default: 3).
  - A missed liveness check during a long-running operation must not immediately drop the connection unless the operation itself has also timed out.
  - The initial connection handshake must verify compatibility versions and authenticate the user if a token is required.
  - The system must default to local-only connections unless remote access is explicitly configured by the user.
  - Connection status must be clearly reported as: `disconnected`, `connecting`, `connected`, `reconnecting`, `failed`, or `closed`.
  - While reconnecting, new operation requests must be either held or rejected based on user configuration.
  - If the connection fails permanently, all pending operations must be cancelled and return a clear "Connection Lost" error.
  - The disconnect action must be safe to call multiple times without causing errors.
  - When gracefully disconnecting, all pending operations must be cancelled with a "Connection Closed" error.
  - Operations currently in progress are not forcibly stopped unless explicitly requested by the user.
- **Edge Cases:** Blender is not running, connection is refused, connection times out, network drops, Blender crashes during a session, authentication fails, versions are incompatible, liveness check gives a false alarm during a long task, disconnect is called while reconnecting.
- **Error Handling:** Return `BlenderConnectionFailure` (with retry details); return `BlenderConnectionExhausted` after 3 failed retries; return `AuthenticationError` for invalid tokens; return `VersionMismatchError` for incompatible versions; return `ConnectionClosedError` for operations rejected after a disconnect.

### FR-002: Execute Custom Code

- **Use Case:** An AI agent or user needs to run custom Python code inside Blender to perform actions not covered by standard commands.
- **User Action:** Provide the Python code string, optional timeout limit, optional background execution flag, and optional tracking key.
- **System Response:** Return the execution result containing status (success/error), returned data, error details (if any), execution time, and a flag indicating if the output was too large and truncated.
- **Business Rules:**
  - All user-provided code is treated as untrusted.
  - The code must be validated for safety before execution. Blocked patterns include, but are not limited to: system commands (`os.system`), process execution (`subprocess`), destructive file operations (`shutil.rmtree`), dynamic evaluation (`eval`, `exec`, `compile`), dynamic imports (`__import__`, `importlib`), unsafe internal attributes, and file writing outside of explicitly allowed directories.
  - Pre-execution validation is a safety filter; the Blender environment must also enforce its own runtime boundaries as the final authority.
  - Allowed directories for file operations must be configurable by the user.
  - The default allowed directory is the folder containing the active Blender project file.
  - Code execution must time out after 30 seconds by default, returning an `ExecutionTimeoutError`.
  - The timeout limit must be configurable.
  - For operations expected to take longer than the timeout, the system must support background task submission, returning a tracking ID for the user to check later.
  - Background task statuses must include: `pending`, `running`, `success`, `error`, `timeout`, `cancelled`.
  - Background task results must be retained for a configurable time (default: 10 minutes).
  - Background tasks can only be cancelled while they are `pending`. Cancelling a `running` task is a best-effort attempt.
  - Checking the status of an unknown or expired background task must return a `TaskNotFoundError`.
  - The size of the code provided must be limited (default max: 1 MB).
  - The execution output must be convertible to a standard structured format.
  - If the output cannot be converted, it must be safely converted to a text representation or rejected.
  - If the output exceeds the maximum allowed response size, it must be truncated, and the response must indicate that truncation occurred.
  - All code execution requests must be processed sequentially to maintain Blender stability.
  - Each request must include a unique tracking ID for logging and troubleshooting.
- **Edge Cases:** Code times out, code has syntax errors, Blender throws an exception, Blender crashes during execution, blocked pattern is detected, blocked pattern is obfuscated to hide it, code is too large, output is too large, output cannot be formatted, connection is lost during execution, background task expires, background task is cancelled, too many pending operations.
- **Error Handling:** Return `ExecutionError` with details from Blender; return `SecurityViolationError` for blocked patterns; return `ExecutionTimeoutError` for timeouts; return `TooManyPendingOperationsError` when the limit of waiting operations is exceeded; return `OperationWaitTimeoutError` when a request waits too long to be processed; return `TaskNotFoundError` for unknown/expired background tasks; return `BlenderConnectionFailure` if the connection drops.

### FR-003: Execute Standard Commands

- **Use Case:** An AI agent or user needs to run a predefined, named Blender action (e.g., create object, render scene).
- **User Action:** Provide the command name, command parameters, and optional timeout limit.
- **System Response:** Return the command result containing status (success/error), returned data, error details (if any), and execution time.
- **Business Rules:**
  - The default response timeout for commands is 5 seconds, returning a `CommandTimeoutError` if exceeded.
  - Individual commands may define their own custom timeout limits if they are expected to take longer.
  - Long-running commands should be submitted as background tasks or explicitly marked as long-running.
  - Commands that only read data (e.g., `get_scene_info`) should be idempotent (safe to run multiple times without changing the result).
  - Each command must define:
    - Required and optional parameters.
    - Default timeout.
    - Whether it is idempotent.
    - Whether it changes the Blender scene state.
  - Command parameters must be validated against the command's defined rules before execution.
  - Commands that do not interact with the Blender scene state may be processed immediately.
  - Commands that interact with or change the Blender scene state must be processed sequentially.
  - Command response sizes must be limited and truncated if they are too large.
- **Edge Cases:** Unknown command name, invalid parameters, Blender is not responding, response format is invalid, response is too large, command times out, too many pending operations.
- **Error Handling:** Return `ProviderError` with command-specific details; return `CommandTimeoutError` for unresponsive commands; return `ValidationError` for invalid parameters; return `TooManyPendingOperationsError` when the limit is exceeded; return `OperationWaitTimeoutError` when waiting too long.

## System Capabilities (User-Facing Operations)


| Operation               | User Action (Input)      | System Response (Output)         | Description                                    |
| ------------------------- | -------------------------- | ---------------------------------- | ------------------------------------------------ |
| `connect`               | Connection Settings      | Connection Status                | Establish secure connection to Blender         |
| `disconnect`            | —                       | —                               | Close connection gracefully                    |
| `send_command`          | Command Name, Parameters | Command Result                   | Run a predefined Blender action (5s timeout)   |
| `execute_blender_code`  | Python Code              | Execution Result                 | Run custom code in Blender (30s timeout)       |
| `submit_async_task`     | Python Code              | Task Tracking ID                 | Submit long-running code for background work   |
| `poll_task_result`      | Task Tracking ID         | Task Status and Execution Result | Check status and get result of background work |
| `get_connection_status` | —                       | Connection Status Details        | Get current connection health and details      |

**Additional Capability Behaviors:**

- `connect` must verify compatibility and authenticate the user if enabled.
- `disconnect` must be safe to call multiple times and must not cause errors if already closed.
- `send_command` uses a 5-second timeout unless the specific command defines a different limit.
- `execute_blender_code` returns the final result immediately for standard execution.
- `submit_async_task` returns a tracking ID, with the initial status usually being `pending`.
- `poll_task_result` returns the current status and, when finished, the final execution result.
- `get_connection_status` returns details including current state, target address, last liveness check time, reconnect attempts, and compatibility version.
- All requests and responses must include a unique tracking ID for troubleshooting.
- All data exchanged must be text-based and structured.
- Maximum data size for requests and responses must be configurable and enforced.

## External Boundaries

- **External Consumers:**
  - AI Clients (e.g., MCP-compatible tools, CLI utilities) that send commands and code.
- **Target Environment:**
  - Blender Application (must be running and listening for connections).
  - Blender Internal Environment (where code and commands are actually executed).
- **External Dependencies:**
  - Optional secret storage or environment variables for managing authentication tokens.

## Non-functional Requirements

- **Performance:**
  - Standard commands must respond within 5 seconds by default.
  - Custom code execution must respond within 30 seconds by default.
  - The system's own processing overhead should be minimal (ideally <100ms excluding Blender's execution time).
  - The wait time for operations being processed sequentially should be configurable, with a default target of <10 seconds under normal load.
- **Reliability:**
  - The system must automatically reconnect on connection loss (3 attempts, with increasing wait times).
  - The system must degrade gracefully if Blender crashes.
  - Pending operations must fail predictably and clearly if the connection is lost.
  - No operation may be silently dropped; every operation must have a defined success, failure, or recovery outcome.
- **Security:**
  - Custom code must be validated against a list of blocked patterns before execution.
  - The Blender environment must enforce its own runtime boundaries.
  - File system access must be restricted to explicitly allowed directories.
  - The default connection target must be local-only for security.
  - Remote connections must require authentication when enabled.
  - Data size limits must be strictly enforced.
  - Security violations must be logged as audit events.
  - Raw code provided by the user must not be logged by default to protect privacy.
- **Observability:**
  - The system must log all connection state changes, command details, execution durations, wait times, retry attempts, and error details.
  - Code provided by the user must be masked, hashed, or truncated in logs.
  - Logs should be structured for easy parsing.
  - Every operation must be traceable using its unique tracking ID.
  - System metrics should include: number of pending operations, reconnect count, execution latency, command latency, failed request count, and security violation count.
- **Stability (Operation Processing):**
  - All operations that interact with the Blender scene must be processed one at a time to prevent application instability.
  - The system must limit the number of pending operations (default: 50).
  - Operations are processed in the order they are received.
  - Operations that do not interact with the Blender scene (like checking connection status) may be processed immediately without waiting.
  - If the limit of pending operations is reached, new requests must be rejected with a `TooManyPendingOperationsError`.
  - If an operation waits too long to be processed, it must be rejected with an `OperationWaitTimeoutError`.

## Test Scenarios / QA Checklist

**Connection & Stability:**

- [ ]  Connect to a running Blender instance succeeds.
- [ ]  Connect to a non-running Blender instance returns `BlenderConnectionFailure`.
- [ ]  Connect with an invalid authentication token returns `AuthenticationError`.
- [ ]  Connect with an unsupported version returns `VersionMismatchError`.
- [ ]  Connection loss triggers automatic reconnection (3 attempts).
- [ ]  After 3 failed reconnections, the system returns `BlenderConnectionExhausted`.
- [ ]  Liveness checks detect a stale connection and trigger reconnection.
- [ ]  Liveness checks do not falsely drop the connection during a long-running operation.
- [ ]  Disconnecting is safe to call multiple times.
- [ ]  Disconnecting cancels pending operations with `ConnectionClosedError`.

**Custom Code Execution:**

- [ ]  Execute valid Python code returns a successful `ExecutionResult`.
- [ ]  Execute code with syntax errors returns an `ExecutionResult` with an error status.
- [ ]  Execute code exceeding the 30s timeout returns `ExecutionTimeoutError`.
- [ ]  Execute code containing blocked patterns (e.g., `os.system`) returns `SecurityViolationError`.
- [ ]  Execute code containing obfuscated blocked patterns returns `SecurityViolationError`.
- [ ]  Execute code attempting to write outside allowed directories returns `SecurityViolationError`.
- [ ]  Execute code writing inside allowed directories succeeds.
- [ ]  Execute code with an oversized data size is rejected.
- [ ]  Execute code with an oversized output returns a truncated result with a truncation flag.
- [ ]  Execute code with an output that cannot be formatted returns a safe text fallback or explicit error.

**Background Tasks:**

- [ ]  Submit a background task returns a tracking ID.
- [ ]  Check a pending background task returns a pending status.
- [ ]  Check a completed background task returns the final `ExecutionResult`.
- [ ]  Check an unknown background task returns `TaskNotFoundError`.
- [ ]  Cancel a pending background task succeeds.
- [ ]  Cancel a running background task returns a best-effort or unsupported status.
- [ ]  Background task results expire after the configured time limit.
- [ ]  Blender crashing during a background task marks the task as an error.

**Standard Commands:**

- [ ]  Send a valid command to Blender returns a response within 5 seconds.
- [ ]  Send a command exceeding the 5s timeout returns `CommandTimeoutError`.
- [ ]  Send a command with a custom timeout respects the configured limit.
- [ ]  Send an unknown command returns `ProviderError`.
- [ ]  Send a command with invalid parameters returns `ValidationError`.
- [ ]  Send a command that results in an invalid response format returns a parsing/provider error.

**Operation Processing:**

- [ ]  Concurrent requests are processed sequentially without crashing.
- [ ]  Pending operation limit (50) is enforced; excess requests return `TooManyPendingOperationsError`.
- [ ]  An operation waiting too long returns `OperationWaitTimeoutError`.
- [ ]  Non-scene operations (like status checks) do not get stuck behind scene operations.
- [ ]  Malformed data received from the network is handled safely without crashing.
- [ ]  Data missing a tracking ID is handled according to system rules.
- [ ]  Large response data is truncated or rejected based on configured limits.

## Assumptions & Constraints

- The Blender application must be running and listening for connections.
- The system supports one active connection to Blender at a time.
- Custom code execution has a 30-second timeout by default (configurable).
- Standard command execution has a 5-second timeout by default.
- Some commands may define custom timeout limits.
- Because the Blender application can only safely process one scene operation at a time, all concurrent requests that interact with the scene are processed sequentially to prevent instability.
- The list of blocked code patterns is maintained in the system settings and updated as needed.
- The system and Blender must use compatible versions.
- All user-provided code is treated as untrusted.
- Pre-execution safety checks are not a complete replacement for runtime boundaries; the Blender environment must also enforce restrictions.
- Allowed directories for file access must be explicitly configured.
- The default allowed directory is the active Blender project folder.
- Authentication tokens are required for remote connections when authentication is enabled.
- The default connection target is local-only for security.
- Background task tracking is stored in memory unless persistent storage is explicitly enabled.
- Background task results have a configurable time-to-live.
- Cancelling a running Blender operation is a best-effort attempt, as the application may not be able to stop it immediately.
- The liveness check mechanism must account for long-running operations to avoid false alarms.
- Maximum data sizes for requests and responses must be configured and enforced.

## Glossary

- **Background Task:** A long-running operation submitted to the system that returns a tracking ID immediately, allowing the user to check its status later.
- **Blocked Patterns:** A configurable list of forbidden code structures or modules used to prevent security violations.
- **Allowed Directory:** A specific folder explicitly permitted for file read/write operations.
- **Connection Status:** The current state of the connection (e.g., connected, disconnected, reconnecting), including target details and last liveness check time.
- **Task Status:** The current lifecycle state of a background task (e.g., pending, running, success, error, timeout, cancelled).
- **Liveness Check (Heartbeat):** A periodic signal sent to verify that the connection to Blender is still active and responsive.
- **Execution Result:** The standardized outcome of a code execution, containing the status, returned data, error details, time taken, and truncation flags.
- **Tracking ID:** A unique identifier assigned to every request and response to correlate logs, track operations, and troubleshoot errors.
- **Security Violation:** An event where user-provided code attempts to perform an action blocked by the system's safety rules.
