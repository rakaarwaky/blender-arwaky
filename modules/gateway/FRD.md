# FRD — Blender Gateway Feature

## Purpose

Manages low-level communication between application and Blender: connection, transport, queue, and raw code execution.

## Scope

- Connection lifecycle to Blender
- Handshake
- Authentication transport
- Protocol version compatibility
- Heartbeat/liveness
- Reconnect
- Message framing
- Request/response correlation
- Payload size limit
- Scene operation scheduler/queue
- Raw command transport
- Raw Python code execution transport

## Out of Scope

- Action catalog
- Domain command schema
- Object/scene/render business rules
- Background task lifecycle
- Product analytics
- Operational metrics storage
- Settings loading
- Process launching

## Depends On

- `config`
- `security`
- `diagnostics` (events/metrics)

## Provides To

- `dispatcher`
- `object`
- `scene`
- `render`
- `asset`

## Functional Requirements

### FR-GWY-001: Establish Connection

Gateway connects application to Blender. Gateway performs handshake. Gateway verifies protocol version. Gateway performs authentication if needed.

### FR-GWY-002: Maintain Connection

Gateway sends heartbeat. Gateway detects stale connection. Gateway reconnects with retry policy. Gateway reports connection state.

### FR-GWY-003: Transport Request and Response

Gateway sends generic command to Blender. Gateway receives response. Gateway enforces transport timeout. Gateway enforces payload limit. Gateway includes tracking ID.

### FR-GWY-004: Serialize Scene-Mutating Operations

Gateway has queue for scene-mutating operations. Gateway processes scene operations one at a time. Read-only operations may bypass queue. Queue depth limit and wait timeout configured by config.

### FR-GWY-005: Execute Raw Python Code

Gateway sends Python code to Blender. Gateway uses security for code validation. Gateway enforces execution timeout. Gateway truncates output if too large. Gateway does not manage task lifecycle.

If code execution runs as background task, task lifecycle remains owned by `job`.

## Error Categories

- `ConnectionError` — connection failed or lost
- `TimeoutError` — transport or execution timeout
- `ProtocolVersionMismatchError` — protocol version incompatible
- `AuthenticationError` — transport auth failed
- `ChannelConflictError` — queue conflict
- `SecurityViolationError` — code validation failed (via security)

## Events

- `gateway.connected` — connection established
- `gateway.disconnected` — connection lost
- `gateway.reconnect` — reconnection attempted
- `gateway.queued` — operation enqueued
- `gateway.executed` — raw code execution completed

## Configuration Keys

- `gateway.host` — Blender host address
- `gateway.port` — Blender port
- `gateway.timeout` — transport timeout
- `gateway.payload_limit` — max payload size
- `gateway.queue_depth` — max scene queue depth
- `gateway.queue_wait_timeout` — max wait for queued operation
- `gateway.heartbeat_interval` — heartbeat frequency
- `gateway.reconnect_retry` — reconnect retry count

## QA Checklist

- [ ] Connection established with handshake and protocol check
- [ ] Heartbeat detects stale connections
- [ ] Reconnect with retry policy
- [ ] Request/response correlation with tracking ID
- [ ] Scene-mutating operations serialized via queue
- [ ] Read-only operations bypass queue
- [ ] Raw code validated by security before execution
- [ ] Execution timeout enforced
- [ ] Output truncated on size limit
