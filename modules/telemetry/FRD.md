# FRD — Anonymous Product Telemetry Feature

## Purpose

Collects anonymous usage analytics on opt-in basis only.

## Scope

- Opt-in consent
- Anonymous event recording
- Session ID
- Environment metadata
- Event categorization
- Background transmission

## Out of Scope

- Operational logs (owner: `diagnostics`)
- Health check (owner: `diagnostics`)
- Metrics for debugging (owner: `diagnostics`)
- Error diagnostics (owner: `diagnostics`)
- Security audit (owner: `security` + `diagnostics`)

## Depends On

- `config`

## Provides To

- Product analytics backend

## Functional Requirements

### FR-TLM-001: Record Anonymous Usage Event

Record event without PII. Event includes timestamp, action type, and session ID.

### FR-TLM-002: Classify and Categorize Events

Categorize events by feature area and operation type. No raw payloads or user content.

### FR-TLM-003: Manage Analytics Sessions

Generate anonymous session ID. Persist session across restarts. Rotate session after timeout.

### FR-TLM-004: Enrich Events with Environment Metadata

Add OS, Python version, Blender version, app version. No identifying information.

## Hard Rules

- Telemetry must NOT be used for operational debugging
- Telemetry must NOT store PII
- Telemetry must NOT block main operations
- Telemetry is opt-in only

## Error Categories

- `ConfigurationError` - telemetry config invalid
- `ProviderError` - analytics backend unreachable (non-blocking)

## Events

- `telemetry.event` - anonymous event recorded
- `telemetry.session` - session created or rotated

## Configuration Keys

- `telemetry.enabled` - opt-in toggle
- `telemetry.backend_url` - analytics endpoint
- `telemetry.session_timeout` - session rotation interval
- `telemetry.transmission_interval` - background send interval

## QA Checklist

- [ ] Events recorded without PII
- [ ] Opt-in consent respected
- [ ] Session ID anonymous and rotatable
- [ ] Environment metadata only (no identifying info)
- [ ] Does not block main operations
- [ ] Not used for operational debugging
