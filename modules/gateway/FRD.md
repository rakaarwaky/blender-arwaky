# FRD — Blender Gateway Feature

## Purpose

Manages low-level communication between the application and Blender for **blender-arwaky**: connection lifecycle, transport, queueing, and raw code execution.

This feature is the single transport authority between application features and the Blender runtime. It owns connection establishment, handshake, authentication transport, protocol compatibility, liveness detection, reconnection, message framing, request and response correlation, payload limits, scene operation scheduling, and raw command and raw code transport.

Higher-level features never open sockets, frame messages, or talk to Blender directly. They delegate all Blender communication to the gateway and receive structured, correlated, policy-enforced results.

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

- Action catalog
- Domain command schema
- Object, scene, and render business rules
- Background task lifecycle
- Product analytics
- Operational metrics storage
- Settings loading
- Process launching
- Code validation policy, owned by security policy feature
- Asset download or provider communication
- Result artifact storage

## Depends On

- config feature for endpoint, timeout, payload, queue, heartbeat, and retry settings
- security policy feature for code validation and credential redaction
- diagnostics feature for event and metric delivery

## Provides To

- dispatcher feature
- object feature
- scene feature
- render feature
- asset feature
- any feature requiring Blender command transport or raw code execution

## Functional Requirements

### FR-GWY-001: Establish Connection

Gateway connects application to Blender. Gateway performs handshake. Gateway verifies protocol version. Gateway performs authentication if needed.

- **Description**: Establish a transport channel to the Blender runtime, negotiate protocol compatibility, and authenticate when required
- **Input**: Connection request concept derived from configuration, including transport type, endpoint reference, timeout, protocol version, and authentication material when enabled
- **Output**: Connection state concept containing established indicator, negotiated protocol version, transport type, endpoint summary, and capability summary
- **Business Rules**:
  - Gateway is the only feature allowed to open a transport channel to Blender
  - Supported transport strategies include local socket channel and standard input/output pipe channel
  - Connection establishment must complete within configured timeout
  - Handshake must exchange protocol version information before any operation is accepted
  - Connection must be rejected when protocol versions are incompatible
  - Authentication material must be transported only when authentication is enabled
  - Authentication material must never be logged or echoed in diagnostics
  - Local endpoint should be default; remote endpoint requires explicit configuration
  - Only one active connection per application instance is supported
  - Connection establishment must be idempotent when already connected
  - Connection state must transition through deterministic states:
    - disconnected
    - connecting
    - connected
    - reconnecting
    - failed
    - closed
  - Capability summary from handshake should expose supported operation classes when provided by Blender side
  - Connection result must include redacted endpoint summary safe for diagnostics
- **Edge Cases**: Blender not running, endpoint refused, establishment timeout, authentication failure, protocol version mismatch, remote endpoint without authentication enabled, stale socket from previous session, transport type unsupported, invalid endpoint configuration, Blender bridge not enabled
- **Error Handling**: Connection error for failed or refused establishment; authentication error when transport authentication fails; protocol version mismatch error when versions are incompatible; configuration validation error when endpoint settings are invalid

### FR-GWY-002: Maintain Connection

Gateway sends heartbeat. Gateway detects stale connection. Gateway reconnects with retry policy. Gateway reports connection state.

- **Description**: Keep the connection healthy through liveness detection, controlled reconnection, and accurate state reporting
- **Input**: None during steady state; liveness signals from heartbeat exchange
- **Output**: Continuously updated connection state concept including last liveness timestamp, reconnect attempt count, and last failure reason
- **Business Rules**:
  - Gateway sends heartbeat at configured interval
  - Connection is considered stale only after configured number of consecutive missed heartbeats
  - Heartbeat handling should remain independent from Blender main-thread execution where supported
  - Missed heartbeat during active long-running execution must not immediately trigger reconnect unless transport is closed or execution timeout is also exceeded
  - Reconnection follows configured retry count with increasing backoff and jitter
  - After retry policy is exhausted, connection transitions to failed state and pending operations fail deterministically
  - Reconnect attempts must emit observability events
  - Connection state must be queryable by other features at any time
  - Graceful disconnect must be idempotent
  - On connection loss, in-flight operations must be failed with connection error rather than silently dropped
  - On connection loss, queued operations must be failed or preserved according to configured policy
  - State transition events must include redacted reason metadata
- **Edge Cases**: Blender crash mid-session, network interruption, heartbeat blocked by long-running execution, stale connection after system sleep, disconnect during reconnect, repeated reconnect cycles, liveness recovered during backoff, heartbeat response delayed but transport alive, connection closed by Blender side
- **Error Handling**: Connection error when liveness is lost; failed state after retry exhaustion; reconnect attempt warnings through observability events; deterministic failure propagation to in-flight and queued operations

### FR-GWY-003: Transport Request and Response

Gateway sends generic command to Blender. Gateway receives response. Gateway enforces transport timeout. Gateway enforces payload limit. Gateway includes tracking ID.

- **Description**: Move generic command messages to Blender and correlated responses back to callers with framing, limits, and timeouts enforced
- **Input**: Command message concept containing operation class, payload, optional timeout override, and tracking identifier
- **Output**: Response message concept containing tracking identifier, status, payload, and transport metadata
- **Business Rules**:
  - Every request must carry a unique tracking identifier
  - Every response must be correlated to its request through tracking identifier
  - Uncorrelated or orphan responses must be discarded safely and logged as transport warning
  - Messages must use deterministic framing, such as length-prefixed or delimiter-separated structured content
  - Message encoding must be UTF-8 structured text
  - Transport timeout must be enforced per request, with optional per-request override within configured bounds
  - Outgoing payload size must be enforced against configured limit
  - Incoming payload size must be enforced against configured limit
  - Oversized payloads must be rejected with clear transport error rather than partial delivery
  - Malformed responses must produce transport parse error, not undefined behavior
  - Request sent during disconnected or reconnecting state must fail fast with connection error unless queue policy applies
  - Non-idempotent operations must not be retried automatically by transport layer
  - Transport layer must not interpret domain meaning of payloads
  - Transport metadata should include duration and payload size summary for observability
- **Edge Cases**: Malformed response frame, partial frame delivery, oversized request payload, oversized response payload, missing tracking identifier, duplicate response, response arriving after timeout, connection lost mid-request, slow response near timeout boundary, interleaved responses from concurrent requests
- **Error Handling**: Timeout error when transport timeout exceeded; connection error when channel unavailable; transport parse error for malformed response; payload limit error for oversized request or response; correlation warning for orphan responses

### FR-GWY-004: Serialize Scene-Mutating Operations

Gateway has queue for scene-mutating operations. Gateway processes scene operations one at a time. Read-only operations may bypass queue. Queue depth limit and wait timeout configured by config.

- **Description**: Serialize operations that mutate Blender scene state to respect Blender main-thread constraints, while allowing safe read-only operations to bypass the queue
- **Input**: Operation request concept with mutation classification, payload, and optional priority hint
- **Output**: Execution result concept for queued operation, including queue wait duration metadata
- **Business Rules**:
  - Operations classified as scene-mutating must pass through the scheduler queue
  - Queued operations must be processed one at a time in deterministic order
  - Default ordering is first-in-first-out
  - Read-only operations may bypass the queue when they do not require Blender main-thread mutation
  - Control-plane operations such as connection status and liveness checks must not be blocked by the queue
  - Queue depth limit must be enforced from configuration
  - Queue wait timeout must be enforced from configuration
  - When queue depth limit is reached, new mutating operations must be rejected with channel conflict error
  - When queue wait timeout is exceeded, waiting operation must be rejected with timeout error
  - On connection loss, pending queued operations must be failed deterministically with connection error
  - On graceful disconnect, pending queued operations must be failed or drained according to configured policy
  - Queue state should be observable, including current depth and busy indicator
  - Long-running queued operation must not silently block the queue beyond its configured execution timeout
  - Mutation classification is provided by calling feature; gateway enforces but does not infer it
- **Edge Cases**: Queue full, wait timeout exceeded, disconnect while operations pending, long-running operation blocking subsequent operations, enqueue after disconnect, concurrent producers, priority hint conflict, operation reclassified during wait, queue drain during shutdown
- **Error Handling**: Channel conflict error when queue depth limit reached; timeout error when queue wait timeout exceeded; connection error for queued operations failed by connection loss; deterministic rejection rather than silent drop in all cases

### FR-GWY-005: Execute Raw Python Code

Gateway sends Python code to Blender. Gateway uses security for code validation. Gateway enforces execution timeout. Gateway truncates output if too large. Gateway does not manage task lifecycle.

If code execution runs as background task, task lifecycle remains owned by job feature.

- **Description**: Transport raw code to Blender for execution with security validation, execution timeout, and bounded output handling
- **Input**: Raw code execution concept containing code text, optional execution timeout override, and tracking identifier
- **Output**: Execution result concept containing status, structured output data, error detail when failed, execution duration, and truncation indicator
- **Business Rules**:
  - Raw code must be validated by security policy feature before transport
  - Gateway must never perform its own code validation policy decisions
  - Execution timeout must be enforced, defaulting to configured value with bounded override
  - Execution result output must be structured and serializable
  - Non-serializable output values must be converted to safe textual representation or rejected
  - Output exceeding configured size limit must be truncated with truncation indicator set
  - Error detail should include failure category, message, and location hint when provided by Blender side
  - Raw code text must not be logged by default; redacted or hashed reference only
  - Gateway must not create, track, or expire background task records
  - When execution is submitted as background task, gateway only performs transport and returns task handoff reference; lifecycle remains owned by job feature
  - Execution transport should reuse scene-mutating serialization when code mutates scene state
  - Execution duration must be reported for observability
  - Security validation disabled override must still emit audit warning through security policy feature
- **Edge Cases**: Syntax error in code, runtime failure inside Blender, execution timeout exceeded, Blender crash during execution, oversized output, non-serializable output, security violation detected, validation disabled override, code rejected by size limit, connection lost during execution, background task handoff requested
- **Error Handling**: Security violation error when validation fails, raised through security policy feature; timeout error when execution timeout exceeded; execution error for runtime failure inside Blender; connection error when channel lost during execution; truncation indicator rather than error for oversized but successful output

## Error Categories

- connection error — connection failed, refused, or lost
- timeout error — transport timeout, execution timeout, or queue wait timeout exceeded
- protocol version mismatch error — protocol version incompatible between application and Blender bridge
- authentication error — transport authentication failed
- channel conflict error — queue conflict, queue depth limit reached, or serialization contention
- security violation error — code validation failed, delegated through security policy feature
- transport parse error — malformed frame or unparseable response content
- payload limit error — request or response exceeded configured payload size

## Events

- connection established event — handshake completed and connection is active
- connection lost event — connection dropped or detected stale
- reconnection attempt event — reconnect cycle started with attempt count and backoff metadata
- connection failed event — retry policy exhausted and connection entered failed state
- operation enqueued event — scene-mutating operation accepted into scheduler queue
- operation rejected event — queued operation rejected due to depth limit, wait timeout, or connection loss
- raw code execution completed event — raw code transport finished with status, duration, and truncation metadata

Event payloads should include:

- event category
- connection state before and after transition
- tracking identifier when applicable
- queue depth when applicable
- duration metadata
- redacted reason summary

Event payloads must avoid:

- raw code text
- authentication material
- full request or response payloads
- sensitive filesystem references

## Configuration Keys


| Configuration Concept       | Description                                                  | Typical Default                   |
| ----------------------------- | -------------------------------------------------------------- | ----------------------------------- |
| Blender host address        | Endpoint host for socket transport                           | Local endpoint                    |
| Blender port                | Endpoint port for socket transport                           | Configured bridge port            |
| Transport timeout           | Default timeout for request and response transport           | Conservative transport limit      |
| Payload limit               | Maximum request and response payload size                    | Conservative payload limit        |
| Queue depth                 | Maximum scene-mutating operations waiting in scheduler queue | Fifty pending operations          |
| Queue wait timeout          | Maximum time a queued operation may wait before rejection    | Conservative wait limit           |
| Heartbeat interval          | Frequency of liveness heartbeat exchange                     | Ten seconds                       |
| Heartbeat failure threshold | Consecutive missed heartbeats before stale detection         | Three missed heartbeats           |
| Reconnect retry count       | Maximum reconnection attempts before failed state            | Three attempts                    |
| Reconnect backoff policy    | Increasing delay with jitter between reconnect attempts      | One, two, four second progression |
| Authentication enabled      | Whether transport authentication material is required        | Enabled for non-local endpoint    |
| Protocol version            | Protocol version advertised during handshake                 | Current supported version         |
| Execution timeout           | Default timeout for raw code execution                       | Thirty seconds                    |
| Output size limit           | Maximum execution output size before truncation              | Conservative output limit         |

## QA Checklist

- [ ]  Connection established with handshake and protocol check
- [ ]  Connection rejected when protocol versions are incompatible
- [ ]  Authentication material transported only when authentication enabled
- [ ]  Authentication material never appears in logs or diagnostics
- [ ]  Connection establishment respects configured timeout
- [ ]  Connection state transitions follow deterministic state machine
- [ ]  Repeat connection request while connected is idempotent
- [ ]  Heartbeat sent at configured interval
- [ ]  Heartbeat detects stale connections after configured threshold
- [ ]  Heartbeat does not falsely trigger reconnect during long-running execution
- [ ]  Reconnect with retry policy and increasing backoff
- [ ]  Retry exhaustion transitions connection to failed state
- [ ]  Pending operations fail deterministically on connection loss
- [ ]  Graceful disconnect is idempotent
- [ ]  Request and response correlation with tracking ID
- [ ]  Orphan response discarded with transport warning
- [ ]  Transport timeout enforced per request
- [ ]  Oversized request payload rejected with payload limit error
- [ ]  Oversized response payload rejected with payload limit error
- [ ]  Malformed response produces transport parse error
- [ ]  Scene-mutating operations serialized via queue
- [ ]  Queued operations processed one at a time in deterministic order
- [ ]  Read-only operations bypass queue
- [ ]  Control-plane operations not blocked by queue
- [ ]  Queue depth limit enforced with channel conflict error
- [ ]  Queue wait timeout enforced with timeout error
- [ ]  Queued operations failed deterministically on disconnect
- [ ]  Queue depth and busy state observable
- [ ]  Raw code validated by security before execution
- [ ]  Gateway does not perform its own code validation policy
- [ ]  Execution timeout enforced
- [ ]  Execution error detail includes category, message, and location hint
- [ ]  Output truncated on size limit with truncation indicator
- [ ]  Non-serializable output handled safely
- [ ]  Raw code text not logged by default
- [ ]  Background task handoff returns task reference without gateway-owned lifecycle
- [ ]  Transport events emitted for connection, queue, and execution lifecycle
