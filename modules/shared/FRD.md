# FRD — Shared Foundation Layer

## Purpose

Foundation module providing shared taxonomy (VOs, entities, errors, events, constants), contract definitions (protocols, aggregates), and utility functions used by all other features. No business logic — pure domain language and reusable helpers.

## Scope

- Value Objects (VOs) for domain data (timestamps, paths, names, IDs)
- Entity definitions for domain objects
- Error types and error hierarchy
- Event definitions for domain events
- Constants and enums for domain vocabulary
- Protocol/trait definitions (contracts) for cross-feature interfaces
- Aggregate definitions for feature boundaries
- Stateless utility functions (string, path, time, validation helpers)
- Type annotations and shared type aliases

## Out of Scope

Business logic, I/O operations, external service calls, feature-specific implementations, UI/rendering, configuration loading, CLI parsing, MCP tool definitions.

## Depends On

Nothing — this is the foundation layer. All other features depend on shared.
