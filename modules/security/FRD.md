# FRD — Security Policy Feature

## Purpose

Central owner for file access, archive safety, untrusted code validation, secret redaction, and security audit policies. Other features delegate security-sensitive decisions here instead of implementing their own. Ensures consistent enforcement, prevents unsafe filesystem access, blocks dangerous code, protects sensitive values from leaking, and produces auditable events.

## Scope

- Allowed directory policy
- Path traversal validation
- Symbolic link escape prevention
- Canonical path resolution
- Safe archive extraction policy
- Archive depth, size, entry count limits
- Untrusted code validation (static syntax-tree analysis)
- Blocked code construct policy
- Sensitive value detection + redaction
- Security audit event definition + categorization
- Policy-driven strict/permissive behavior
- Redaction-safe diagnostics + observability support

## Out of Scope

Connection auth, network transport security, background task tracking, asset provider logic, render output, object manipulation, scene cleanup policy, actual code execution, actual download, legal compliance decisions, secret storage/management infrastructure.

## Depends On

config (allowed directories, archive limits, code validation toggles, redaction rules, audit behavior), shared (taxonomy, result envelope, error categories), diagnostics/logging (audit event delivery, redacted diagnostics).

## Provides To

gateway, asset, render, diagnostics, CLI, MCP — any feature that writes files, extracts archives, executes code, logs values, or reports output.

## Functional Requirements

### FR-SEC-001: Validate File Path Access

- **Description**: Validate whether filesystem path is allowed for requested access mode
- **Input**: Target path, access mode (read/write/create/delete/extract), optional base directory, optional operation context
- **Output**: Path validation result (allowed, canonical path, denial reason, audit metadata)
- **Rules**: Checks if path is within allowed directories. Rejects traversal attempts, symlink escape, out-of-bounds paths, paths outside configured allowed directories. Path normalized + canonicalized before final decision. Relative paths resolved against trusted base directory. Symlinks resolved safely when platform supports. Write access against write-allowed dirs. Read access against read-allowed dirs when configured. Parent directory must be allowed even if target file doesn't exist. Deterministic across platforms. Case-insensitive fs handled consistently. Denial → security violation category. Every denial emits audit metadata. Result never exposes sensitive path details beyond redacted diagnostic info.
- **Edge Cases**: Missing/empty/relative path, symlink, circular symlink, outside allowed dir, parent directory traversal, case-insensitive collision, network path, overly long, permission denied, allowed dir missing, path is dir vs file
- **Error Handling**: Security violation (traversal/unauthorized); permission error; validation error (malformed)

### FR-SEC-002: Safely Extract Archive

- **Description**: Validate + guard archive extraction so entries cannot escape allowed directory or exhaust resources
- **Input**: Archive entry metadata, destination directory, extraction options (max depth/size/entry count, symlink policy)
- **Output**: Safe extraction result (allowed, safe destination, rejected entry list, warnings, audit metadata)
- **Rules**: Each entry validated before extraction. Destination inside allowed dirs. Entry paths normalized relative to destination. Absolute paths rejected. Traversal segments rejected. Symlink entries rejected unless explicitly allowed. Hardlink entries rejected unless explicitly allowed. Max depth enforced. Max total extracted size enforced. Max individual entry size enforced. Max entry count enforced. Archive bomb patterns protected against. Unsupported/malformed metadata → safe reject. Rejected entries reported without exposing unsafe raw paths. Security may provide guarded validation hooks; actual archive reading may remain in asset feature.
- **Edge Cases**: Entry outside destination, nested archive, bomb, excessive count/size, symlink/hardlink, invalid encoding, duplicate names, unsupported format, permission denied, missing destination, partially extracted
- **Error Handling**: Security violation (escape/forbidden link); archive safety error (depth/size/count); permission error; validation error (malformed)

### FR-SEC-003: Validate Untrusted Code

- **Description**: Validate untrusted code via static syntax-tree analysis and configurable blocked construct policy
- **Input**: Code text, validation policy, optional execution context, optional max code size
- **Output**: Code validation result (allowed, violation list, redacted violation metadata, audit metadata)
- **Rules**: Validation before code sent for execution. Syntax-tree-based static analysis (not just text matching). Rejects code exceeding max size. Rejects unparseable code in strict mode. Blocked constructs (configurable): dynamic execution/compilation/import, system/subprocess execution, unsafe file access outside allowed dirs, reflection/sandbox escape, unsafe internal attributes, network access when disabled. Optional allowed exception list for trusted operations. Distinguishes policy violation from syntax failure from size limit failure. Raw code not in audit events/logs by default. Violation metadata: construct category, redacted fragment ref, location hint when safe. Enabled by default. Disabled → explicit warning + audit event.
- **Edge Cases**: Obfuscated/encoded/dynamically-constructed forbidden construct, unparseable, oversized, empty, comment-only, false positive, disabled, partially supported language, code containing sensitive values
- **Error Handling**: Security violation (blocked construct); validation error (unparseable in strict); size limit error; audit warning (validation disabled)

### FR-SEC-004: Redact Sensitive Values

- **Description**: Detect + redact sensitive values before logs, diagnostics, CLI, MCP output
- **Input**: Text/structured data, redaction policy, optional sensitivity level
- **Output**: Redacted data (sensitive values replaced by safe placeholders)
- **Rules**: Raw code not in logs by default. Tokens/credentials/passwords/sensitive paths/connection strings redacted. Key-based + pattern-based detection. Preserves structure when input structured. Replaces with stable placeholders. Supports nested mappings/lists. Truncates overly large payloads safely. Preserves non-sensitive diagnostic context. Applied before audit event emission. Failure → drop or mask entire payload (never leak). Debug mode may expose more detail only when explicitly enabled — still no secrets.
- **Edge Cases**: Secret in text blob/nested structure/encoded/multiline/binary, unknown format, oversized payload, sensitive path in error message, token in query param, credential in connection string, rule conflict
- **Error Handling**: Redaction error → safe fallback placeholder or payload suppression; diagnostic warning without exposing value

### FR-SEC-005: Emit Security Audit Events

- **Description**: Emit structured security audit events for violations, suspicious activity, redaction failures, policy overrides
- **Input**: Audit context (violation category, operation type, source feature, target metadata, severity, timestamp, correlation ID, redacted reason)
- **Output**: Security audit event
- **Rules**: Every security violation produces audit event. Categories: path traversal, unauthorized access, archive entry rejection, code violation, redaction failure, permission denied, validation disabled override. No raw secrets. No raw untrusted code by default. Redacted metadata only. Includes severity level, correlation ID (when available), source feature, operation type. Immutable once emitted. Sync or async delivery per config. Sink unavailable → violation still returned to caller + local fallback record. Emission failure never suppresses original violation. High-frequency: rate-limited or grouped.
- **Edge Cases**: Sink unavailable, high-frequency/duplicate violations, sensitive data in context, missing correlation ID, clock skew, oversized metadata, redaction failure during construction
- **Error Handling**: Emission → fallback record or local warning; original violation remains primary error; never leaks sensitive data

## Error Categories

- security violation — traversal/unauthorized access/forbidden construct/unsafe entry
- permission error — insufficient filesystem/runtime permissions
- archive safety error — depth/size/entry count/link policy violation
- code validation error — unparseable/oversized/invalid
- redaction error — failure to safely redact
- audit emission error — failure to deliver audit event
- validation error — malformed request or invalid input

## Events

- security violation (detected)
- security audit (auditable activity)
- redaction failure (cannot safely complete)
- policy override (control disabled/bypassed)

Payloads: category, severity, source feature, operation type, redacted target metadata, correlation ID, timestamp, policy mode. Never: raw secrets/tokens/credentials/code, sensitive paths beyond redacted form.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| allowed_directories | Permitted for read/write/extract/output | App-managed safe dirs |
| archive_maximum_depth | Max nested extraction depth | Conservative |
| archive_maximum_total_size | Max extracted size | Conservative |
| archive_maximum_entry_count | Max entries | Conservative |
| archive_symlink_policy | Allow symlink entries | Disallowed |
| code_validation_enabled | Untrusted code validation | Enabled |
| blocked_code_constructs | Forbidden construct categories | Dangerous execution + imports |
| maximum_code_size | Max untrusted code payload | Conservative |
| redaction_patterns | Key/pattern detection | Common secret patterns |
| redaction_debug_mode | Less-redacted output | Disabled |
| audit_retention_behavior | Retention/forwarding | Observability-managed |
| security_policy_mode | strict/permissive | strict |

## QA Checklist

- [ ] Path traversal rejected for all write/read ops
- [ ] Symlink escape rejected; out-of-bounds rejected
- [ ] Relative path resolved safely; case-insensitive consistent
- [ ] Permission denied → permission error
- [ ] Archive: allowed destination enforcement, traversal rejection, absolute path rejection
- [ ] Archive: symlink rejected by default; depth/size/entry count enforced
- [ ] Archive bomb limited; unsafe patterns detected
- [ ] Code validated before execution; dangerous constructs rejected
- [ ] Oversized/unparseable code rejected (strict)
- [ ] Disabled override → audit warning
- [ ] Raw code not in logs by default
- [ ] Secrets redacted in logs/diagnostics/CLI/MCP output
- [ ] Nested values redacted correctly; failure → safe fallback
- [ ] Audit events on path/archive/code/redaction violations
- [ ] No raw secrets or untrusted code in audit events
- [ ] Emission failure doesn't suppress original violation
- [ ] Delegation: other features use security instead of implementing own validation
