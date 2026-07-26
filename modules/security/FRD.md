# FRD — Security Policy Feature

## Purpose

Central owner for file access, archive safety, untrusted code validation, secret redaction, and security audit policies for **blender-arwaky**.

This feature acts as the single authoritative security policy layer. Other features must delegate security-sensitive decisions to this feature instead of implementing their own path validation, archive safety checks, code validation, or redaction logic.

The goal is to ensure consistent security enforcement, reduce duplicated validation logic, prevent unsafe filesystem access, block dangerous code patterns, protect sensitive values from leaking into logs or diagnostics, and produce auditable security events.

## Scope

- Allowed directory policy
- Path traversal validation
- Symbolic link escape prevention
- Canonical path resolution
- Safe archive extraction policy
- Archive depth, size, and entry count limits
- Untrusted code validation
- Static syntax-tree-based code analysis
- Blocked code construct policy
- Sensitive value detection
- Sensitive value redaction
- Security audit event definition
- Security violation categorization
- Policy-driven strict and permissive behavior
- Redaction-safe diagnostics and observability support

## Out of Scope

- Connection authentication
- Network transport security
- Background task tracking
- Asset provider logic
- Render output generation
- Object manipulation logic
- Scene cleanup policy
- Actual execution of untrusted code
- Actual download of remote assets
- Final legal or licensing compliance decisions
- Secret storage or secret management infrastructure

## Depends On

- config feature for allowed directories, archive limits, code validation toggles, redaction rules, and audit behavior
- shared feature for common taxonomy, result envelope, and error category concepts
- logging or observability capability for audit event delivery and redacted diagnostics

## Provides To

- gateway feature
- asset feature
- render feature
- diagnostics feature
- command-line diagnostics feature
- MCP layer
- any feature that writes files, extracts archives, executes code, logs sensitive values, or reports diagnostic output

## Functional Requirements

### FR-SEC-001: Validate File Path Access

All features that read or write files must delegate path validation to security.

- **Description**: Validate whether a filesystem path is allowed for the requested access mode
- **Input**: Target path concept, access mode concept such as read, write, create, delete, or extract, optional base directory, optional operation context
- **Output**: Path validation result concept containing allowed indicator, canonical path reference, denial reason when rejected, and audit metadata
- **Business Rules**:
  - Security checks whether path is within allowed directories
  - Security rejects path traversal attempts
  - Security rejects symbolic link escape attempts
  - Security rejects out-of-bounds paths
  - Security rejects paths outside configured allowed directories
  - Path must be normalized and canonicalized before final decision
  - Relative paths must be resolved against a trusted base directory
  - Symbolic links must be resolved safely when supported by platform
  - Write access must be validated against write-allowed directories
  - Read access may be validated against read-allowed directories when configured
  - Parent directory must be allowed even if target file does not yet exist
  - Path validation must be deterministic across supported platforms
  - Case-insensitive filesystems must be handled consistently
  - Validation failure must produce security violation category
  - Every denial should emit security audit metadata
  - Validation result should not expose sensitive path details beyond redacted diagnostic information
- **Edge Cases**: Missing path, empty path, relative path, symbolic link, circular symbolic link, path outside allowed directory, path pointing to parent directory, case-insensitive path collision, network path, overly long path, permission denied, allowed directory missing, path is directory instead of file, path is file instead of directory
- **Error Handling**: Security violation error for traversal or unauthorized access; permission error for insufficient filesystem permissions; validation error for malformed path concept

### FR-SEC-002: Safely Extract Archive

Asset feature must not implement path traversal protection itself. Asset feature uses security for archive extraction safety.

- **Description**: Validate and guard archive extraction so extracted entries cannot escape allowed extraction directory or exhaust system resources
- **Input**: Archive entry metadata concept, destination directory concept, extraction options such as maximum depth, maximum size, maximum entry count, and symbolic link policy
- **Output**: Safe extraction result concept containing allowed indicator, safe destination path, rejected entry list, warnings, and audit metadata
- **Business Rules**:
  - Each archive entry must be validated before extraction
  - Destination directory must be inside allowed directories
  - Archive entry paths must be normalized and canonicalized relative to destination
  - Absolute entry paths must be rejected
  - Entry paths containing traversal segments must be rejected
  - Symbolic link entries must be rejected unless explicitly allowed by policy
  - Hard link entries must be rejected unless explicitly allowed by policy
  - Extraction depth must not exceed configured maximum depth
  - Total extracted size must not exceed configured maximum total size
  - Individual entry size must not exceed configured maximum entry size
  - Total entry count must not exceed configured maximum entry count
  - Archive extraction should protect against archive bomb patterns
  - Unsupported or malformed archive metadata should be rejected safely
  - Rejected entries must be reported without exposing unsafe target paths in raw form
  - Extraction safety violations should emit audit metadata
  - Security may provide guarded extraction validation hooks or safe extraction policy, but actual archive reading may remain in asset feature
- **Edge Cases**: Archive entry outside destination, nested archive, archive bomb, excessive entry count, excessive compressed size, symbolic link entry, hard link entry, invalid entry encoding, duplicate entry names, unsupported archive format, permission denied destination, missing destination, partially extracted archive
- **Error Handling**: Security violation error for path escape or forbidden link entry; archive safety error for depth, size, or count violation; permission error for destination access failure; validation error for malformed archive metadata

### FR-SEC-003: Validate Untrusted Code

Gateway feature must not implement code validator separately. Gateway feature uses security for untrusted code validation.

- **Description**: Validate untrusted code before execution using static syntax-tree-based analysis and configurable blocked construct policy
- **Input**: Code text concept, validation policy, optional execution context, optional maximum code size
- **Output**: Code validation result concept containing allowed indicator, violation list, redacted violation metadata, and audit metadata
- **Business Rules**:
  - Validation must occur before code is sent for execution
  - Validation should use syntax-tree-based static analysis where possible, not only simple text matching
  - Validation must reject code exceeding configured maximum size
  - Validation must reject unparseable code when strict mode is enabled
  - Blocked constructs may include:
    - dynamic code execution
    - dynamic compilation
    - dynamic import mechanisms
    - system command execution
    - subprocess execution
    - unsafe file access outside allowed directories
    - reflection or sandbox escape patterns
    - access to unsafe internal attributes
    - network access when disabled by policy
  - Blocked construct list must be configurable
  - Validation may support allowed exception list for trusted operations when explicitly configured
  - Validation result must distinguish between policy violation, syntax parse failure, and size limit failure
  - Raw code must not be included in audit events or logs by default
  - Violation metadata should include construct category, redacted code fragment reference, and location hint when safe
  - Code validation is enabled by default
  - If code validation is disabled by configuration, operation may proceed only with explicit warning and audit event
- **Edge Cases**: Obfuscated code, encoded payload, dynamically constructed forbidden construct, unparseable code, oversized code, empty code, comment-only code, false positive on allowed pattern, validation disabled, partially supported language syntax, code containing sensitive values
- **Error Handling**: Security violation error when blocked construct detected; validation error for malformed or unparseable code in strict mode; size limit error when code exceeds maximum size; audit warning when validation is disabled but execution is allowed

### FR-SEC-004: Redact Sensitive Values

Security provides redaction capability for log, diagnostics, command-line output, and MCP responses.

- **Description**: Detect and redact sensitive values before they are written to logs, diagnostics, or user-facing output
- **Input**: Text or structured data concept, redaction policy, optional sensitivity level
- **Output**: Redacted data concept with sensitive values replaced by safe placeholders
- **Business Rules**:
  - Raw code must not appear in logs by default
  - Tokens must not appear in logs
  - Credentials must not appear in logs
  - Passwords must not appear in logs
  - Sensitive paths must be redacted or generalized when configured
  - Connection strings containing secrets must be redacted
  - Redaction should support both key-based detection and pattern-based detection
  - Redaction should preserve data structure when input is structured
  - Redaction should replace sensitive values with stable placeholder concepts
  - Redaction should support nested mappings and lists
  - Redaction should truncate overly large payloads safely
  - Redaction should avoid destroying non-sensitive diagnostic context
  - Redaction should be applied before audit event emission
  - If redaction fails, system should prefer dropping or masking the entire payload over leaking sensitive data
  - Debug mode may expose more detail only when explicitly enabled and still should not expose secrets
- **Edge Cases**: Secret inside text blob, secret inside nested structure, encoded secret, multiline secret, binary data, unknown secret format, oversized payload, sensitive path in error message, token in query parameter, credential in connection string, redaction rule conflict
- **Error Handling**: Redaction error results in safe fallback placeholder or payload suppression; redaction failure should emit diagnostic warning without exposing sensitive value

### FR-SEC-005: Emit Security Audit Events

Every security violation produces an audit event. Diagnostics feature consumes these audit events.

- **Description**: Emit structured security audit events for violations, suspicious activity, redaction failures, and policy overrides
- **Input**: Audit context concept containing violation category, operation type, source feature, target metadata, severity, timestamp, correlation identifier, and redacted reason
- **Output**: Security audit event concept
- **Business Rules**:
  - Every security violation must produce an audit event
  - Audit event must be emitted for:
    - path traversal violation
    - unauthorized file access attempt
    - unsafe archive entry rejection
    - untrusted code violation
    - redaction failure
    - permission denied security event
    - validation disabled override
  - Audit event must not include raw secrets
  - Audit event must not include raw untrusted code by default
  - Audit event must use redacted metadata
  - Audit event should include severity level
  - Audit event should include correlation identifier when available
  - Audit event should include source feature and operation type
  - Audit event should be immutable once emitted
  - Audit event delivery may be synchronous or asynchronous depending on observability configuration
  - If audit sink is unavailable, violation must still be returned to caller and local fallback audit record should be created
  - Audit emission failure must not suppress original security violation
  - High-frequency violations may be rate-limited or grouped to avoid observability overload
- **Edge Cases**: Audit sink unavailable, high-frequency violations, duplicate violations, sensitive data in audit context, missing correlation identifier, clock skew, oversized audit metadata, redaction failure during audit construction
- **Error Handling**: Audit emission error produces fallback audit record or local warning; original security violation remains primary error; audit failure must not leak sensitive data

## Error Categories

- security violation error — path traversal, unauthorized access, forbidden code construct, unsafe archive entry
- permission error — insufficient filesystem or runtime permissions
- archive safety error — archive depth, size, entry count, or link policy violation
- code validation error — unparseable code, oversized code, or invalid code submission
- redaction error — failure to safely redact sensitive value
- audit emission error — failure to deliver audit event to observability sink
- validation error — malformed request or invalid security policy input

## Events

- security violation event — emitted when a security policy violation is detected
- security audit event — emitted for auditable security-related activity
- redaction failure event — emitted when sensitive value redaction cannot be safely completed
- policy override event — emitted when a security control is explicitly disabled or bypassed by configuration

Event payloads should include:

- event category
- severity
- source feature
- operation type
- redacted target metadata
- correlation identifier when available
- timestamp
- policy mode

Event payloads must avoid:

- raw secrets
- raw tokens
- raw credentials
- raw untrusted code
- sensitive filesystem paths beyond redacted form

## Configuration Keys


| Configuration Concept        | Description                                                                          | Typical Default                                   |
| ------------------------------ | -------------------------------------------------------------------------------------- | --------------------------------------------------- |
| Allowed directories          | List of directories permitted for file read, write, extraction, or output operations | Application-managed safe directories              |
| Archive maximum depth        | Maximum allowed nested extraction depth                                              | Conservative depth limit                          |
| Archive maximum total size   | Maximum allowed total extracted size                                                 | Conservative size limit                           |
| Archive maximum entry count  | Maximum allowed number of archive entries                                            | Conservative entry limit                          |
| Archive symbolic link policy | Whether symbolic link entries are allowed during extraction                          | Disallowed                                        |
| Code validation enabled      | Toggle for untrusted code validation before execution                                | Enabled                                           |
| Blocked code constructs      | Configurable list of forbidden code construct categories                             | Dangerous execution and import constructs blocked |
| Maximum code size            | Maximum allowed untrusted code payload size                                          | Conservative payload limit                        |
| Redaction patterns           | Patterns or key names used to detect sensitive values                                | Common secret and credential patterns             |
| Redaction debug mode         | Whether debug output may include less-redacted diagnostic context                    | Disabled                                          |
| Audit retention behavior     | How long audit events are retained or forwarded                                      | Observability-managed retention                   |
| Security policy mode         | Strict or permissive behavior for non-fatal policy issues                            | Strict                                            |

## QA Checklist

- [ ]  Path traversal rejected for all write operations
- [ ]  Path traversal rejected for read operations when read policy enabled
- [ ]  Symbolic link escape rejected during path validation
- [ ]  Out-of-bounds path rejected when outside allowed directories
- [ ]  Relative path resolved safely against trusted base directory
- [ ]  Case-insensitive filesystem handled consistently
- [ ]  Permission denied produces permission error category
- [ ]  Archive extraction enforces allowed destination policy
- [ ]  Archive extraction rejects entry path traversal
- [ ]  Archive extraction rejects absolute entry paths
- [ ]  Archive extraction rejects symbolic link entries by default
- [ ]  Archive extraction enforces maximum depth
- [ ]  Archive extraction enforces maximum total size
- [ ]  Archive extraction enforces maximum entry count
- [ ]  Archive bomb pattern is detected or limited
- [ ]  Untrusted code validated before gateway execution
- [ ]  Dangerous code construct rejected by policy
- [ ]  Oversized code payload rejected
- [ ]  Unparseable code rejected in strict mode
- [ ]  Code validation disabled override emits audit warning
- [ ]  Raw code not included in logs by default
- [ ]  Sensitive values redacted in log output
- [ ]  Sensitive values redacted in diagnostics output
- [ ]  Sensitive values redacted in command-line output
- [ ]  Sensitive values redacted in MCP-facing output
- [ ]  Nested sensitive values redacted correctly
- [ ]  Redaction failure falls back to safe placeholder or payload suppression
- [ ]  Audit events emitted on path violations
- [ ]  Audit events emitted on archive violations
- [ ]  Audit events emitted on code violations
- [ ]  Audit events emitted on redaction failures
- [ ]  Audit events do not contain raw secrets
- [ ]  Audit events do not contain raw untrusted code
- [ ]  Audit emission failure does not suppress original security violation
- [ ]  Security policy decisions are delegated from other features instead of duplicated
