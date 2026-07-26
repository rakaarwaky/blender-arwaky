# FRD — Configuration & Workspace Feature

## Purpose

Single owner for loading, validating, and providing settings to all features.

## Scope

- Load settings from file, environment, and defaults
- Precedence rules
- Type conversion
- Validation schema
- Immutable settings snapshot
- Hierarchical setting retrieval
- Project workspace resolution
- Settings metadata
- Redaction policy for secret values

## Out of Scope

- Runtime process state
- Blender connection state
- Background task state
- Feature-specific business rules
- Command catalog
- Logging infrastructure

## Depends On

None (foundational feature).

## Provides To

All features.

## Functional Requirements

### FR-CFG-001: Load and Apply Settings

Config is the only feature that loads settings. No other feature reads config files directly.

### FR-CFG-002: Retrieve Settings Values

Features request settings through config. Config returns immutable values or deep copies.

### FR-CFG-003: Resolve Project Workspace Directory

Config determines project root. Asset and render do not determine project root rules themselves.

### FR-CFG-004: Provide Settings Metadata

Config provides config source, override count, and warnings. Metadata must not leak secrets.

### FR-CFG-005: Provide Redaction Rules

Config or security provides list of sensitive keys. Diagnostics, CLI, and MCP use these rules for masking.

## Error Categories

- `ConfigurationError` — invalid/missing config file
- `ValidationError` — config schema violation

## Events

- `config.loaded` — settings loaded successfully
- `config.reload` — settings reloaded

## Configuration Keys

- `config.path` — path to config file
- `config.workspace` — project root directory
- `config.secrets` — list of redacted keys

## QA Checklist

- [ ] Settings load from file, env, and defaults with correct precedence
- [ ] Immutable snapshot returned on retrieve
- [ ] Redaction keys mask sensitive values in diagnostics
- [ ] Project workspace resolves correctly
