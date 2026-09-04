# FRD — Security Policy Feature

## System Overview
The Security module is the central owner for file access, archive safety, untrusted code validation, secret redaction, and security audit policies. Other features delegate security-sensitive decisions here to ensure consistent enforcement and prevent unsafe filesystem access or code injection.

## Functional Requirements

### FR-001: File Path and Archive Validation
- **Description**: Validate filesystem paths and guard archive extraction to prevent traversal and resource exhaustion.
- **Input**: Target path, access mode, archive entry metadata, destination.
- **Output**: Validation result (allowed, canonical path, safe destination, rejected entries).
- **Business Rules**: Rejects traversal, symlink escape, out-of-bounds paths. Archive entries normalized. Absolute paths rejected. Max depth/size/count enforced.
- **Edge Cases**: Circular symlink; archive bomb; hardlinks; case-insensitive collision.
- **Error Handling**: `security_violation`; `archive_safety_error`; `permission_error`.

### FR-002: Untrusted Code Validation and Redaction
- **Description**: Validate code via static syntax-tree analysis and redact sensitive values before logging/output.
- **Input**: Code text, validation policy, text/structured data.
- **Output**: Code validation result, Redacted data.
- **Business Rules**: Rejects dynamic execution, system/subprocess, unsafe file access. Replaces secrets with stable placeholders. Raw code not in logs by default.
- **Edge Cases**: Obfuscated code; oversized payload; secret in nested structure; redaction rule conflict.
- **Error Handling**: `security_violation` for blocked constructs; `code_validation_error`; `redaction_error`.

### FR-003: Security Audit Events
- **Description**: Emit structured security audit events for violations and policy overrides.
- **Input**: Audit context (violation category, severity, correlation ID).
- **Output**: Security audit event.
- **Business Rules**: Every violation produces audit event. Immutable once emitted. High-frequency rate-limited. Sink failure triggers local fallback.
- **Edge Cases**: Sink unavailable; missing correlation ID; oversized metadata.
- **Error Handling**: `audit_emission_error` triggers fallback record; original violation remains primary error.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `validate_path` | `path`, `access_mode` | `SecurityResult` | Internal: path traversal check returning allow/deny plus canonical path; rejects traversal, symlink escape, out-of-bounds paths; violations emit audit events |
| `validate_archive` | `entry_metadata`, `destination` | `SecurityResult` | Internal: archive safety check with normalized entries, rejected absolute paths, and max depth/size/count enforcement; violations emit audit events |
| `validate_code` | `code_text` | `SecurityResult` | Internal: AST-based analysis rejecting dynamic execution, system/subprocess, and unsafe file access; raw code never logged by default |
| `redact_data` | `data`, `policy` | `RedactedData` | Internal: secret masking with stable placeholders at ingestion; raises `redaction_error` on masking failure (entire payload masked as fallback) |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `config` (allowed dirs, patterns), `shared` (taxonomy), `diagnostics` (audit delivery).

## Non-functional Requirements (Detailed)

- **Performance**: Redaction is lightweight and applied at ingestion. Code validation uses fast AST parsing.
- **Security**: Strict path canonicalization. Blocked code constructs configurable. Secrets never leaked in audit events.
- **Scalability**: Audit events rate-limited to prevent log flooding. Fallback buffers handle sink backpressure.

## Test Scenarios / QA Checklist

- [ ] Verify path traversal and symlink escape are rejected for all write/read ops.
- [ ] Verify archive extraction rejects absolute paths and enforces depth/size limits.
- [ ] Verify code validation rejects `subprocess` and `os.system` calls.
- [ ] Verify secrets are redacted in nested structures and logs.
- [ ] Verify audit events emit even when general logging sink is unavailable.

## Assumptions & Constraints

- Security does not execute code or download files; it only validates and redacts.
- Network transport security (TLS) is handled by the OS/Gateway layer, not this module.

## Glossary

- **AST (Abstract Syntax Tree)**: Tree representation of source code used for static analysis.
- **Canonical Path**: The absolute, normalized filesystem path with symlinks resolved.
- **Redaction Placeholder**: Stable string (e.g., `[REDACTED]`) replacing sensitive values.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: `config`, `shared`, `diagnostics`
