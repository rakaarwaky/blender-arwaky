# FRD — Action Dispatcher Feature

## System Overview
The Dispatcher is the single routing and catalog authority between consumers (CLI/MCP) and domain capabilities. It resolves actions from the catalog, validates parameters, routes execution to owning features, coordinates background submission, and returns every outcome in a unified result envelope.

## Functional Requirements

### FR-001: Register and Discover Action Catalog
- **Description**: Accept action registrations from domain features and expose the canonical catalog to consumers.
- **Input**: Action registration (name, schema, metadata), Discovery request (filters).
- **Output**: Registration result, Discovery result (action list with metadata).
- **Business Rules**: Dispatcher is sole catalog owner. Schema integrity validated before acceptance. Duplicate names handled per policy. Catalog deterministic ordering. Degraded features marked in discovery.
- **Edge Cases**: Duplicate name; invalid schema; empty catalog; discovery during hot re-registration.
- **Error Handling**: `registration_error` for conflict; `validation_error` for malformed schema.

### FR-002: Validate and Dispatch Synchronous Action
- **Description**: Validate incoming request against catalog schema and route to owning domain feature.
- **Input**: Action request (name, payload, execution mode, tracking ID).
- **Output**: Unified result envelope (outcome data or categorized failure).
- **Business Rules**: Payload must satisfy schema. Destructive actions require confirmation flag. Enforces action timeout. Domain errors mapped to unified categories. Non-idempotent actions never retried automatically.
- **Edge Cases**: Unknown action; missing/wrong-type param; destructive without confirmation; timeout during execution.
- **Error Handling**: `not_found` for unknown action; `validation_error` with field-level detail; `confirmation_error` for missing flag; `timeout_error`.

### FR-003: Submit Background Action and Normalize Results
- **Description**: Create job for long-running actions and normalize every outcome into one unified envelope.
- **Input**: Validated request with background mode.
- **Output**: Unified envelope (task reference, initial job state, submission metadata).
- **Business Rules**: Only for actions with background eligibility flag. Creates job via `job` feature. Capacity limit enforced. Oversized data truncated with indicator.
- **Edge Cases**: Capacity exceeded; not background eligible; job creation failure; non-serializable data.
- **Error Handling**: `capacity_error`; `unsupported` for non-eligible action; `execution_error` for job creation failure.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `list_commands` | `domain`, `format` | `UnifiedEnvelope` | Discover available actions and schemas |
| `execute_command` | `action`, `args` | `UnifiedEnvelope` | Universal action executor |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `gateway`, `object`, `scene`, `render`, `asset`, `job`, `security`, `diagnostics`.

## Non-functional Requirements (Detailed)

- **Performance**: Catalog discovery is fast and in-memory. Validation occurs before routing to prevent wasted compute.
- **Security**: Destructive action confirmation enforced. Secrets/raw code never leaked in envelopes.
- **Scalability**: Background capacity limits prevent system exhaustion. Hot re-registration supported without interrupting in-flight dispatch.

## Test Scenarios / QA Checklist

- [ ] Verify invalid schema is rejected at registration.
- [ ] Verify unknown action returns `not_found` error.
- [ ] Verify destructive action without confirmation flag returns `confirmation_error`.
- [ ] Verify background submission returns task reference and respects capacity limits.
- [ ] Verify oversized result data is truncated with an indicator in the envelope.

## Assumptions & Constraints

- CLI and MCP never call domain features directly; they must use the Dispatcher.
- The Dispatcher never interprets or transforms domain meaning beyond schema validation.

## Glossary

- **Action Catalog**: The centralized registry of all available canonical actions, their schemas, and metadata.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.
- **Background Eligibility**: Metadata flag indicating an action can be safely offloaded to the `job` feature.

## Reference

- PRD: `./PRD.md`
- Depends On: `gateway`, `object`, `scene`, `render`, `asset`, `job`, `security`, `diagnostics`
