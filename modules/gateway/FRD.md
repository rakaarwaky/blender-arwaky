# FRD — Blender Gateway Feature

## Purpose

Single transport authority between application features and Blender runtime. Owns connection lifecycle, handshake, auth transport, protocol compatibility, liveness detection, reconnection, message framing, request/response correlation, payload limits, scene operation scheduling, raw command and raw code transport. Higher-level features never open sockets or talk to Blender directly.

## Scope

- Connection lifecycle to Blender
- Handshake and capability exchange
- Authentication transport
- Protocol version compatibility
- Heartbeat and liveness detection
- Reconnect with retry policy
- Message framing and encoding
- Request and response correlation
- Payload size limit enforcement
- Scene operation scheduler and queue
- Raw command transport
- Raw code execution transport
- Connection state reporting
- Transport-level error categorization
- Transport observability events

## Out of Scope

Action catalog, domain command schema, object/scene/render business rules, background task lifecycle, analytics, metrics storage, settings loading, process launching, code validation policy (security), asset download/provider comms, result artifact storage.

## Depends On

config (endpoint, timeout, payload, queue, heartbeat, retry settings), security policy (code validation, credential redaction), diagnostics (event + metric delivery).

## Provides To

dispatcher, object, scene, render, asset — any feature requiring Blender command transport or raw code execution.

## Functional Requirements

### FR-GWY-001: Establish Connection

- **Description**: Open transport channel to Blender, negotiate protocol, authenticate when required
- **Input**: Connection request (transport type, endpoint, timeout, protocol version, auth material if enabled)
- **Output**: Connection state (established, negotiated protocol, transport type, endpoint summary, capability summary)
- **Rules**: Gateway is sole feature allowed to open transport to Blender. Supported transports: local socket, stdin/stdout pipe. Establishment must complete within timeout. Handshake exchanges protocol version before any operation. Incompatible → rejected. Auth material transported only when auth enabled; never logged/echoed. Local endpoint default; remote requires config. One active connection per instance. Idempotent when already connected. State machine: disconnected → connecting → connected → reconnecting → failed → closed. Capability summary from handshake exposed when provided. Result includes redacted endpoint summary safe for diagnostics.
- **Edge Cases**: Blender not running, endpoint refused, timeout, auth failure, version mismatch, remote without auth, stale socket from previous session, unsupported transport, invalid endpoint config, bridge not enabled
- **Error Handling**: Connection error; auth error; protocol version mismatch error; config validation error

### FR-GWY-002: Maintain Connection

- **Description**: Keep connection healthy via liveness detection, controlled reconnection, accurate state reporting
- **Input**: None (steady state); liveness signals from heartbeat
- **Output**: Updated connection state (last liveness timestamp, reconnect count, last failure reason)
- **Rules**: Heartbeat at configured interval. Stale after configured consecutive missed heartbeats. Missed heartbeat during long-running execution must not immediately trigger reconnect unless transport closed or execution timeout exceeded. Reconnect: retry count with increasing backoff + jitter. Exhaustion → failed state, pending ops fail deterministically. Reconnect attempts emit events. State queryable at any time. Graceful disconnect idempotent. On connection loss: in-flight ops failed with connection error (not silently dropped); queued ops failed or preserved per policy. State transition events include redacted reason.
- **Edge Cases**: Blender crash, network interruption, heartbeat blocked by long execution, stale after sleep, disconnect during reconnect, repeated cycles, liveness recovered during backoff, delayed heartbeat response but transport alive, closed by Blender side
- **Error Handling**: Connection error on liveness loss; failed state after retry exhaustion; reconnect warnings via events; deterministic failure to in-flight + queued ops

### FR-GWY-003: Transport Request and Response

- **Description**: Move generic command messages to Blender and correlated responses back with framing, limits, timeouts enforced
- **Input**: Command message (operation class, payload, optional timeout override, tracking ID)
- **Output**: Response message (tracking ID, status, payload, transport metadata)
- **Rules**: Every request carries unique tracking ID. Every response correlated by tracking ID. Uncorrelated/orphan responses discarded safely + logged as transport warning. Deterministic framing (length-prefixed or delimiter). UTF-8 structured text encoding. Per-request timeout with optional override within bounds. Incoming/outgoing payload size enforced against configured limit. Oversized → clear transport error (not partial). Malformed → transport parse error. Sent during disconnected/reconnecting → fail fast with connection error (unless queue policy). Non-idempotent never retried by transport. Transport never interprets domain meaning. Metadata includes duration + payload size.
- **Edge Cases**: Malformed/partial frame, oversized request/response, missing tracking ID, duplicate response, response after timeout, connection lost mid-request, slow response near boundary, interleaved concurrent responses
- **Error Handling**: Timeout error; connection error; transport parse error; payload limit error; correlation warning for orphan responses

### FR-GWY-004: Serialize Scene-Mutating Operations

- **Description**: Serialize scene-mutating ops via queue to respect Blender main-thread constraints; read-only ops may bypass
- **Input**: Operation request (mutation classification, payload, optional priority hint)
- **Output**: Execution result (including queue wait duration)
- **Rules**: Scene-mutating ops pass through scheduler queue. Processed one at a time in deterministic order (default FIFO). Read-only ops may bypass the queue. Control-plane ops (status, liveness) never blocked by queue. Queue depth limit from config. Queue wait timeout from config. Depth limit reached → channel conflict error. Wait timeout exceeded → timeout error. Connection loss → pending queued ops fail deterministically. Graceful disconnect → fail or drain per policy. Queue state observable (depth + busy indicator). Long-running queued op must not silently block beyond configured execution timeout. Mutation classification provided by caller; gateway enforces, doesn't infer.
- **Edge Cases**: Queue full, wait timeout, disconnect while ops pending, long-running op blocking subsequent ops, enqueue after disconnect, concurrent producers, priority conflict, reclassification during wait, drain during shutdown
- **Error Handling**: Channel conflict error; timeout error; connection error; deterministic rejection (never silent drop)

### FR-GWY-005: Execute Raw Python Code

- **Description**: Transport raw code to Blender with security validation, execution timeout, bounded output handling
- **Input**: Raw code execution request (code text, optional timeout override, tracking ID)
- **Output**: Execution result (status, structured output, error detail, execution duration, truncation indicator)
- **Rules**: Raw code validated by security policy before transport — gateway never performs own validation. Execution timeout enforced (default + bounded override). Output structured + serializable; non-serializable → safe text representation or reject. Exceeding output size limit → truncation with indicator. Error detail: category, message, location hint (when provided by Blender). Raw code text not logged by default (redacted/hashed ref only). Gateway never creates/tracks/expires background task records — when submitted as background, only performs transport + returns task handoff ref. May reuse scene-mutating serialization when code mutates scene state. Duration reported. Security validation disabled override → audit warning.
- **Edge Cases**: Syntax error, runtime failure, timeout, Blender crash during execution, oversized/non-serializable output, security violation detected, validation disabled override, code rejected by size limit, connection lost, background task handoff
- **Error Handling**: Security violation error (delegated); timeout error; execution error (runtime failure); connection error; truncation indicator for oversized but successful output

## Error Categories

- connection error — failed/refused/lost
- timeout error — transport/execution/queue wait exceeded
- protocol version mismatch — incompatible versions
- authentication error — transport auth failed
- channel conflict — queue depth limit/serialization contention
- security violation — code validation failed (delegated)
- transport parse error — malformed frame/unparseable response
- payload limit error — oversized request/response

## Events

- connection established (handshake complete)
- connection lost (dropped/stale)
- reconnection attempt (count + backoff)
- connection failed (retry exhausted)
- operation enqueued (accepted into scheduler queue)
- operation rejected (depth limit, wait timeout, or connection loss)
- raw code execution completed (status, duration, truncation)

Payloads: category, connection state before/after, tracking ID, queue depth, duration, redacted reason. Never: raw code, auth material, full payloads, sensitive filesystem refs.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| blender_host | Endpoint host | Local |
| blender_port | Endpoint port | Configured bridge port |
| transport_timeout | Default request/response timeout | Conservative |
| payload_limit | Max request/response payload size | Conservative |
| queue_depth | Max scene-mutating ops in queue | 50 |
| queue_wait_timeout | Max queue wait before rejection | Conservative |
| heartbeat_interval | Liveness check frequency | 10s |
| heartbeat_failure_threshold | Missed heartbeats before stale | 3 |
| reconnect_retry_count | Max reconnection attempts | 3 |
| reconnect_backoff_policy | Delay progression | 1s, 2s, 4s + jitter |
| authentication_enabled | Require auth material | Enabled for non-local |
| protocol_version | Advertised version | Current supported |
| execution_timeout | Default raw code timeout | 30s |
| output_size_limit | Max execution output | Conservative |

## QA Checklist

- [ ] Connection established with handshake + protocol check
- [ ] Incompatible protocol → rejected
- [ ] Auth material only when auth enabled; never in logs/diagnostics
- [ ] Timeout respected; idempotent when already connected
- [ ] State machine: disconnected→connecting→connected→reconnecting→failed→closed
- [ ] Heartbeat at interval; stale after threshold
- [ ] Missed heartbeat during long execution doesn't falsely trigger reconnect
- [ ] Reconnect with retry + backoff; exhaustion → failed state
- [ ] Pending ops fail deterministically on connection loss
- [ ] Graceful disconnect idempotent
- [ ] Request/response correlation with tracking ID
- [ ] Orphan response → transport warning
- [ ] Transport timeout per request; oversized → payload limit error
- [ ] Malformed → transport parse error
- [ ] Scene-mutating ops serialized via queue; FIFO
- [ ] Read-only + control-plane ops bypass queue
- [ ] Queue depth limit → channel conflict error
- [ ] Queue wait timeout → timeout error
- [ ] Queued ops fail deterministically on disconnect
- [ ] Queue state observable
- [ ] Raw code validated by security; gateway never validates itself
- [ ] Execution timeout enforced; output truncated on size limit
- [ ] Non-serializable output handled safely
- [ ] Raw code text not logged by default
- [ ] Background task handoff → task ref, no gateway-owned lifecycle
- [ ] All transport events emitted
