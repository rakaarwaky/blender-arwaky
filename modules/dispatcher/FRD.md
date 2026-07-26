# FRD — Action Dispatcher Feature

## Purpose

Manages action catalog, validates requests, routes to domain features, and normalizes results.

## Scope

- Action catalog
- Action schema
- Action metadata (timeout, idempotent, mutates_scene, background_allowed, destructive)
- Request validation
- Routing action to correct feature
- Background submission coordination
- Unified result envelope
- Tracking ID propagation

## Out of Scope

- Blender transport
- Queue
- Task lifecycle
- Security validation
- Domain business rules
- Logging/metrics storage

## Depends On

- `gateway`
- `object`
- `scene`
- `render`
- `asset`
- `job`
- `security`
- `diagnostics`

## Provides To

- `cli`
- `mcp`

## Functional Requirements

### FR-DSP-001: Register Action Catalog

Domain features register actions to dispatcher. Dispatcher stores action metadata.

### FR-DSP-002: Discover Actions

CLI and MCP request action list from dispatcher. Dispatcher returns the same catalog to both.

### FR-DSP-003: Validate Action Request

Dispatcher validates action name and parameters. Unknown action produces ValidationError. Invalid parameters produce ValidationError.

### FR-DSP-004: Dispatch Synchronous Action

Dispatcher forwards action to domain feature or gateway. Dispatcher returns standardized result.

### FR-DSP-005: Submit Background Action

If action supports background execution, dispatcher creates job. Dispatcher returns task ID. Dispatcher does not manage task lifecycle directly.

### FR-DSP-006: Normalize Operation Result

All action results returned in same envelope: success, data, error category, message, tracking_id, warnings, metadata.

## Error Categories

- `ValidationError` — unknown action or invalid parameters
- `NotFoundError` — action not found in catalog
- `ExecutionError` — action execution failed
- `CapacityError` — background capacity exceeded
- `UnsupportedError` — action does not support requested mode

## Events

- `dispatcher.routed` — action routed to feature
- `dispatcher.completed` — action completed
- `dispatcher.background_submitted` — background job created

## Configuration Keys

- `dispatcher.default_timeout` — default action timeout
- `dispatcher.max_timeout` — maximum allowed timeout
- `dispatcher.background_capacity` — max concurrent background tasks

## QA Checklist

- [ ] Action catalog registered by domain features
- [ ] Same catalog returned to CLI and MCP
- [ ] Unknown action rejected with ValidationError
- [ ] Invalid parameters rejected with ValidationError
- [ ] Synchronous action dispatched and result normalized
- [ ] Background action creates job and returns task_id
- [ ] Unified result envelope with tracking_id on all results
