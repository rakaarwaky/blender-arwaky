# FRD — Security Policy Feature

## Purpose

Central owner for file, archive, code, and secret redaction security policies.

## Scope

- Allowed directory policy
- Path traversal validation
- Safe archive extraction
- Untrusted Python code validation
- Sensitive value redaction
- Security audit event definition

## Out of Scope

- Connection authentication
- Network transport
- Background task
- Asset provider logic
- Render output logic
- Object/scene logic

## Depends On

- `config`

## Provides To

- `gateway`
- `asset`
- `render`
- `diagnostics`
- `cli`
- `mcp`

## Functional Requirements

### FR-SEC-001: Validate File Path Access

All features that write files call security. Security checks whether path is within allowed directories. Security rejects path traversal, symlink escape, and out-of-bounds paths.

### FR-SEC-002: Safely Extract Archive

Asset must not implement path traversal protection itself. Asset uses security for archive extraction.

### FR-SEC-003: Validate Untrusted Code

Gateway must not implement AST validator separately. Gateway uses security for code validation.

### FR-SEC-004: Redact Sensitive Values

Security provides redaction function for log, diagnostics, CLI, and MCP. Raw code, tokens, credentials, and sensitive paths must not appear in logs.

### FR-SEC-005: Emit Security Audit Events

Every security violation produces an audit event. Diagnostics consumes these audit events.

## Error Categories

- `SecurityViolationError` — path traversal, unauthorized access
- `PermissionError` — insufficient permissions

## Events

- `security.violation` — path or code security violation
- `security.audit` — audit event emitted

## Configuration Keys

- `security.allowed_dirs` — list of allowed directories
- `security.archive_max_depth` — max extraction depth
- `security.code_validation_enabled` — toggle untrusted code validation

## QA Checklist

- [ ] Path traversal rejected for all write operations
- [ ] Archive extraction enforces safety rules
- [ ] Untrusted code validated before gateway execution
- [ ] Sensitive values redacted in all output
- [ ] Audit events emitted on violations
