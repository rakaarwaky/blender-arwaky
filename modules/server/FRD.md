
# FRD — Server Feature Module

## System Overview

The server module manages TCP socket communication between the blender-arwaky server and the Blender addon. It handles connection lifecycle, code execution, and Blender-side operations. This module is the bridge between external consumers (MCP, CLI) and the Blender runtime. It follows a AES Architechture pattern

The module treats user-provided code as untrusted or semi-trusted input and applies layered protection: server-side static validation using AST-based analysis, and runtime sandbox enforcement on the Blender addon side. All operations that access Blender’s Python API (`bpy`) are serialized through a single execution queue because `bpy` is not thread-safe and must run on Blender’s main thread.

The module also defines connection state handling, heartbeat behavior, protocol version compatibility, authentication expectations, payload limits, async task handling, observability requirements, and error classification

## Functional Requirements

### FR-SRV-001: Manage Blender Socket Connection

- **Description:** Establish and maintain TCP socket connection to Blender addon
- **Input:** ConnectionConfig (host, port, timeout, retry_policy, auth_token, protocol_version, heartbeat_interval_seconds, heartbeat_failure_threshold)
- **Output:** Active socket connection and current `ConnectionStatus`
- **Business Rules:**
  - Auto-reconnect on failure with max 3 retry attempts using exponential backoff with jitter (1s, 2s, 4s)
  - Connection establishment timeout: 30 seconds
  - Heartbeat/ping every 10 seconds to detect stale connections
  - Connection is considered stale only after configurable consecutive heartbeat failures, default 3
  - Heartbeat handling must be independent from Blender main-thread code execution where possible
  - A missed heartbeat during active long-running execution must not immediately trigger reconnect unless TCP connection is closed or execution timeout is also exceeded
  - Connection handshake must include protocol version and authentication token when authentication is enabled
  - Default listener target should be localhost unless remote binding is explicitly configured
  - Connection state must be represented as event: `disconnected`, `connecting`, `connected`, `reconnecting`, `failed`, `closed`
  - While reconnecting, new operations may be queued or rejected based on configuration
  - On permanent connection failure, pending operations must be failed deterministically with a clear error
  - `disconnect` must be idempotent
  - On graceful disconnect, pending queued operations are failed with `ConnectionClosedError`
  - In-flight operations are not forcibly cancelled unless explicitly requested by caller or system policy
- **Edge Cases:** Blender not running, connection refused, timeout, network error, Blender crashes mid-session, authentication failure, protocol version mismatch, heartbeat false positive during long execution, disconnect called during reconnect, stale TCP connection
- **Error Handling:** `BlenderConnectionFailure` with retry logic; after 3 failed attempts, raise `BlenderConnectionExhausted`; `AuthenticationError` for invalid credentials; `ProtocolVersionMismatchError` for incompatible protocol; `ConnectionClosedError` for operations rejected after disconnect

### FR-SRV-002: Execute Blender Code

- **Description:** Send Python code to Blender for execution via TCP socket
- **Input:** Prompt (Python code string), optional execution_timeout_ms, optional async flag, optional idempotency_key for async submission
- **Output:** `ExecutionResult {status: "success"|"error", data: JSONSerializable | null, error: {type: str, message: str, traceback: str | null, line: int | null} | null, execution_time_ms: int, truncated: bool}`
- **Business Rules:**
  - User-provided code is treated as untrusted or semi-trusted input
  - Code validated before sending using AST-based static analysis, not only regex or simple string matching
  - Blocked constructs include but are not limited to:
    - `os.system`
    - `subprocess`
    - `shutil.rmtree`
    - `eval()`
    - `exec()`
    - `compile()`
    - `__import__`
    - dynamic import mechanisms such as `importlib`
    - access to unsafe dunder attributes commonly used for sandbox escape
    - `open()` with write mode outside allowed Blender project directories
  - Server-side validation is a pre-filter only; Blender addon must perform runtime enforcement as the final authority
  - Allowed directories for file write operations must be configurable
  - Default allowed directory is the active `.blend` file directory unless configured otherwise
  - Execution timeout: 30 seconds by default; raise `ExecutionTimeoutError` if exceeded
  - Execution timeout must be configurable via ConnectionConfig or request metadata
  - For long-running operations (>30s), support async task submission with `task_id` polling
  - Async task status must include: `pending`, `running`, `success`, `error`, `timeout`, `cancelled`
  - Async task result retention must be configurable, default 10 minutes
  - Async task cancellation is supported only while task is `pending`; cancellation of running task is best-effort due to Blender main-thread constraints
  - Polling unknown or expired task returns `TaskNotFoundError`
  - Code payload size must be limited, default configurable max 1 MB
  - Execution output must be JSON-serializable
  - Non-serializable output must be converted to safe string representation or rejected
  - If output exceeds max response size, output must be truncated and `truncated: true` must be set
  - All code execution requests must go through serialized execution queue
  - Each request should include unique `request_id` for correlation and observability
- **Edge Cases:** Code execution timeout, syntax error, Blender exception, Blender crash during execution, blocked pattern detected, obfuscated blocked pattern, oversized payload, oversized output, non-serializable return value, connection lost during execution, async task expired, async task cancelled, queue full, queue wait timeout
- **Error Handling:** `ExecutionError` with error details from Blender; `SecurityViolationError` for blocked patterns; `ExecutionTimeoutError` for timeout; `QueueFullError` when queue depth limit exceeded; `QueueTimeoutError` when request waits too long in queue; `TaskNotFoundError` for unknown/expired async task; `BlenderConnectionFailure` for connection loss

### FR-SRV-003: Send Blender Commands

- **Description:** Dispatch named commands to Blender addon
- **Input:** ActionName (enum), command arguments (dict), optional timeout_ms
- **Output:** Command result dictionary `{status: "success"|"error", data: dict, error: {type: str, message: str, details: dict | null} | null, execution_time_ms: int}`
- **Business Rules:**
  - Commands routed through TCP socket; response parsed as JSON
  - Default command response timeout: 5 seconds; raise `CommandTimeoutError` if exceeded
  - Individual commands may define custom timeout metadata when operation is expected to take longer
  - Long-running commands should be submitted through async task mechanism or explicitly marked as long-running
  - Commands are idempotent where possible (e.g., `get_scene_info`)
  - Each ActionName should define:
    - argument schema
    - default timeout
    - idempotency flag
    - whether it mutates Blender state
    - whether it requires `bpy` main-thread access
  - Command arguments must be validated against schema before sending
  - Commands that do not require Blender state access may bypass the main execution queue
  - Commands that access or mutate Blender state must be serialized through the execution queue
  - Command response size must be limited and truncated if too large
- **Edge Cases:** Unknown command, invalid arguments, Blender not responding, malformed JSON response, command schema mismatch, response too large, command timeout, queue full, queue wait timeout
- **Error Handling:** `ProviderError` with command-specific error message; `CommandTimeoutError` for unresponsive commands; `ValidationError` for invalid command arguments; `QueueFullError` when queue depth limit exceeded; `QueueTimeoutError` when queued command exceeds wait timeout

### FR-SRV-004: Connection Factory

- **Description:** Create new Blender connection instances based on configuration
- **Input:** ConnectionConfig (host, port, timeout, retry_policy, auth_token, protocol_version, max_payload_bytes, heartbeat_interval_seconds, heartbeat_failure_threshold, allowed_directories)
- **Output:** contract_blender_connection_protocol instance
- **Business Rules:**
  - Factory validates configuration before instantiation
  - Returns BlenderConnection adapter implementation
  - Host and port are required
  - Port must be valid, range 1–65535
  - Timeout must be greater than zero and within configured maximum
  - Retry policy must be within configured min/max bounds
  - Protocol version must be supported by server
  - Authentication token must be present when connecting to non-local target if authentication is enabled
  - Configuration object should be immutable after creation
- **Edge Cases:** Invalid configuration, missing required fields, invalid port, invalid timeout, unsupported protocol version, missing auth token for remote connection, invalid allowed directory configuration
- **Error Handling:** `ConnectionConfigError` for factory failures with descriptive validation message

## API Contract


| Operation               | Input            | Output                | Description                                  |
| ------------------------- | ------------------ | ----------------------- | ---------------------------------------------- |
| `connect`               | ConnectionConfig | contract_blender_connection_protocol | Establish TCP socket connection              |
| `disconnect`            | —               | —                    | Close connection gracefully                  |
| `send_command`          | ActionName, dict | dict                  | Send command to Blender (5s timeout)         |
| `execute_blender_code`  | Prompt (str)     | ExecutionResult       | Execute Python code in Blender (30s timeout) |
| `submit_async_task`     | Prompt (str)     | task_id (str)         | Submit long-running code for async execution |
| `poll_task_result`      | task_id (str)    | ExecutionResult       | Poll async task status and result            |
| `get_connection_status` | —               | ConnectionStatus      | Return current connection state              |

Additional contract behavior:

- `connect` must perform handshake, protocol version validation, and authentication when enabled
- `disconnect` must be idempotent and must not throw an error if connection is already closed
- `send_command` uses default 5 second timeout unless command metadata defines another timeout
- `execute_blender_code` returns synchronous `ExecutionResult` for normal execution
- `submit_async_task` returns `{task_id, status}` where initial status is usually `pending`
- `poll_task_result` returns task status and, when finished, final `ExecutionResult`
- `poll_task_result` should not require Blender main-thread execution queue if task state is stored locally
- `get_connection_status` returns `ConnectionStatus {state, host, port, last_error, last_heartbeat_at, reconnect_attempts, protocol_version}`
- All requests should include `request_id`
- All responses should include corresponding `request_id`
- All messages must be UTF-8 encoded JSON
- Message framing must be deterministic, for example length-prefixed JSON or newline-delimited JSON
- Maximum request and response payload size must be configurable

## Integration Points

- **Internal:**
  - **blender-arwaky/modules/shared** for sharing vo,entity,error,event,utility,contract,constant
  - **blender-arwaky/modules/config** for server settings (host, port, timeout, retry policy, blocked patterns list, allowed directories, payload limits, heartbeat settings, authentication settings)
  - **blender-arwaky/modules/mcp**  MCP tool definitions and response formatting
- **External:**
  - Blender addon (TCP socket listener on configurable port)
  - Blender Python API (`bpy`) — accessed exclusively through the addon
  - optional secret store or environment configuration for authentication token

## Non-functional Requirements

- **Performance:** Command response within 5 seconds by default; code execution within 30 seconds by default; server-side processing overhead should be minimal, ideally <100ms excluding Blender execution time; queue wait time should be configurable, default target <10 seconds under normal load
- **Reliability:** Auto-reconnect on connection loss (3 attempts, exponential backoff with jitter); graceful degradation on Blender crash; pending operations must fail deterministically; no operation may be silently dropped; in-flight operations must have defined failure or recovery behavior
- **Security:** Code execution validates against blocked patterns list using AST-based analysis; runtime sandbox enforcement must exist on Blender addon side; no arbitrary file system access outside allowed directories; default connection target is localhost; authentication token required for remote connections when enabled; payload size limits enforced; security violations logged as audit events; raw code payload not logged by default
- **Observability:** Log all connection state changes, command metadata, execution duration, queue wait duration, retry attempts, and error stack traces; code payload logging masked/hashed/truncated for sensitive content; structured logging recommended; each operation should be correlated using `request_id`; metrics should include queue depth, reconnect count, execution latency, command latency, failed request count, and security violation count
- **Concurrency:** All requests that access Blender state serialized (queued) due to Blender's single-threaded `bpy` constraint; queue depth limit of 50 pending operations; queue is FIFO by default; control operations such as connection status or task polling may bypass Blender execution queue; when queue is full, reject with `QueueFullError`; when queue wait timeout exceeded, reject with `QueueTimeoutError`

## Test Scenarios / QA Checklist

- Connect to running Blender instance succeeds
- Connect to non-running Blender returns `BlenderConnectionFailure`
- Connect with invalid config returns `ConnectionConfigError`
- Connect with invalid authentication token returns `AuthenticationError`
- Connect with unsupported protocol version returns `ProtocolVersionMismatchError`
- Connection loss triggers auto-reconnect (3 attempts, exponential backoff with jitter)
- After 3 failed reconnects, raises `BlenderConnectionExhausted`
- Heartbeat detects stale connection and triggers reconnect
- Heartbeat does not falsely trigger reconnect during active long-running execution
- Disconnect is idempotent
- Disconnect fails pending queued operations with `ConnectionClosedError`
- Execute valid Python code returns `ExecutionResult` with status "success"
- Execute code with syntax error returns `ExecutionResult` with status "error"
- Execute code exceeding 30s timeout returns `ExecutionTimeoutError`
- Execute code with blocked pattern (e.g., `os.system`) returns `SecurityViolationError`
- Execute code with obfuscated blocked import returns `SecurityViolationError`
- Execute code writing outside allowed directory returns `SecurityViolationError`
- Execute code writing inside allowed directory succeeds
- Execute code with oversized payload is rejected
- Execute code with oversized output returns truncated result with `truncated: true`
- Execute code with non-serializable output returns safe serialized fallback or explicit error
- Submit async task returns task_id
- Poll pending async task returns pending status
- Poll completed async task returns final `ExecutionResult`
- Poll unknown async task returns `TaskNotFoundError`
- Cancel pending async task succeeds
- Cancel running async task returns best-effort or unsupported status
- Async task result expires after configured TTL
- Blender crash during async task marks task as error
- Send valid command to Blender returns response within 5 seconds
- Send command exceeding 5s timeout returns `CommandTimeoutError`
- Send command with custom timeout respects configured timeout
- Send unknown command returns `ProviderError`
- Send command with invalid arguments returns `ValidationError`
- Send command with malformed JSON response returns parse/provider error
- Factory creates socket connection with valid config
- Factory rejects invalid port
- Factory rejects missing required fields
- Factory rejects unsupported protocol version
- Concurrent requests are serialized (queued) correctly
- Queue depth limit (50) enforced; excess requests rejected with `QueueFullError`
- Queued request exceeding wait timeout returns `QueueTimeoutError`
- Control operations do not block behind Blender execution queue when designed to bypass it
- Protocol message with malformed JSON is handled safely
- Protocol message with missing `request_id` is handled according to protocol rules
- Large response payload is truncated or rejected based on configured limit

## Assumptions & Constraints

- Blender addon must be running and listening on TCP socket
- Single connection per server instance
- Code execution has 30-second timeout (configurable via ConnectionConfig)
- Command execution has 5-second timeout by default
- Some commands may define custom timeout metadata
- Because Blender's Python API (`bpy`) is not thread-safe and runs on the main thread, all concurrent requests from external consumers (MCP, CLI) are serialized (queued) to prevent race conditions and Blender crashes
- Blocked patterns list is maintained in config and updated as needed
- Blender addon protocol version must match or be compatible with server protocol version
- User-provided code is treated as untrusted or semi-trusted input
- Server-side static validation is not a complete sandbox; Blender addon must enforce runtime restrictions
- Allowed directories for file access must be explicitly configured
- Default allowed directory is the active `.blend` file directory unless otherwise configured
- Authentication token is required for non-local connections when authentication is enabled
- Default connection target should be localhost for security
- Async task state is stored in-memory unless persistence is explicitly enabled
- Async task result retention has configurable TTL
- Cancellation of running Blender execution is best-effort because Blender main-thread execution may not be immediately interruptible
- Heartbeat mechanism must account for long-running Blender operations to avoid false stale-connection detection
- Maximum payload size for requests and responses must be configured and enforced

## Glossary

- **MCP (Model Context Protocol):** Standard protocol for AI agent tool integration; defines how the AI agent invokes tools and receives results
- **contract_blender_connection_protocol:** Contract (interface) for Blender TCP communication
- **contract_code_execution_protocol:** Contract (interface) for Python code execution in Blender
- **ConnectionConfig:** Configuration object containing host, port, timeout, retry_policy, authentication settings, protocol version, payload limits, heartbeat settings, and allowed directories
- **ExecutionResult:** Standardized response object for code execution containing status, data, error details, execution_time_ms, and truncation flag
- **Blocked Patterns:** Configurable list of forbidden Python patterns/modules to prevent security violations
- **AST Validation:** Static code analysis based on Python Abstract Syntax Tree, used to detect forbidden constructs more reliably than regex/string matching
- **Runtime Sandbox:** Enforcement mechanism on the Blender addon side that restricts file access, module usage, and unsafe operations during actual code execution
- **Allowed Directory:** Directory explicitly permitted for file write or file access operations
- **ConnectionStatus:** Object describing current connection state, endpoint info, last heartbeat, reconnect attempts, protocol version, and last error
- **TaskStatus:** Object describing async task lifecycle state, including pending, running, success, error, timeout, and cancelled
- **QueueFullError:** Error raised when serialized execution queue has reached maximum depth
- **QueueTimeoutError:** Error raised when a queued operation waits longer than configured queue wait timeout
- **AuthenticationError:** Error raised when connection authentication fails
- **ProtocolVersionMismatchError:** Error raised when server and Blender addon protocol versions are incompatible
- **Request ID:** Unique identifier used to correlate requests, responses, logs, and errors
