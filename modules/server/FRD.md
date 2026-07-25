# FRD — Server Feature Module

## System Overview

The server module manages TCP socket communication between the MCP server and the Blender addon. It handles connection lifecycle, code execution, and Blender-side operations. This module is the bridge between the AI agent layer (MCP) and the Blender runtime. It follows a Hexagonal Architecture (Ports and Adapters) pattern to decouple business logic from transport implementation.

## Functional Requirements

### FR-SRV-001: Manage Blender Socket Connection

- **Description:** Establish and maintain TCP socket connection to Blender addon
- **Input:** ConnectionConfig (host, port, transport_type, timeout)
- **Output:** Active socket connection
- **Business Rules:**
  - Auto-reconnect on failure with max 3 retry attempts using exponential backoff (1s, 2s, 4s)
  - Connection establishment timeout: 30 seconds
  - Heartbeat/ping every 10 seconds to detect stale connections
- **Edge Cases:** Blender not running, connection refused, timeout, network error, Blender crashes mid-session
- **Error Handling:** `BlenderConnectionFailure` with retry logic; after 3 failed attempts, raise `BlenderConnectionExhausted`

### FR-SRV-002: Execute Blender Code

- **Description:** Send Python code to Blender for execution via TCP socket
- **Input:** Prompt (Python code string)
- **Output:** `ExecutionResult {status: "success"|"error", data: Any, error_message: str, execution_time_ms: int}`
- **Business Rules:**
  - Code validated against blocked patterns before sending (see Security section)
  - Execution timeout: 30 seconds; raise `ExecutionTimeoutError` if exceeded
  - For long-running operations (>30s), support async task submission with `task_id` polling
  - Blocked patterns include: `os.system`, `subprocess`, `shutil.rmtree`, `eval()`, `exec()`, `__import__`, `open()` with write mode outside Blender project directory
- **Edge Cases:** Code execution timeout, syntax error, Blender exception, Blender crash during execution, blocked pattern detected
- **Error Handling:** `ExecutionError` with error details from Blender; `SecurityViolationError` for blocked patterns

### FR-SRV-003: Send Blender Commands

- **Description:** Dispatch named commands to Blender addon
- **Input:** ActionName (enum), command arguments (dict)
- **Output:** Command result dictionary `{status: "success"|"error", data: dict, error_message: str}`
- **Business Rules:**
  - Commands routed through TCP socket; response parsed as JSON
  - Command response timeout: 5 seconds; raise `CommandTimeoutError` if exceeded
  - Commands are idempotent where possible (e.g., `get_scene_info`)
- **Edge Cases:** Unknown command, invalid arguments, Blender not responding, malformed JSON response
- **Error Handling:** `ProviderError` with command-specific error message; `CommandTimeoutError` for unresponsive commands

### FR-SRV-004: Connection Factory

- **Description:** Create new Blender connection instances based on configuration
- **Input:** ConnectionConfig (transport_type: "socket"|"stdio", host, port, timeout, retry_policy)
- **Output:** BlenderConnectionPort instance
- **Business Rules:**
  - Supports multiple connection strategies (TCP socket, stdio pipe)
  - Factory validates configuration before instantiation
  - Returns appropriate adapter implementation based on transport_type
- **Edge Cases:** Invalid configuration, unsupported transport type, missing required fields
- **Error Handling:** `ConnectionConfigError` for factory failures with descriptive validation message

### FR-SRV-005: Socket Adapter Surface

- **Description:** Surface layer for Blender socket operations; maps MCP tool calls to Blender operations
- **Input:** MCP tool calls (structured tool input schema)
- **Output:** Delegated to Blender via connection; returns MCP-compatible response
- **Business Rules:**
  - Thin wrapper responsible for mapping MCP tool inputs to respective Blender commands or code execution payloads
  - Strictly no business logic in the surface layer
  - Translates MCP response format to/from Blender response format
- **Edge Cases:** Connection lost during operation, MCP tool schema mismatch
- **Error Handling:** Delegates to connection error handling; wraps unexpected errors as `AdapterSurfaceError`

## API Contract


| Operation               | Input            | Output                | Description                                  |
| ------------------------- | ------------------ | ----------------------- | ---------------------------------------------- |
| `connect`               | ConnectionConfig | BlenderConnectionPort | Establish connection (socket/stdio)          |
| `disconnect`            | —               | —                    | Close connection gracefully                  |
| `send_command`          | ActionName, dict | dict                  | Send command to Blender (5s timeout)         |
| `execute_blender_code`  | Prompt (str)     | ExecutionResult       | Execute Python code in Blender (30s timeout) |
| `submit_async_task`     | Prompt (str)     | task_id (str)         | Submit long-running code for async execution |
| `poll_task_result`      | task_id (str)    | ExecutionResult       | Poll async task status and result            |
| `get_connection_status` | —               | ConnectionStatus      | Return current connection state              |

## Integration Points

- **Internal:**
  - `shared` module: taxonomy (ActionName enum, error types), contracts (Port interfaces)
  - `config` module: server settings (host, port, timeout, retry policy, blocked patterns list)
  - `mcp_layer`: MCP tool definitions and response formatting
- **External:**
  - Blender addon (TCP socket listener on configurable port)
  - Blender Python API (`bpy`) — accessed exclusively through the addon

## Non-functional Requirements

- **Performance:** Command response within 5 seconds; code execution within 30 seconds
- **Reliability:** Auto-reconnect on connection loss (3 attempts, exponential backoff); graceful degradation on Blender crash
- **Security:** Code execution validates against blocked patterns list (configurable); no arbitrary file system access outside Blender project directory
- **Observability:** Log all connection state changes, command metadata, execution duration, and error stack traces; code payload logging masked/hashed for sensitive content
- **Concurrency:** All requests serialized (queued) due to Blender's single-threaded `bpy` constraint; queue depth limit of 50 pending operations

## Test Scenarios / QA Checklist

- Connect to running Blender instance succeeds
- Connect to non-running Blender returns `BlenderConnectionFailure`
- Connect with invalid config returns `ConnectionConfigError`
- Connection loss triggers auto-reconnect (3 attempts, exponential backoff)
- After 3 failed reconnects, raises `BlenderConnectionExhausted`
- Execute valid Python code returns `ExecutionResult` with status "success"
- Execute code with syntax error returns `ExecutionResult` with status "error"
- Execute code exceeding 30s timeout returns `ExecutionTimeoutError`
- Execute code with blocked pattern (e.g., `os.system`) returns `SecurityViolationError`
- Send valid command to Blender returns response within 5 seconds
- Send command exceeding 5s timeout returns `CommandTimeoutError`
- Send unknown command returns `ProviderError`
- Factory creates socket connection with valid config
- Factory creates stdio connection with valid config
- Factory rejects unsupported transport type
- Concurrent requests are serialized (queued) correctly
- Queue depth limit (50) enforced; excess requests rejected
- Heartbeat detects stale connection and triggers reconnect
- MCP tool call maps correctly to Blender command via adapter surface

## Assumptions & Constraints

- Blender addon must be running and listening on TCP socket (or stdio pipe)
- Single connection per server instance
- Code execution has 30-second timeout (configurable via ConnectionConfig)
- Command execution has 5-second timeout
- Because Blender's Python API (`bpy`) is not thread-safe and runs on the main thread, all concurrent requests from the MCP server are serialized (queued) to prevent race conditions and Blender crashes
- Blocked patterns list is maintained in config and updated as needed
- Blender addon protocol version must match server protocol version

## Glossary

- **MCP (Model Context Protocol):** Standard protocol for AI agent tool integration; defines how the AI agent invokes tools and receives results
- **BlenderConnectionPort:** Contract (interface) for Blender TCP/stdio communication; part of Hexagonal Architecture
- **CodeExecutionPort:** Contract (interface) for Python code execution in Blender
- **SocketAdapter:** Surface layer (adapter) for Blender socket operations; maps MCP calls to Blender operations
- **ConnectionConfig:** Configuration object containing transport_type, host, port, timeout, and retry_policy
- **ExecutionResult:** Standardized response object for code execution containing status, data, error_message, and execution_time_ms
- **Blocked Patterns:** Configurable list of forbidden Python patterns/modules to prevent security violations
