# FRD — Action Dispatcher Feature

## Purpose

Single routing and catalog authority between consumers and domain capabilities. CLI and MCP never call domain features directly — they submit action requests to dispatcher, which resolves from catalog, validates params, routes execution to owning feature, coordinates background submission where supported, and returns every outcome in one unified result envelope.

## Scope

- Action catalog registration and storage
- Action schema definition and validation
- Action metadata (timeout, idempotency, mutation, background, destructive, read-only, long-running flags, risk level, owning feature, examples)
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

Blender transport/message framing, queue management/serialization, task lifecycle, security validation of code/paths, domain business rules, logging/metrics storage, consumer-specific presentation formatting, asset provider communication, authentication/connection management.

## Depends On

gateway (transport-backed action execution + queue), object/scene/render/asset (domain actions), job (background task creation + correlation), security policy (destructive confirmation, redaction), diagnostics (routing + completion events).

## Provides To

CLI, MCP layer, any consumer requiring unified action discovery, dispatch, or normalized results.

## Functional Requirements

### FR-DSP-001: Register Action Catalog

- **Description**: Accept action registrations from domain features, maintain consistent queryable catalog
- **Input**: Action registration (name, owning feature, description, param schema, result hints, metadata)
- **Output**: Registration result (accepted, catalog version, warnings)
- **Rules**: Dispatcher is sole catalog owner. Each registration: unique name, owning feature, description, param schema (required fields, types, ranges, allowed values), default timeout + timeout class, idempotency flag, scene mutation flag, background eligibility flag, destructive flag, read-only flag, long-running flag, risk level, ≥1 usage example. Schema integrity validated before acceptance. Duplicate name → rejected or replaced per policy with warning. Catalog deterministic ordering (by name). Immutable for consumers after registration phase. Hot re-registration configurable without interrupting in-flight dispatch. Catalog version exposed. No secrets/sensitive defaults. Degraded owning feature → marked in discovery.
- **Edge Cases**: Duplicate name, invalid schema, missing owning feature, registration after startup, conflicting metadata, empty catalog, oversized examples, unauthorized feature, version regression
- **Error Handling**: Registration error for conflict; validation error for malformed schema; warning for duplicate replacement + degraded feature

### FR-DSP-002: Discover Actions

- **Description**: Expose canonical catalog to consumers with optional filtering
- **Input**: Discovery request (name filter, category/capability filter, detail level)
- **Output**: Discovery result (action list with metadata, catalog version, count)
- **Rules**: Same canonical content to all consumers. Presentation is consumer responsibility. Read-only, idempotent. Each action: name, description, param schema, examples, timeout, flags, risk level, owning feature, degraded indicator. Filtering deterministic, case-consistent. Filter matching nothing → empty list, not error. Never exposes routing internals or secrets. Fast from in-memory catalog. Catalog version for consumer compatibility.
- **Edge Cases**: Empty catalog, filter mutching nothing, malformed filter, oversized metadata at full detail, discovery during hot re-registration, unsupported detail level, degraded feature
- **Error Handling**: Validation error for malformed filter; empty result for no match; degraded indicator surfaced

### FR-DSP-003: Validate Action Request

- **Description**: Validate incoming request against catalog schema before routing
- **Input**: Action request (name, payload, optional execution mode, timeout override, confirmation flag, tracking ID)
- **Output**: Validated request enriched with resolved metadata + tracking ID
- **Rules**: Name must exist in catalog → not found error. Payload must satisfy schema: required fields present, types correct, numeric ranges, text length limits, enumerated allowed sets, payload size limit. Invalid → validation error with field-level detail. Unknown extra params: rejected (strict) or ignored with warning (tolerant). Execution mode compatible with metadata → unsupported error. Destructive → requires confirmation flag. Timeout override within bounds. Tracking ID generated if absent. Never mutates request or catalog.
- **Edge Cases**: Unknown action, missing/wrong-type/out-of-range param, invalid enumerated, unknown extra, oversized payload, destructive without confirmation, timeout out of bounds, ambiguous casing, malformed tracking ID, degraded feature
- **Error Handling**: Not found error; validation error with field-level detail; unsupported error for mode mismatch; confirmation error for missing flag

### FR-DSP-004: Dispatch Synchronous Action

- **Description**: Route validated action to owning domain feature or gateway, return normalized result
- **Input**: Validated request (resolved metadata + tracking ID)
- **Output**: Unified result envelope (outcome data or categorized failure)
- **Rules**: Routing target = owning feature from catalog metadata. Dispatcher never interprets/transforms domain meaning beyond schema validation. Enforces action timeout from metadata or bounded override. Tracking ID propagates to feature, gateway, and envelope. Domain errors mapped to unified categories. Non-idempotent actions never retried automatically. Read-only actions may flag to bypass serialization (final queue decision by gateway). Destructive → carries confirmation state. Records duration + owning feature in metadata. Unavailable feature → execution error with degraded detail. Partial results normalized with warning list. Stateless across requests.
- **Edge Cases**: Feature unavailable, timeout during execution, domain error without category, partial result with warnings, connection loss mid-dispatch, duplicate tracking ID, dispatch during hot re-registration, oversized/non-serializable result, destructive confirmation revoked mid-dispatch
- **Error Handling**: Execution error for domain failure; timeout error; connection error mapped from gateway; unsupported error for incompatible mode; normalization fallback for uncategorized errors

### FR-DSP-005: Submit Background Action

- **Description**: Create job for long-running actions, return task reference in unified envelope
- **Input**: Validated request with background mode
- **Output**: Unified envelope (task reference, initial job state, submission metadata)
- **Rules**: Only for actions with background eligibility flag. Creates job via job feature, returns task ref. Dispatcher never manages task lifecycle after handoff. Capacity limit enforced from config; exhaustion → capacity error, no orphan job. Tracking ID → job correlation ID. Atomic submission: job created + acknowledged before success; failure before creation → execution error with no task ref. Duplicate with idempotency hint may return existing task ref. Result clearly indicates polling required. Payload size limits respected. Emits observability event.
- **Edge Cases**: Capacity exceeded, not background eligible, job creation failure, duplicate with idempotency hint, oversized payload, submission during shutdown, tracking ID collision, job feature unavailable
- **Error Handling**: Capacity error; unsupported error for non-eligible action; execution error for job creation failure; warning for duplicate resolved to existing task

### FR-DSP-006: Normalize Operation Result

- **Description**: Normalize every dispatch/submission outcome into one unified result envelope
- **Input**: Raw outcome from sync dispatch or background submission
- **Output**: Unified result envelope
- **Rules**: Envelope: success indicator, data payload, error category (when failed), human-readable message, tracking ID, warning list, metadata summary (action name, feature, execution mode, duration, applied timeout, task ref for background, truncation indicator). Data serializable and bounded by max size; oversized → truncated with indicator. Non-serializable → safe text representation. Error detail: category, message, field-level detail. Mixed outcomes (success + warnings) preserve warning list. No secrets/raw code/sensitive paths. Construction failure → safe error envelope. Identical shape for CLI and MCP.
- **Edge Cases**: Non-serializable data, oversized payload, missing tracking ID, domain result without error category, success with warnings, partial failure, envelope construction failure, sensitive value inside data, empty data with success, incomplete background metadata
- **Error Handling**: Normalization fallback to safe error envelope; truncation indicator; redaction before emission; warnings preserved, not converted to failure

## Error Categories

- validation error — invalid params, malformed request, schema violation
- not found error — action not in catalog
- execution error — action execution failed within feature/gateway
- capacity error — background capacity exceeded
- unsupported error — execution mode not supported
- timeout error — action timeout exceeded
- confirmation error — destructive without required confirmation
- registration error — conflict or invalid schema at registration

## Events

- action routed (validated + tracking ID)
- action completed (finished with outcome + duration)
- action rejected (validation failure with error category)
- background job submitted (task ref + action name)
- catalog registered (action count + version)
- action failed (mapped error + feature reference)

Payloads: category, action name, tracking ID, feature, execution mode, error category (when failed), duration. Never: full params by default, secrets, raw code, oversized result.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| default_action_timeout | When metadata doesn't declare one | Conservative |
| maximum_allowed_timeout | Upper bound for overrides | Bounded multiple of default |
| background_capacity | Max concurrent background tasks | Conservative |
| unknown_parameter_policy | strict/tolerant | strict |
| destructive_confirmation_enforced | Require confirmation flag | Enabled |
| maximum_result_data_size | Envelope data payload limit | Conservative |
| catalog_hot_re_registration | Allow re-registration after startup | Disabled |
| tracking_id_generation | Generate when absent | Enabled |

## QA Checklist

- [ ] Catalog registered with complete metadata; duplicate → handled per policy
- [ ] Invalid schema rejected at registration
- [ ] Deterministic ordering + catalog version
- [ ] Same catalog to CLI and MCP
- [ ] Filter matching nothing → empty list
- [ ] Degraded feature surfaced in discovery
- [ ] Unknown action → not found error
- [ ] Invalid params → validation error with field-level detail
- [ ] Unknown extra params: strict=reject, tolerant=ignore
- [ ] Destructive without confirmation → confirmation error
- [ ] Timeout override out of bounds → reject
- [ ] Tracking ID generated if absent, propagated onward
- [ ] Sync dispatch to correct owning feature
- [ ] Result normalized into unified envelope
- [ ] Action timeout enforced
- [ ] Non-idempotent not retried automatically
- [ ] Domain errors mapped to unified categories
- [ ] Partial results with warning list preserved
- [ ] Background → job created + task ref returned
- [ ] Non-eligible → unsupported error
- [ ] Capacity exhausted → capacity error, no orphan job
- [ ] Duplicate with idempotency hint → existing task ref
- [ ] Envelope: success, data, error, message, tracking ID, warnings, metadata
- [ ] Oversized data → truncation with indicator
- [ ] Non-serializable → safe representation
- [ ] Secrets/raw code/sensitive paths never leaked
- [ ] Envelope construction failure → safe error envelope
- [ ] All events emitted
