# FRD — telemetry (Telemetry Feature Module)

## System Overview

The telemetry module handles anonymous usage analytics — event recording, session tracking, and usage metrics. It provides the telemetry recording port and event types.

## Functional Requirements

### FR-001: Record Telemetry Event

- **Description**: Record anonymous usage event with structured metadata
- **Input**: TelemetryEvent (event_type, customer_uuid, session_id, timestamp, tool_name, ...)
- **Output**: None (fire-and-forget)
- **Business Rules**: Events are anonymous (no PII); batched for efficiency; opt-out supported
- **Edge Cases**: Network unavailable, invalid event data, duplicate events
- **Error Handling**: Silent failure (telemetry must never block operations)

### FR-002: Event Type Classification

- **Description**: Categorize events by type for analytics
- **Input**: Event type string
- **Output**: EventType enum (STARTUP, TOOL_EXECUTION, PROMPT_SENT, CONNECTION, ERROR)
- **Business Rules**: Each event must have exactly one type; types are exhaustive
- **Edge Cases**: Unknown event type, missing type
- **Error Handling**: Default to UNKNOWN type for unrecognized events

### FR-003: Session Tracking

- **Description**: Track user sessions across tool executions
- **Input**: Session ID (auto-generated UUID)
- **Output**: Session-scoped event grouping
- **Business Rules**: Session ID persists across MCP server lifetime; new session on restart
- **Edge Cases**: Session ID collision, session timeout
- **Error Handling**: Generate new session ID on collision

### FR-004: Version and Platform Metadata

- **Description**: Attach version and platform info to events
- **Input**: Version string, platform name, Blender version
- **Output**: Enriched telemetry events
- **Business Rules**: Version from pyproject.toml; platform from sys.platform; Blender version from bpy
- **Edge Cases**: Version not available, Blender not running
- **Error Handling**: Use "unknown" for missing metadata

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `record_event` | TelemetryEvent | None | Record usage event |
| `record_startup` | None | None | Record server startup |
| `record_tool_execution` | tool_name, success, duration_ms | None | Record tool call |
| `record_error` | error_message, context | None | Record error event |

## Integration Points

- **Internal**: shared (taxonomy VOs, telemetry constants)
- **External**: PostHog (analytics backend), Blender (version info)

## Non-functional Requirements (Detailed)

- Performance: Event recording < 10ms (non-blocking)
- Reliability: Best-effort delivery; failures silently ignored
- Privacy: No PII collected; customer UUID is anonymous

## Test Scenarios / QA Checklist

- [ ] Record event with valid data succeeds silently
- [ ] Record event with network failure does not raise exception
- [ ] Event types correctly classified
- [ ] Session ID persists across multiple events
- [ ] Version metadata correctly attached

## Assumptions & Constraints

- Telemetry is opt-in (can be disabled via config)
- No personally identifiable information collected
- Network failures must not block core operations

## Glossary

- **TelemetryEvent**: Domain entity representing an anonymous usage event
- **EventType**: Enum of supported event categories
- **CustomerUuid**: Anonymous user identifier

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
