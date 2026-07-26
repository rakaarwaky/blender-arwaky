Below is the complete, developer-ready plan content for:

```text
.agents/plan/plan-server-remediation.md
```

I interpreted your answers as product decisions. Two answers required interpretation:

- You wrote `10C` near the end. I interpreted this as **D33 = C**: decide contract mismatches per contract using FRD as source of truth.
- For **D17**, you requested a timestamped temporary Blender file so there is effectively no “unsaved file” state. I converted this into a mandatory **Session Workspace Bootstrap** requirement.

---

# Plan: Server Remediation and Major Refactor — `server v2.0.0`

## 0. Product Decision Log


| ID  | Decision Area                                         | Final Product Decision                                                                                                                                                                                                              |
| ----- | ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| D1  | Release type                                          | **Major refactor release**. Server version target: `v2.0.0` because public contracts, error names, and aggregate responses change.                                                                                                  |
| D2  | Feature freeze                                        | **Partial freeze**. No new server features until P0 remediation is complete. Documentation, tests, observability, and non-conflicting surface work are allowed.                                                                     |
| D3  | Release gate                                          | **Strict**. All critical stability, security, contract, queue, observability, and testability requirements must pass before release.                                                                                                |
| D4  | New operations while reconnecting                     | **Reject immediately by default**. Configurability is approved conceptually but must not be implemented now. Config may contain a reserved field `reconnect_request_policy`, but only `reject` is supported in `v2.0.0`.            |
| D5  | Pending operations on graceful disconnect             | **Cancel all pending operations**. Running operations are not forcibly cancelled by default.                                                                                                                                        |
| D6  | Pending operations after permanent connection failure | **Cancel all pending operations** and return a clear connection-lost error.                                                                                                                                                         |
| D7  | Version handshake timing                              | **Always perform version handshake**, even when authentication is not required.                                                                                                                                                     |
| D8  | Version compatibility rule                            | **Same major version is compatible**. Example: server `2.1.0` accepts addon `2.9.3`, rejects addon `3.0.0`.                                                                                                                         |
| D9  | Authentication policy                                 | **Local-only default, no auth required. Remote connections require auth token.**                                                                                                                                                    |
| D10 | Queue ownership                                       | **Agent orchestrator owns queue processing**.                                                                                                                                                                                       |
| D11 | Operations serialized                                 | **Custom code execution and scene-mutating commands are serialized**. Non-scene read-only commands may bypass the queue.                                                                                                            |
| D12 | Scene-mutation classification                         | **Use command catalog metadata**. Remove prefix-based heuristics such as `action.startswith("get_")`.                                                                                                                               |
| D13 | Queue full behavior                                   | **Reject immediately** with `TooManyPendingOperationsError`.                                                                                                                                                                        |
| D14 | Queue wait timeout                                    | **Configurable**, default `10000 ms`. Reject with `OperationWaitTimeoutError`.                                                                                                                                                      |
| D15 | AST validation ownership                              | **Centralize in Utility layer**. Remove duplicated validator logic from capabilities.                                                                                                                                               |
| D16 | File-write policy                                     | **Strict deny by default**. File writes are allowed only when static analysis can prove the target path is inside an allowed directory.                                                                                             |
| D17 | Unsaved Blender file policy                           | **Session Workspace Bootstrap required**. Blender addon must ensure an active timestamped temporary `.blend` file exists so there is no unsaved-file state. Server uses the active file directory as the default allowed directory. |
| D18 | Obfuscation detection                                 | **Strict**. Block dynamic attribute access, dynamic imports, dynamic evaluation, and common obfuscation primitives.                                                                                                                 |
| D19 | Raw code logging                                      | **Never log raw user code by default**. No configuration option may enable raw code logging in this release.                                                                                                                        |
| D20 | Public task cancellation API                          | **Add public `cancel_async_task`** to aggregate contract.                                                                                                                                                                           |
| D21 | Task polling response                                 | **Return `TaskStatus`**, not bare `ExecutionResult`. `TaskStatus` may contain an optional `ExecutionResult`.                                                                                                                        |
| D22 | Running task cancellation semantics                   | **Attempt Python async cancellation only**. If the Blender operation was already dispatched, Blender may continue; local task state must reflect best-effort cancellation.                                                          |
| D23 | Task persistence                                      | **In-memory only** for `v2.0.0`. Document that restart clears tasks.                                                                                                                                                                |
| D24 | Background commands                                   | **No background commands in this release**. Only custom code supports background execution.                                                                                                                                         |
| D25 | Unknown command error                                 | **`ValidationError`** with error code `unknown_command`.                                                                                                                                                                            |
| D26 | Oversized command response                            | **Truncate with flag**.                                                                                                                                                                                                             |
| D27 | Error naming                                          | **Rename code errors to FRD-aligned names exactly**. Breaking change.                                                                                                                                                               |
| D28 | Tracking ID format                                    | **UUID4 string**. Server generates one if client does not provide one.                                                                                                                                                              |
| D29 | Event emission                                        | **Emit events through an event bus/port**.                                                                                                                                                                                          |
| D30 | Metrics                                               | **Full metrics endpoint**. Server exposes metrics through aggregate and a diagnostics controller; CLI/MCP surfaces must expose it to clients.                                                                                       |
| D31 | Configuration surface                                 | **Programmatic config + config file + environment variables**.                                                                                                                                                                      |
| D32 | Configuration schema                                  | Approved, with adjustments from D4, D17, D19, and D26.                                                                                                                                                                              |
| D33 | Contract mismatch policy                              | **Decide per contract using FRD as source of truth**. Where FRD is ambiguous, this plan defines the binding behavior.                                                                                                               |
| D34 | External`ConfigPort` dependency                       | **Remove dependency from server capability for now**. Server receives fully resolved server configuration. Centralized config system may be introduced later.                                                                       |
| D35 | Gherkin acceptance criteria                           | **Mandatory** for all functional requirements.                                                                                                                                                                                      |
| D36 | Test levels                                           | **Unit + integration + functional** are mandatory.                                                                                                                                                                                  |
| D37 | Plan location                                         | `.agents/plan/plan-server-remediation.md`                                                                                                                                                                                           |

---

## 1. Objective

Refactor the `server` module into a stable, secure, observable, and contract-compliant Blender communication server.

The release must guarantee:

1. FRD-promised connection lifecycle behavior is implemented.
2. Scene-affecting operations are truly processed sequentially.
3. User-provided code is validated through a single centralized security policy.
4. File-write access is restricted to explicitly allowed directories.
5. Background task lifecycle is complete, cancellable, and semantically correct.
6. All public APIs return typed value objects, not ad hoc dictionaries.
7. All errors use FRD-aligned names and stable error codes.
8. Every request is traceable by UUID4 tracking ID.
9. Events are emitted through an event bus.
10. Metrics are collected and exposed through a diagnostics endpoint.
11. Acceptance criteria are written in Gherkin and automated.
12. AES layer rules are enforced.

---

## 2. Release Scope

### 2.1 In Scope

- Major refactor of `modules/server`.
- Breaking contract changes in `modules/shared/src/server`.
- Taxonomy updates for VOs, errors, events, constants, and command catalog metadata.
- Utility-layer centralization for:
  - AST security validation
  - payload size validation
  - command schema validation
  - config loading
  - request ID generation
  - message framing
  - truncation
  - code fingerprinting
- Agent-owned operation queue with FIFO execution.
- Event bus and metrics collector.
- Public task cancellation.
- Metrics diagnostics controller.
- Gherkin acceptance criteria.
- Unit, integration, and functional tests.
- FRD addendum.
- Migration notes for breaking changes.

### 2.2 Out of Scope for v2.0.0

- Persistent task storage.
- Background execution for standard commands.
- Configurable reconnect request policy beyond `reject`.
- Centralized application-wide config system.
- Raw code logging for diagnostics.
- Multi-connection support.
- Remote anonymous access.
- Full HTTP metrics server inside the core server module.
  - The server module exposes metrics through aggregate/controller.
  - Transport exposure is done by CLI/MCP surface modules.

---

## 3. Non-Negotiable Engineering Rules

All implementation work must obey these rules.

### 3.1 AES Rules

- Taxonomy must contain only stable domain types.
- Contracts must depend only on Taxonomy.
- Utility must contain stateless standalone functions only.
- Capabilities must implement contracts.
- Capabilities must not import other capabilities.
- Agent must coordinate flows and depend on contracts only.
- Root may wire concrete implementations but must not contain business logic.
- Shared technical logic must not be duplicated in capabilities.

### 3.2 Async Rules

- Do not call `time.sleep()` inside async functions.
- Do not call an async coroutine from `run_in_executor` without awaiting it.
- Do not block the asyncio event loop with synchronous socket I/O.
- Use asyncio streams or executor-bound adapters consistently.
- All background asyncio tasks must be tracked and cancellable.

### 3.3 Security Rules

- Never log raw user code.
- Log only code fingerprint, length, request ID, and validation outcome.
- All security violations must emit an audit event.
- File writes must be denied unless the target path is statically provable inside an allowed directory.
- Dynamic path writes must be rejected by static validation.

### 3.4 API Rules

- Public aggregate methods must not return raw `dict` as the final typed response.
- Public errors must use FRD-aligned class names.
- Every request and response must carry a tracking ID.
- Every error response must include error code, message, details, and tracking ID.

---

## 4. Target Behavior Specification

## 4.1 Configuration Behavior

### 4.1.1 Configuration Priority

Configuration resolution order must be:

```text
1. Explicit programmatic ServerConfig
2. Environment variables
3. Config file
4. Built-in defaults
```

### 4.1.2 Config File Discovery

Default config file:

```text
config.yaml
```

Environment override:

```text
BLENDERMCP_CONFIG_PATH=/path/to/config.yaml
```

### 4.1.3 Approved Server Configuration Schema

```yaml
server:
  host: localhost
  port: 9876
  transport_type: socket
  connection_timeout_seconds: 30.0
  protocol_version: "2.0.0"
  auth_token: null
  require_auth_for_remote: true
  heartbeat_interval_seconds: 10
  heartbeat_failure_threshold: 3
  reconnect_max_attempts: 3
  reconnect_base_delay_seconds: 1.0
  reconnect_max_delay_seconds: 4.0
  reconnect_request_policy: reject

queue:
  max_depth: 50
  wait_timeout_ms: 10000

execution:
  default_timeout_ms: 30000
  max_code_payload_bytes: 1048576
  max_output_bytes: 10240

command:
  default_timeout_ms: 5000
  max_response_bytes: 1048576

tasks:
  retention_seconds: 600

security:
  allowed_directories: []
  use_active_file_directory: true

workspace:
  temp_blend_directory: "<system_temp>/blender-arwaky/sessions"
  filename_prefix: "blender_session"
  ensure_temp_blend_file: true

observability:
  metrics_enabled: true
  event_bus_enabled: true
```

### 4.1.4 Reserved or Restricted Fields

These fields are reserved but not configurable beyond allowed values in `v2.0.0`:

```yaml
server.reconnect_request_policy: reject
```

If any value other than `reject` is provided:

```text
Raise ConnectionConfigError:
"reconnect_request_policy only supports 'reject' in v2.0.0"
```

Raw code logging must not be configurable:

```text
No config key named log_raw_code may exist.
```

Oversized response policy is always truncate-with-flag:

```text
No oversize_policy config key may exist in v2.0.0.
```

### 4.1.5 Environment Variables

Minimum required environment variables:

```text
BLENDERMCP_CONFIG_PATH
BLENDER_HOST
BLENDER_PORT
BLENDER_AUTH_TOKEN
BLENDER_PROTOCOL_VERSION
SERVER_QUEUE_MAX_DEPTH
SERVER_QUEUE_WAIT_TIMEOUT_MS
SERVER_EXECUTION_TIMEOUT_MS
SERVER_ALLOWED_DIRECTORIES
```

`SERVER_ALLOWED_DIRECTORIES` must use the platform path separator:

- Linux/macOS: `:`
- Windows: `;`

---

## 4.2 Connection Lifecycle Behavior

### 4.2.1 Connection States

The connection must report exactly these states:

```text
disconnected
connecting
connected
reconnecting
failed
closed
```

### 4.2.2 Connect Behavior

`connect(config: ConnectionConfig)` must:

1. Validate configuration.
2. Reject remote connections when authentication token is missing and `require_auth_for_remote` is true.
3. Set state to `connecting`.
4. Open asyncio TCP connection.
5. Apply per-attempt timeout:

```text
config.timeout_seconds
```

6. Send handshake request.
7. Verify protocol version.
8. Authenticate if token is present or required.
9. Receive session workspace metadata.
10. Set state to `connected`.
11. Start heartbeat task.
12. Emit `ConnectionEstablished`.
13. Return `ConnectionStatus`.

### 4.2.3 Timeout Semantics

```text
connection_timeout_seconds applies per connection attempt.
Total connection time may exceed connection_timeout_seconds because retries use backoff.
```

### 4.2.4 Retry Behavior

Retry rules:

```text
max_attempts = server.reconnect_max_attempts
default = 3

delay for attempt n:
  base = reconnect_base_delay_seconds * 2^n
  capped = min(base, reconnect_max_delay_seconds)
  jitter = deterministic or random jitter between 0 and 0.5 * capped
  final_delay = capped + jitter
```

After all attempts fail:

```text
state = failed
raise BlenderConnectionExhausted
emit ConnectionReconnectFailed
cancel pending operations with BlenderConnectionExhausted
```

### 4.2.5 Version Handshake

Handshake must always occur.

Server sends:

```json
{
  "type": "handshake",
  "request_id": "<uuid4>",
  "protocol_version": "2.0.0",
  "params": {
    "auth_token": "<token-or-null>",
    "workspace": {
      "ensure_temp_blend_file": true,
      "temp_directory": "<configured-temp-directory>",
      "filename_prefix": "blender_session"
    }
  }
}
```

Addon responds:

```json
{
  "status": "ok",
  "request_id": "<uuid4>",
  "protocol_version": "2.3.1",
  "result": {
    "session_id": "<uuid4>",
    "active_file_path": "/tmp/blender-arwaky/sessions/blender_session_20260726_153045_3f9a1b2c.blend",
    "active_directory": "/tmp/blender-arwaky/sessions"
  }
}
```

Compatibility rule:

```text
major(server_protocol_version) == major(addon_protocol_version)
```

If incompatible:

```text
raise VersionMismatchError(expected=server_version, actual=addon_version)
```

### 4.2.6 Authentication Behavior

Local hosts:

```text
localhost
127.0.0.1
::1
```

Rules:

```text
If host is local:
  auth_token optional

If host is remote:
  auth_token required
  missing token => ConnectionConfigError
  invalid token => AuthenticationError
```

### 4.2.7 Session Workspace Bootstrap

This implements decision D17.

The Blender addon must guarantee that an active Blender file exists.

If `bpy.data.filepath` is empty when the server handshake occurs, the addon must:

1. Create directory:

```text
<workspace.temp_blend_directory>
```

2. Create file name:

```text
<filename_prefix>_YYYYMMDD_HHMMSS_<uuid4-hex-8>.blend
```

Example:

```text
blender_session_20260726_153045_3f9a1b2c.blend
```

3. Save the current Blender session as that file.
4. Return:

```json
{
  "active_file_path": "<full-path>",
  "active_directory": "<parent-directory>"
}
```

Server behavior:

```text
If security.use_active_file_directory is true:
    add active_directory to effective allowed_directories

If active_directory is empty:
    effective allowed_directories remains configured list only
    file writes are denied unless allowed_directories is explicitly configured
    emit SecurityViolationDetected only when a write is attempted
```

### 4.2.8 Heartbeat Behavior

Heartbeat must be an asyncio task.

Rules:

```text
interval = server.heartbeat_interval_seconds
failure_threshold = server.heartbeat_failure_threshold
```

Heartbeat sends:

```json
{
  "type": "ping",
  "request_id": "<uuid4>",
  "params": {}
}
```

Expected response:

```json
{
  "status": "ok",
  "result": {}
}
```

Failure handling:

```text
If no response before next interval:
  increment consecutive_failures

If consecutive_failures >= failure_threshold:
  if active_operation_in_progress:
     do not reconnect immediately
     log warning
     wait until operation completes or operation timeout occurs
  else:
     set state=reconnecting
     emit ConnectionLost(reason="timeout")
     attempt reconnect
```

### 4.2.9 Active Operation Protection

The connection must expose:

```python
def set_active_operation_in_progress(self, active: bool) -> None:
    ...
```

The orchestrator must call:

```python
connection.set_active_operation_in_progress(True)
```

before executing a queued Blender operation, and:

```python
connection.set_active_operation_in_progress(False)
```

after completion, failure, timeout, or cancellation.

### 4.2.10 New Operations While Reconnecting

Because D4 is `reject`:

```text
If connection state is not connected:
  reject new operations immediately
```

Error mapping:

```text
state=reconnecting => BlenderConnectionFailure with details.state="reconnecting"
state=failed => BlenderConnectionExhausted
state=closed => ConnectionClosedError
state=disconnected => BlenderConnectionFailure with details.state="disconnected"
```

### 4.2.11 Disconnect Behavior

`disconnect()` must:

1. Be idempotent.
2. Stop accepting new operations.
3. Cancel all pending queued operations with `ConnectionClosedError`.
4. Stop heartbeat task.
5. Close socket.
6. Set state to `closed`.
7. Emit `ConnectionLost(reason="closed")`.

Running operations:

```text
Running operations are not explicitly cancelled by disconnect.
However, because the socket is closed, local waiters receive ConnectionClosedError.
Blender may continue the operation internally.
This must be documented.
```

---

## 4.3 Operation Queue Behavior

### 4.3.1 Queue Ownership

The Agent layer, `ServerOrchestrator`, owns queue processing.

The command adapter must not own the execution queue.

### 4.3.2 Operations That Must Be Serialized

Serialized operations:

```text
execute_code
submit_async_task execution
all commands where command_spec.mutates_scene == true
```

Bypass queue:

```text
commands where command_spec.mutates_scene == false
get_status
get_metrics
```

### 4.3.3 Queue Limits

Defaults:

```text
queue_max_depth = 50
queue_wait_timeout_ms = 10000
```

When depth limit exceeded:

```text
raise TooManyPendingOperationsError
emit OperationRejected(reason="queue_full")
```

When operation waits too long to start:

```text
raise OperationWaitTimeoutError
emit OperationRejected(reason="queue_wait_timeout")
```

### 4.3.4 FIFO Guarantee

Operations must start in the exact order received.

Exception:

```text
Non-scene read-only commands bypass the queue and may execute immediately.
```

### 4.3.5 Queue Worker Behavior

The orchestrator must run a queue worker task.

Worker pseudocode:

```text
while running:
    operation = await queue.dequeue()

    if operation is None:
        sleep briefly
        continue

    mark operation started
    set connection active operation = true

    try:
        if operation.type == "code_sync":
            result = await code_executor.execute_blender_code(...)
        elif operation.type == "code_async":
            result = await code_executor.execute_task(...)
        elif operation.type == "command":
            result = await command_adapter.send_command(...)

        queue.complete(operation.request_id, result)

    except CancelledError:
        queue.fail(operation.request_id, cancelled_error)

    except Exception as error:
        queue.fail(operation.request_id, error)

    finally:
        set connection active operation = false
```

### 4.3.6 Pending Cancellation

Pending operations must be cancelled when:

```text
disconnect() is called
connection permanently fails
shutdown() is called
```

Pending operations receive:

```text
disconnect/shutdown => ConnectionClosedError
permanent failure => BlenderConnectionExhausted
```

---

## 4.4 Security Policy Behavior

### 4.4.1 Single Validator

All AST validation must use:

```text
modules/shared/src/server/utility_server_validator.py
```

Capabilities must not contain private AST denylists.

### 4.4.2 Blocked Modules

Minimum blocked modules:

```text
os
subprocess
shutil
importlib
sys
socket
urllib
requests
ctypes
multiprocessing
threading
signal
pickle
shelve
io
```

### 4.4.3 Blocked Functions

Minimum blocked functions:

```text
eval
exec
compile
__import__
breakpoint
exit
quit
globals
locals
vars
getattr
setattr
delattr
```

### 4.4.4 Blocked Attributes

Minimum blocked attributes:

```text
__subclasses__
__bases__
__mro__
__globals__
__builtins__
__import__
__loader__
__spec__
__file__
__name__
__package__
```

### 4.4.5 File Write Rules

File write modes:

```text
w
a
x
+
```

For any `open(...)` or `.open(...)` call with a write mode:

```text
If path argument is a literal string:
    normalize path
    if path is inside one of effective allowed_directories:
        allow
    else:
        raise SecurityViolationError(rule="file_write_outside_allowed_directory")

If path argument is not a literal string:
    raise SecurityViolationError(rule="dynamic_file_write_path_not_allowed")
```

Read-only open is allowed.

### 4.4.6 Effective Allowed Directories

Effective allowed directories are calculated as:

```text
configured security.allowed_directories
+
active_directory from handshake if security.use_active_file_directory == true
```

All directories must be normalized before comparison.

### 4.4.7 Code Fingerprinting

Utility must provide:

```python
def code_fingerprint(code: str) -> str:
    ...
```

Behavior:

```text
Return sha256 hex digest prefix, maximum 16 characters.
Never return raw code.
```

Logs must include:

```text
request_id
code_fingerprint
code_length_bytes
validation_result
error_type
execution_time_ms
```

Logs must never include:

```text
raw code
code snippet
user file contents
```

### 4.4.8 Security Audit Event

Every security violation must emit:

```python
SecurityViolationDetected(
    request_id=request_id,
    rule=rule_name,
    code_fingerprint=fingerprint,
)
```

---

## 4.5 Code Execution Behavior

### 4.5.1 Sync Execution

Public API:

```python
async def execute_code(
    self,
    code: str,
    request_id: RequestId | None = None,
) -> ExecutionResult:
    ...
```

Behavior:

1. Generate request ID if missing.
2. Validate payload size.
3. Validate code AST.
4. Emit `CodeExecutionRequested` or log request metadata.
5. Enqueue operation.
6. Wait for queue start using `queue.wait_timeout_ms`.
7. Wait for execution result using `execution.default_timeout_ms` unless overridden.
8. Return `ExecutionResult`.

### 4.5.2 Execution Result Requirements

`ExecutionResult` must include:

```text
request_id
status
data
error
execution_time_ms
truncated
```

### 4.5.3 Output Truncation

If execution output exceeds:

```text
execution.max_output_bytes
```

then:

```text
truncate output
set truncated = true
append marker: "\n...[truncated]"
```

### 4.5.4 Error Handling for Sync Execution

Return `ExecutionResult(status="error")` for:

```text
Blender runtime exceptions
syntax errors detected during execution result
invalid response payload from Blender
```

Raise typed errors for:

```text
SecurityViolationError
TooManyPendingOperationsError
OperationWaitTimeoutError
ExecutionTimeoutError
ConnectionClosedError
BlenderConnectionFailure
BlenderConnectionExhausted
```

---

## 4.6 Background Task Behavior

### 4.6.1 Task States

Task states:

```text
pending
running
success
error
timeout
cancelled
```

### 4.6.2 Submit Async Task

Public API:

```python
async def submit_async_task(
    self,
    code: str,
    request_id: RequestId | None = None,
) -> str:
    ...
```

Behavior:

1. Generate request ID if missing.
2. Validate code.
3. Create task with state `pending`.
4. Enqueue operation of type `code_async`.
5. Emit `TaskCreated`.
6. Return `task_id`.

### 4.6.3 Poll Task Result

Public API:

```python
async def poll_task_result(
    self,
    task_id: str,
    request_id: RequestId | None = None,
) -> TaskStatus:
    ...
```

Return:

```python
TaskStatus(
    task_id=task_id,
    state=state,
    result=execution_result_or_none,
    request_id=request_id,
    created_at=created_at,
    completed_at=completed_at,
    cancel_requested=cancel_requested,
)
```

For unknown or expired task:

```text
raise TaskNotFoundError
```

### 4.6.4 Cancel Async Task

Public API:

```python
async def cancel_async_task(
    self,
    task_id: str,
    request_id: RequestId | None = None,
) -> TaskStatus:
    ...
```

Behavior:

```text
If task is pending:
    remove from queue if possible
    mark state=cancelled
    emit TaskCancelled
    return TaskStatus

If task is running:
    attempt asyncio cancellation of local operation task
    set cancel_requested=true

    if cancellation succeeds before completion:
        mark state=cancelled
        emit TaskCancelled
    else:
        task may finish as success/error/timeout

    return current TaskStatus

If task is terminal:
    return current TaskStatus

If task unknown:
    raise TaskNotFoundError
```

### 4.6.5 Task Retention

Default retention:

```text
600 seconds
```

Expired tasks must be removed.

Cleanup must occur:

```text
on task creation
on task polling
on queue worker cycle
```

No persistent storage is supported.

---

## 4.7 Standard Command Behavior

### 4.7.1 Command Catalog

Create server command catalog metadata.

Each command must define:

```text
name
required_params
optional_params
param_types
default_timeout_ms
max_timeout_ms
idempotent
mutates_scene
background_allowed
```

### 4.7.2 Initial Required Commands

Minimum command specs:


| Command            | Mutates Scene | Idempotent | Default Timeout |
| -------------------- | --------------: | -----------: | ----------------: |
| `ping`             |         false |       true |            5000 |
| `get_status`       |         false |       true |            5000 |
| `get_version`      |         false |       true |            5000 |
| `get_scene_info`   |         false |       true |            5000 |
| `get_object_info`  |         false |       true |            5000 |
| `get_screenshot`   |         false |       true |            5000 |
| `execute_code`     |          true |      false |           30000 |
| `ensure_workspace` |          true |       true |            5000 |

### 4.7.3 Unknown Command

Unknown command must raise:

```python
ValidationError(message="Unknown command: <name>")
```

Error code:

```text
unknown_command
```

### 4.7.4 Invalid Parameters

Invalid parameters must raise:

```python
ValidationError
```

Examples:

```text
missing required parameter
unknown parameter
wrong primitive type
```

### 4.7.5 Command Timeout

Default:

```text
5000 ms
```

Command-specific timeout:

```text
use command_spec.default_timeout_ms if caller does not provide timeout_ms
use caller timeout_ms if provided and <= command_spec.max_timeout_ms
reject caller timeout_ms > max_timeout_ms with ValidationError
```

Timeout error:

```python
CommandTimeoutError(action=action, timeout_ms=effective_timeout)
```

### 4.7.6 Command Response Truncation

If serialized command response exceeds:

```text
command.max_response_bytes
```

then:

```text
truncate response
set CommandResult.truncated = true
```

---

## 4.8 Observability Behavior

### 4.8.1 Event Bus

Create event bus contract and in-memory capability.

Contract:

```python
class IEventPublisher(ABC):
    async def publish(self, event: ServerEvent) -> None:
        ...

class IEventSubscriber(ABC):
    async def handle(self, event: ServerEvent) -> None:
        ...
```

### 4.8.2 Required Events

Minimum events:

```text
ConnectionEstablished
ConnectionLost
ConnectionStateChanged
ConnectionReconnectAttempted
ConnectionReconnectFailed
CodeExecuted
CodeExecutionFailed
SecurityViolationDetected
TaskCreated
TaskStarted
TaskCompleted
TaskFailed
TaskTimedOut
TaskCancelled
CommandDispatched
CommandFailed
CommandTimedOut
ItemEnqueued
ItemDequeued
OperationRejected
```

All events must include optional or required `request_id` where relevant.

### 4.8.3 Metrics Collector

Metrics collector subscribes to event bus.

It must maintain:

```text
pending_operations
running_operations
reconnect_count
failed_request_count
security_violation_count
code_execution_count
command_count
task_created_count
task_completed_count
task_failed_count
task_timeout_count
task_cancelled_count
average_code_latency_ms
average_command_latency_ms
last_updated_at
```

### 4.8.4 Metrics VO

```python
@dataclass(frozen=True)
class ServerMetrics:
    pending_operations: int
    running_operations: int
    reconnect_count: int
    failed_request_count: int
    security_violation_count: int
    code_execution_count: int
    command_count: int
    task_created_count: int
    task_completed_count: int
    task_failed_count: int
    task_timeout_count: int
    task_cancelled_count: int
    average_code_latency_ms: float
    average_command_latency_ms: float
    last_updated_at: float
    request_id: RequestId | None = None
```

### 4.8.5 Metrics Endpoint

Server aggregate must expose:

```python
async def get_metrics(
    self,
    request_id: RequestId | None = None,
) -> ServerMetrics:
    ...
```

Diagnostics controller must format JSON:

```python
class ServerDiagnosticsController:
    def __init__(self, aggregate: IBlenderServerAggregate) -> None:
        ...

    async def get_metrics_json(
        self,
        request_id: RequestId | None = None,
    ) -> dict[str, Any]:
        ...
```

CLI/MCP surface modules must expose this controller through their transport.

---

## 5. Error Catalog

### 5.1 Error Class Renames

Rename exactly:


| Old Class                      | New Class                       |
| -------------------------------- | --------------------------------- |
| `QueueFullError`               | `TooManyPendingOperationsError` |
| `QueueTimeoutError`            | `OperationWaitTimeoutError`     |
| `ProtocolVersionMismatchError` | `VersionMismatchError`          |

Remove old class names in `v2.0.0`. Do not keep aliases.

### 5.2 Public Error Codes


| Error Class                     | Error Code                     | Used When                                        |
| --------------------------------- | -------------------------------- | -------------------------------------------------- |
| `TooManyPendingOperationsError` | `too_many_pending_operations`  | Queue depth limit exceeded.                      |
| `OperationWaitTimeoutError`     | `operation_wait_timeout`       | Operation waited too long to start.              |
| `VersionMismatchError`          | `version_mismatch`             | Server/addon major protocol versions differ.     |
| `AuthenticationError`           | `authentication_failed`        | Token missing where required or invalid.         |
| `ConnectionConfigError`         | `connection_config_error`      | Invalid configuration.                           |
| `ConnectionClosedError`         | `connection_closed`            | Operation rejected after disconnect/close.       |
| `BlenderConnectionExhausted`    | `connection_retries_exhausted` | All reconnect attempts failed.                   |
| `BlenderConnectionFailure`      | `blender_connection_failure`   | Connection lost or unavailable.                  |
| `SecurityViolationError`        | `security_violation`           | Blocked code pattern or file access violation.   |
| `ExecutionTimeoutError`         | `execution_timeout`            | Code execution exceeded timeout.                 |
| `CommandTimeoutError`           | `command_timeout`              | Command exceeded timeout.                        |
| `TaskNotFoundError`             | `task_not_found`               | Unknown or expired task.                         |
| `ValidationError`               | `validation_error`             | Unknown command or invalid parameters.           |
| `ProviderError`                 | `provider_error`               | Blender addon returned command-specific failure. |
| `ExecutionError`                | `execution_error`              | Blender code execution returned runtime failure. |

---

## 6. Required File Changes

## 6.1 Shared Taxonomy Files

### 6.1.1 `modules/shared/src/server/taxonomy_server_constant.py`

Update constants:

```python
DEFAULT_PROTOCOL_VERSION: str = "2.0.0"
```

Add connection state constants:

```python
CONNECTION_STATE_DISCONNECTED: str = "disconnected"
CONNECTION_STATE_CONNECTING: str = "connecting"
CONNECTION_STATE_CONNECTED: str = "connected"
CONNECTION_STATE_RECONNECTING: str = "reconnecting"
CONNECTION_STATE_FAILED: str = "failed"
CONNECTION_STATE_CLOSED: str = "closed"
```

Add task state constants:

```python
TASK_STATE_PENDING: str = "pending"
TASK_STATE_RUNNING: str = "running"
TASK_STATE_SUCCESS: str = "success"
TASK_STATE_ERROR: str = "error"
TASK_STATE_TIMEOUT: str = "timeout"
TASK_STATE_CANCELLED: str = "cancelled"
```

Add operation type constants:

```python
OPERATION_TYPE_CODE_SYNC: str = "code_sync"
OPERATION_TYPE_CODE_ASYNC: str = "code_async"
OPERATION_TYPE_COMMAND: str = "command"
```

---

### 6.1.2 `modules/shared/src/server/taxonomy_server_vo.py`

Update `ConnectionStatus`:

```python
@dataclass(frozen=True)
class ConnectionStatus:
    state: ConnectionState
    host: str
    port: int
    transport_type: str = "socket"
    last_error: str | None = None
    protocol_version: str | None = None
    reconnect_attempts: int = 0
    request_id: RequestId | None = None
    last_heartbeat_at: float | None = None
    heartbeat_interval_seconds: int = 10
    heartbeat_failure_threshold: int = 3
    session_id: str | None = None
    active_file_path: str | None = None
    active_directory: str | None = None
```

Update `ExecutionResult`:

```python
@dataclass(frozen=True)
class ExecutionResult:
    status: ExecutionStatus
    data: dict | str | bytes | None = None
    error: ExecutionErrorDetail | None = None
    execution_time_ms: float = 0.0
    truncated: bool = False
    request_id: RequestId | None = None
```

Update `CommandResult`:

```python
@dataclass(frozen=True)
class CommandResult:
    status: str
    data: dict | str | None = None
    error: ExecutionErrorDetail | None = None
    execution_time_ms: float = 0.0
    truncated: bool = False
    request_id: RequestId | None = None
```

Update `TaskStatus`:

```python
@dataclass(frozen=True)
class TaskStatus:
    task_id: str
    state: TaskState
    result: ExecutionResult | None = None
    request_id: RequestId | None = None
    created_at: float | None = None
    completed_at: float | None = None
    cancel_requested: bool = False
```

Add `ServerMetrics` as defined above.

Add `CodeSecurityPolicy`:

```python
@dataclass(frozen=True)
class CodeSecurityPolicy:
    allowed_directories: tuple[str, ...] = ()
    max_payload_bytes: int = 1_048_576
```

Add `QueuedOperation`:

```python
@dataclass(frozen=True)
class QueuedOperation:
    request_id: RequestId
    operation_type: str
    payload: dict
    task_id: str | None = None
    action: str | None = None
    timeout_ms: float | None = None
    enqueued_at: float = 0.0
```

Add `ServerConfig` and nested config VOs:

```python
@dataclass(frozen=True)
class ServerConfig:
    host: str = "localhost"
    port: int = 9876
    transport_type: str = "socket"
    connection_timeout_seconds: float = 30.0
    protocol_version: str = "2.0.0"
    auth_token: str | None = None
    require_auth_for_remote: bool = True
    heartbeat_interval_seconds: int = 10
    heartbeat_failure_threshold: int = 3
    reconnect_max_attempts: int = 3
    reconnect_base_delay_seconds: float = 1.0
    reconnect_max_delay_seconds: float = 4.0
    reconnect_request_policy: str = "reject"
    queue_max_depth: int = 50
    queue_wait_timeout_ms: float = 10_000.0
    execution_default_timeout_ms: float = 30_000.0
    max_code_payload_bytes: int = 1_048_576
    max_execution_output_bytes: int = 10_240
    command_default_timeout_ms: float = 5_000.0
    max_command_response_bytes: int = 1_048_576
    task_retention_seconds: float = 600.0
    allowed_directories: tuple[str, ...] = ()
    use_active_file_directory: bool = True
    temp_blend_directory: str | None = None
    workspace_filename_prefix: str = "blender_session"
    ensure_temp_blend_file: bool = True
    metrics_enabled: bool = True
    event_bus_enabled: bool = True
```

---

### 6.1.3 `modules/shared/src/server/taxonomy_server_error.py`

Rename errors:

```python
class TooManyPendingOperationsError(ServerError):
    ...

class OperationWaitTimeoutError(ServerError):
    ...

class VersionMismatchError(ServerError):
    ...
```

Remove:

```python
QueueFullError
QueueTimeoutError
ProtocolVersionMismatchError
CodeValidationError
```

Use `ValidationError` from common taxonomy for invalid syntax, unknown command, and invalid parameters.

All server errors must support:

```python
request_id: str | None = None
```

Example:

```python
class TooManyPendingOperationsError(ServerError):
    def __init__(
        self,
        max_depth: int = 50,
        request_id: str | None = None,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            "too_many_pending_operations",
            f"Queue full (depth={max_depth})",
            {"max_depth": max_depth, "request_id": request_id, **(details or {})},
        )
```

---

### 6.1.4 `modules/shared/src/server/taxonomy_server_event.py`

Add missing events:

```python
@dataclass(frozen=True)
class SecurityViolationDetected:
    request_id: str | None
    rule: str
    code_fingerprint: str

@dataclass(frozen=True)
class ConnectionStateChanged:
    old_state: str
    new_state: str
    reason: str | None = None

@dataclass(frozen=True)
class ConnectionReconnectAttempted:
    attempt: int
    delay_seconds: float

@dataclass(frozen=True)
class ConnectionReconnectFailed:
    attempts: int
    error_type: str
    message: str

@dataclass(frozen=True)
class CommandFailed:
    action: str
    request_id: str | None
    error_type: str
    message: str

@dataclass(frozen=True)
class OperationRejected:
    request_id: str | None
    reason: str
```

Add type alias:

```python
ServerEvent = (
    ConnectionEstablished
    | ConnectionLost
    | ConnectionStateChanged
    | ConnectionReconnectAttempted
    | ConnectionReconnectFailed
    | CodeExecuted
    | CodeExecutionFailed
    | SecurityViolationDetected
    | TaskCreated
    | TaskStarted
    | TaskCompleted
    | TaskFailed
    | TaskTimedOut
    | TaskCancelled
    | CommandDispatched
    | CommandFailed
    | CommandTimedOut
    | ItemEnqueued
    | ItemDequeued
    | OperationRejected
)
```

---

## 6.2 Shared Contract Files

### 6.2.1 `contract_connection_protocol.py`

Replace protocol with:

```python
class IBlenderConnectionProtocol(ABC):
    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        ...

    @abstractmethod
    async def send_command(
        self,
        command_type: ActionName,
        params: Details | None = None,
        request_id: RequestId | None = None,
        timeout_ms: float | None = None,
    ) -> CommandResult:
        ...

    @abstractmethod
    async def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        ...

    @abstractmethod
    def set_active_operation_in_progress(self, active: bool) -> None:
        ...
```

---

### 6.2.2 `contract_command_protocol.py`

Remove queue methods.

New protocol:

```python
class IBlenderCommandProtocol(ABC):
    @abstractmethod
    async def send_command(
        self,
        action: ActionName,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: RequestId | None = None,
    ) -> CommandResult:
        ...
```

---

### 6.2.3 `contract_code_execution_protocol.py`

Update protocol:

```python
class ICodeExecutionProtocol(ABC):
    @abstractmethod
    async def execute_blender_code(
        self,
        code: Prompt,
        request_id: RequestId | None = None,
    ) -> ExecutionResult:
        ...

    @abstractmethod
    async def execute_task(
        self,
        task_id: str,
        code: Prompt,
        request_id: RequestId | None = None,
    ) -> ExecutionResult:
        ...

    @abstractmethod
    def create_task(self, request_id: RequestId) -> str:
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> TaskStatus:
        ...

    @abstractmethod
    async def poll_task_result(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        ...

    @abstractmethod
    async def cancel_async_task(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        ...

    @abstractmethod
    def cleanup_expired(self) -> int:
        ...
```

Internal state-transition methods may remain private or protected.

---

### 6.2.4 `contract_server_aggregate.py`

New aggregate:

```python
class IBlenderServerAggregate(ABC):
    @abstractmethod
    async def start(self) -> None:
        ...

    @abstractmethod
    async def shutdown(self) -> None:
        ...

    @abstractmethod
    async def connect(
        self,
        config: ConnectionConfig,
        request_id: RequestId | None = None,
    ) -> ConnectionStatus:
        ...

    @abstractmethod
    async def disconnect(
        self,
        request_id: RequestId | None = None,
    ) -> None:
        ...

    @abstractmethod
    async def get_status(
        self,
        request_id: RequestId | None = None,
    ) -> ConnectionStatus:
        ...

    @abstractmethod
    async def execute_code(
        self,
        code: str,
        request_id: RequestId | None = None,
    ) -> ExecutionResult:
        ...

    @abstractmethod
    async def submit_async_task(
        self,
        code: str,
        request_id: RequestId | None = None,
    ) -> str:
        ...

    @abstractmethod
    async def poll_task_result(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        ...

    @abstractmethod
    async def cancel_async_task(
        self,
        task_id: str,
        request_id: RequestId | None = None,
    ) -> TaskStatus:
        ...

    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: RequestId | None = None,
    ) -> CommandResult:
        ...

    @abstractmethod
    async def get_metrics(
        self,
        request_id: RequestId | None = None,
    ) -> ServerMetrics:
        ...
```

---

### 6.2.5 New `contract_event_bus_protocol.py`

Create:

```python
class IEventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: ServerEvent) -> None:
        ...

class IEventSubscriber(ABC):
    @abstractmethod
    async def handle(self, event: ServerEvent) -> None:
        ...

class IEventBus(IEventPublisher):
    @abstractmethod
    def subscribe(self, subscriber: IEventSubscriber) -> None:
        ...
```

---

### 6.2.6 New `contract_metrics_protocol.py`

Create:

```python
class IMetricsProvider(ABC):
    @abstractmethod
    async def get_metrics(
        self,
        request_id: RequestId | None = None,
    ) -> ServerMetrics:
        ...
```

---

### 6.2.7 New `contract_operation_queue_protocol.py`

Create:

```python
class IOperationQueueProtocol(ABC):
    @abstractmethod
    async def enqueue(self, operation: QueuedOperation) -> int:
        ...

    @abstractmethod
    async def dequeue(self) -> QueuedOperation | None:
        ...

    @abstractmethod
    async def mark_started(self, request_id: RequestId) -> None:
        ...

    @abstractmethod
    async def complete(
        self,
        request_id: RequestId,
        result: ExecutionResult | CommandResult | str,
    ) -> None:
        ...

    @abstractmethod
    async def fail(self, request_id: RequestId, error: Exception) -> None:
        ...

    @abstractmethod
    async def wait_for_started(
        self,
        request_id: RequestId,
        timeout_ms: float,
    ) -> None:
        ...

    @abstractmethod
    async def wait_for_result(
        self,
        request_id: RequestId,
    ) -> ExecutionResult | CommandResult | str:
        ...

    @abstractmethod
    async def cancel_pending(self, error: Exception) -> int:
        ...

    @abstractmethod
    async def cancel_by_task_id(self, task_id: str, error: Exception) -> bool:
        ...

    @abstractmethod
    async def get_depth(self) -> int:
        ...
```

---

## 6.3 Shared Utility Files

### 6.3.1 `utility_server_validator.py`

Replace duplicated validation logic.

Required functions:

```python
def validate_code_ast(
    code: str,
    policy: CodeSecurityPolicy | None = None,
) -> None:
    ...

def check_payload_size(code: str, max_bytes: int) -> None:
    ...

def code_fingerprint(code: str) -> str:
    ...
```

Behavior must match Section 4.4.

---

### 6.3.2 `utility_server_schema.py`

Replace `_COMMAND_SCHEMAS` with catalog-driven validation.

Required functions:

```python
def get_command_spec(command: str) -> ServerCommandSpec:
    ...

def validate_command_args(
    command: str,
    params: dict[str, Any] | None,
) -> None:
    ...

def is_scene_mutating(command: str) -> bool:
    ...

def effective_command_timeout_ms(
    command: str,
    requested_timeout_ms: float | None,
) -> float:
    ...
```

Unknown command:

```python
raise ValidationError(f"Unknown command: {command}")
```

---

### 6.3.3 New `utility_server_config_loader.py`

Create stateless loader:

```python
def load_server_config(
    config_path: str | None = None,
    env: Mapping[str, str] | None = None,
    overrides: dict[str, Any] | None = None,
) -> ServerConfig:
    ...
```

Rules:

```text
- Load YAML if file exists.
- Apply environment overrides.
- Apply programmatic overrides.
- Validate all values.
- Return frozen ServerConfig.
- Raise ConnectionConfigError for invalid config.
```

---

### 6.3.4 New `utility_server_id.py`

Create:

```python
def new_request_id() -> RequestId:
    return RequestId(str(uuid.uuid4()))
```

---

### 6.3.5 `utility_server_message.py`

Implement wire protocol v2.

Frame format:

```text
[4-byte big-endian unsigned int length][UTF-8 JSON payload]
```

Required functions:

```python
def encode_message(payload: dict[str, Any]) -> bytes:
    ...

def decode_message_header(header: bytes) -> int:
    ...

def decode_message_payload(payload: bytes) -> dict[str, Any]:
    ...

def build_request(
    message_type: str,
    params: dict[str, Any],
    request_id: RequestId,
    protocol_version: str,
) -> dict[str, Any]:
    ...

def parse_response(data: bytes) -> dict[str, Any]:
    ...
```

Enforce maximum frame size.

---

### 6.3.6 `modules/shared/src/server/__init__.py`

Fix export inconsistency:

```text
Remove snake_to_camel from __all__ if it is not imported,
or import snake_to_camel from utility_server_string.
```

Export all new contracts, VOs, errors, events, and utilities.

---

## 6.4 Server Capability Files

### 6.4.1 `capabilities_blender_connection.py`

Rewrite completely.

Requirements:

- Remove dependency on `modules.config.src.contract_config.ConfigPort`.
- Remove synchronous socket blocking from async methods.
- Use asyncio streams.
- Accept `IEventPublisher` in constructor.
- Store `ConnectionConfig` on connect.
- Implement `connect(config) -> ConnectionStatus`.
- Implement handshake with workspace bootstrap parameters.
- Implement version compatibility check.
- Implement authentication policy.
- Implement heartbeat asyncio task.
- Implement reconnect with asyncio sleep.
- Implement `set_active_operation_in_progress`.
- Emit connection events.
- Return `CommandResult` from `send_command`.
- Never log raw payloads.

Constructor target:

```python
def __init__(
    self,
    event_publisher: IEventPublisher,
) -> None:
    ...
```

---

### 6.4.2 `capabilities_blender_command_adapter.py`

Rewrite.

Requirements:

- Remove queue state.
- Remove `enqueue`, `dequeue`, `wait_for_completion`, `get_depth`.
- Use command catalog validation.
- Use connection protocol.
- Return `CommandResult`.
- Apply command timeout.
- Truncate oversized responses.
- Emit command events.
- Raise `ValidationError` for unknown command/invalid params.
- Raise `CommandTimeoutError` on timeout.
- Return or raise provider errors according to Section 4.7.

Constructor target:

```python
def __init__(
    self,
    connection_port: IBlenderConnectionProtocol,
    event_publisher: IEventPublisher,
    max_command_response_bytes: int,
) -> None:
    ...
```

---

### 6.4.3 `capabilities_code_execution_adapter.py`

Rewrite.

Requirements:

- Remove private AST validator.
- Use `validate_code_ast`.
- Use `code_fingerprint`.
- Never log raw code.
- Accept `IEventPublisher`.
- Accept security policy.
- Accept execution timeout and output limits.
- Implement task lifecycle.
- Implement `execute_task`.
- Implement `cancel_async_task`.
- Return `TaskStatus` from polling.
- Use typed `ExecutionErrorDetail`.
- Emit task and execution events.
- Cleanup expired tasks.

Constructor target:

```python
def __init__(
    self,
    connection_port: IBlenderConnectionProtocol,
    event_publisher: IEventPublisher,
    security_policy: CodeSecurityPolicy,
    task_config: TaskManagerConfig,
    default_timeout_ms: float,
    max_output_bytes: int,
) -> None:
    ...
```

---

### 6.4.4 New `capabilities_operation_queue.py`

Create queue capability.

Requirements:

- Implement `IOperationQueueProtocol`.
- Own queue depth, pending futures, and operation state.
- Emit `ItemEnqueued`, `ItemDequeued`, `OperationRejected`.
- Raise `TooManyPendingOperationsError`.
- Raise `OperationWaitTimeoutError`.
- Support cancellation by request ID and task ID.
- Be safe under concurrent asyncio access.

Constructor target:

```python
def __init__(
    self,
    event_publisher: IEventPublisher,
    max_depth: int,
    wait_timeout_ms: float,
) -> None:
    ...
```

---

### 6.4.5 New `capabilities_event_bus_inmemory.py`

Create in-memory event bus.

Requirements:

- Implement `IEventBus`.
- Support async subscribers.
- Isolate subscriber exceptions.
- Log subscriber failures without stopping publish flow.

---

### 6.4.6 New `capabilities_metrics_collector.py`

Create metrics collector.

Requirements:

- Implement `IEventSubscriber`.
- Implement `IMetricsProvider`.
- Update counters from events.
- Track average latency for code and command operations.
- Return immutable `ServerMetrics`.

---

## 6.5 Agent File

### 6.5.1 `agent_server_orchestrator.py`

Rewrite.

Requirements:

- Implement new `IBlenderServerAggregate`.
- Depend only on contracts.
- Start queue worker in `start()`.
- Stop queue worker in `shutdown()`.
- Own operation routing.
- Serialize code and scene-mutating commands.
- Bypass non-scene commands.
- Reject operations when connection not connected.
- Cancel pending operations on disconnect/shutdown/permanent failure.
- Subscribe to connection failure events.
- Generate request ID when absent.
- Propagate tracking ID into results and logs.
- Return typed VOs.
- Expose metrics via `IMetricsProvider`.

Constructor target:

```python
def __init__(
    self,
    connection: IBlenderConnectionProtocol,
    code_executor: ICodeExecutionProtocol,
    command_adapter: IBlenderCommandProtocol,
    operation_queue: IOperationQueueProtocol,
    event_publisher: IEventPublisher,
    metrics_provider: IMetricsProvider,
    queue_wait_timeout_ms: float,
    execution_default_timeout_ms: float,
) -> None:
    ...
```

---

## 6.6 Root File

### 6.6.1 `root_server_container.py`

Rewrite.

Requirements:

- Accept `ServerConfig`.
- Use `load_server_config` if config not provided.
- Remove direct host/port-only factory as primary API.
- Build event bus.
- Build metrics collector.
- Subscribe metrics collector to event bus.
- Build connection, command adapter, code executor, queue, orchestrator.
- Subscribe orchestrator to event bus if needed.
- Provide async `start()` and `shutdown()`.
- Do not contain business logic.

Target API:

```python
class ServerContainer:
    def __init__(self, config: ServerConfig | None = None) -> None:
        ...

    async def start(self) -> IBlenderServerAggregate:
        ...

    async def shutdown(self) -> None:
        ...

    def get_aggregate(self) -> IBlenderServerAggregate:
        ...
```

Factory:

```python
def create_container(
    config_path: str | None = None,
    overrides: dict[str, Any] | None = None,
) -> ServerContainer:
    ...
```

---

## 6.7 Surface Diagnostics File

### 6.7.1 New `surface_server_diagnostics_controller.py`

Create server diagnostics controller.

Requirements:

- Depend only on aggregate contract.
- Format metrics as JSON-compatible dict.
- Include request ID.
- Include timestamp.

Target:

```python
class ServerDiagnosticsController:
    def __init__(self, aggregate: IBlenderServerAggregate) -> None:
        ...

    async def get_metrics_json(
        self,
        request_id: RequestId | None = None,
    ) -> dict[str, Any]:
        ...
```

CLI/MCP surface modules must consume this controller.

---

## 7. External Blender Addon Requirements

The server cannot fully satisfy D17 without addon support.

The addon must implement protocol version `2.0.0`.

### 7.1 Addon Handshake Requirements

On handshake:

```text
If no active Blender file exists:
    create timestamped temp .blend file
    save current session as active file
```

Return:

```json
{
  "session_id": "<uuid4>",
  "active_file_path": "<path>",
  "active_directory": "<directory>"
}
```

### 7.2 Addon Message Requirements

Addon must support:

```text
length-prefixed JSON frames
request_id propagation
protocol_version field
status field
error object
```

### 7.3 Addon Commands

Addon must support at least:

```text
ping
get_status
get_version
get_scene_info
get_object_info
get_screenshot
execute_code
ensure_workspace
```

---

## 8. Acceptance Criteria

All acceptance criteria must be automated as Gherkin tests.

### 8.1 Connection Acceptance Criteria

```gherkin
Feature: Server connection lifecycle

  Scenario: Connect successfully to local Blender
    Given Blender addon is running locally
    And protocol version is compatible
    When the client calls connect
    Then connection state is "connected"
    And ConnectionEstablished is emitted
    And ConnectionStatus includes last_heartbeat_at
    And ConnectionStatus includes active_directory

  Scenario: Reject remote connection without auth token
    Given host is "192.168.1.50"
    And auth token is missing
    When the client calls connect
    Then ConnectionConfigError is raised
    And error code is "connection_config_error"

  Scenario: Reject incompatible protocol version
    Given server protocol version is "2.0.0"
    And addon protocol version is "3.0.0"
    When the client calls connect
    Then VersionMismatchError is raised
    And error code is "version_mismatch"

  Scenario: Reject new operation while reconnecting
    Given connection state is "reconnecting"
    When the client calls execute_code
    Then BlenderConnectionFailure is raised
    And error details include state "reconnecting"

  Scenario: Cancel pending operations on disconnect
    Given three operations are pending
    When disconnect is called
    Then all pending operations receive ConnectionClosedError
    And connection state is "closed"
```

### 8.2 Queue Acceptance Criteria

```gherkin
Feature: Sequential operation processing

  Scenario: Process scene operations in FIFO order
    Given three scene-mutating commands are submitted concurrently
    When the queue worker processes them
    Then execution order matches submission order
    And no two scene operations run at the same time

  Scenario: Reject operation when queue is full
    Given queue max depth is 50
    And 50 operations are pending
    When one more operation is submitted
    Then TooManyPendingOperationsError is raised
    And error code is "too_many_pending_operations"

  Scenario: Reject operation that waits too long
    Given queue wait timeout is 10000 ms
    And an operation does not start within 10000 ms
    When the wait timeout expires
    Then OperationWaitTimeoutError is raised
    And error code is "operation_wait_timeout"

  Scenario: Bypass non-scene commands
    Given a long scene-mutating operation is running
    When get_scene_info is called
    Then get_scene_info does not wait behind the queue
    And get_scene_info returns a CommandResult
```

### 8.3 Security Acceptance Criteria

```gherkin
Feature: Code execution security

  Scenario: Block os.system
    Given code contains "import os"
    And code contains "os.system('ls')"
    When execute_code is called
    Then SecurityViolationError is raised
    And SecurityViolationDetected is emitted
    And no raw code is logged

  Scenario: Block dynamic getattr obfuscation
    Given code contains "getattr(os, 'system')"
    When execute_code is called
    Then SecurityViolationError is raised
    And error details include rule "blocked_function_call"

  Scenario: Allow file write inside allowed directory
    Given allowed directory is "/tmp/blender-arwaky/sessions"
    And code writes to "/tmp/blender-arwaky/sessions/output.txt"
    When execute_code is called
    Then validation succeeds

  Scenario: Block file write outside allowed directory
    Given allowed directory is "/tmp/blender-arwaky/sessions"
    And code writes to "/etc/passwd"
    When execute_code is called
    Then SecurityViolationError is raised
    And error details include rule "file_write_outside_allowed_directory"

  Scenario: Block dynamic file write path
    Given code uses open(path_variable, "w")
    When execute_code is called
    Then SecurityViolationError is raised
    And error details include rule "dynamic_file_write_path_not_allowed"
```

### 8.4 Background Task Acceptance Criteria

```gherkin
Feature: Background task lifecycle

  Scenario: Submit background task
    Given valid Python code
    When submit_async_task is called
    Then a task ID is returned
    And task state is "pending"
    And TaskCreated is emitted

  Scenario: Poll pending task
    Given a task is pending
    When poll_task_result is called
    Then TaskStatus state is "pending"
    And TaskStatus result is empty

  Scenario: Poll completed task
    Given a task completed successfully
    When poll_task_result is called
    Then TaskStatus state is "success"
    And TaskStatus result contains ExecutionResult

  Scenario: Cancel pending task
    Given a task is pending
    When cancel_async_task is called
    Then TaskStatus state is "cancelled"
    And TaskCancelled is emitted

  Scenario: Cancel running task best effort
    Given a task is running
    When cancel_async_task is called
    Then cancel_requested is true
    And local async execution is attempted to cancel
    And Blender may continue execution

  Scenario: Unknown task
    Given task ID does not exist
    When poll_task_result is called
    Then TaskNotFoundError is raised
```

### 8.5 Command Acceptance Criteria

```gherkin
Feature: Standard command execution

  Scenario: Unknown command
    Given command name is "unknown_command"
    When send_command is called
    Then ValidationError is raised
    And error code is "unknown_command"

  Scenario: Missing required parameter
    Given command "get_object_info" requires "name"
    And params do not include "name"
    When send_command is called
    Then ValidationError is raised

  Scenario: Command timeout
    Given command timeout is 5000 ms
    And Blender does not respond within 5000 ms
    When send_command is called
    Then CommandTimeoutError is raised

  Scenario: Command response truncation
    Given command response exceeds max_command_response_bytes
    When send_command is called
    Then CommandResult truncated is true
    And CommandResult data is truncated safely
```

### 8.6 Observability Acceptance Criteria

```gherkin
Feature: Observability

  Scenario: Emit events through event bus
    Given event bus is enabled
    When execute_code succeeds
    Then CodeExecuted is emitted
    And event includes request_id
    And event includes execution_time_ms

  Scenario: Expose metrics
    Given one code execution succeeded
    And one security violation occurred
    When get_metrics is called
    Then ServerMetrics code_execution_count is 1
    And ServerMetrics security_violation_count is 1
    And ServerMetrics includes last_updated_at

  Scenario: Do not log raw code
    Given execute_code is called with private code
    When logs are captured
    Then logs do not contain the private code
    And logs contain code_fingerprint
```

---

## 9. Test Plan

### 9.1 Required Test Files

Create or update:

```text
tests/server/unit/test_taxonomy_server_vo.py
tests/server/unit/test_taxonomy_server_errors.py
tests/server/unit/test_utility_server_validator.py
tests/server/unit/test_utility_server_schema.py
tests/server/unit/test_utility_server_config_loader.py
tests/server/unit/test_utility_server_message.py
tests/server/unit/test_capabilities_metrics_collector.py
tests/server/unit/test_capabilities_event_bus.py
tests/server/unit/test_capabilities_operation_queue.py

tests/server/integration/test_server_container_wiring.py
tests/server/integration/test_orchestrator_queue_serialization.py
tests/server/integration/test_orchestrator_task_lifecycle.py
tests/server/integration/test_event_bus_metrics_flow.py

tests/server/functional/test_connection_flows.py
tests/server/functional/test_code_execution_flows.py
tests/server/functional/test_command_flows.py
tests/server/functional/test_security_flows.py
tests/server/functional/test_background_task_flows.py
tests/server/functional/test_metrics_endpoint.py

tests/server/fakes/fake_blender_addon_server.py
tests/server/fakes/fake_event_subscriber.py
```

### 9.2 Fake Blender Addon

Create a fake TCP addon server for functional tests.

It must support:

```text
protocol v2 handshake
ping
get_scene_info
get_object_info
execute_code
ensure_workspace
configurable latency
configurable failures
configurable version mismatch
configurable auth failure
```

### 9.3 Coverage Requirements

Minimum coverage for changed paths:

```text
modules/server: 80%
modules/shared/src/server: 80%
```

Critical paths require explicit tests:

```text
queue serialization
queue cancellation
security validation
connection reconnect
task cancellation
metrics collection
error mapping
config loading
```

---

## 10. Traceability Matrix


| FRD ID        | Requirement           | Implementation                                                       | Tests                                                              |
| --------------- | ----------------------- | ---------------------------------------------------------------------- | -------------------------------------------------------------------- |
| FR-001        | Connection lifecycle  | `capabilities_blender_connection.py`, `agent_server_orchestrator.py` | `test_connection_flows.py`                                         |
| FR-001        | Reconnect retries     | `capabilities_blender_connection.py`                                 | `test_connection_flows.py`                                         |
| FR-001        | Heartbeat             | `capabilities_blender_connection.py`                                 | `test_connection_flows.py`                                         |
| FR-001        | Version handshake     | `capabilities_blender_connection.py`                                 | `test_connection_flows.py`                                         |
| FR-001        | Authentication        | `capabilities_blender_connection.py`, config loader                  | `test_connection_flows.py`, `test_utility_server_config_loader.py` |
| FR-002        | Custom code execution | `capabilities_code_execution_adapter.py`, orchestrator               | `test_code_execution_flows.py`                                     |
| FR-002        | Security validation   | `utility_server_validator.py`                                        | `test_security_flows.py`, `test_utility_server_validator.py`       |
| FR-002        | Allowed directories   | `utility_server_validator.py`, connection workspace metadata         | `test_security_flows.py`                                           |
| FR-002        | Background tasks      | orchestrator, code executor, queue                                   | `test_background_task_flows.py`                                    |
| FR-002        | Task cancellation     | orchestrator, code executor, queue                                   | `test_background_task_flows.py`                                    |
| FR-003        | Standard commands     | `capabilities_blender_command_adapter.py`                            | `test_command_flows.py`                                            |
| FR-003        | Command validation    | `utility_server_schema.py`                                           | `test_utility_server_schema.py`, `test_command_flows.py`           |
| FR-003        | Command timeout       | command adapter                                                      | `test_command_flows.py`                                            |
| Stability     | Sequential processing | orchestrator, operation queue                                        | `test_orchestrator_queue_serialization.py`                         |
| Stability     | Queue limits          | operation queue                                                      | `test_capabilities_operation_queue.py`                             |
| Observability | Events                | event bus, capabilities, orchestrator                                | `test_event_bus_metrics_flow.py`                                   |
| Observability | Metrics               | metrics collector, diagnostics controller                            | `test_metrics_endpoint.py`                                         |

---

## 11. Implementation Milestones

### Milestone M1 — Taxonomy and Contracts

Tasks:

1. Update `taxonomy_server_constant.py`.
2. Update `taxonomy_server_vo.py`.
3. Rename errors in `taxonomy_server_error.py`.
4. Add new events and `ServerEvent` union.
5. Update all contracts.
6. Add new contracts for event bus, metrics, operation queue.
7. Update shared `__init__.py` exports.

Exit criteria:

```text
All shared types compile.
No old error names remain.
Contracts match this plan.
```

---

### Milestone M2 — Utility Layer

Tasks:

1. Rewrite `utility_server_validator.py`.
2. Rewrite `utility_server_schema.py`.
3. Add `utility_server_config_loader.py`.
4. Add `utility_server_id.py`.
5. Update `utility_server_message.py` for protocol v2.
6. Add truncation helpers for JSON data.
7. Fix `snake_to_camel` export issue.

Exit criteria:

```text
Utility functions are stateless.
Unit tests pass.
Security validator enforces allowed directories.
Command catalog validation rejects unknown commands.
```

---

### Milestone M3 — Observability Capabilities

Tasks:

1. Create in-memory event bus.
2. Create metrics collector.
3. Add diagnostics controller.
4. Test event-to-metric flows.

Exit criteria:

```text
Events publish successfully.
Metrics update from events.
get_metrics returns ServerMetrics.
```

---

### Milestone M4 — Connection Capability

Tasks:

1. Rewrite `capabilities_blender_connection.py` with asyncio.
2. Remove `ConfigPort` dependency.
3. Implement handshake.
4. Implement version compatibility.
5. Implement auth policy.
6. Implement heartbeat.
7. Implement reconnect.
8. Emit events.

Exit criteria:

```text
Connection uses non-blocking async I/O.
Handshake always verifies version.
Remote without token fails.
Heartbeat does not falsely drop during active operation.
```

---

### Milestone M5 — Command and Code Capabilities

Tasks:

1. Rewrite command adapter.
2. Remove queue from command adapter.
3. Rewrite code execution adapter.
4. Remove duplicated AST validation.
5. Implement task lifecycle.
6. implement task cancellation support.
7. Implement output truncation.

Exit criteria:

```text
Command adapter returns CommandResult.
Code adapter returns ExecutionResult and TaskStatus.
No raw code logged.
Security violations emit audit events.
```

---

### Milestone M6 — Queue and Orchestrator

Tasks:

1. Create operation queue capability.
2. Rewrite orchestrator.
3. Implement queue worker.
4. Implement FIFO execution.
5. Implement bypass for non-scene commands.
6. Implement pending cancellation.
7. Implement reconnect rejection.
8. Implement metrics delegation.

Exit criteria:

```text
Scene operations are serialized.
Non-scene operations bypass.
Queue limits enforced.
Pending operations cancelled on disconnect.
```

---

### Milestone M7 — Root Wiring

Tasks:

1. Rewrite `root_server_container.py`.
2. Load `ServerConfig`.
3. Wire event bus, metrics, queue, capabilities, orchestrator.
4. Implement async start/shutdown.
5. Remove sync shutdown behavior.

Exit criteria:

```text
Container starts aggregate.
Container shuts down cleanly.
No async coroutine is left unawaited.
```

---

### Milestone M8 — Tests and FRD Addendum

Tasks:

1. Create fake Blender addon.
2. Write unit tests.
3. Write integration tests.
4. Write functional tests.
5. Convert QA checklist to Gherkin.
6. Update FRD with final decisions.
7. Add migration guide.

Exit criteria:

```text
All required tests pass.
Coverage thresholds met.
FRD matches implementation.
Breaking changes documented.
```

---

## 12. Definition of Done

The release is complete only when all of the following are true.

### 12.1 Functional

- [ ]  Connection handshake always verifies protocol version.
- [ ]  Remote connections require auth token.
- [ ]  Reconnect rejects new operations.
- [ ]  Pending operations cancel on disconnect.
- [ ]  Pending operations cancel after permanent connection failure.
- [ ]  Scene operations execute sequentially.
- [ ]  Non-scene commands bypass queue.
- [ ]  Queue full and wait timeout errors are correct.
- [ ]  Background tasks support pending, running, success, error, timeout, cancelled.
- [ ]  Task cancellation is exposed and tested.
- [ ]  Command catalog validates unknown commands and invalid parameters.
- [ ]  Command responses truncate with flag.
- [ ]  Code output truncates with flag.
- [ ]  Session workspace bootstrap provides active directory.
- [ ]  File writes outside allowed directories are blocked.
- [ ]  Dynamic file write paths are blocked.
- [ ]  Raw code is never logged.

### 12.2 Contract

- [ ]  Aggregate returns typed VOs only.
- [ ]  No public API returns raw dict as final response.
- [ ]  Error names match FRD-aligned names.
- [ ]  Tracking ID exists on requests, responses, logs, and events.
- [ ]  Contracts and implementations match exactly.

### 12.3 Observability

- [ ]  Event bus emits all required events.
- [ ]  Metrics collector updates from events.
- [ ]  `get_metrics` returns complete `ServerMetrics`.
- [ ]  Diagnostics controller produces JSON output.
- [ ]  Security violations emit audit events.

### 12.4 Architecture

- [ ]  No capability imports another capability.
- [ ]  Agent depends only on contracts.
- [ ]  Utility functions are stateless.
- [ ]  Duplicated validation logic removed.
- [ ]  Root contains no business logic.
- [ ]  No blocking async violations.
- [ ]  AES lint scan passes.

### 12.5 Quality

- [ ]  `uv run pytest` passes.
- [ ]  `uv run ruff check .` passes.
- [ ]  `uv run mypy modules/server modules/shared/src/server` passes.
- [ ]  Coverage >= 80% for changed server/shared-server files.
- [ ]  Gherkin acceptance tests exist for FR-001, FR-002, FR-003.
- [ ]  Fake addon functional tests pass.
- [ ]  Migration guide exists.
- [ ]  FRD addendum exists.

---

## 13. Migration Notes for Breaking Changes

### 13.1 Error Renames

```text
QueueFullError -> TooManyPendingOperationsError
QueueTimeoutError -> OperationWaitTimeoutError
ProtocolVersionMismatchError -> VersionMismatchError
```

### 13.2 Aggregate Changes

```text
poll_task_result now returns TaskStatus.
send_command now returns CommandResult.
cancel_async_task added.
get_metrics added.
start and shutdown added.
request_id optional parameter added to most methods.
```

### 13.3 Contract Changes

```text
IBlenderConnectionProtocol.connect requires ConnectionConfig.
IBlenderConnectionProtocol.is_connected returns bool.
IBlenderConnectionProtocol.send_command returns CommandResult.
IBlenderCommandProtocol no longer contains queue methods.
ICodeExecutionProtocol.poll_task_result returns TaskStatus.
```

### 13.4 Configuration Changes

```text
ServerConfig is the primary configuration object.
ConfigPort is no longer used by BlenderConnection.
Config file, environment variables, and programmatic config are supported.
```

---

## 14. Implementation Order for Developers

Developers must implement in this exact order:

```text
1. Taxonomy
2. Contracts
3. Utility
4. Event bus
5. Metrics collector
6. Operation queue
7. Connection capability
8. Command adapter
9. Code execution adapter
10. Orchestrator
11. Root container
12. Diagnostics controller
13. Fake addon
14. Unit tests
15. Integration tests
16. Functional tests
17. FRD addendum and migration guide
```

Do not implement capabilities before contracts are stable.

Do not implement orchestrator before queue and capabilities are contract-complete.

Do not mark release ready until the Definition of Done is fully satisfied.
