# FRD — Blender Gateway Feature

## System Overview
The Gateway is the single transport authority between application features and the Blender runtime. It owns connection lifecycle, handshake, protocol compatibility, liveness detection, message framing, scene operation scheduling, and raw code transport. Higher-level features never open sockets or talk to Blender directly.

## Functional Requirements

### FR-001: Establish and Maintain Connection
- **Description**: Open transport channel to Blender, negotiate protocol, and maintain health via heartbeats.
- **Input**: Connection request (transport type, endpoint, timeout).
- **Output**: Connection state (established, negotiated protocol, capability summary).
- **Business Rules**: Supported transports: local socket, stdin/stdout pipe. Handshake exchanges protocol version. Heartbeat at configured interval. Reconnect with retry + backoff. State machine: disconnected → connecting → connected → reconnecting → failed → closed.
- **Edge Cases**: Blender not running; endpoint refused; version mismatch; stale socket; missed heartbeat during long execution.
- **Error Handling**: `connection_error`; `protocol_version_mismatch`; `authentication_error`.

### FR-002: Transport Request and Serialize Operations
- **Description**: Move command messages to Blender, correlate responses, and serialize scene-mutating ops.
- **Input**: Command message (operation class, payload, tracking ID).
- **Output**: Response message (tracking ID, status, payload).
- **Business Rules**: Every request/response correlated by tracking ID. Scene-mutating ops pass through scheduler queue (FIFO). Read-only ops may bypass. Payload size enforced.
- **Edge Cases**: Malformed frame; oversized payload; missing tracking ID; queue full; disconnect while ops pending.
- **Error Handling**: `timeout_error`; `transport_parse_error`; `payload_limit_error`; `channel_conflict`.

### FR-003: Execute Raw Python Code
- **Description**: Transport raw code to Blender with security validation and bounded output handling.
- **Input**: Raw code execution request (code text, timeout, tracking ID).
- **Output**: Execution result (status, structured output, error detail, truncation indicator).
- **Business Rules**: Raw code validated by `security` policy before transport. Execution timeout enforced. Output structured + serializable. Raw code text not logged by default.
- **Edge Cases**: Syntax error; runtime failure; Blender crash; oversized output; security violation.
- **Error Handling**: `security_violation` (delegated); `execution_error`; `connection_error`.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `execute_blender_code` | `code` | `UnifiedEnvelope` | Run Python in Blender via Gateway |

## Integration Points

- **3rd Party**: Blender Process (via socket/pipe bridge addon).
- **Internal**: `config` (endpoint/timeout settings), `security` (code validation), `diagnostics` (event delivery).

## Non-functional Requirements (Detailed)

- **Performance**: Heartbeat interval configurable. Queue wait timeout prevents indefinite blocking.
- **Security**: Auth material transported only when enabled, never logged. Raw code validated by `security` before execution.
- **Scalability**: Scene-mutating operations serialized to respect Blender's main-thread constraints. Queue depth limit enforced.

## Test Scenarios / QA Checklist

- [ ] Verify connection state machine transitions correctly (disconnected → connecting → connected).
- [ ] Verify incompatible protocol versions are rejected during handshake.
- [ ] Verify scene-mutating ops are serialized via FIFO queue.
- [ ] Verify queue depth limit triggers `channel_conflict` error.
- [ ] Verify raw code execution truncates output safely on size limit.

## Assumptions & Constraints

- Gateway never performs its own code validation; it delegates to `security`.
- Gateway never creates or tracks background task records; it only performs transport and returns task handoff refs.

## Glossary

- **Bridge Addon**: The Blender-side Python script that accepts socket/pipe connections and executes commands.
- **Scheduler Queue**: FIFO queue used to serialize scene-mutating operations to prevent Blender race conditions.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: `config`, `security`, `diagnostics`
