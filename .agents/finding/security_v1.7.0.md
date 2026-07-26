# Module: security (v1.7.0)

This document contains the source code for module `security` along with related and imported definitions from the `shared` module.

## File List

- [ARCHITECTURE.md](<ARCHITECTURE.md>)
- [modules/security/FRD.md](<modules/security/FRD.md>)
- [modules/security/src/__init__.py](<modules/security/src/__init__.py>)
- [modules/security/src/agent_security_orchestrator.py](<modules/security/src/agent_security_orchestrator.py>)
- [modules/security/src/capabilities_archive_guard.py](<modules/security/src/capabilities_archive_guard.py>)
- [modules/security/src/capabilities_audit_emitter.py](<modules/security/src/capabilities_audit_emitter.py>)
- [modules/security/src/capabilities_code_validator.py](<modules/security/src/capabilities_code_validator.py>)
- [modules/security/src/capabilities_path_validator.py](<modules/security/src/capabilities_path_validator.py>)
- [modules/security/src/capabilities_sensitive_redactor.py](<modules/security/src/capabilities_sensitive_redactor.py>)
- [modules/security/src/root_security_container.py](<modules/security/src/root_security_container.py>)
- [modules/shared/src/security/__init__.py](<modules/shared/src/security/__init__.py>)
- [modules/shared/src/security/contract_emit_audit_protocol.py](<modules/shared/src/security/contract_emit_audit_protocol.py>)
- [modules/shared/src/security/contract_extract_archive_protocol.py](<modules/shared/src/security/contract_extract_archive_protocol.py>)
- [modules/shared/src/security/contract_redact_sensitive_protocol.py](<modules/shared/src/security/contract_redact_sensitive_protocol.py>)
- [modules/shared/src/security/contract_security_operate_aggregate.py](<modules/shared/src/security/contract_security_operate_aggregate.py>)
- [modules/shared/src/security/contract_validate_code_protocol.py](<modules/shared/src/security/contract_validate_code_protocol.py>)
- [modules/shared/src/security/contract_validate_path_protocol.py](<modules/shared/src/security/contract_validate_path_protocol.py>)
- [modules/shared/src/security/taxonomy_security_vo.py](<modules/shared/src/security/taxonomy_security_vo.py>)
- [pyproject.toml](<pyproject.toml>)
- [README.md](<README.md>)

---

## File: ARCHITECTURE.md

````markdown
# Agentic Engineering System Architecture

## 1. Purpose

The Agentic Engineering System is a layered, AI-native architecture pattern. It keeps domain models stable, business logic readable, technical detail isolated, and layer boundaries explicit enough for both humans and AI agents to modify the system safely.

---

## 2. Workspace Organization

The architecture supports multi-language workspaces.

| Term               | Meaning                                                           |
| ------------------ | ----------------------------------------------------------------- |
| Project Workspaces | Project root containing all configuration and language members    |
| Workspace Member   | One self-contained crate, package, or module inside the workspace |
| Crates directory   | Rust workspace members                                            |
| Packages directory | TypeScript or JavaScript packages                                 |
| Modules directory  | Python modules or sub-projects                                    |

---

## 3. Naming Convention

File names must communicate three parts:

1. Layer as prefix
2. Concern as middle name
3. Role as suffix

The parts are joined by underscores, followed by the normal file extension for the language.

`layer_concern_role.rs/py/ts`

---

## 4. Vertical Slicing Folder Structure

The recommended folder structure follows this order:

#### Features member

_Example feature crate `crates|packages|modules/<name-features>/`_

```text
surface_<concern>_<role>.rs/py/ts                ← surface layer
capabilities_<concern>_<role>.rs/py/ts           ← capabilities layer
agent_<concern>_orchestrator.rs/py/ts            ← agent layer
```

Exceptions: `main.rs`, `lib.rs`, `mod.rs`, `__init__.py`, `index.ts`, `index.js`.

#### Shared member

`crates|packages|modules/shared/<common>or<domain-folder>`

```text
contract_<concern>_protocol.rs/py/ts             ← contract layer
contract_<concern>_aggregate.rs/py/ts            ← contract layer
taxonomy_<concern>_vo.rs/py/ts                   ← taxonomy layer
taxonomy_<concern>_event.rs/py/ts                ← taxonomy layer
taxonomy_<concern>_entity.rs/py/ts               ← taxonomy layer
taxonomy_<concern>_constant.rs/py/ts             ← taxonomy layer
utility_<concern>_<role>.rs/py/ts                ← utility layer
```

`shared` folder groups by domain. Use `shared/common/` for generic files.

---

## 5. Taxonomy Layer

### Purpose

Taxonomy is the domain foundation layer. It defines the stable language of the domain and must remain free from technical or behavioral concerns.

### Components

| Role         | Meaning                               |
| ------------ | ------------------------------------- |
| Value object | Immutable data concept                |
| Entity       | Stateful domain concept with identity |
| Event        | Immutable domain fact                 |
| Error        | Domain-level error                    |
| Constant     | Compile-time literal value            |

### Dependencies

Taxonomy depends on nothing.

### Special Rules

- Value objects and Constants may use all primitive types.
- Entities, Events, and Errors must use Value objects/Constants instead of primitive types (bool/str is an exception).
- Constants must be compile-time values.
- Taxonomy must not contain business rules, infrastructure, or imports from other layers.

---

## 6. Contract Layer

### Purpose

Contract defines the public behavior of the system without exposing implementation. It allows callers to depend on stable interfaces instead of concrete logic.

### Components

| Role      | Meaning                                                                                           |
| --------- | ------------------------------------------------------------------------------------------------- |
| Protocol  | Interface defining inbound behavior. It is implemented by Capabilities and consumed by the Agent. |
| Aggregate | Facade definition implemented by Agent, used by Surface to access feature behavior.               |

### Dependencies

Contract may depend on Taxonomy only.

### Special Rules

- Protocol defines behavior only without implementation.
- Aggregate hides Capabilities from Surface.

---

## 7. Utility Layer

### Purpose

Utility contains low-level technical mechanics. It exists so that Capabilities can remain clean and expressive.

### Role Naming

Utility role suffixes are unlimited. The role name is chosen based on demand and must describe the technical responsibility and concern of the file.

parser
splitter
trimmer
slugifier
sanitizer
normalizer
extractor
replacer
converter
counter
resolver
detector
builder
joiner
serializer
deserializer
encoder
decoder
hasher
generator
formatter
comparator
differ
matcher
checker
calculator
mapper
merger
grouper
sorter
deduplicator
printer

### Dependencies

Utility may depend only on Taxonomy.

### Technical Concern Examples

| Concern                 | Responsibility                                      |
| ----------------------- | --------------------------------------------------- |
| File discovery          | Walk directories, detect files, apply ignore        |
| External tool execution | Run linters, compilers, formatters, analyzers       |
| Parsing and matching    | Parse text, match patterns, extract structured data |
| Path normalization      | Normalize paths across platforms                    |
| System operations       | Handle process or environment mechanics             |

### Special Rules

- Utility must use stateless standalone functions only.
- Utility must not contain stateful objects, behavior definitions, or contract implementations.
- Utility must not make business decisions.
- Utility may perform technical operations if needed.
- Utility must not implement any contract.
- Utility role names may expand freely, but the layer must remain technical and standalone.
- Utility must use stateless standalone functions only.

---

## 8. Capabilities Layer

### Purpose

Capabilities contain the concrete implementation of the system's behavior. This layer encapsulates both **pure business logic** (computations, validations) and **external adaptations** (database access, third-party API calls, infrastructure mechanics). By hiding these implementations behind Contracts, the system keeps its behavior modular, swappable, and fully isolated from orchestration.

### Role Naming

#### Internal Examples

validator
assessor
calculator
resolver
classifier
selector
mapper
transformer
policy
enricher
evaluator
analyzer
scorer
grader
ranker
filter
checker
reviewer
approver
rejector

#### External Examples

repository
gateway
client
provider
fetcher
reader
writer
scanner
executor
publisher
subscriber
adapter
connector
uploader
downloader
sender
receiver
dispatcher
watcher
monitor

### Dependencies

- Capabilities may depend on Taxonomy, Contract, and Utility.
- Capabilities must not depend on or import other Capabilities.

### Concern Examples

Capabilities generally handle two types of concerns:

| Category                | Concern        | Responsibility                                 |
| ----------------------- | -------------- | ---------------------------------------------- |
| **Business Logic**      | Validation     | Check domain conditions or input correctness   |
|                         | Computation    | Calculate scores, totals, or derived values    |
|                         | Transformation | Map, filter, reduce, or reshape data           |
|                         | Resolution     | Apply rules and decide outcomes                |
|                         | Assessment     | Judge severity, compliance, grade, or quality  |
| **External Adaptation** | Repository     | Fetch or persist domain entities to a database |
|                         | Integration    | Communicate with third-party services or APIs  |
|                         | Provider       | Generate data from external systems            |

### Special Rules

- **No Inter-Capability Dependency:** Capabilities must never import or call other Capabilities directly. They are standalone execution units.
- **Pipeline Aggregation:** Multiple Capabilities (e.g., Capability A for data fetching, Capability B for business calculation) are designed to be composed into a sequential pipeline by the **Agent Layer**, not by themselves.
- **Shared Logic Extraction (DRY):** If multiple Capabilities require the same technical mechanics or functions, that logic must be extracted into a reusable standalone function in the **Utility Layer**. Capabilities must not duplicate technical code (Don't Repeat Yourself).
- **Contract Implementation:** Capabilities must implement the `protocol_` defined in the Contract Layer.
- **State Ownership:** Capabilities are the owners of business and technical state within their execution scope.
- **Utility Delegation:** Capabilities must call Utility standalone functions when low-level technical operations are required, passing their state/data as arguments.
- **No Orchestration:** Capabilities must not contain flow control (looping across capabilities, branching between capabilities, or error escalation policy). They execute their single responsibility and return a result.
- **No Domain Definition:** Capabilities must not define domain models (Entities, Value Objects); they only consume and produce Taxonomy.

---

## 9. Agent Layer

### Purpose

Agent coordinates multiple capabilities into executable flows. It controls sequence and movement, not business calculation.

### Allowed Role

The only Agent role is orchestrator.

### Dependencies

Agent may depend only on Taxonomy, Contract, and Utility.

### Allowed Flow Control

| Flow Type               | Purpose                                |
| ----------------------- | -------------------------------------- |
| Sequential execution    | Run steps in order                     |
| Looping                 | Process multiple items or events       |
| Branching               | Choose path based on result            |
| Error handling          | Recover, abort, continue, or escalate  |
| Timeout or cancellation | Stop long-running or asynchronous work |

### Special Rules

- Agent must depend on Contract, not concrete implementations.
- Agent must not use and must be completely ignorant of Capabilities implementations.
- Agent must not calculate business results.
- Agent must not define domain models.

---

## 10. Surface Layer

### Purpose

Surface is the outer boundary of the system. It handles user-facing or external-facing interaction and translates it into architectural actions.

### Allowed Roles

Surface roles include:

- command
- controller
- page
- view
- component
- router
- layout
- hook
- store
- action
- screen

### Surface Groups

| Group            | Roles                             | Dependencies                          | Rule                                            |
| ---------------- | --------------------------------- | ------------------------------------- | ----------------------------------------------- |
| Smart surfaces   | command, controller, page, router | Taxonomy, Contract Aggregate, Utility | May initiate feature behavior through aggregate |
| Utility surfaces | hook, store, action, screen       | Taxonomy, Contract Aggregate, Utility | Support smart surfaces but must not import smart surfaces |
| Passive surfaces | component, view, layout           | Taxonomy only                         | Presentation-only, no logic or orchestration    |

### Special Rules

- Smart surfaces must consume Contract Aggregates.
- Surfaces must not import Capabilities, Utility, or Agent directly.
- Surfaces must not contain business calculation or orchestration.

---

## 11. Root Layer

### Purpose

Root is the composition layer. It assembles the system by connecting concrete implementations to contracts and starting the application.

### Components

| Role      | Meaning                                                                           |
| --------- | --------------------------------------------------------------------------------- |
| Container | Wires one feature by connecting Capabilities to Contract protocols and aggregates |
| Entry     | Bootstraps the application and composes feature containers                        |

### Dependencies

Root may depend on all layers.

### Special Rules

- Root may instantiate and wire components.
- Root must not contain business logic.
- Root must not contain orchestration policy.
- Root must not contain technical parsing or user interface behavior.
````

---

## File: modules/security/FRD.md

```markdown
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
```

---

## File: modules/security/src/__init__.py

```python
"""Security feature module — AES implementation.

Layers:
  - Taxonomy (shared/src/security/)   → VOs, Errors, Events, Constants
  - Contract (shared/src/security/)   → 5 individual protocols + Aggregate ABC
  - Capabilities (5 executors)        → One per FR-SEC operation
  - Agent                             → SecurityOrchestrator (implements Aggregate facade)
  - Root                              → SecurityContainer (DI wiring)

Surface layer is intentionally absent — MCP/CLI command handlers live in
their respective feature modules (modules/mcp, modules/cli).
"""

from . import root_security_container
from .root_security_container import SecurityContainer, create_security_feature

__all__ = [
    "SecurityContainer",
    "create_security_feature",
    "root_security_container",
]
```

---

## File: modules/security/src/agent_security_orchestrator.py

```python
"""Agent: Security feature orchestrator.

Coordinates security flows via the SecurityOperateAggregate contract.
Orchestration only — no business logic, depends on individual capability protocols.

Structure:
  1. Constants & imports
  2. SecurityOrchestrator — implements aggregate, delegates to 5 individual protocols
"""

import logging

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol
from modules.shared.src.security.contract_security_operate_aggregate import SecurityOperateAggregate
from modules.shared.src.security.contract_validate_code_protocol import ValidateCodeProtocol
from modules.shared.src.security.contract_validate_path_protocol import ValidatePathProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    CodeValidationVO,
    PathValidationVO,
    RedactionVO,
    SecurityAuditEventVO,
)

logger = logging.getLogger("BlenderMCPServer")


class SecurityOrchestrator(SecurityOperateAggregate):
    """Orchestrates security operations through 5 individual capability protocols."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        validate_path_cap: ValidatePathProtocol,
        validate_archive_cap: ExtractArchiveProtocol,
        validate_code_cap: ValidateCodeProtocol,
        redact_cap: RedactSensitiveProtocol,
        emit_audit_cap: EmitAuditProtocol,
    ) -> None:
        self._validate_path = validate_path_cap
        self._validate_archive = validate_archive_cap
        self._validate_code = validate_code_cap
        self._redact = redact_cap
        self._emit_audit = emit_audit_cap

    # ─── Block 2: Aggregate Implementation ───────────────────

    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """Delegate path validation to the capabilities layer."""
        logger.info("Orchestrating validate_path for %s", request.target_path)
        return await self._validate_path.validate_path(request)

    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Delegate archive extraction validation to the capabilities layer."""
        logger.info("Orchestrating validate_extraction for %s", request.destination_directory)
        return await self._validate_archive.validate_extraction(request)

    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Delegate code validation to the capabilities layer."""
        logger.info("Orchestrating validate_code (%d bytes)", len(request.code_text))
        return await self._validate_code.validate_code(request)

    async def redact(self, request: RedactionVO) -> RedactionVO:
        """Delegate redaction to the capabilities layer."""
        logger.info("Orchestrating redact (%d chars)", len(request.text))
        return await self._redact.redact(request)

    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Delegate audit emission to the capabilities layer."""
        logger.info("Orchestrating emit_audit: %s", event.violation_category.value)
        return await self._emit_audit.emit_audit(event)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────

    @property
    def security_operate_capability(self) -> SecurityOperateAggregate:
        """Expose self as the security operate aggregate facade for dispatch."""
        return self

    def __repr__(self) -> str:
        return "SecurityOrchestrator()"
```

---

## File: modules/security/src/capabilities_archive_guard.py

```python
"""Capabilities: Archive guard — FR-SEC-002.

Validates archive extraction safety: path traversal, symlink, depth, size, count limits.
Implements ExtractArchiveProtocol.
"""

from __future__ import annotations

import os

from modules.shared.src.security.contract_extract_archive_protocol import ExtractArchiveProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    ArchiveExtractionVO,
    RejectedEntryVO,
)


class ArchiveGuard(ExtractArchiveProtocol):
    """Validates archive extraction against safety policy."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self) -> None:
        pass

    # ─── Block 2: Public Contract  ────────────────────────
    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Validate and guard archive extraction against safety policy."""
        opts = request.options
        dest = os.path.normpath(os.path.abspath(request.destination_directory))
        rejected: list[RejectedEntryVO] = []
        warnings: list[str] = []

        if not dest:
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                rejected_entries=tuple(rejected),
                warnings=tuple(warnings),
                audit_metadata={"rule": "missing_destination"},
            )

        total_size = 0
        entry_count = 0

        for entry in request.entries:
            entry_count += 1

            if entry_count > opts.max_entry_count:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Exceeds maximum entry count"))
                continue

            if entry.is_symbolic_link and not opts.allow_symbolic_links:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Symbolic link entry not allowed"))
                continue

            if entry.is_hard_link and not opts.allow_hard_links:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Hard link entry not allowed"))
                continue

            if entry.uncompressed_size > opts.max_entry_size:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason=f"Entry exceeds maximum size: {entry.uncompressed_size} > {opts.max_entry_size}"))
                continue

            if os.path.isabs(entry.entry_path):
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Absolute entry path not allowed"))
                continue

            if ".." in entry.entry_path.split("/") or ".." in entry.entry_path.split(os.sep):
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Path traversal in entry path"))
                continue

            entry_resolved = os.path.normpath(os.path.join(dest, entry.entry_path))
            if not entry_resolved.startswith(dest + os.sep) and entry_resolved != dest:
                rejected.append(RejectedEntryVO(entry_path=entry.entry_path, reason="Entry escapes destination directory"))
                continue

            total_size += entry.uncompressed_size

        if total_size > opts.max_total_size:
            return ArchiveExtractionVO(
                destination_directory=request.destination_directory,
                entries=request.entries,
                options=request.options,
                allowed=False,
                safe_destination=dest,
                rejected_entries=tuple(rejected),
                warnings=tuple(warnings + [f"Total extracted size {total_size} exceeds limit {opts.max_total_size}"]),
                audit_metadata={"rule": "total_size_exceeded", "total_size": total_size},
            )

        allowed = len(rejected) == 0
        return ArchiveExtractionVO(
            destination_directory=request.destination_directory,
            entries=request.entries,
            options=request.options,
            allowed=allowed,
            safe_destination=dest,
            rejected_entries=tuple(rejected),
            warnings=tuple(warnings),
            audit_metadata={"entry_count": entry_count, "total_size": total_size},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "ArchiveGuard()"
```

---

## File: modules/security/src/capabilities_audit_emitter.py

```python
"""Capabilities: Audit emitter — FR-SEC-005.

Emits structured security audit events for violations, suspicious activity, and policy overrides.
Implements EmitAuditProtocol.
"""

from __future__ import annotations

import contextlib
import time
import uuid
from typing import Protocol

from modules.shared.src.security.contract_emit_audit_protocol import EmitAuditProtocol
from modules.shared.src.security.taxonomy_security_vo import SecurityAuditEventVO


class _AuditSink(Protocol):
    """Protocol for delivering audit events to observability (DI boundary)."""

    def deliver(self, event: SecurityAuditEventVO) -> None: ...


class AuditEmitter(EmitAuditProtocol):
    """Emits structured security audit events with fallback on sink failure."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, sink: _AuditSink | None = None) -> None:
        self._sink = sink

    # ─── Block 2: Public Contract  ────────────────────────
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Emit a structured security audit event for violations and policy activity."""
        emitted = SecurityAuditEventVO(
            violation_category=event.violation_category,
            operation_type=event.operation_type,
            source_feature=event.source_feature,
            target_metadata=event.target_metadata,
            severity=event.severity,
            correlation_id=event.correlation_id,
            redacted_reason=event.redacted_reason,
            event_id=uuid.uuid4().hex[:16],
            timestamp=time.time(),
            policy_mode=event.policy_mode,
        )

        if self._sink:
            with contextlib.suppress(Exception):
                self._sink.deliver(emitted)

        return emitted

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "AuditEmitter()"
```

---

## File: modules/security/src/capabilities_code_validator.py

```python
"""Capabilities: Code validator — FR-SEC-003.

Validates untrusted code using AST analysis and blocked construct policy.
Implements ValidateCodeProtocol.
"""

from __future__ import annotations

import ast
from typing import Protocol

from modules.shared.src.security.contract_validate_code_protocol import ValidateCodeProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    CodeValidationVO,
    CodeViolationVO,
    SecurityPolicyVO,
)


class _CodePayloadChecker(Protocol):
    """Protocol for checking code payload size (DI boundary)."""

    def check(self, code: str, max_bytes: int) -> None: ...


class CodeValidator(ValidateCodeProtocol):
    """Validates untrusted code before execution using static AST analysis."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        policy: SecurityPolicyVO | None = None,
        payload_checker: _CodePayloadChecker | None = None,
    ) -> None:
        self._policy = policy
        self._checker = payload_checker

    # ─── Block 2: Public Contract  ────────────────────────
    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Validate untrusted code using static analysis and blocked construct policy."""
        violations: list[CodeViolationVO] = []

        code_bytes = len(request.code_text.encode("utf-8"))
        if code_bytes > request.max_code_size:
            return CodeValidationVO(
                code_text=request.code_text,
                max_code_size=request.max_code_size,
                strict_mode=request.strict_mode,
                execution_context=request.execution_context,
                allowed=False,
                violations=(CodeViolationVO(category="size_limit", description=f"Code too large: {code_bytes} > {request.max_code_size}"),),
                audit_metadata={"rule": "code_oversized", "size": code_bytes},
            )

        if not request.code_text or not request.code_text.strip():
            return CodeValidationVO(
                code_text=request.code_text,
                max_code_size=request.max_code_size,
                strict_mode=request.strict_mode,
                allowed=False,
                violations=(CodeViolationVO(category="empty_code", description="Empty code payload"),),
                audit_metadata={"rule": "empty_code"},
            )

        if self._policy and not self._policy.code_validation_enabled:
            return CodeValidationVO(
                code_text=request.code_text,
                max_code_size=request.max_code_size,
                strict_mode=request.strict_mode,
                execution_context=request.execution_context,
                allowed=True,
                redacted_metadata={"warning": "Code validation disabled by policy"},
                audit_metadata={"rule": "validation_disabled"},
            )

        try:
            tree = ast.parse(request.code_text)
        except SyntaxError as exc:
            if request.strict_mode:
                return CodeValidationVO(
                    code_text=request.code_text,
                    max_code_size=request.max_code_size,
                    strict_mode=request.strict_mode,
                    allowed=False,
                    violations=(CodeViolationVO(category="syntax_error", description=f"Syntax error: {exc.msg} at line {exc.lineno}", location_hint=f"line {exc.lineno}"),),
                    audit_metadata={"rule": "syntax_error", "line": exc.lineno},
                )
            violations.append(CodeViolationVO(category="syntax_error", description=f"Syntax error: {exc.msg}", location_hint=f"line {exc.lineno}"))

        blocked_modules = {"os", "subprocess", "shutil", "importlib", "sys", "socket", "ctypes", "multiprocessing", "threading", "signal", "pickle"}
        blocked_functions = {"eval", "exec", "compile", "__import__", "breakpoint", "globals", "locals", "getattr", "setattr", "delattr"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name.split(".")[0]
                    if mod in blocked_modules:
                        violations.append(CodeViolationVO(category="blocked_module_import", description=f"Blocked import: {alias.name}"))
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    mod = node.module.split(".")[0]
                    if mod in blocked_modules:
                        violations.append(CodeViolationVO(category="blocked_module_import", description=f"Blocked import from: {node.module}"))
            elif isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id in blocked_functions:
                    violations.append(CodeViolationVO(category="blocked_function_call", description=f"Blocked function call: {func.id}()"))
                elif isinstance(func, ast.Attribute) and func.attr in blocked_functions:
                    violations.append(CodeViolationVO(category="blocked_function_call", description=f"Blocked method call: .{func.attr}()"))

        allowed = len(violations) == 0
        return CodeValidationVO(
            code_text=request.code_text,
            max_code_size=request.max_code_size,
            strict_mode=request.strict_mode,
            execution_context=request.execution_context,
            allowed=allowed,
            violations=tuple(violations),
            audit_metadata={"violation_count": len(violations)},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "CodeValidator()"
```

---

## File: modules/security/src/capabilities_path_validator.py

```python
"""Capabilities: Path validator — FR-SEC-001.

Validates filesystem path access: traversal, symlink escape, allowed directories.
Implements ValidatePathProtocol.
"""

from __future__ import annotations

import os
from typing import Protocol

from modules.shared.src.security.contract_validate_path_protocol import ValidatePathProtocol
from modules.shared.src.security.taxonomy_security_vo import (
    PathValidationVO,
    SecurityPolicyVO,
)


class _PathResolver(Protocol):
    """Protocol for resolving canonical paths (DI boundary)."""

    def resolve(self, path: str) -> str: ...


class PathValidator(ValidatePathProtocol):
    """Validates filesystem path access against security policy."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        policy: SecurityPolicyVO,
        path_resolver: _PathResolver | None = None,
    ) -> None:
        self._policy = policy
        self._resolver = path_resolver

    # ─── Block 2: Public Contract  ────────────────────────
    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """Validate whether a filesystem path is allowed for the requested access mode."""
        target = request.target_path
        if not target:
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                base_directory=request.base_directory,
                operation_context=request.operation_context,
                allowed=False,
                denial_reason="Empty path",
                audit_metadata={"rule": "empty_path"},
            )

        if not os.path.isabs(target):
            base = request.base_directory or (self._policy.allowed_directories[0] if self._policy.allowed_directories else ".")
            target = os.path.join(base, target)

        try:
            normalized = os.path.normpath(os.path.abspath(target))
        except (OSError, ValueError) as exc:
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason=f"Path resolution failed: {exc}",
                audit_metadata={"rule": "path_resolution_failed"},
            )

        if ".." in target.split(os.sep):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Path traversal detected",
                audit_metadata={"rule": "path_traversal", "path": _redact_path(normalized)},
            )

        if self._resolver:
            try:
                resolved = self._resolver.resolve(normalized)
                if resolved != normalized:
                    return PathValidationVO(
                        target_path=request.target_path,
                        access_mode=request.access_mode,
                        allowed=False,
                        denial_reason="Symbolic link escape",
                        audit_metadata={"rule": "symlink_escape", "path": _redact_path(normalized)},
                    )
            except (OSError, ValueError):
                return PathValidationVO(
                    target_path=request.target_path,
                    access_mode=request.access_mode,
                    allowed=False,
                    denial_reason="Symlink resolution failed",
                    audit_metadata={"rule": "symlink_resolution_failed"},
                )

        if not self._is_within_allowed_dirs(normalized):
            return PathValidationVO(
                target_path=request.target_path,
                access_mode=request.access_mode,
                allowed=False,
                denial_reason="Path outside allowed directories",
                canonical_path=normalized,
                audit_metadata={"rule": "unauthorized_access", "path": _redact_path(normalized)},
            )

        return PathValidationVO(
            target_path=request.target_path,
            access_mode=request.access_mode,
            base_directory=request.base_directory,
            operation_context=request.operation_context,
            allowed=True,
            canonical_path=normalized,
            audit_metadata={"path": _redact_path(normalized), "mode": request.access_mode.value},
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def _is_within_allowed_dirs(self, normalized_path: str) -> bool:
        if not self._policy.allowed_directories:
            return True
        for allowed_dir in self._policy.allowed_directories:
            norm_allowed = os.path.normpath(os.path.abspath(allowed_dir))
            if normalized_path.startswith(norm_allowed + os.sep) or normalized_path == norm_allowed:
                return True
        return False

    def __repr__(self) -> str:
        return "PathValidator()"


def _redact_path(path: str) -> str:
    parts = path.replace("\\", "/").split("/")
    if len(parts) <= 2:
        return "***"
    return "/".join(["***"] + parts[-2:])
```

---

## File: modules/security/src/capabilities_sensitive_redactor.py

```python
"""Capabilities: Sensitive redactor — FR-SEC-004.

Detects and redacts sensitive values from text and structured data.
Implements RedactSensitiveProtocol.
"""

from __future__ import annotations

import re

from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol
from modules.shared.src.security.taxonomy_security_vo import RedactionVO

_DEFAULT_PATTERNS: tuple[str, ...] = (
    r"(?i)(password|passwd|secret|token|api[_-]?key|access[_-]?key|private[_-]?key)\s*[=:]\s*\S+",
    r"(?i)(bearer|basic)\s+[A-Za-z0-9\-._~+/]+=*",
    r"(?i)sk-[A-Za-z0-9]{20,}",
    r"(?i)ghp_[A-Za-z0-9]{36}",
    r"(?i)AKIA[0-9A-Z]{16}",
)


class SensitiveRedactor(RedactSensitiveProtocol):
    """Detects and redacts sensitive values from text using pattern and key-based detection."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        extra_patterns: tuple[str, ...] = (),
        extra_key_names: tuple[str, ...] = (),
        debug_mode: bool = False,
    ) -> None:
        self._patterns = _DEFAULT_PATTERNS + extra_patterns
        self._key_names = extra_key_names
        self._debug_mode = debug_mode

    # ─── Block 2: Public Contract  ────────────────────────
    async def redact(self, request: RedactionVO) -> RedactionVO:
        """Detect and redact sensitive values from text."""
        try:
            text = request.text
            redacted_count = 0

            patterns = self._patterns + request.patterns
            for pattern in patterns:
                text, count = re.subn(pattern, "[REDACTED]", text)
                redacted_count += count

            all_keys = self._key_names + request.key_names
            for key in all_keys:
                pattern = rf"(?i)({re.escape(key)})\s*[=:]\s*\S+"
                text, count = re.subn(pattern, r"\1=[REDACTED]", text)
                redacted_count += count

            if len(text) > 10_000:
                text = text[:10_000] + "\n[TRUNCATED]"

            return RedactionVO(
                text=request.text,
                sensitivity_level=request.sensitivity_level,
                patterns=request.patterns,
                key_names=request.key_names,
                redacted_text=text,
                redacted_count=redacted_count,
            )
        except Exception as exc:
            return RedactionVO(
                text=request.text,
                sensitivity_level=request.sensitivity_level,
                redacted_text="[REDACTION_FAILED]",
                failed=True,
                failure_reason=str(exc),
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    def __repr__(self) -> str:
        return "SensitiveRedactor()"
```

---

## File: modules/security/src/root_security_container.py

```python
"""Root: Security feature composition container.

Wires concrete implementations to contracts and bootstraps the security module:
  Capabilities (5 individual) → Agent Orchestrator → (exposed as SecurityOperateAggregate)

This file is the composition root for the security feature. It instantiates
concrete implementations, connects them to protocol/aggregate contracts,
and provides the assembled aggregate for dependency injection by callers.

Structure:
  1. Constants & imports
  2. SecurityContainer — wires 5 individual capabilities to aggregate
"""

import logging

from modules.shared.src.security.contract_security_operate_aggregate import SecurityOperateAggregate
from modules.shared.src.security.taxonomy_security_vo import SecurityPolicyVO

from .agent_security_orchestrator import SecurityOrchestrator
from .capabilities_archive_guard import ArchiveGuard
from .capabilities_audit_emitter import AuditEmitter
from .capabilities_code_validator import CodeValidator
from .capabilities_path_validator import PathValidator
from .capabilities_sensitive_redactor import SensitiveRedactor

logger = logging.getLogger("BlenderMCPServer")


class SecurityContainer:
    """Dependency injection container for the security feature module.

    Wires 5 individual capability protocols to their executors,
    then assembles them into the SecurityOrchestrator aggregate facade.

    Capabilities → Agent Orchestrator → (exposed as SecurityOperateAggregate)
    """

    def __init__(self, policy: SecurityPolicyVO | None = None) -> None:
        """Initialize the security feature container.

        Args:
            policy: Optional security policy configuration.
        """
        self._policy = policy or SecurityPolicyVO()
        self._orchestrator: SecurityOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire 5 individual capability executors to the orchestrator.

        Creates the capability → orchestrator chain for each FR:
          PathValidator, ArchiveGuard, CodeValidator, SensitiveRedactor, AuditEmitter
          All 5 → SecurityOrchestrator (implements SecurityOperateAggregate)
        """
        if self._wired:
            return

        logger.info("Wiring security feature module (5 individual capabilities)")

        # Capabilities layer — each implements its own protocol
        validate_path_cap = PathValidator(policy=self._policy)
        validate_archive_cap = ArchiveGuard()
        validate_code_cap = CodeValidator(policy=self._policy)
        redact_cap = SensitiveRedactor(debug_mode=self._policy.redaction_debug_mode)
        emit_audit_cap = AuditEmitter()

        # Agent layer — implements aggregate, depends on all 5 protocols
        self._orchestrator = SecurityOrchestrator(
            validate_path_cap=validate_path_cap,
            validate_archive_cap=validate_archive_cap,
            validate_code_cap=validate_code_cap,
            redact_cap=redact_cap,
            emit_audit_cap=emit_audit_cap,
        )

        self._wired = True
        logger.info("Security feature module wired successfully (5 capabilities)")

    @property
    def aggregate(self) -> SecurityOperateAggregate:
        """Return the assembled SecurityOperateAggregate facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired:
            raise RuntimeError("SecurityContainer not wired — call wire() first")
        if self._orchestrator is None:
            raise RuntimeError("Orchestrator not initialized — call wire() first")
        return self._orchestrator


def create_security_feature(
    policy: SecurityPolicyVO | None = None,
) -> SecurityOperateAggregate:
    """Factory function to create and wire the security feature module.

    Convenience function for top-level entry points that need the aggregate.

    Args:
        policy: Optional security policy configuration.

    Returns:
        The assembled SecurityOperateAggregate ready for use.
    """
    container = SecurityContainer(policy)
    container.wire()
    return container.aggregate
```

---

## File: modules/shared/src/security/__init__.py

```python
"""Security domain — taxonomy types and contracts.

Provides Value Objects, Entities, Events, Errors, Constants,
5 individual Protocol interfaces, and Aggregate facade for all 5 security operations per the Security FRD.
"""

from . import (
    taxonomy_security_constant,
    taxonomy_security_error,
    taxonomy_security_event,
    taxonomy_security_vo,
)
from .contract_emit_audit_protocol import EmitAuditProtocol
from .contract_extract_archive_protocol import ExtractArchiveProtocol
from .contract_redact_sensitive_protocol import RedactSensitiveProtocol
from .contract_security_operate_aggregate import SecurityOperateAggregate
from .contract_validate_code_protocol import ValidateCodeProtocol
from .contract_validate_path_protocol import ValidatePathProtocol

__all__ = [
    "EmitAuditProtocol",
    "ExtractArchiveProtocol",
    "RedactSensitiveProtocol",
    "SecurityOperateAggregate",
    "ValidateCodeProtocol",
    "ValidatePathProtocol",
    "taxonomy_security_constant",
    "taxonomy_security_error",
    "taxonomy_security_event",
    "taxonomy_security_vo",
]
```

---

## File: modules/shared/src/security/contract_emit_audit_protocol.py

```python
"""Security domain contract: emit audit protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-005: Emit Security Audit Events.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import SecurityAuditEventVO


class EmitAuditProtocol(ABC):
    """Protocol interface for emitting structured security audit events."""

    @abstractmethod
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """Emit a structured security audit event for violations and policy activity."""
        ...
```

---

## File: modules/shared/src/security/contract_extract_archive_protocol.py

```python
"""Security domain contract: extract archive protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-002: Safely Extract Archive.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import ArchiveExtractionVO


class ExtractArchiveProtocol(ABC):
    """Protocol interface for validating archive extraction safety."""

    @abstractmethod
    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """Validate and guard archive extraction against safety policy."""
        ...
```

---

## File: modules/shared/src/security/contract_redact_sensitive_protocol.py

```python
"""Security domain contract: redact sensitive protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-004: Redact Sensitive Values.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import RedactionVO


class RedactSensitiveProtocol(ABC):
    """Protocol interface for detecting and redacting sensitive values."""

    @abstractmethod
    async def redact(self, request: RedactionVO) -> RedactionVO:
        """Detect and redact sensitive values from text or structured data."""
        ...
```

---

## File: modules/shared/src/security/contract_security_operate_aggregate.py

```python
"""Security domain contract: security operate aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for all 5 security operations: path, archive, code, redaction, audit.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import (
    ArchiveExtractionVO,
    CodeValidationVO,
    PathValidationVO,
    RedactionVO,
    SecurityAuditEventVO,
)


class SecurityOperateAggregate(ABC):
    """Aggregate facade for all security operations.

    The Agent orchestrator implements this interface.
    Surface layers call through this aggregate.
    """

    @abstractmethod
    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """FR-SEC-001: Validate filesystem path access."""
        ...

    @abstractmethod
    async def validate_extraction(self, request: ArchiveExtractionVO) -> ArchiveExtractionVO:
        """FR-SEC-002: Validate archive extraction safety."""
        ...

    @abstractmethod
    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """FR-SEC-003: Validate untrusted code before execution."""
        ...

    @abstractmethod
    async def redact(self, request: RedactionVO) -> RedactionVO:
        """FR-SEC-004: Detect and redact sensitive values."""
        ...

    @abstractmethod
    async def emit_audit(self, event: SecurityAuditEventVO) -> SecurityAuditEventVO:
        """FR-SEC-005: Emit structured security audit event."""
        ...
```

---

## File: modules/shared/src/security/contract_validate_code_protocol.py

```python
"""Security domain contract: validate code protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-003: Validate Untrusted Code.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import CodeValidationVO


class ValidateCodeProtocol(ABC):
    """Protocol interface for validating untrusted code before execution."""

    @abstractmethod
    async def validate_code(self, request: CodeValidationVO) -> CodeValidationVO:
        """Validate untrusted code using static analysis and blocked construct policy."""
        ...
```

---

## File: modules/shared/src/security/contract_validate_path_protocol.py

```python
"""Security domain contract: validate path protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-SEC-001: Validate File Path Access.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_security_vo import PathValidationVO


class ValidatePathProtocol(ABC):
    """Protocol interface for validating filesystem path access."""

    @abstractmethod
    async def validate_path(self, request: PathValidationVO) -> PathValidationVO:
        """Validate whether a filesystem path is allowed for the requested access mode."""
        ...
```

---

## File: modules/shared/src/security/taxonomy_security_vo.py

```python
"""Security domain — Value Objects for path validation, archive safety, code validation, redaction, and audit.

Frozen dataclasses with explicit types. All VOs are immutable.
Input and output fields live in a single VO per concept.
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field as dc_field
from enum import Enum

# ============================================================
# Access Mode
# ============================================================

class AccessMode(str, Enum):
    """File access mode for path validation."""
    READ = "read"
    WRITE = "write"
    CREATE = "create"
    DELETE = "delete"
    EXTRACT = "extract"


# ============================================================
# Path Validation (FR-SEC-001)
# ============================================================

@dataclass(frozen=True)
class PathValidationVO:
    """Unified path validation — input and output in one VO.

    Caller sets target_path, access_mode, base_directory, operation_context.
    Callee sets allowed, canonical_path, denial_reason, audit_metadata.
    """
    # Input
    target_path: str = ""
    access_mode: AccessMode = AccessMode.READ
    base_directory: str | None = None
    operation_context: str | None = None
    # Output
    allowed: bool = False
    canonical_path: str | None = None
    denial_reason: str | None = None
    audit_metadata: dict = dc_field(default_factory=dict)


# ============================================================
# Archive Extraction (FR-SEC-002)
# ============================================================

@dataclass(frozen=True)
class ArchiveEntryVO:
    """Metadata for a single archive entry."""
    entry_path: str
    is_directory: bool = False
    is_symbolic_link: bool = False
    is_hard_link: bool = False
    compressed_size: int = 0
    uncompressed_size: int = 0


@dataclass(frozen=True)
class ArchiveExtractionOptionsVO:
    """Options controlling archive extraction safety."""
    max_depth: int = 5
    max_total_size: int = 104_857_600  # 100 MB
    max_entry_size: int = 10_485_760  # 10 MB
    max_entry_count: int = 1_000
    allow_symbolic_links: bool = False
    allow_hard_links: bool = False


@dataclass(frozen=True)
class RejectedEntryVO:
    """A rejected archive entry with reason."""
    entry_path: str
    reason: str


@dataclass(frozen=True)
class ArchiveExtractionVO:
    """Unified archive extraction — input and output in one VO.

    Caller sets destination_directory, entries, options.
    Callee sets allowed, safe_destination, rejected_entries, warnings, audit_metadata.
    """
    # Input
    destination_directory: str = ""
    entries: tuple[ArchiveEntryVO, ...] = dc_field(default_factory=tuple)
    options: ArchiveExtractionOptionsVO = dc_field(default_factory=ArchiveExtractionOptionsVO)
    # Output
    allowed: bool = False
    safe_destination: str | None = None
    rejected_entries: tuple[RejectedEntryVO, ...] = dc_field(default_factory=tuple)
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    audit_metadata: dict = dc_field(default_factory=dict)


# ============================================================
# Code Validation (FR-SEC-003)
# ============================================================

@dataclass(frozen=True)
class CodeViolationVO:
    """A single code validation violation."""
    category: str
    description: str
    location_hint: str | None = None


@dataclass(frozen=True)
class CodeValidationVO:
    """Unified code validation — input and output in one VO.

    Caller sets code_text, max_code_size, strict_mode, execution_context.
    Callee sets allowed, violations, redacted_metadata, audit_metadata.
    """
    # Input
    code_text: str = ""
    max_code_size: int = 1_048_576  # 1 MB
    strict_mode: bool = True
    execution_context: str | None = None
    # Output
    allowed: bool = False
    violations: tuple[CodeViolationVO, ...] = dc_field(default_factory=tuple)
    redacted_metadata: dict = dc_field(default_factory=dict)
    audit_metadata: dict = dc_field(default_factory=dict)


# ============================================================
# Redaction (FR-SEC-004)
# ============================================================

class SensitivityLevel(str, Enum):
    """Sensitivity level for redaction."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RedactionVO:
    """Unified redaction — input and output in one VO.

    Caller sets text, sensitivity_level, patterns, key_names.
    Callee sets redacted_text, redacted_count, failed, failure_reason.
    """
    # Input
    text: str = ""
    sensitivity_level: SensitivityLevel = SensitivityLevel.HIGH
    patterns: tuple[str, ...] = dc_field(default_factory=tuple)
    key_names: tuple[str, ...] = dc_field(default_factory=tuple)
    # Output
    redacted_text: str = ""
    redacted_count: int = 0
    failed: bool = False
    failure_reason: str | None = None


# ============================================================
# Audit Events (FR-SEC-005)
# ============================================================

class AuditSeverity(str, Enum):
    """Audit event severity level."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ViolationCategory(str, Enum):
    """Security violation category."""
    PATH_TRAVERSAL = "path_traversal"
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    UNSAFE_ARCHIVE_ENTRY = "unsafe_archive_entry"
    CODE_VIOLATION = "code_violation"
    REDACTION_FAILURE = "redaction_failure"
    PERMISSION_DENIED = "permission_denied"
    POLICY_OVERRIDE = "policy_override"


@dataclass(frozen=True)
class SecurityAuditEventVO:
    """Unified security audit event — input context and emitted event in one VO.

    Caller sets violation_category, operation_type, source_feature, severity, etc.
    Callee sets event_id, timestamp, policy_mode.
    """
    # Input (context)
    violation_category: ViolationCategory = ViolationCategory.PATH_TRAVERSAL
    operation_type: str = ""
    source_feature: str = ""
    target_metadata: dict = dc_field(default_factory=dict)
    severity: AuditSeverity = AuditSeverity.WARNING
    correlation_id: str | None = None
    redacted_reason: str | None = None
    # Output (emitted event)
    event_id: str = ""
    timestamp: float = 0.0
    policy_mode: str = "strict"


# ============================================================
# Security Policy Config
# ============================================================

@dataclass(frozen=True)
class SecurityPolicyVO:
    """Security policy configuration."""
    allowed_directories: tuple[str, ...] = ()
    archive_max_depth: int = 5
    archive_max_total_size: int = 104_857_600
    archive_max_entry_count: int = 1_000
    archive_allow_symbolic_links: bool = False
    code_validation_enabled: bool = True
    blocked_code_constructs: tuple[str, ...] = dc_field(default_factory=tuple)
    max_code_size: int = 1_048_576
    redaction_patterns: tuple[str, ...] = dc_field(default_factory=tuple)
    redaction_debug_mode: bool = False
    security_policy_mode: str = "strict"
```

---

## File: pyproject.toml

```toml
[project]
name = "blender-arwaky"
version = "1.7.0"
description = "Blender integration through the Model Context Protocol"
readme = "README.md"
requires-python = ">=3.10"
authors = [
    {name = "rakaarwaky", email = "arwaky90@gmail.com"}
]
license = {text = "MIT"}
classifiers = [
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
]
dependencies = [
    "mcp[cli]>=1.3.0",
    "tomli>=2.0.0",
    "python-dotenv>=1.0.0",
    "pyyaml>=6.0.3",
    "pillow>=12.2.0",
]

[project.optional-dependencies]
test = [
    "pytest>=9.0.3",
    "pytest-asyncio>=1.3.0",
    "pytest-cov>=7.1.0",
    "pytest-mock>=3.15.1",
    "requests>=2.31.0",  # Used by blender_mcp_addon modules (bundled with Blender at runtime)
]
lint = [
    "ruff>=0.11.0",
    "mypy>=1.15.0",
    "bandit>=1.8.0",
]
dev = [
    "blender-arwaky[test]",
    "blender-arwaky[lint]",
]

[dependency-groups]
test = ["blender-arwaky[test]"]
lint = ["blender-arwaky[lint]"]
dev = ["blender-arwaky[dev]"]

[project.scripts]
blender-arwaky = "modules.cli.cli_main:main"
blender-mcp = "modules.root_mcp_entry:main"

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
where = ["."]
include = ["modules*", "blender_mcp_addon*"]
exclude = ["*.tests", "tests*", "log*", "plugin*"]

[project.urls]
"Homepage" = "https://github.com/rakaarwaky/blender-arwaky"
"Bug Tracker" = "https://github.com/rakaarwaky/blender-arwaky/issues"

[tool.ruff]
line-length = 120
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "B", "SIM", "ARG", "RUF100"]
ignore = ["E501"]

# Blender API contracts: class names (N801), argument names (N803/ARG001/ARG002),
# and Hunyuan API field names (N806) are dictated by external APIs.
[tool.ruff.lint.per-file-ignores]
"blender_mcp_addon/__init__.py"   = ["N801"]  # bl_info keys
"blender_mcp_addon/operators.py"  = ["N801"]  # Operator.bl_idname convention
"blender_mcp_addon/ui.py"         = ["N801", "ARG002"]  # Panel/AddonPreferences + context arg required by bpy
"blender_mcp_addon/polyhaven.py"  = ["B007"]  # `dirs` is required by os.walk contract
"blender_mcp_addon/sketchfab.py"  = ["B007"]  # `dirs` is required by os.walk contract
"blender_mcp_addon/properties.py" = []  # noqa already used inline

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

# ─── Pytest configuration ───────────────────────────────────────────────────
[tool.pytest.ini_options]
minversion = "9.0"
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--cov=src",
    "--cov=modules",
    "--cov=blender_mcp_addon",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml:coverage.xml",
]
markers = [
    "unit: Pure logic tests, no external dependencies",
    "integration: Layer interaction tests with real DI, mocked I/O",
    "functional: End-to-end command flows within project boundaries",
    "addon: Blender addon tests using bpy mock (tests/addon/)",
    "slow: Tests that take >1s to run",
    "asyncio: Async test marker (pytest-asyncio)",
]
asyncio_mode = "auto"

# ─── Coverage configuration ────────────────────────────────────────────────
[tool.coverage.run]
source = ["src", "modules", "blender_mcp_addon"]
branch = true
parallel = true
omit = [
    "*/tests/*",
    "*/__pycache__/*",
    "*/.*",
    "*/dist/*",
    "*/build/*",
    # Exclude external-API clients from global threshold.
    # They require recorded HTTP fixtures (vcrpy) to test meaningfully.
    "blender_mcp_addon/polyhaven.py",
    "blender_mcp_addon/sketchfab.py",
]

[tool.coverage.report]
precision = 2
show_missing = true
skip_covered = false
# Realistic current threshold — increase as tests mature.
# Excludes external-API modules (polyhaven, sketchfab)
# that require live network mocking to test.
fail_under = 60
exclude_lines = [
    "pragma: no cover",
    "raise NotImplementedError",
    "if TYPE_CHECKING:",
    "if __name__ == .__main__.:",
    "\\.\\.\\.",
    "pass",
]
exclude_also = [
    "raise ImportError",
    "except ImportError",
    "@overload",
    "@abstractmethod",
]

```

---

## File: README.md

````markdown
# BlenderArwaky

> Connect Blender to AI agents through the Model Context Protocol.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Blender 3.0+](https://img.shields.io/badge/Blender-3.0%2B-orange.svg)](https://www.blender.org/)

BlenderArwaky bridges [Blender 3D](https://www.blender.org/) with any MCP-compatible client — Claude Desktop, Cursor, Continue.dev, or custom agents. Control scenes, import assets, render, and execute Blender Python through 4 universal MCP tools.

## Prerequisites

- **Blender 3.0+** (tested on 5.1)
- **Python 3.10+**

## Quick Start

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync
```

### Install Blender Addon

1. Blender → Edit → Preferences → Add-ons
2. Install `blender_mcp_addon/` directory
3. Enable **"Interface: Blender Arwaky"**

### Start MCP Server

```bash
uv run blender-mcp
```

### Configure MCP Client

```json
{
  "mcpServers": {
    "blender-arwaky": {
      "command": "uv",
      "args": ["--directory", "/path/to/blender-arwaky", "run", "blender-mcp"]
    }
  }
}
```

## Architecture

AES 7-layer architecture with full dependency inversion:

```
taxonomy → contract → capabilities → agent → surface → entry
                ↑
            infrastructure
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for full specification.

## Project Structure

```
modules/
├── shared/         ← Taxonomy + Contracts (FRD: modules/shared/FRD.md)
├── object/         ← Object operations (FRD: modules/object/FRD.md)
├── scene/          ← Scene management (FRD: modules/scene/FRD.md)
├── render/         ← Rendering + assets (FRD: modules/render/FRD.md)
├── telemetry/      ← Usage analytics (FRD: modules/telemetry/FRD.md)
├── job/            ← Job tracking (FRD: modules/job/FRD.md)
├── cli/            ← Standalone CLI (FRD: modules/cli/FRD.md)
├── root_mcp_entry.py
└── root_cli_entry.py
```

## Available Scripts

| Command | Description |
|---------|-------------|
| `uv run blender-mcp` | Start MCP server |
| `uv run blender-arwaky` | Run standalone CLI |
| `uv run pytest` | Run tests (455+) |
| `uv run pytest -m unit` | Unit tests only |
| `uv run ruff check .` | Lint code |
| `lint-arwaky-cli scan .` | AES architecture compliance |

## Configuration

```yaml
blender:
  executable_path: "/path/to/blender"
  host: "localhost"
  port: 9876

server:
  transport: "stdio"
  log_dir: "log"
```

| Env Var | Description |
|---------|-------------|
| `BLENDERMCP_CONFIG_PATH` | Override config.yaml path |
| `BLENDERMCP_BLENDER.HOST` | Override Blender host |
| `BLENDERMCP_BLENDER.PORT` | Override Blender port |
| `BLENDERMCP_CONFIG_V2` | Enable v1.7.0 new enforcement (schema validation, 1 MiB size limit, `\` path escaping, strict ConfigTypeError, runtime overrides). Default OFF; flips ON in v1.8.0. |

## Testing

```bash
uv run pytest              # Full suite
uv run pytest -m unit      # Unit tests
uv run pytest -m integration  # Integration tests
```

## Documentation

- [PRD.md](PRD.md) — Product requirements (stakeholders)
- [ARCHITECTURE.md](ARCHITECTURE.md) — System architecture
- [SKILL.md](SKILL.md) — Agent usage reference
- [AGENT.md](AGENT.md) — Developer reference
- [TEST.md](TEST.md) — Testing guide
- [modules/\*/FRD.md](modules/shared/FRD.md) — Feature specs (engineers)

## License

[MIT License](LICENSE) — Originally by Siddharth Ahuja, extended by Raka Arwaky.
````

---

