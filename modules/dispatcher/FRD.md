# FRD — Action Dispatcher Feature

## Purpose

Manages the action catalog, validates action requests, routes actions to domain features, and normalizes results for **blender-arwaky**.

This feature is the single routing and catalog authority between consumers and domain capabilities. Command-line tooling and the MCP layer never call domain features directly. They submit action requests to the dispatcher, which resolves the action from the catalog, validates parameters, routes execution to the owning feature, coordinates background submission where supported, and returns every outcome in one unified result envelope.

The dispatcher owns routing, validation, and normalization. It does not own domain behavior, transport, queueing, task lifecycle, or security policy decisions.

## Scope

- Action catalog registration and storage
- Action schema definition and validation
- Action metadata:
  - timeout class and default timeout
  - idempotency flag
  - scene mutation flag
  - background eligibility flag
  - destructive flag
  - read-only flag
  - long-running flag
  - risk level
  - owning feature reference
  - usage examples
- Request validation against catalog schema
- Routing action to correct domain feature or gateway
- Background submission coordination with job feature
- Unified result envelope for all outcomes
- Tracking ID generation and propagation
- Capability discovery for consumers
- Destructive action confirmation enforcement
- Timeout override bounds enforcement
- Domain error mapping into unified categories

## Out of Scope

- Blender transport and message framing
- Queue management and serialization
- Task lifecycle management
- Security validation of code or paths
- Domain business rules
- Logging and metrics storage
- Consumer-specific presentation formatting
- Asset provider communication
- Authentication and connection management

## Depends On

- gateway feature for transport-backed action execution and queue behavior
- object feature for object domain actions
- scene feature for scene domain actions
- render feature for render domain actions
- asset feature for asset domain actions
- job feature for background task creation and correlation
- security policy feature for destructive confirmation guidance and redaction
- diagnostics feature for routing and completion events

## Provides To

- cli feature
- mcp layer
- any consumer requiring unified action discovery, dispatch, or normalized results

## Functional Requirements

### FR-DSP-001: Register Action Catalog

Domain features register actions to dispatcher. Dispatcher stores action metadata.

- **Description**: Accept action registrations from domain features and maintain a consistent, queryable action catalog
- **Input**: Action registration concept containing action name, owning feature reference, description, parameter schema, result hints, and action metadata
- **Output**: Registration result concept containing accepted indicator, catalog version, and registration warnings
- **Business Rules**:
  - Dispatcher is the only owner of the action catalog
  - Domain features register actions; they do not expose action invocation directly to consumers
  - Each registration must include:
    - action name concept, unique within catalog
    - owning feature reference
    - human-readable description
    - parameter schema with required fields, types, ranges, and allowed values
    - default timeout and timeout class
    - idempotency flag
    - scene mutation flag
    - background eligibility flag
    - destructive flag
    - read-only flag
    - long-running flag
    - risk level
    - at least one usage example
  - Registration must validate schema integrity before acceptance
  - Duplicate action name registration must be rejected or replaced according to configured policy, with warning emitted
  - Catalog must expose deterministic ordering, sorted by action name
  - Catalog content must be immutable for consumers once registration phase completes
  - Hot re-registration may be supported when enabled by configuration, without interrupting in-flight dispatch
  - Catalog should expose catalog version for consumer diagnostics
  - Registration must not include secrets or sensitive defaults
  - Actions whose owning feature is unavailable may remain registered but should be marked degraded in discovery results
- **Edge Cases**: Duplicate action name, invalid parameter schema, missing owning feature reference, registration after startup phase, conflicting metadata between versions, empty catalog, oversized example content, action registered by unauthorized feature, catalog version regression
- **Error Handling**: Registration error for invalid or conflicting registration; validation error for malformed schema; warning emitted for duplicate replacement and degraded owning feature

### FR-DSP-002: Discover Actions

CLI and MCP request action list from dispatcher. Dispatcher returns the same catalog to both.

- **Description**: Expose the action catalog to consumers in one canonical shape, with optional filtering
- **Input**: Discovery request concept containing optional name filter, optional category or capability filter, optional metadata detail level
- **Output**: Discovery result concept containing action list with metadata, catalog version, and result count
- **Business Rules**:
  - Dispatcher returns the same canonical catalog content to all consumers
  - Presentation formatting is the responsibility of the consuming feature, not dispatcher
  - Discovery is read-only and idempotent
  - Discovery result should include for each action:
    - action name
    - description
    - parameter schema
    - usage examples
    - default timeout and timeout class
    - idempotency, mutation, background, destructive, read-only, and long-running flags
    - risk level
    - owning feature reference
    - degraded indicator when owning feature is unavailable
  - Filtering must be deterministic and case-consistent
  - Filter matching nothing returns empty list, not error
  - Discovery must never expose internal routing implementation or secrets
  - Discovery should complete quickly from in-memory catalog without touching domain features
  - Catalog version should be included for consumer compatibility checks
- **Edge Cases**: Empty catalog, filter matching nothing, malformed filter, oversized metadata at full detail level, discovery during hot re-registration, consumer requesting unsupported detail level, degraded owning feature
- **Error Handling**: Validation error for malformed discovery filter; empty result for unmatched filter; degraded actions surfaced with indicator rather than hidden

### FR-DSP-003: Validate Action Request

Dispatcher validates action name and parameters. Unknown action produces not found error. Invalid parameters produce validation error.

- **Description**: Validate an incoming action request against the catalog before routing
- **Input**: Action request concept containing action name, parameter payload, optional execution mode, optional timeout override, optional confirmation flag, optional tracking identifier
- **Output**: Validated request concept enriched with resolved action metadata and tracking identifier
- **Business Rules**:
  - Action name must exist in catalog; unknown action produces not found error
  - Parameter payload must satisfy the registered parameter schema:
    - required fields present
    - field types correct
    - numeric values within declared ranges
    - textual values within declared length limits
    - enumerated values within declared allowed set
    - payload size within configured limit
  - Invalid parameters produce validation error with field-level detail
  - Unknown extra parameters are rejected in strict mode and ignored with warning in tolerant mode
  - Execution mode must be compatible with action metadata:
    - background mode requires background eligibility
    - incompatible mode produces unsupported error
  - Destructive actions require explicit confirmation flag when destructive confirmation is enforced
  - Timeout override must fall within configured minimum and maximum bounds
  - Tracking identifier must be generated when not supplied and propagated onward
  - Validation must not mutate request payload or catalog state
  - Validation outcome must be deterministic for identical request and catalog state
- **Edge Cases**: Unknown action, missing required parameter, wrong parameter type, out-of-range value, invalid enumerated value, unknown extra parameter, oversized payload, destructive action without confirmation, timeout override out of bounds, ambiguous action name casing, malformed tracking identifier, request against degraded owning feature
- **Error Handling**: Not found error for unknown action; validation error for invalid parameters with field-level detail; unsupported error for incompatible execution mode; confirmation error for destructive action lacking required confirmation

### FR-DSP-004: Dispatch Synchronous Action

Dispatcher forwards action to domain feature or gateway. Dispatcher returns standardized result.

- **Description**: Route a validated action to its owning domain feature or gateway and return a normalized synchronous result
- **Input**: Validated request concept with resolved action metadata and tracking identifier
- **Output**: Unified result envelope containing outcome data or categorized failure
- **Business Rules**:
  - Routing target is resolved from owning feature reference in catalog metadata
  - Dispatcher must not interpret or transform domain meaning of parameters beyond schema validation
  - Dispatch must enforce action timeout from metadata or bounded override
  - Tracking identifier must propagate to owning feature, gateway transport, and result envelope
  - Domain errors must be mapped into unified error categories before returning
  - Non-idempotent actions must not be retried automatically by dispatcher
  - Read-only actions may be flagged to bypass scene-mutating serialization, with final queue decision owned by gateway
  - Destructive action dispatch must carry confirmation state to owning feature
  - Dispatch should record duration and owning feature in result metadata
  - Owning feature unavailable at dispatch time produces execution error with degraded feature detail
  - Partial results from domain features must be normalized with warning list rather than discarded
  - Dispatch must remain stateless across requests except catalog and tracking context
- **Edge Cases**: Owning feature unavailable, timeout during execution, domain error without category, partial result with warnings, connection loss mid-dispatch, duplicate tracking identifier, dispatch during hot re-registration, oversized result data, non-serializable result data, destructive action confirmation revoked mid-dispatch
- **Error Handling**: Execution error for domain failure; timeout error when action timeout exceeded; connection error mapped from gateway failures; unsupported error when resolved action cannot execute in requested mode; normalization fallback for uncategorized domain errors

### FR-DSP-005: Submit Background Action

If action supports background execution, dispatcher creates job. Dispatcher returns task ID. Dispatcher does not manage task lifecycle directly.

- **Description**: Coordinate background submission for long-running actions by creating a job and returning its reference inside the unified envelope
- **Input**: Validated request concept with background execution mode and action metadata
- **Output**: Unified result envelope containing task reference, initial job state, and submission metadata
- **Business Rules**:
  - Background submission is permitted only for actions with background eligibility flag
  - Dispatcher creates job through job feature and returns task reference to caller
  - Dispatcher must not manage task lifecycle after successful handoff
  - Background capacity limit must be enforced from configuration
  - Capacity exhaustion produces capacity error without creating orphan job records
  - Tracking identifier must propagate to job correlation identifier
  - Submission must be atomic:
    - job created and acknowledged before success envelope returned
    - failure before job creation returns execution error with no task reference
  - Duplicate submission with same idempotency hint may return existing task reference when supported by job feature
  - Submission result must clearly indicate that polling is required for final outcome
  - Payload handoff to job feature must respect configured size limits
  - Background submission should emit observability event with action name and task reference
- **Edge Cases**: Background capacity exceeded, action not background eligible, job creation failure, duplicate submission with idempotency hint, oversized payload for background handoff, submission during shutdown, tracking identifier collision, job feature unavailable
- **Error Handling**: Capacity error when background capacity exceeded; unsupported error when action lacks background eligibility; execution error when job creation fails before handoff; warning emitted for duplicate submission resolved to existing task

### FR-DSP-006: Normalize Operation Result

All action results returned in same envelope: success, data, error category, message, tracking ID, warnings, metadata.

- **Description**: Normalize every dispatch and submission outcome into one unified result envelope consumed by CLI and MCP layer
- **Input**: Raw outcome concept from synchronous dispatch or background submission
- **Output**: Unified result envelope concept
- **Business Rules**:
  - Unified envelope must contain:
    - success indicator
    - data payload when present
    - error category when failed
    - human-readable message
    - tracking identifier
    - warning list
    - metadata summary
  - Metadata summary should include:
    - action name
    - owning feature reference
    - execution mode
    - duration
    - applied timeout
    - task reference for background submission
    - truncation indicator when data bounded
  - Data payload must be serializable and bounded by configured maximum size
  - Oversized data must be truncated with truncation indicator rather than failing the envelope
  - Non-serializable data values must be converted to safe textual representation
  - Error detail must include category, message, and field-level detail when available
  - Mixed outcomes with success plus warnings must preserve warning list
  - Envelope must never include secrets, raw code, or sensitive paths
  - Envelope construction failure must fall back to safe error envelope, never propagate raw domain structures
  - Envelope shape must be identical for CLI and MCP consumers
- **Edge Cases**: Non-serializable data, oversized data payload, missing tracking identifier, domain result without error category, success with warnings, partial failure, envelope construction failure, sensitive value inside data payload, empty data with success, background submission metadata incomplete
- **Error Handling**: Normalization fallback to safe error envelope when construction fails; truncation indicator for bounded data; redaction applied before envelope emission; warning preserved rather than converted to failure

## Error Categories

- validation error — invalid parameters, malformed request, or schema violation
- not found error — action not found in catalog
- execution error — action execution failed within owning feature or gateway
- capacity error — background capacity exceeded
- unsupported error — action does not support requested execution mode
- timeout error — action timeout or bounded override exceeded
- confirmation error — destructive action submitted without required confirmation
- registration error — action registration rejected due to conflict or invalid schema

## Events

- action routed event — validated action routed to owning feature with tracking identifier
- action completed event — synchronous action finished with categorized outcome and duration
- action rejected event — request rejected during validation with error category
- background job submitted event — background job created with task reference and action name
- catalog registered event — action catalog registration phase completed with action count and catalog version
- action failed event — dispatch failed with mapped error category and owning feature reference

Event payloads should include:

- event category
- action name
- tracking identifier
- owning feature reference
- execution mode
- error category when failed
- duration metadata

Event payloads must avoid:

- full parameter payloads by default
- secrets and sensitive values
- raw code content
- oversized result data

## Configuration Keys


| Configuration Concept             | Description                                                    | Typical Default               |
| ----------------------------------- | ---------------------------------------------------------------- | ------------------------------- |
| Default action timeout            | Timeout applied when action metadata does not declare one      | Conservative action limit     |
| Maximum allowed timeout           | Upper bound for timeout overrides                              | Bounded multiple of default   |
| Background capacity               | Maximum concurrent background tasks accepted                   | Conservative concurrent limit |
| Unknown parameter policy          | Strict rejection or tolerant ignore for undeclared parameters  | Strict                        |
| Destructive confirmation enforced | Whether destructive actions require explicit confirmation flag | Enabled                       |
| Maximum result data size          | Upper bound for envelope data payload before truncation        | Conservative payload limit    |
| Catalog hot re-registration       | Whether catalog may be re-registered after startup phase       | Disabled                      |
| Tracking identifier generation    | Whether dispatcher generates tracking identifier when absent   | Enabled                       |

## QA Checklist

- [ ]  Action catalog registered by domain features with complete metadata
- [ ]  Duplicate action registration rejected or replaced according to policy
- [ ]  Invalid parameter schema rejected at registration
- [ ]  Catalog exposes deterministic ordering and catalog version
- [ ]  Same catalog returned to CLI and MCP in canonical shape
- [ ]  Discovery filtering by name and capability works deterministically
- [ ]  Discovery filter matching nothing returns empty list
- [ ]  Degraded owning feature surfaced in discovery results
- [ ]  Unknown action rejected with not found error
- [ ]  Invalid parameters rejected with validation error and field-level detail
- [ ]  Unknown extra parameters handled according to strict or tolerant policy
- [ ]  Destructive action without confirmation rejected with confirmation error
- [ ]  Timeout override outside bounds rejected
- [ ]  Tracking identifier generated when absent and propagated onward
- [ ]  Synchronous action dispatched to correct owning feature
- [ ]  Synchronous action result normalized into unified envelope
- [ ]  Action timeout enforced during dispatch
- [ ]  Non-idempotent action not retried automatically
- [ ]  Domain errors mapped into unified error categories
- [ ]  Partial result preserved with warning list
- [ ]  Background action creates job and returns task reference
- [ ]  Background submission rejected for non-eligible action with unsupported error
- [ ]  Background capacity exhaustion produces capacity error without orphan job
- [ ]  Duplicate background submission with idempotency hint resolves to existing task
- [ ]  Background submission envelope indicates polling requirement
- [ ]  Unified result envelope includes success, data, error category, message, tracking ID, warnings, and metadata
- [ ]  Oversized data truncated with truncation indicator
- [ ]  Non-serializable data converted to safe representation
- [ ]  Envelope never leaks secrets, raw code, or sensitive paths
- [ ]  Envelope construction failure falls back to safe error envelope
- [ ]  Routing, completion, rejection, and background submission events emitted
