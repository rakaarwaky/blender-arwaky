# FRD — Shared Foundation Layer

## System Overview
The Shared Foundation module provides the core taxonomy (VOs, entities, errors, events, constants), contract definitions (protocols, aggregates), and stateless utility functions used by all other features. It contains no business logic, I/O operations, or feature-specific implementations.

## Functional Requirements

### FR-001: Define Core Taxonomy and Value Objects
- **Description**: Define immutable Value Objects and domain entities for consistent data representation.
- **Input**: Domain data (timestamps, paths, names, IDs).
- **Output**: Immutable, hashable VOs (`Timestamp`, `WorkspacePath`, `TrackingID`, `BlenderObjectRef`).
- **Business Rules**: VOs strictly immutable. `WorkspacePath` derived from Config. `TrackingID` is UUIDv4.
- **Edge Cases**: Invalid ISO8601 strings; malformed UUIDs; relative paths passed as WorkspacePath.
- **Error Handling**: `validation_error` for malformed VO construction.

### FR-002: Define Unified Error Categories and Events
- **Description**: Map all domain failures to canonical categories and define standard domain events.
- **Input**: Domain failure context, lifecycle state changes.
- **Output**: Canonical error category, Canonical event payload.
- **Business Rules**: Categories: `validation_error`, `not_found`, `security_violation`, `capacity_error`, `timeout_error`, `connection_error`, `state_error`, `execution_error`, `unsupported`. Features cannot invent new top-level categories.
- **Edge Cases**: Overlapping error conditions; uncategorized Blender exceptions.
- **Error Handling**: Fallback to `execution_error` for unmapped Blender exceptions.

### FR-003: Define Protocols and Utility Functions
- **Description**: Provide cross-feature interfaces (protocols) and stateless helpers.
- **Input**: Strings, paths, time values.
- **Output**: Validated strings, normalized paths, formatted timestamps.
- **Business Rules**: No shared utility may perform I/O unless explicitly designated. Type checkers enforce protocol adherence.
- **Edge Cases**: Platform-specific path separators; encoding issues.
- **Error Handling**: `validation_error` for helper constraint violations.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `create_timestamp` | `iso_string` | `Timestamp` | Internal: Immutable time VO |
| `create_workspace_path`| `raw_path` | `WorkspacePath` | Internal: Normalized path VO |
| `create_tracking_id` | `uuid_string` | `TrackingID` | Internal: Correlation ID VO |
| `map_error_category` | `exception` | `ErrorCategory` | Internal: Canonical error mapping |

## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: None (this is the foundation layer; all modules depend on it).

## Non-functional Requirements (Detailed)

- **Performance**: VOs are lightweight and hashable for use in dictionaries/sets.
- **Security**: Path VOs enforce normalization to assist `security` module.
- **Scalability**: Stateless utilities ensure thread-safety across concurrent dispatcher requests.

## Test Scenarios / QA Checklist

- [ ] Verify VO immutability and equality (hashable).
- [ ] Verify all error categories are exhaustive and map correctly.
- [ ] Verify type checkers (mypy) enforce protocol adherence.
- [ ] Verify no domain feature imports another domain feature directly.

## Assumptions & Constraints

- Shared contains zero business logic, I/O, or external service calls.
- Linter rules enforce that features use Dispatcher or Shared contracts, not direct imports.

## Glossary

- **Value Object (VO)**: Immutable, hashable object representing a domain concept (e.g., `Timestamp`).
- **Protocol**: Python typing construct defining a contract/interface that aggregates must implement.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: None
