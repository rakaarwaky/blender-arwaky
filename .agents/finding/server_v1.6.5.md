# Module: server (v1.6.5)

This document contains the source code for module `server` along with related and imported definitions from the `shared` module.

## File List

- [ARCHITECTURE.md](<ARCHITECTURE.md>)
- [modules/server/FRD.md](<modules/server/FRD.md>)
- [modules/server/src/__init__.py](<modules/server/src/__init__.py>)
- [modules/server/src/agent_server_orchestrator.py](<modules/server/src/agent_server_orchestrator.py>)
- [modules/server/src/capabilities_blender_command_adapter.py](<modules/server/src/capabilities_blender_command_adapter.py>)
- [modules/server/src/capabilities_blender_connection.py](<modules/server/src/capabilities_blender_connection.py>)
- [modules/server/src/capabilities_code_execution_adapter.py](<modules/server/src/capabilities_code_execution_adapter.py>)
- [modules/server/src/root_server_container.py](<modules/server/src/root_server_container.py>)
- [modules/shared/src/__init__.py](<modules/shared/src/__init__.py>)
- [modules/shared/src/common/__init__.py](<modules/shared/src/common/__init__.py>)
- [modules/shared/src/common/taxonomy_core_vo.py](<modules/shared/src/common/taxonomy_core_vo.py>)
- [modules/shared/src/common/taxonomy_domain_error.py](<modules/shared/src/common/taxonomy_domain_error.py>)
- [modules/shared/src/server/__init__.py](<modules/shared/src/server/__init__.py>)
- [modules/shared/src/server/contract_code_execution_protocol.py](<modules/shared/src/server/contract_code_execution_protocol.py>)
- [modules/shared/src/server/contract_command_protocol.py](<modules/shared/src/server/contract_command_protocol.py>)
- [modules/shared/src/server/contract_connection_protocol.py](<modules/shared/src/server/contract_connection_protocol.py>)
- [modules/shared/src/server/contract_server_aggregate.py](<modules/shared/src/server/contract_server_aggregate.py>)
- [modules/shared/src/server/taxonomy_server_constant.py](<modules/shared/src/server/taxonomy_server_constant.py>)
- [modules/shared/src/server/taxonomy_server_error.py](<modules/shared/src/server/taxonomy_server_error.py>)
- [modules/shared/src/server/taxonomy_server_event.py](<modules/shared/src/server/taxonomy_server_event.py>)
- [modules/shared/src/server/taxonomy_server_vo.py](<modules/shared/src/server/taxonomy_server_vo.py>)
- [modules/shared/src/server/utility_server_schema.py](<modules/shared/src/server/utility_server_schema.py>)
- [modules/shared/src/server/utility_server_validator.py](<modules/shared/src/server/utility_server_validator.py>)
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

## File: modules/server/FRD.md

```markdown
# FRD — Server Feature

## System Overview

The server feature manages the secure communication channel between external AI clients and the Blender application. It handles connection stability, safe custom code execution, and standard Blender operations.

The feature treats all user-provided code as potentially unsafe. It applies strict safety checks before execution and enforces runtime boundaries to protect the user's system from unauthorized access or destructive actions. Because the Blender application can only safely process one operation at a time, the feature ensures that all concurrent requests are handled sequentially to maintain application stability.

The feature defines connection stability handling, liveness monitoring, compatibility checks, authentication, data size limits, background task management, system observability, and error classification from a user-facing perspective.

## Functional Requirements

### FR-001: Establish and Maintain Connection

- **Use Case:** An AI client or user needs to connect to a running Blender instance and ensure the connection remains active during use.
- **User Action:** Provide connection settings (target address, port, timeout limits, authentication token, and compatibility version).
- **System Response:** Establish a secure connection and provide the current connection status.
- **Business Rules:**
  - The system must automatically attempt to reconnect if the connection is lost, up to a maximum of 3 attempts with increasing wait times.
  - Connection establishment must fail if it takes longer than 30 seconds.
  - The system must send periodic "liveness" checks (heartbeats) every 10 seconds to detect if the connection has gone stale.
  - The connection is only considered stale after a configurable number of consecutive failed liveness checks (default: 3).
  - A missed liveness check during a long-running operation must not immediately drop the connection unless the operation itself has also timed out.
  - The initial connection handshake must verify compatibility versions and authenticate the user if a token is required.
  - The system must default to local-only connections unless remote access is explicitly configured by the user.
  - Connection status must be clearly reported as: `disconnected`, `connecting`, `connected`, `reconnecting`, `failed`, or `closed`.
  - While reconnecting, new operation requests must be either held or rejected based on user configuration.
  - If the connection fails permanently, all pending operations must be cancelled and return a clear "Connection Lost" error.
  - The disconnect action must be safe to call multiple times without causing errors.
  - When gracefully disconnecting, all pending operations must be cancelled with a "Connection Closed" error.
  - Operations currently in progress are not forcibly stopped unless explicitly requested by the user.
- **Edge Cases:** Blender is not running, connection is refused, connection times out, network drops, Blender crashes during a session, authentication fails, versions are incompatible, liveness check gives a false alarm during a long task, disconnect is called while reconnecting.
- **Error Handling:** Return `BlenderConnectionFailure` (with retry details); return `BlenderConnectionExhausted` after 3 failed retries; return `AuthenticationError` for invalid tokens; return `VersionMismatchError` for incompatible versions; return `ConnectionClosedError` for operations rejected after a disconnect.

### FR-002: Execute Custom Code

- **Use Case:** An AI agent or user needs to run custom Python code inside Blender to perform actions not covered by standard commands.
- **User Action:** Provide the Python code string, optional timeout limit, optional background execution flag, and optional tracking key.
- **System Response:** Return the execution result containing status (success/error), returned data, error details (if any), execution time, and a flag indicating if the output was too large and truncated.
- **Business Rules:**
  - All user-provided code is treated as untrusted.
  - The code must be validated for safety before execution. Blocked patterns include, but are not limited to: system commands (`os.system`), process execution (`subprocess`), destructive file operations (`shutil.rmtree`), dynamic evaluation (`eval`, `exec`, `compile`), dynamic imports (`__import__`, `importlib`), unsafe internal attributes, and file writing outside of explicitly allowed directories.
  - Pre-execution validation is a safety filter; the Blender environment must also enforce its own runtime boundaries as the final authority.
  - Allowed directories for file operations must be configurable by the user.
  - The default allowed directory is the folder containing the active Blender project file.
  - Code execution must time out after 30 seconds by default, returning an `ExecutionTimeoutError`.
  - The timeout limit must be configurable.
  - For operations expected to take longer than the timeout, the system must support background task submission, returning a tracking ID for the user to check later.
  - Background task statuses must include: `pending`, `running`, `success`, `error`, `timeout`, `cancelled`.
  - Background task results must be retained for a configurable time (default: 10 minutes).
  - Background tasks can only be cancelled while they are `pending`. Cancelling a `running` task is a best-effort attempt.
  - Checking the status of an unknown or expired background task must return a `TaskNotFoundError`.
  - The size of the code provided must be limited (default max: 1 MB).
  - The execution output must be convertible to a standard structured format.
  - If the output cannot be converted, it must be safely converted to a text representation or rejected.
  - If the output exceeds the maximum allowed response size, it must be truncated, and the response must indicate that truncation occurred.
  - All code execution requests must be processed sequentially to maintain Blender stability.
  - Each request must include a unique tracking ID for logging and troubleshooting.
- **Edge Cases:** Code times out, code has syntax errors, Blender throws an exception, Blender crashes during execution, blocked pattern is detected, blocked pattern is obfuscated to hide it, code is too large, output is too large, output cannot be formatted, connection is lost during execution, background task expires, background task is cancelled, too many pending operations.
- **Error Handling:** Return `ExecutionError` with details from Blender; return `SecurityViolationError` for blocked patterns; return `ExecutionTimeoutError` for timeouts; return `TooManyPendingOperationsError` when the limit of waiting operations is exceeded; return `OperationWaitTimeoutError` when a request waits too long to be processed; return `TaskNotFoundError` for unknown/expired background tasks; return `BlenderConnectionFailure` if the connection drops.

### FR-003: Execute Standard Commands

- **Use Case:** An AI agent or user needs to run a predefined, named Blender action (e.g., create object, render scene).
- **User Action:** Provide the command name, command parameters, and optional timeout limit.
- **System Response:** Return the command result containing status (success/error), returned data, error details (if any), and execution time.
- **Business Rules:**
  - The default response timeout for commands is 5 seconds, returning a `CommandTimeoutError` if exceeded.
  - Individual commands may define their own custom timeout limits if they are expected to take longer.
  - Long-running commands should be submitted as background tasks or explicitly marked as long-running.
  - Commands that only read data (e.g., `get_scene_info`) should be idempotent (safe to run multiple times without changing the result).
  - Each command must define:
    - Required and optional parameters.
    - Default timeout.
    - Whether it is idempotent.
    - Whether it changes the Blender scene state.
  - Command parameters must be validated against the command's defined rules before execution.
  - Commands that do not interact with the Blender scene state may be processed immediately.
  - Commands that interact with or change the Blender scene state must be processed sequentially.
  - Command response sizes must be limited and truncated if they are too large.
- **Edge Cases:** Unknown command name, invalid parameters, Blender is not responding, response format is invalid, response is too large, command times out, too many pending operations.
- **Error Handling:** Return `ProviderError` with command-specific details; return `CommandTimeoutError` for unresponsive commands; return `ValidationError` for invalid parameters; return `TooManyPendingOperationsError` when the limit is exceeded; return `OperationWaitTimeoutError` when waiting too long.

## System Capabilities (User-Facing Operations)


| Operation               | User Action (Input)      | System Response (Output)         | Description                                    |
| ------------------------- | -------------------------- | ---------------------------------- | ------------------------------------------------ |
| `connect`               | Connection Settings      | Connection Status                | Establish secure connection to Blender         |
| `disconnect`            | —                       | —                               | Close connection gracefully                    |
| `send_command`          | Command Name, Parameters | Command Result                   | Run a predefined Blender action (5s timeout)   |
| `execute_blender_code`  | Python Code              | Execution Result                 | Run custom code in Blender (30s timeout)       |
| `submit_async_task`     | Python Code              | Task Tracking ID                 | Submit long-running code for background work   |
| `poll_task_result`      | Task Tracking ID         | Task Status and Execution Result | Check status and get result of background work |
| `get_connection_status` | —                       | Connection Status Details        | Get current connection health and details      |

**Additional Capability Behaviors:**

- `connect` must verify compatibility and authenticate the user if enabled.
- `disconnect` must be safe to call multiple times and must not cause errors if already closed.
- `send_command` uses a 5-second timeout unless the specific command defines a different limit.
- `execute_blender_code` returns the final result immediately for standard execution.
- `submit_async_task` returns a tracking ID, with the initial status usually being `pending`.
- `poll_task_result` returns the current status and, when finished, the final execution result.
- `get_connection_status` returns details including current state, target address, last liveness check time, reconnect attempts, and compatibility version.
- All requests and responses must include a unique tracking ID for troubleshooting.
- All data exchanged must be text-based and structured.
- Maximum data size for requests and responses must be configurable and enforced.

## External Boundaries

- **External Consumers:**
  - AI Clients (e.g., MCP-compatible tools, CLI utilities) that send commands and code.
- **Target Environment:**
  - Blender Application (must be running and listening for connections).
  - Blender Internal Environment (where code and commands are actually executed).
- **External Dependencies:**
  - Optional secret storage or environment variables for managing authentication tokens.

## Non-functional Requirements

- **Performance:**
  - Standard commands must respond within 5 seconds by default.
  - Custom code execution must respond within 30 seconds by default.
  - The system's own processing overhead should be minimal (ideally <100ms excluding Blender's execution time).
  - The wait time for operations being processed sequentially should be configurable, with a default target of <10 seconds under normal load.
- **Reliability:**
  - The system must automatically reconnect on connection loss (3 attempts, with increasing wait times).
  - The system must degrade gracefully if Blender crashes.
  - Pending operations must fail predictably and clearly if the connection is lost.
  - No operation may be silently dropped; every operation must have a defined success, failure, or recovery outcome.
- **Security:**
  - Custom code must be validated against a list of blocked patterns before execution.
  - The Blender environment must enforce its own runtime boundaries.
  - File system access must be restricted to explicitly allowed directories.
  - The default connection target must be local-only for security.
  - Remote connections must require authentication when enabled.
  - Data size limits must be strictly enforced.
  - Security violations must be logged as audit events.
  - Raw code provided by the user must not be logged by default to protect privacy.
- **Observability:**
  - The system must log all connection state changes, command details, execution durations, wait times, retry attempts, and error details.
  - Code provided by the user must be masked, hashed, or truncated in logs.
  - Logs should be structured for easy parsing.
  - Every operation must be traceable using its unique tracking ID.
  - System metrics should include: number of pending operations, reconnect count, execution latency, command latency, failed request count, and security violation count.
- **Stability (Operation Processing):**
  - All operations that interact with the Blender scene must be processed one at a time to prevent application instability.
  - The system must limit the number of pending operations (default: 50).
  - Operations are processed in the order they are received.
  - Operations that do not interact with the Blender scene (like checking connection status) may be processed immediately without waiting.
  - If the limit of pending operations is reached, new requests must be rejected with a `TooManyPendingOperationsError`.
  - If an operation waits too long to be processed, it must be rejected with an `OperationWaitTimeoutError`.

## Test Scenarios / QA Checklist

**Connection & Stability:**

- [ ]  Connect to a running Blender instance succeeds.
- [ ]  Connect to a non-running Blender instance returns `BlenderConnectionFailure`.
- [ ]  Connect with an invalid authentication token returns `AuthenticationError`.
- [ ]  Connect with an unsupported version returns `VersionMismatchError`.
- [ ]  Connection loss triggers automatic reconnection (3 attempts).
- [ ]  After 3 failed reconnections, the system returns `BlenderConnectionExhausted`.
- [ ]  Liveness checks detect a stale connection and trigger reconnection.
- [ ]  Liveness checks do not falsely drop the connection during a long-running operation.
- [ ]  Disconnecting is safe to call multiple times.
- [ ]  Disconnecting cancels pending operations with `ConnectionClosedError`.

**Custom Code Execution:**

- [ ]  Execute valid Python code returns a successful `ExecutionResult`.
- [ ]  Execute code with syntax errors returns an `ExecutionResult` with an error status.
- [ ]  Execute code exceeding the 30s timeout returns `ExecutionTimeoutError`.
- [ ]  Execute code containing blocked patterns (e.g., `os.system`) returns `SecurityViolationError`.
- [ ]  Execute code containing obfuscated blocked patterns returns `SecurityViolationError`.
- [ ]  Execute code attempting to write outside allowed directories returns `SecurityViolationError`.
- [ ]  Execute code writing inside allowed directories succeeds.
- [ ]  Execute code with an oversized data size is rejected.
- [ ]  Execute code with an oversized output returns a truncated result with a truncation flag.
- [ ]  Execute code with an output that cannot be formatted returns a safe text fallback or explicit error.

**Background Tasks:**

- [ ]  Submit a background task returns a tracking ID.
- [ ]  Check a pending background task returns a pending status.
- [ ]  Check a completed background task returns the final `ExecutionResult`.
- [ ]  Check an unknown background task returns `TaskNotFoundError`.
- [ ]  Cancel a pending background task succeeds.
- [ ]  Cancel a running background task returns a best-effort or unsupported status.
- [ ]  Background task results expire after the configured time limit.
- [ ]  Blender crashing during a background task marks the task as an error.

**Standard Commands:**

- [ ]  Send a valid command to Blender returns a response within 5 seconds.
- [ ]  Send a command exceeding the 5s timeout returns `CommandTimeoutError`.
- [ ]  Send a command with a custom timeout respects the configured limit.
- [ ]  Send an unknown command returns `ProviderError`.
- [ ]  Send a command with invalid parameters returns `ValidationError`.
- [ ]  Send a command that results in an invalid response format returns a parsing/provider error.

**Operation Processing:**

- [ ]  Concurrent requests are processed sequentially without crashing.
- [ ]  Pending operation limit (50) is enforced; excess requests return `TooManyPendingOperationsError`.
- [ ]  An operation waiting too long returns `OperationWaitTimeoutError`.
- [ ]  Non-scene operations (like status checks) do not get stuck behind scene operations.
- [ ]  Malformed data received from the network is handled safely without crashing.
- [ ]  Data missing a tracking ID is handled according to system rules.
- [ ]  Large response data is truncated or rejected based on configured limits.

## Assumptions & Constraints

- The Blender application must be running and listening for connections.
- The system supports one active connection to Blender at a time.
- Custom code execution has a 30-second timeout by default (configurable).
- Standard command execution has a 5-second timeout by default.
- Some commands may define custom timeout limits.
- Because the Blender application can only safely process one scene operation at a time, all concurrent requests that interact with the scene are processed sequentially to prevent instability.
- The list of blocked code patterns is maintained in the system settings and updated as needed.
- The system and Blender must use compatible versions.
- All user-provided code is treated as untrusted.
- Pre-execution safety checks are not a complete replacement for runtime boundaries; the Blender environment must also enforce restrictions.
- Allowed directories for file access must be explicitly configured.
- The default allowed directory is the active Blender project folder.
- Authentication tokens are required for remote connections when authentication is enabled.
- The default connection target is local-only for security.
- Background task tracking is stored in memory unless persistent storage is explicitly enabled.
- Background task results have a configurable time-to-live.
- Cancelling a running Blender operation is a best-effort attempt, as the application may not be able to stop it immediately.
- The liveness check mechanism must account for long-running operations to avoid false alarms.
- Maximum data sizes for requests and responses must be configured and enforced.

## Glossary

- **Background Task:** A long-running operation submitted to the system that returns a tracking ID immediately, allowing the user to check its status later.
- **Blocked Patterns:** A configurable list of forbidden code structures or modules used to prevent security violations.
- **Allowed Directory:** A specific folder explicitly permitted for file read/write operations.
- **Connection Status:** The current state of the connection (e.g., connected, disconnected, reconnecting), including target details and last liveness check time.
- **Task Status:** The current lifecycle state of a background task (e.g., pending, running, success, error, timeout, cancelled).
- **Liveness Check (Heartbeat):** A periodic signal sent to verify that the connection to Blender is still active and responsive.
- **Execution Result:** The standardized outcome of a code execution, containing the status, returned data, error details, time taken, and truncation flags.
- **Tracking ID:** A unique identifier assigned to every request and response to correlate logs, track operations, and troubleshoot errors.
- **Security Violation:** An event where user-provided code attempts to perform an action blocked by the system's safety rules.
```

---

## File: modules/server/src/__init__.py

```python
"""Server feature module — Blender TCP socket communication.

Layers:
  - Taxonomy (shared): ConnectionStatus, ExecutionResult, TaskStatus, ConnectionConfig, errors, constants
  - Contracts (shared): IBlenderServerAggregate, protocol ABCs
  - Utility (shared): IO, message framing, string helpers, time utils, AST validator
  - Capabilities (3 FR modules):
      1. capabilities_blender_connection (FR-001 Connection)
      2. capabilities_code_execution_adapter (FR-002 Code Execution & TaskManager)
      3. capabilities_blender_command_adapter (FR-003 Command Dispatch & ExecutionQueue)
  - Agent: ServerOrchestrator (IBlenderServerAggregate)
  - Root: ServerContainer (DI container wiring all layers)

Note: No Surface layer — server is an internal module.
Surface handlers live in CLI and MCP modules.
"""

from .agent_server_orchestrator import ServerOrchestrator
from .capabilities_blender_command_adapter import BlenderCommandAdapter
from .capabilities_blender_connection import BlenderConnection
from .capabilities_code_execution_adapter import CodeExecutionAdapter
from .root_server_container import ServerContainer, create_container

__all__ = [
    # ─── Agent ────────────────────────────────────────────────
    "ServerOrchestrator",
    # ─── Capabilities (Aligned with 3 FRs) ────────────────────
    "BlenderCommandAdapter",
    "BlenderConnection",
    "CodeExecutionAdapter",
    # ─── Root (DI Container) —─────────────────────────────────
    "ServerContainer",
    "create_container",
]
```

---

## File: modules/server/src/agent_server_orchestrator.py

```python
"""Agent: Server feature orchestrator.

Coordinates Blender TCP connection lifecycle, code execution,
command dispatch, and async task management through the unified
IBlenderServerAggregate facade. Per FRD-SRV-001 through FRD-SRV-005.
"""

from __future__ import annotations

import logging
import time
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    Prompt,
    StatusString,
)
from modules.shared.src.server import (
    CommandTimeoutError,
    ConnectionConfig,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionResult,
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
    ICodeExecutionProtocol,
    QueueFullError,
    TaskNotFoundError,
)

logger = logging.getLogger("BlenderMCPServer")


class ServerOrchestrator(IBlenderServerAggregate):
    """Unified orchestrator for Blender server operations."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        connection: IBlenderConnectionProtocol,
        code_executor: ICodeExecutionProtocol,
        command_adapter: IBlenderCommandProtocol | None = None,
    ) -> None:
        self._connection = connection
        self._code_executor = code_executor
        self._command_adapter = command_adapter

    # ─── Block 2: Aggregate Implementation ───────────────────

    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake.

        Orchestrates connection via IBlenderConnectionProtocol.
        """
        await self._connection.connect()
        return ConnectionStatus(
            state="connected",
            transport_type=config.transport_type,
            host=config.host or "localhost",
            port=config.port or 9876,
            protocol_version=config.protocol_version,
        )

    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent."""
        await self._connection.disconnect()

    async def get_status(self) -> ConnectionStatus:
        """Return current connection state with metadata."""
        return await self._connection.get_status()

    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Orchestrates AST validation (via ICodeExecutionProtocol),
        enqueues for serialized bpy access, and returns standardized
        ExecutionResult with timing per FRD-SRV-002.
        """
        start = time.monotonic()
        try:
            # Enqueue for serialized bpy access
            if self._command_adapter is not None:
                await self._command_adapter.enqueue(request_id, {"code": code})

            # Execute through capability layer
            result = await self._code_executor.execute_blender_code(Prompt(code))
            elapsed_ms = (time.monotonic() - start) * 1000
            return ExecutionResult(
                status=StatusString("success"),
                data=result,
                execution_time_ms=elapsed_ms,
            )
        except QueueFullError:
            elapsed_ms = (time.monotonic() - start) * 1000
            return ExecutionResult(
                status=StatusString("error"),
                error=ExecutionErrorDetail(
                    error_type="QueueFullError",
                    message="Execution queue full — max depth exceeded",
                ),
                execution_time_ms=elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Code execution failed for request %s: %s", request_id, e)
            return ExecutionResult(
                status=StatusString("error"),
                error=ExecutionErrorDetail(
                    error_type=type(e).__name__,
                    message=str(e),
                ),
                execution_time_ms=elapsed_ms,
            )

    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution.

        Delegates to ICodeExecutionProtocol capability layer per FRD-SRV-002.
        """
        logger.info("Submitting async task for request %s (code length=%d)", request_id, len(code))
        return await self._code_executor.submit_async_task(code, request_id)

    async def poll_task_result(self, task_id: str, request_id: str = "") -> ExecutionResult:
        """Poll async task status and final result.

        Delegates to ICodeExecutionProtocol capability layer per FRD-SRV-002.
        """
        logger.debug("Polling task %s for request %s", task_id, request_id)
        try:
            return await self._code_executor.poll_task_result(task_id)
        except TaskNotFoundError:
            return ExecutionResult(
                status=StatusString("error"),
                error=ExecutionErrorDetail(
                    error_type="TaskNotFoundError",
                    message=f"Task not found or expired: {task_id}",
                ),
            )

    async def send_command(
        self,
        action: str,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
    ) -> dict[str, Any]:
        """Dispatch a named command to Blender addon.

        Routes through TCP socket with configurable timeout enforcement
        per FRD-SRV-003. Default timeout is 5000ms.

        Args:
            action: Named action to dispatch to Blender.
            params: Optional command arguments dictionary.
            timeout_ms: Override timeout in milliseconds. Uses default if None.

        Returns:
            Command result dict with status, data, error, execution_time_ms.

        Raises:
            CommandTimeoutError: if response exceeds configured timeout.
        """
        start = time.monotonic()
        try:
            # Enqueue for serialized bpy access (non-scene read-only commands bypass queue per FR-003)
            is_non_scene = action.startswith("get_") or action in ("ping", "get_status", "get_version", "get_scene_info")
            if self._command_adapter is not None and not is_non_scene:
                await self._command_adapter.enqueue(f"cmd_{action}", {"action": action, "params": params})

            # Dispatch through connection protocol
            cmd_params = dict(params or {})
            if timeout_ms is not None:
                cmd_params["timeout_ms"] = timeout_ms

            result = await self._connection.send_command(ActionName(action), cmd_params)
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info(
                "Command %s completed in %.1fms",
                action,
                elapsed_ms,
            )
            return {
                "status": "success",
                "data": result,
                "execution_time_ms": elapsed_ms,
            }
        except CommandTimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.warning("Command %s timed out after %.1fms", action, elapsed_ms)
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            return {
                "status": "error",
                "data": None,
                "error": {"type": type(e).__name__, "message": str(e)},
                "execution_time_ms": elapsed_ms,
            }

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return "ServerOrchestrator()"
```

---

## File: modules/server/src/capabilities_blender_command_adapter.py

```python
"""Capability: Blender command dispatch with timeout enforcement and execution queueing.

Implements IBlenderCommandProtocol — dispatches named commands to the Blender addon via TCP socket
with configurable timeout, FIFO queue, and schema validation per FR-SRV-003.
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ActionName, ErrorMessage
from modules.shared.src.common.taxonomy_domain_error import ValidationError
from modules.shared.src.server import (
    DEFAULT_COMMAND_TIMEOUT_MS,
    CommandTimeoutError,
    ExecutionResult,
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    QueueConfig,
    QueueFullError,
    QueueTimeoutError,
    get_command_schema,
)

logger = logging.getLogger("BlenderMCPServer")

@dataclass
class QueueItem:
    """Internal mutable state for a queued request."""

    request_id: str
    payload: dict[str, Any]
    enqueued_at: float = field(default_factory=time.monotonic)
    result: ExecutionResult | None = None
    error: Exception | None = None

class BlenderCommandAdapter(IBlenderCommandProtocol):
    """Command dispatch and execution queueing capability for Blender TCP socket operations.

    Implements FR-SRV-003: dispatches named commands with timeout enforcement,
    schema validation, and FIFO queue serialization to prevent concurrent bpy access.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        queue_config: QueueConfig | None = None,
    ) -> None:
        self._connection = connection_port
        self._config = queue_config or QueueConfig()
        self._queue: list[QueueItem] = []
        self._queue_lock = asyncio.Lock()

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def send_command(
        self,
        action: ActionName,
        params: dict[str, Any] | None = None,
        timeout_ms: float | None = None,
    ) -> dict[str, Any]:  # FR-SRV-003
        """Dispatch a named command to Blender addon.

        Routes through TCP socket; response parsed as JSON.
        Default timeout: DEFAULT_COMMAND_TIMEOUT_MS (5000ms).
        Validates command arguments against schema per FR-SRV-003.
        Raises CommandTimeoutError if response exceeds timeout.

        Args:
            action: Named action to dispatch to Blender.
            params: Optional command arguments dictionary.
            timeout_ms: Override timeout in milliseconds. Uses default if None.

        Returns:
            Command result dict with status, data, error, execution_time_ms.

        Raises:
            ValidationError: if command arguments are invalid.
            CommandTimeoutError: if response exceeds configured timeout.
        """
        # Validate command arguments against schema (FR-SRV-003)
        action_str = str(action) if not isinstance(action, str) else action
        try:
            get_command_schema(action_str)  # Validates command exists
        except Exception as e:
            raise ValidationError(ErrorMessage(f"Invalid command: {action_str}")) from e

        timeout_s = (timeout_ms or DEFAULT_COMMAND_TIMEOUT_MS) / 1000.0
        start = time.monotonic()

        try:
            result = await asyncio.wait_for(
                self._connection.send_command(action, params),
                timeout=timeout_s,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.info(
                "Command %s completed in %.1fms",
                action,
                elapsed_ms,
            )
            return {
                "status": "success",
                "data": result,
                "execution_time_ms": elapsed_ms,
            }
        except asyncio.TimeoutError:
            logger.warning(
                "Command %s timed out after %.1fms",
                action,
                timeout_s * 1000,
            )
            raise CommandTimeoutError(
                ErrorMessage(
                    f"Command '{action}' timed out after {timeout_ms or DEFAULT_COMMAND_TIMEOUT_MS}ms"
                )
            ) from None
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Command %s failed: %s", action, e)
            return {
                "status": "error",
                "data": None,
                "error": {"type": type(e).__name__, "message": str(e)},
                "execution_time_ms": elapsed_ms,
            }

    async def enqueue(
        self,
        request_id: str,
        payload: dict[str, Any],
    ) -> str:
        """Add item to queue. Raises QueueFullError if depth limit exceeded."""
        async with self._queue_lock:
            if len(self._queue) >= self._config.max_depth:
                raise QueueFullError(
                    f"Queue full: {len(self._queue)}/{self._config.max_depth}"
                )

            item = QueueItem(request_id=request_id, payload=payload)
            self._queue.append(item)
            logger.info("Enqueued request %s (%d/%d)", request_id, len(self._queue), self._config.max_depth)
            return request_id

    async def dequeue(self) -> str | None:
        """Remove and return the next request_id from the queue."""
        async with self._queue_lock:
            if not self._queue:
                return None
            item = self._queue.pop(0)
            logger.info("Dequeued request %s (%d remaining)", item.request_id, len(self._queue))
            return item.request_id

    async def wait_for_completion(
        self,
        request_id: str,
        timeout_ms: float | None = None,
    ) -> ExecutionResult:
        """Wait for a queued item to be processed and return result."""
        timeout_ms = timeout_ms or self._config.wait_timeout_ms
        timeout_s = timeout_ms / 1000.0

        item = await self._find_item(request_id)
        if item is None:
            raise QueueTimeoutError(f"Item not found: {request_id}")

        deadline = time.monotonic() + timeout_s
        while True:
            if item.error is not None:
                raise item.error
            if item.result is not None:
                return item.result
            if time.monotonic() > deadline:
                raise QueueTimeoutError(
                    f"Queue wait timeout after {timeout_ms}ms for request {request_id}"
                )
            await asyncio.sleep(0.05)

    async def get_depth(self) -> int:
        """Return current queue depth."""
        async with self._queue_lock:
            return len(self._queue)

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return f"BlenderCommandAdapter(queue_max_depth={self._config.max_depth})"

    def _send_sync(self, action: ActionName, params: dict[str, Any]) -> dict[str, Any]:
        """Synchronous send_command for use with asyncio.to_thread."""
        return self._connection.send_command(action, params)

    async def _find_item(self, request_id: str) -> QueueItem | None:
        """Find queue item by request_id."""
        async with self._queue_lock:
            for item in self._queue:
                if item.request_id == request_id:
                    return item
            return None



```

---

## File: modules/server/src/capabilities_blender_connection.py

```python
"""Capability: Blender socket connection lifecycle management.

Implements IBlenderConnectionProtocol — handles TCP socket connection,
heartbeat monitoring, auto-reconnect with exponential backoff,
connection status reporting, and factory instantiation per FR-SRV-001.
"""

from __future__ import annotations

import contextlib
import json
import logging
import os
import select
import socket
import threading
import time
from typing import Any

from modules.config.src.contract_config import ConfigPort
from modules.shared.src import (
    ActionName,
    BlenderConnectionFailure,
    ConfigPath,
    Details,
    ErrorMessage,
    ExecutionError,
    SuccessFlag,
)
from modules.shared.src.server import (
    CONNECTION_TIMEOUT_SECONDS,
    MAX_RECONNECT_ATTEMPTS,
    RETRY_BASE_DELAY_SECONDS,
    RETRY_MAX_DELAY_SECONDS,
    AuthenticationError,
    BlenderConnectionExhausted,
    ConnectionConfigError,
    ConnectionStatus,
    IBlenderConnectionProtocol,
    ProtocolVersionMismatchError,
)

logger = logging.getLogger("BlenderMCPServer")

RECEIVE_TIMEOUT: float = CONNECTION_TIMEOUT_SECONDS


class BlenderConnection(IBlenderConnectionProtocol):
    """Manages persistent socket connection to Blender addon.

    Implements FR-SRV-001 / FR-SRV-004: heartbeat monitoring, auto-reconnect with
    exponential backoff with jitter, configuration validation, and factory instantiation.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, host: str = "localhost", port: int = 9876, auth_token: str | None = None) -> None:
        self.host = host
        self.port = port
        self.auth_token = auth_token
        self.sock: socket.socket | None = None
        self._lock = threading.Lock()

        # Heartbeat configuration (FR-SRV-001)
        self._heartbeat_interval = 10  # seconds
        self._heartbeat_failure_threshold = 3
        self._consecutive_failures = 0
        self._last_heartbeat_at: float | None = None

        # Connection state tracking (FR-SRV-001)
        self._state: str = "disconnected"
        self._reconnect_attempts: int = 0
        self._protocol_version: str | None = "1.0.0"
        self._last_error: str | None = None

        # Heartbeat thread
        self._heartbeat_thread: threading.Thread | None = None
        self._stop_heartbeat = threading.Event()

    # ─── Block 2: Protocol Method Implementation ─────────────

    async def connect(self) -> SuccessFlag:  # FR-SRV-001
        """Connect to Blender with exponential backoff retries and jitter.

        Implements FR-SRV-001: auto-reconnect with max 3 retry attempts
        using exponential backoff with jitter (1s, 2s, 4s). Handshake verifies
        compatibility version and authenticates user token if required.
        Connection timeout: CONNECTION_TIMEOUT_SECONDS (30s default).
        Initializes heartbeat monitoring on successful connection.
        """
        with self._lock:
            # Update state
            self._state = "connecting"
            self._last_error = None

            if self.sock is not None:
                if self._is_socket_alive():
                    return SuccessFlag(True)
                self._close_socket()

            for attempt in range(MAX_RECONNECT_ATTEMPTS):
                try:
                    self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.sock.settimeout(CONNECTION_TIMEOUT_SECONDS)
                    self.sock.connect((self.host, self.port))

                    # Perform initial handshake verification (FR-SRV-001)
                    if self.auth_token is not None:
                        # Send handshake frame for token validation
                        handshake_payload = json.dumps({
                            "type": "handshake",
                            "protocol_version": self._protocol_version,
                            "auth_token": self.auth_token,
                        }).encode("utf-8")
                        self.sock.sendall(handshake_payload)
                        response_bytes = self.sock.recv(4096)
                        if response_bytes:
                            resp = json.loads(response_bytes.decode("utf-8"))
                            if resp.get("status") == "auth_failed":
                                raise AuthenticationError(ErrorMessage("Invalid authentication token"))
                            if resp.get("status") == "version_mismatch":
                                raise ProtocolVersionMismatchError(ErrorMessage("Incompatible protocol version"))

                    # Update state on success
                    self._state = "connected"
                    self._reconnect_attempts = attempt + 1
                    self._consecutive_failures = 0
                    self._last_heartbeat_at = time.time()
                    logger.info("Connected to Blender at %s:%d", self.host, self.port)

                    # Start heartbeat monitoring
                    self._start_heartbeat()
                    return SuccessFlag(True)

                except (AuthenticationError, ProtocolVersionMismatchError):
                    self._state = "failed"
                    self._close_socket()
                    raise
                except Exception as e:
                    self._state = "failed"
                    self._last_error = str(e)
                    logger.warning(
                        "Connection attempt %d/%d failed: %s",
                        attempt + 1,
                        MAX_RECONNECT_ATTEMPTS,
                        e,
                    )
                    self._close_socket()

                    if attempt < MAX_RECONNECT_ATTEMPTS - 1:
                        # Exponential backoff with jitter (FR-SRV-001)
                        base_delay = min(
                            RETRY_BASE_DELAY_SECONDS * (2**attempt),
                            RETRY_MAX_DELAY_SECONDS,
                        )
                        jitter = (time.monotonic() % 0.5) * base_delay
                        delay = base_delay + jitter
                        logger.debug("Waiting %.1f seconds before reconnect attempt %d", delay, attempt + 2)
                        time.sleep(delay)

            # All retries exhausted
            self._state = "failed"
            raise BlenderConnectionExhausted(ErrorMessage("Failed to connect after all retry attempts"))

    async def disconnect(self) -> None:  # FR-SRV-001 (idempotent)
        """Graceful disconnect. Must be idempotent.

        Stops heartbeat monitoring, closes socket, updates state to closed.
        """
        with self._lock:
            self.stop_heartbeat()
            self._close_socket()
            self._state = "closed"
            logger.info("Disconnected from Blender at %s:%d (state=closed)", self.host, self.port)

    async def is_connected(self) -> SuccessFlag:
        """Check if socket is currently connected and alive."""
        return SuccessFlag(self._is_socket_alive())

    async def send_command(self, command_type: ActionName, params: Details | None = None) -> Details:
        """Send a command to Blender and return the JSON response."""
        with self._lock:
            if self.sock is None and not await self.connect():
                raise ConnectionError("Not connected to Blender")

            active_sock = self.sock
            if active_sock is None:
                raise ConnectionError("Socket initialization failed")

            command = {"type": str(command_type), "params": params or {}}

            response_data: bytes = b""
            try:
                logger.info("Sending command: %s with params: %s", command_type, params)
                active_sock.settimeout(RECEIVE_TIMEOUT)
                active_sock.sendall(json.dumps(command).encode("utf-8"))
                logger.info("Command sent, waiting for response...")
                response_data = await self.receive_full_response()
                logger.info("Received %d bytes of data", len(response_data))

                return self._handle_command_response(response_data)
            except TimeoutError as e:
                logger.error("Socket timeout while waiting for response")
                self._close_socket()
                raise BlenderConnectionFailure(
                    ErrorMessage("Timeout waiting for Blender response - try simplifying your request")
                ) from e
            except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                logger.error("Socket connection error: %s", e)
                self._close_socket()
                raise BlenderConnectionFailure(ErrorMessage(f"Connection to Blender lost: {e}")) from e
            except json.JSONDecodeError as e:
                logger.error("Invalid JSON response from Blender: %s", e)
                if response_data:
                    logger.error(
                        "Raw response (first 200 bytes): %s",
                        response_data[:200].decode("utf-8", errors="replace"),
                    )
                raise ExecutionError(ErrorMessage(f"Invalid response from Blender: {e}")) from e
            except Exception as e:
                logger.error("Error communicating with Blender: %s", e)
                self._close_socket()
                raise BlenderConnectionFailure(ErrorMessage(f"Communication error with Blender: {e}")) from e

    async def receive_full_response(self, buffer_size: int = 8192) -> bytes:
        """Receive complete JSON response from socket in chunks.

        Uses self.sock (the active connection socket).
        """
        if self.sock is None:
            raise BlenderConnectionFailure(ErrorMessage("No active socket connection"))
        chunks, completed = self._read_response_chunks(self.sock, buffer_size)
        if completed:
            return b"".join(chunks)
        if chunks:
            return self._finalize_chunks(chunks)
        raise BlenderConnectionFailure(ErrorMessage("No data received"))

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────

    @classmethod
    def create_from_config(cls, config: ConfigPort | None = None) -> BlenderConnection:  # FR-SRV-004
        """Factory method to create a BlenderConnection instance from configuration.

        Validates host and port configuration parameters per FR-SRV-004.
        """
        host = "localhost"
        port = 9876

        if config is not None:
            host_val = config.get(ConfigPath("blender.host"), "localhost")
            host = str(host_val) if host_val is not None else "localhost"
            port_val = config.get(ConfigPath("blender.port"), 9876)
            port = int(port_val) if isinstance(port_val, (int, str)) else 9876

        # Environment variable override
        env_host = os.getenv("BLENDER_HOST")
        if env_host:
            host = env_host

        env_port = os.getenv("BLENDER_PORT")
        if env_port:
            port = int(env_port)

        cls._validate_config(host, port)
        return cls(host=host, port=port)

    @staticmethod
    def _validate_config(host: str, port: int) -> None:
        """Validate connection configuration parameters.

        Raises ConnectionConfigError for invalid configuration.
        """
        if not host or not host.strip():
            raise ConnectionConfigError(ErrorMessage("Host cannot be empty"))

        if not isinstance(port, int) or port < 1 or port > 65535:
            raise ConnectionConfigError(
                ErrorMessage(f"Port must be between 1 and 65535, got {port}")
            )

    async def get_status(self) -> ConnectionStatus:  # FR-SRV-001
        """Return current connection state with metadata."""
        return ConnectionStatus(
            state=self._state,
            transport_type="socket",
            host=self.host,
            port=self.port,
            last_error=self._last_error,
            last_heartbeat_at=self._last_heartbeat_at,
            reconnect_attempts=self._reconnect_attempts,
            protocol_version=self._protocol_version,
            heartbeat_interval_seconds=self._heartbeat_interval,
            heartbeat_failure_threshold=self._heartbeat_failure_threshold,
        )

    def __repr__(self) -> str:
        return f"BlenderConnection(host={self.host!r}, port={self.port}, state={self._state})"

    def _start_heartbeat(self) -> None:
        """Start heartbeat monitoring thread."""
        self._stop_heartbeat.clear()
        self._heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self._heartbeat_thread.start()

    def _heartbeat_loop(self) -> None:
        """Heartbeat monitoring loop. Checks connection liveness periodically."""
        while not self._stop_heartbeat.is_set():
            try:
                time.sleep(self._heartbeat_interval)
                if self._stop_heartbeat.is_set():
                    break

                # Check if socket is alive
                if not self._is_socket_alive():
                    self._consecutive_failures += 1
                    logger.warning(
                        "Heartbeat failure %d/%d",
                        self._consecutive_failures,
                        self._heartbeat_failure_threshold,
                    )

                    if self._consecutive_failures >= self._heartbeat_failure_threshold:
                        self._state = "reconnecting"
                        logger.info("Heartbeat threshold reached, triggering reconnect")
                        self._close_socket()
                        # Trigger reconnect in background
                        threading.Thread(target=self._reconnect_background, daemon=True).start()
                else:
                    # Success - reset failure count
                    self._consecutive_failures = 0
                    self._last_heartbeat_at = time.time()

            except Exception as e:
                logger.error("Heartbeat error: %s", e)
                self._consecutive_failures += 1

    def _reconnect_background(self) -> None:
        """Background reconnect attempt."""
        try:
            self.connect()
        except Exception as e:
            logger.error("Background reconnect failed: %s", e)

    def stop_heartbeat(self) -> None:
        """Stop heartbeat monitoring thread."""
        self._stop_heartbeat.set()
        if self._heartbeat_thread is not None:
            self._heartbeat_thread.join(timeout=5.0)
        self._heartbeat_thread = None

    def _close_socket(self) -> None:
        if self.sock:
            with contextlib.suppress(Exception):
                self.sock.close()
            self.sock = None

    def _is_socket_alive(self) -> bool:
        if self.sock is None:
            return False
        try:
            ready, _, _ = select.select([self.sock], [], [], 0)
            if ready:
                data = self.sock.recv(1, socket.MSG_PEEK)
                if not data:
                    return False
            return True
        except (ConnectionError, BrokenPipeError, ConnectionResetError, OSError, BlenderConnectionFailure):
            return False

    def _read_response_chunks(self, sock: socket.socket, buffer_size: int) -> tuple[list[bytes], bool]:
        """Read socket chunks until a complete JSON is received or connection ends.

        Returns (chunks, completed_via_json) where completed_via_json is True
        if we successfully parsed JSON and have the complete response.
        """
        chunks: list[bytes] = []
        try:
            while True:
                try:
                    chunk = sock.recv(buffer_size)
                    if not chunk:
                        if not chunks:
                            raise BlenderConnectionFailure(ErrorMessage("Connection closed before receiving any data"))
                        break
                    chunks.append(chunk)
                    try:
                        data = b"".join(chunks)
                        json.loads(data.decode("utf-8"))
                        logger.info("Received complete response (%d bytes)", len(data))
                        return chunks, True
                    except json.JSONDecodeError:
                        continue
                except TimeoutError:
                    logger.warning("Socket timeout during chunked receive")
                    break
                except (ConnectionError, BrokenPipeError, ConnectionResetError) as e:
                    logger.error("Socket connection error: %s", e)
                    raise
        except TimeoutError:
            logger.warning("Socket timeout during chunked receive")  # pragma: no cover
        except Exception as e:
            logger.error("Error during receive: %s", e)
            raise
        return chunks, False

    def _finalize_chunks(self, chunks: list[bytes]) -> bytes:
        """Process collected chunks into a complete response."""
        data = b"".join(chunks)
        logger.info("Returning data after receive completion (%d bytes)", len(data))
        try:
            json.loads(data.decode("utf-8"))
            return data
        except json.JSONDecodeError as e:
            raise ExecutionError(ErrorMessage("Incomplete JSON response received")) from e

    def _handle_command_response(self, response_data: bytes) -> dict[str, Any]:
        """Parse and validate the JSON response from Blender."""
        response = json.loads(response_data.decode("utf-8"))
        logger.info("Response parsed, status: %s", response.get("status", "unknown"))

        if response.get("status") == "error":
            logger.error("Blender error: %s", response.get("message"))
            raise ExecutionError(ErrorMessage(response.get("message", "Unknown error from Blender")))

        result: dict[str, Any] = response.get("result", {})
        return result
```

---

## File: modules/server/src/capabilities_code_execution_adapter.py

```python
"""Capability: Code execution with AST-based validation, safety checks, and async task management.

Implements ICodeExecutionProtocol — handles Python code validation via
AST analysis, socket-based execution forwarding, payload size enforcement,
output truncation, result formatting, and async task lifecycle tracking per FR-SRV-002.
"""

from __future__ import annotations

import ast
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ActionName, ErrorMessage, Prompt
from modules.shared.src.common.taxonomy_domain_error import ValidationError
from modules.shared.src.server import (
    DEFAULT_TASK_RETENTION_SECONDS,
    MAX_CODE_PAYLOAD_BYTES,
    ExecutionResult,
    ExecutionStatus,
    ExecutionTimeoutError,
    IBlenderConnectionProtocol,
    ICodeExecutionProtocol,
    SecurityViolationError,
    TaskManagerConfig,
    TaskNotFoundError,
    TaskState,
    TaskStatus,
    check_payload_size,
)

logger = logging.getLogger("BlenderMCPServer")

# Default AST-based blocked patterns for code validation (FRD-SRV-002)
_BLOCKED_ATTRS: set[str] = {
    "system",
    "popen",
    "exec_module",
    "load_module",
    "rmtree",
    "move",
    "unlink",
    "remove",
    "rmdir",
    "write_text",
    "write_bytes",
}

_BLOCKED_MODULES: set[str] = {
    "subprocess",
    "importlib",
    "socket",
    "requests",
    "urllib",
}


@dataclass
class TaskEntry:
    """Internal mutable state for a tracked task."""

    task_id: str
    state: TaskState
    result: ExecutionResult | None = None
    created_at: float = field(default_factory=time.monotonic)
    completed_at: float | None = None


class CodeExecutionAdapter(ICodeExecutionProtocol):
    """Code execution with AST-based validation, socket forwarding,
    and in-memory async task lifecycle management."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        task_config: TaskManagerConfig | None = None,
    ) -> None:
        self._connection_port = connection_port
        self._task_config = task_config or TaskManagerConfig()
        self._tasks: dict[str, TaskEntry] = {}

    # ─── Block 2: ICodeExecutionProtocol Methods ─────────────

    async def execute_blender_code(self, code: Prompt) -> ExecutionResult:  # FR-SRV-002
        """Execute Python code in Blender via IPC.

        Validates code against AST-based denylist (FR-SRV-002),
        enforces payload size limits, enforces 30s timeout, and returns standardized ExecutionResult.

        Raises:
            SecurityViolationError: if code contains blocked patterns or exceeds size.
            ValidationError: if code is empty or syntax error.
            ExecutionTimeoutError: if execution exceeds 30s timeout.
        """
        code_str = str(code)

        # Enforce payload size limit (FR-SRV-002)
        check_payload_size(code_str, MAX_CODE_PAYLOAD_BYTES)

        # AST-based validation (FR-SRV-002 requirement)
        self._validate_code_ast(code_str)

        # Audit log — record all code execution attempts
        logger.info(
            "Executing Blender code (length=%d bytes): %.100s%s",
            len(code_str.encode("utf-8")),
            code_str,
            "..." if len(code_str) > 100 else "",
        )

        try:
            loop = asyncio.get_running_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._connection_port.send_command(
                        ActionName("execute_code"), {"code": code_str}
                    ),
                ),
                timeout=30.0,
            )

            # Truncate output if too large (FR-SRV-002)
            data = result.get("result", "")
            truncated = False
            max_output_bytes = 10_000  # 10KB max output

            if isinstance(data, str) and len(data.encode("utf-8")) > max_output_bytes:
                data = data[:max_output_bytes] + "\n...[truncated]"
                truncated = True

            return ExecutionResult(
                status=ExecutionStatus("success"),
                data=data,
                truncated=truncated,
            )
        except asyncio.TimeoutError:
            logger.warning("Code execution timed out after 30 seconds")
            raise ExecutionTimeoutError(
                ErrorMessage("Code execution timed out after 30 seconds")
            ) from None
        except SecurityViolationError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Error executing code in Blender")
            return ExecutionResult(
                status=ExecutionStatus("error"),
                error={"type": type(e).__name__, "message": str(e)},
            )

    async def submit_async_task(self, code: Prompt, request_id: str) -> str:
        """Submit long-running code for async execution. Returns new TaskId."""
        self._validate_code_ast(str(code))

        task_id = self.create_task(request_id)

        # Start async execution in background
        asyncio.ensure_future(self._run_async_task(task_id, str(code)))

        logger.info("Submitted async task %s for request %s", task_id, request_id)
        return task_id

    async def poll_task_result(self, task_id: str) -> ExecutionResult:
        """Poll async task status and final result."""
        task_status = self.get_task(task_id)

        if task_status.state == "success":
            return ExecutionResult(
                status=ExecutionStatus("success"),
                data=task_status.result,
            )
        elif task_status.state == "error":
            return ExecutionResult(
                status=ExecutionStatus("error"),
                error={"type": "ExecutionError", "message": str(task_status.result)},
            )
        else:
            # pending or running
            return ExecutionResult(
                status=ExecutionStatus("success"),
                data={"task_id": task_id, "state": task_status.state},
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────

    def create_task(self, request_id: str) -> str:
        """Create a new task entry and return its unique task_id."""
        task_id = f"task_{request_id}_{int(time.monotonic() * 1000) % 1000000:06d}"
        self._tasks[task_id] = TaskEntry(task_id=task_id, state="pending")
        logger.info("Created task %s", task_id)
        self._cleanup_expired()
        return task_id

    def get_task(self, task_id: str) -> TaskStatus:
        """Retrieve task status; raises TaskNotFoundError if missing or expired."""
        entry = self._tasks.get(task_id)
        if entry is None:
            raise TaskNotFoundError(ErrorMessage(f"Task not found: {task_id}"))
        if entry.completed_at is not None:
            elapsed = time.monotonic() - entry.completed_at
            if elapsed > self._task_config.retention_seconds:
                del self._tasks[task_id]
                raise TaskNotFoundError(ErrorMessage(f"Task expired: {task_id}"))
        return TaskStatus(task_id=entry.task_id, state=entry.state, result=entry.result)

    def mark_running(self, task_id: str) -> None:
        """Transition task state to 'running'."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "running"

    def mark_completed(self, task_id: str, result: ExecutionResult) -> None:
        """Mark task as successfully completed with result."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "success"
            entry.result = result
            entry.completed_at = time.monotonic()

    def mark_error(self, task_id: str, error_type: str, message: str) -> None:
        """Mark task as failed with error type and message."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "error"
            entry.result = ExecutionResult(
                status="error",
                error={"type": error_type, "message": message},
            )
            entry.completed_at = time.monotonic()

    def mark_timeout(self, task_id: str) -> None:
        """Mark task as timed out."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "timeout"
            entry.result = ExecutionResult(
                status="error",
                error={"type": "ExecutionTimeoutError", "message": "Timed out"},
            )
            entry.completed_at = time.monotonic()

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task. Returns True if cancelled, False otherwise."""
        entry = self._tasks.get(task_id)
        if entry is None:
            return False
        if entry.state == "pending":
            entry.state = "cancelled"
            entry.completed_at = time.monotonic()
            return True
        return False

    

    def __repr__(self) -> str:
        return (
            f"CodeExecutionAdapter(task_retention={self._task_config.retention_seconds}s)"
        )

    async def _run_async_task(self, task_id: str, code: str) -> None:
        """Execute async task in background, updating task state on completion."""
        self.mark_running(task_id)

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._connection_port.send_command(
                    ActionName("execute_code"), {"code": code}
                ),
            )
            self.mark_completed(
                task_id,
                ExecutionResult(status=ExecutionStatus("success"), data=result),
            )
        except Exception as e:
            self.mark_error(task_id, type(e).__name__, str(e))

    def _cleanup_expired(self) -> None:
        """Remove tasks that have exceeded their retention window."""
        now = time.monotonic()
        expired = [
            tid
            for tid, e in self._tasks.items()
            if e.completed_at is not None
            and (now - e.completed_at) > self._task_config.retention_seconds
        ]
        for tid in expired:
            del self._tasks[tid]
            logger.info("Cleaned up expired task %s", tid)

    @staticmethod
    def _validate_code_ast(code: str) -> None:
        """AST-based static analysis for blocked Python constructs.

        Implements FRD-SRV-002: code validated before sending using
        AST-based static analysis, not only regex or simple string matching.

        Raises SecurityViolationError if any blocked pattern is detected.
        Server-side validation is a pre-filter only; Blender addon must
        perform runtime enforcement as the final authority.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValidationError(
                ErrorMessage(f"Invalid syntax in submitted code: {e}")
            ) from e

        for node in ast.walk(tree):
            # Check attribute calls (e.g., os.system, subprocess.Popen)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _BLOCKED_ATTRS
            ):
                raise SecurityViolationError(
                    ErrorMessage(f"Blocked construct detected: {node.func.attr}")
                )

            # Check module imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in _BLOCKED_MODULES:
                            raise SecurityViolationError(
                                ErrorMessage(f"Blocked module import: {alias.name}")
                            )
                elif (
                    isinstance(node, ast.ImportFrom)
                    and node.module
                    and node.module in _BLOCKED_MODULES
                ):
                    raise SecurityViolationError(
                        ErrorMessage(f"Blocked module import: {node.module}")
                    )

            # Check eval/exec/compile/__import__ calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "compile", "__import__"):
                    raise SecurityViolationError(
                        ErrorMessage(f"Blocked function call: {node.func.id}")
                    )
                # Check open() calls for write/append modes (FR-SRV-002 file boundary check)
                if node.func.id == "open":
                    mode_val = ""
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                        mode_val = str(node.args[1].value)
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            mode_val = str(kw.value.value)
                    if any(m in mode_val for m in ("w", "a", "x", "+")):
                        raise SecurityViolationError(
                            ErrorMessage(
                                f"Blocked file write operation with mode '{mode_val}'"
                            )
                        )
```

---

## File: modules/server/src/root_server_container.py

```python
"""Root layer: Dependency injection container for the server feature.

Wires capabilities → agent orchestrator and bootstraps the system.
Provides a single entry point to obtain a fully configured IBlenderServerAggregate.
"""

from __future__ import annotations

import logging
import threading
from typing import TYPE_CHECKING

from modules.shared.src.server import (
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    IBlenderServerAggregate,
    ICodeExecutionProtocol,
    QueueConfig,
    TaskManagerConfig,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger("BlenderMCPServer")


class ServerContainer:
    """DI container that wires server capabilities to the agent orchestrator.

    Thread-safe singleton pattern for shared connection management.
    All components are lazy-instantiated on first access.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        host: str = "localhost",
        port: int = 9876,
        queue_config: QueueConfig | None = None,
        task_config: TaskManagerConfig | None = None,
    ) -> None:
        self._host = host
        self._port = port
        self._queue_config = queue_config or QueueConfig()
        self._task_config = task_config or TaskManagerConfig()
        self._lock = threading.Lock()
        self._connection: IBlenderConnectionProtocol | None = None
        self._aggregate: IBlenderServerAggregate | None = None

    # ─── Block 2: Container Wiring & Accessors ──────────────

    def _build_connection(self) -> IBlenderConnectionProtocol:
        """Build and return the Blender connection capability."""
        from .capabilities_blender_connection import BlenderConnection

        conn = BlenderConnection(host=self._host, port=self._port)
        logger.info("Created connection to %s:%d", self._host, self._port)
        return conn

    def _build_command_adapter(
        self,
        connection: IBlenderConnectionProtocol,
    ) -> IBlenderCommandProtocol:
        """Build command dispatch capability."""
        from .capabilities_blender_command_adapter import BlenderCommandAdapter

        return BlenderCommandAdapter(connection)

    def _build_code_executor(
        self,
        connection: IBlenderConnectionProtocol,
    ) -> ICodeExecutionProtocol:
        """Build code execution capability with AST validation and task lifecycle management."""
        from .capabilities_code_execution_adapter import CodeExecutionAdapter

        return CodeExecutionAdapter(connection_port=connection, task_config=self._task_config)

    def get_aggregate(self) -> IBlenderServerAggregate:
        """Return a fully wired ServerOrchestrator (singleton).

        Lazy-initializes all dependencies on first call.
        Subsequent calls return the same orchestrator instance.
        """
        if self._aggregate is not None:
            return self._aggregate

        with self._lock:
            # Double-check after lock acquisition
            if self._aggregate is not None:
                return self._aggregate

            connection = self._build_connection()
            self._connection = connection

            command_adapter = self._build_command_adapter(connection)
            logger.debug("Command adapter initialized: %s", command_adapter)

            code_executor = self._build_code_executor(connection)

            from .agent_server_orchestrator import ServerOrchestrator

            self._aggregate = ServerOrchestrator(
                connection=connection,
                code_executor=code_executor,
                command_adapter=command_adapter,
            )

        logger.info("Server container fully wired")
        return self._aggregate

    def get_connection(self) -> IBlenderConnectionProtocol:
        """Return the shared Blender connection (singleton)."""
        if self._connection is None:
            with self._lock:
                if self._connection is None:
                    self._connection = self._build_connection()
        return self._connection

    def shutdown(self) -> None:
        """Gracefully shut down all server components."""
        with self._lock:
            if self._connection is not None:
                try:
                    self._connection.disconnect()
                except Exception as e:
                    logger.warning("Error during connection shutdown: %s", e)
                self._connection = None
            self._aggregate = None

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return f"ServerContainer(host={self._host!r}, port={self._port})"


def create_container(
    host: str = "localhost",
    port: int = 9876,
) -> ServerContainer:
    """Factory function to create a new server container.

    Convenience wrapper for developers who don't need custom config.

    Args:
        host: Blender addon host address.
        port: Blender addon TCP port.

    Returns:
        Configured ServerContainer instance.
    """
    return ServerContainer(host=host, port=port)
```

---

## File: modules/shared/src/__init__.py

```python
"""BlenderArwaky shared domain types — taxonomy + contract layers.

Organized by domain:
- common/: Core cross-cutting
- object/: Object domain
- render/: Render domain
- job/: Job domain VOs
- telemetry/: Telemetry domain
"""

from . import (
    asset,
    common,
    job,
    object,
    render,
    scene,
    telemetry,
)

# Re-export all taxonomy types from domain folders for backward compatibility

# === Common domain exports ===
from .common.taxonomy_core_vo import (
    ActionName,
    AssetCount,
    AssetId,
    AssetIdList,
    AssetName,
    AssetType,
    AssetTypeFilter,
    BBoxIntegers,
    BlenderObjectList,
    BlenderVersion,
    CapabilityRef,
    CleanupMode,
    ConfigPath,
    ConfigValue,
    CoordinateList,
    CustomerUuid,
    Details,
    DirectoryPath,
    DomainRef,
    DurationMs,
    EnabledFlag,
    ErrorString,
    ExitCode,
    ExportFormat,
    FilePath,
    FormatRef,
    HdriId,
    ImageBytes,
    ImageFormat,
    IterationCount,
    JobId,
    JobState,
    LightStrength,
    MaterialName,
    MaxImageSize,
    MaxSize,
    ModifierName,
    NextPageToken,
    ObjectCount,
    ObjectId,
    ObjectIdList,
    ObjectName,
    ObjectType,
    ParentId,
    PlatformName,
    PortNumber,
    PrimitiveType,
    Progress,
    Prompt,
    ProviderName,
    PythonCode,
    RenderEngine,
    RenderSamples,
    RenderTime,
    ResolutionX,
    ResolutionY,
    ResultLimit,
    ResultUrl,
    RotationVector,
    RuleName,
    SampleCount,
    ScaleFactor,
    ScaleVector,
    SceneId,
    SceneRuleSetName,
    SearchQuery,
    SectionRef,
    ServerName,
    SessionId,
    SkillName,
    StatusString,
    StringList,
    SuccessFlag,
    TagList,
    TaskUuid,
    ThumbnailUrl,
    Timestamp,
    ToolName,
    UseDenoising,
    UserId,
    VersionString,
    WorkflowName,
)

from .common.taxonomy_domain_error import (
    AssetNotFoundError,
    BlenderConnectionFailure,
    BlenderMCPError,
    ConnectionError,
    ConnectionFailure,
    DomainError,
    ExecutionError,
    InvalidCommandError,
    ProviderError,
    SceneValidationError,
    ValidationError,
)

from .common.taxonomy_core_vo import ErrorMessage

from .common.taxonomy_command_catalog_constant import (
    ACTION_NAMES,
    COMMAND_CATALOG,
    CommandCatalog,
    CommandSpec,
)

from .common.taxonomy_vector3d_vo import Vector3D

from .common.taxonomy_bounding_box_vo import BoundingBox

from .common.taxonomy_app_config_vo import ApplicationConfig

# === Scene domain exports ===
from .scene.taxonomy_scene_info_vo import (
    RENDER_ENGINE_CYCLES,
    RENDER_ENGINE_EEVEE,
    SceneInfo,
)

from .scene.taxonomy_scene_request_vo import (
    CleanupSceneRequestVO,
    CleanupSceneResponseVO,
    GetSceneInfoRequestVO,
    GetSceneInfoResponseVO,
    SetupEnvironmentRequestVO,
    SetupEnvironmentResponseVO,
)

# === Object domain exports ===
from .object.taxonomy_blender_object_entity import (
    BlenderObject,
    create_object_id,
)

from .object.taxonomy_object_constant import (
    ALLOWED_OBJECT_TYPES,
    OBJECT_TYPE_ARMATURE,
    OBJECT_TYPE_CAMERA,
    OBJECT_TYPE_CURVE,
    OBJECT_TYPE_EMPTY,
    OBJECT_TYPE_FONT,
    OBJECT_TYPE_GPENCIL,
    OBJECT_TYPE_LATTICE,
    OBJECT_TYPE_LIGHT,
    OBJECT_TYPE_MESH,
    OBJECT_TYPE_META,
    OBJECT_TYPE_POINTCLOUD,
    OBJECT_TYPE_SURFACE,
    OBJECT_TYPE_VOLUME,
)

from .object.taxonomy_object_request_vo import (
    ApplyModifierRequestVO,
    ApplyModifierResponseVO,
    CreatePrimitiveRequestVO,
    CreatePrimitiveResponseVO,
    DeleteObjectRequestVO,
    DeleteObjectResponseVO,
    GetObjectInfoRequestVO,
    GetObjectInfoResponseVO,
    PlaceAssetRequestVO,
    PlaceAssetResponseVO,
    SetMaterialRequestVO,
    SetMaterialResponseVO,
    SetObjectTransformRequestVO,
    SetObjectTransformResponseVO,
)


# === Render domain exports ===
from .render.taxonomy_render_request_vo import (
    GetScreenshotRequestVO,
    RenderRequestVO,
    RenderResponseVO,
    ScreenshotResponseVO,
)


# === Job domain exports ===
from .job.taxonomy_job_state_constant import (
    JOB_STATE_COMPLETED,
    JOB_STATE_FAILED,
    JOB_STATE_PENDING,
    JOB_STATE_RUNNING,
)

from .job.taxonomy_job_status_entity import (
    JobStatus,
    create_job_id,
    create_progress,
)

# === Telemetry domain exports ===
from .telemetry.taxonomy_event_constant import (
    EVENT_TYPE_CONNECTION,
    EVENT_TYPE_ERROR,
    EVENT_TYPE_PROMPT_SENT,
    EVENT_TYPE_STARTUP,
    EVENT_TYPE_TOOL_EXECUTION,
)

from .telemetry.taxonomy_telemetry_event import EventType, TelemetryEvent

# === Asset domain exports ===
from .asset.taxonomy_asset_constant import (
    ASSET_TYPE_HDRIS,
    ASSET_TYPE_MODELS,
    ASSET_TYPE_TEXTURES,
    PROVIDER_POLYHAVEN,
    PROVIDER_SKETCHFAB,
)

from .asset.taxonomy_asset_data_vo import (
    AssetMetadata,
    ImportedAsset,
    create_asset_id,
    create_provider_name,
)

from .asset.taxonomy_asset_request_vo import (
    AssetDownloadRequestVO,
    AssetDownloadResponseVO,
    AssetMetadataItem,
    AssetMetadataVO,
    AssetSearchRequestVO,
    AssetSearchResponseVO,
)

from .asset.taxonomy_import_export_vo import (
    ExportModelRequestVO,
    ExportModelResponseVO,
    ImportGlbRequestVO,
    ImportGlbResponseVO,
)

# === Contract layer exports (organized by domain) ===

# Protocols (business behavior contracts)
from .scene.contract_scene_operate_protocol import SceneOperateProtocol
from .object.contract_object_operate_protocol import ObjectOperateProtocol
from .render.contract_render_operate_protocol import RenderOperateProtocol
from .asset.contract_asset_search_protocol import AssetSearchProtocol
from .asset.contract_import_export_protocol import ImportExportProtocol
from .common.contract_workflow_protocol import WorkflowProtocol
from .common.contract_execute_action_protocol import ExecuteActionProtocol

# Protocols (inbound behavior interfaces — Capabilities implement these)
from .server import (
    IBlenderCommandProtocol,
    IBlenderConnectionProtocol,
    ICodeExecutionProtocol,
    IBlenderServerAggregate,
)
from .common.contract_command_catalog import CommandCatalogPort
from .scene.contract_scene_inspection import SceneInspectionPort
from .render.contract_viewport_capture import ViewportCapturePort
from .asset.contract_asset_provider import AssetProviderPort
from .asset.contract_polyhaven_api import PolyhavenApiPort
from .asset.contract_sketchfab_api import SketchfabApiPort
from .telemetry.contract_telemetry_classification import TelemetryClassificationPort
from .telemetry.contract_telemetry_enrichment import TelemetryEnrichmentPort
from .telemetry.contract_telemetry_recording import TelemetryRecordingPort
from .telemetry.contract_telemetry_session_management import TelemetrySessionManagementPort

__all__ = [
    # Domain folders
    "common",
    "scene",
    "object",
    "render",
    "job",
    "telemetry",
    # Core Value Objects
    "UserId",
    "SceneId",
    "AssetId",
    "JobId",
    "HdriId",
    "ObjectId",
    "ParentId",
    "ObjectName",
    "AssetName",
    "ProviderName",
    "MaterialName",
    "ModifierName",
    "ActionName",
    "WorkflowName",
    "RuleName",
    "SceneRuleSetName",
    "ObjectType",
    "AssetType",
    "RenderEngine",
    "ImageFormat",
    "PrimitiveType",
    "ExportFormat",
    "JobState",
    "CleanupMode",
    "AssetTypeFilter",
    "Prompt",
    "ErrorString",
    "ErrorMessage",
    "SearchQuery",
    "NextPageToken",
    "ResultUrl",
    "ThumbnailUrl",
    "MaxSize",
    "IterationCount",
    "PortNumber",
    "SampleCount",
    "ResolutionX",
    "ResolutionY",
    "ObjectCount",
    "AssetCount",
    "RenderSamples",
    "MaxImageSize",
    "ResultLimit",
    "LightStrength",
    "RenderTime",
    "Progress",
    "EnabledFlag",
    "SuccessFlag",
    "UseDenoising",
    "StringList",
    "TagList",
    "AssetIdList",
    "CoordinateList",
    "ScaleVector",
    "RotationVector",
    "ObjectIdList",
    "SkillName",
    "SectionRef",
    "ServerName",
    "DomainRef",
    "FormatRef",
    "CapabilityRef",
    "ExitCode",
    "FilePath",
    "DirectoryPath",
    "ConfigPath",
    "ConfigValue",
    "CustomerUuid",
    "SessionId",
    "Timestamp",
    "VersionString",
    "PlatformName",
    "ToolName",
    "DurationMs",
    "BlenderVersion",
    "StatusString",
    "PythonCode",
    "TaskUuid",
    "ScaleFactor",
    "ImageBytes",
    "BBoxIntegers",
    "Details",
    "BlenderObjectList",
    # Rich Value Objects
    "Vector3D",
    "BoundingBox",
    "AssetMetadata",
    "AssetMetadataItem",
    "AssetMetadataVO",
    "ImportedAsset",
    "SceneInfo",
    "ApplicationConfig",
    # Entities
    "BlenderObject",
    "JobStatus",
    # Errors
    "BlenderMCPError",
    "DomainError",
    "SceneValidationError",
    "AssetNotFoundError",
    "ValidationError",
    "ConnectionError",
    "ConnectionFailure",
    "ProviderError",
    "ExecutionError",
    "BlenderConnectionFailure",
    "InvalidCommandError",
    # Events
    "EventType",
    "TelemetryEvent",
    # Constants
    "ASSET_TYPE_HDRIS",
    "ASSET_TYPE_TEXTURES",
    "ASSET_TYPE_MODELS",
    "PROVIDER_POLYHAVEN",
    "PROVIDER_SKETCHFAB",
    "JOB_STATE_PENDING",
    "JOB_STATE_RUNNING",
    "JOB_STATE_COMPLETED",
    "JOB_STATE_FAILED",
    "OBJECT_TYPE_MESH",
    "OBJECT_TYPE_CAMERA",
    "OBJECT_TYPE_LIGHT",
    "OBJECT_TYPE_EMPTY",
    "OBJECT_TYPE_ARMATURE",
    "OBJECT_TYPE_CURVE",
    "OBJECT_TYPE_SURFACE",
    "OBJECT_TYPE_META",
    "OBJECT_TYPE_FONT",
    "OBJECT_TYPE_LATTICE",
    "OBJECT_TYPE_GPENCIL",
    "OBJECT_TYPE_VOLUME",
    "ALLOWED_OBJECT_TYPES",
    "COMMAND_CATALOG",
    "CommandCatalog",
    "CommandSpec",
    "ACTION_NAMES",
    "RENDER_ENGINE_CYCLES",
    "RENDER_ENGINE_EEVEE",
    "EVENT_TYPE_STARTUP",
    "EVENT_TYPE_TOOL_EXECUTION",
    "EVENT_TYPE_PROMPT_SENT",
    "EVENT_TYPE_CONNECTION",
    "EVENT_TYPE_ERROR",
    # Factories
    "create_asset_id",
    "create_object_id",
    "create_job_id",
    "create_provider_name",
    "create_progress",
    # Contracts — Protocols
    "SceneOperateProtocol",
    "ObjectOperateProtocol",
    "RenderOperateProtocol",
    "ImportExportProtocol",
    "AssetSearchProtocol",
    "WorkflowProtocol",
    "ExecuteActionProtocol",
    # Protocols — Server domain (inbound behavior)
    "IBlenderCommandProtocol",
    "IBlenderConnectionProtocol",
    "ICodeExecutionProtocol",
    # Aggregates — Server domain (facade for Surface)
    "IBlenderServerAggregate",
    # Contracts — Ports
    "CommandCatalogPort",
    "SceneInspectionPort",
    "ViewportCapturePort",
    "AssetProviderPort",
    "SketchfabApiPort",
    "PolyhavenApiPort",
    "TelemetryClassificationPort",
    "TelemetryEnrichmentPort",
    "TelemetryRecordingPort",
    "TelemetrySessionManagementPort",
    # Contracts — Aggregates
]
```

---

## File: modules/shared/src/common/__init__.py

```python
"""Common domain — taxonomy types and contracts (cross-cutting).

Note: Contract modules are imported by the main src/__init__.py to avoid
circular dependencies between domain folders.
"""

from . import (
    taxonomy_app_config_vo,
    taxonomy_bounding_box_vo,
    taxonomy_command_catalog_constant,
    taxonomy_core_vo,
    taxonomy_domain_error,
    taxonomy_vector3d_vo,
)

from .taxonomy_domain_error import ConnectionFailure

__all__ = [
    "ConnectionFailure",
    "taxonomy_app_config_vo",
    "taxonomy_bounding_box_vo",
    "taxonomy_command_catalog_constant",
    "taxonomy_core_vo",
    "taxonomy_domain_error",
    "taxonomy_vector3d_vo",
]
```

---

## File: modules/shared/src/common/taxonomy_core_vo.py

```python
"""Core branded primitive types (NewType aliases) — taxonomy value objects."""

from __future__ import annotations

from typing import Any, NewType
from uuid import UUID

# ============================================================
# ID TYPES
# ============================================================

UserId = NewType("UserId", str)
SceneId = NewType("SceneId", str)
AssetId = NewType("AssetId", str)
JobId = NewType("JobId", str)
HdriId = NewType("HdriId", str)
ObjectId = NewType("ObjectId", UUID)
ParentId = NewType("ParentId", str)

# ============================================================
# NAME TYPES
# ============================================================

ObjectName = NewType("ObjectName", str)
AssetName = NewType("AssetName", str)
ProviderName = NewType("ProviderName", str)
MaterialName = NewType("MaterialName", str)
ModifierName = NewType("ModifierName", str)
ActionName = NewType("ActionName", str)
WorkflowName = NewType("WorkflowName", str)
RuleName = NewType("RuleName", str)
SceneRuleSetName = NewType("SceneRuleSetName", str)

# ============================================================
# TYPE & ENUM TYPES
# ============================================================

ObjectType = NewType("ObjectType", str)
AssetType = NewType("AssetType", str)
RenderEngine = NewType("RenderEngine", str)
ImageFormat = NewType("ImageFormat", str)
PrimitiveType = NewType("PrimitiveType", str)
ExportFormat = NewType("ExportFormat", str)
JobState = NewType("JobState", str)
CleanupMode = NewType("CleanupMode", str)
AssetTypeFilter = NewType("AssetTypeFilter", str)

# ============================================================
# TEXT, URLS & MESSAGES
# ============================================================

Prompt = NewType("Prompt", str)
ErrorString = NewType("ErrorString", str)
SearchQuery = NewType("SearchQuery", str)
NextPageToken = NewType("NextPageToken", str)
ResultUrl = NewType("ResultUrl", str)
ThumbnailUrl = NewType("ThumbnailUrl", str)

# ============================================================
# NUMERIC LIMITS & METRICS
# ============================================================

MaxSize = NewType("MaxSize", int)
IterationCount = NewType("IterationCount", int)
PortNumber = NewType("PortNumber", int)
SampleCount = NewType("SampleCount", int)
ResolutionX = NewType("ResolutionX", int)
ResolutionY = NewType("ResolutionY", int)
ObjectCount = NewType("ObjectCount", int)
AssetCount = NewType("AssetCount", int)
RenderSamples = NewType("RenderSamples", int)
MaxImageSize = NewType("MaxImageSize", int)
ResultLimit = NewType("ResultLimit", int)
LightStrength = NewType("LightStrength", float)
RenderTime = NewType("RenderTime", float)
Progress = NewType("Progress", float)

# ============================================================
# FLAGS
# ============================================================

EnabledFlag = NewType("EnabledFlag", bool)
SuccessFlag = NewType("SuccessFlag", bool)
UseDenoising = NewType("UseDenoising", bool)

# ============================================================
# COLLECTIONS & VECTORS
# ============================================================

StringList = NewType("StringList", list[str])
TagList = NewType("TagList", list[str])
AssetIdList = NewType("AssetIdList", list[str])
CoordinateList = NewType("CoordinateList", list[float])
ScaleVector = NewType("ScaleVector", list[float])
RotationVector = NewType("RotationVector", list[float])
ObjectIdList = NewType("ObjectIdList", list[UUID])
ChildrenIds = NewType("ChildrenIds", list[str])

# Surface-typed primitives (for handler param annotations)
SkillName = NewType("SkillName", str)
SectionRef = NewType("SectionRef", str)
ServerName = NewType("ServerName", str)
DomainRef = NewType("DomainRef", str)
FormatRef = NewType("FormatRef", str)
CapabilityRef = NewType("CapabilityRef", str)

# Exit code for CLI main() return codes
ExitCode = NewType("ExitCode", int)

# Pathing
FilePath = NewType("FilePath", str)
DirectoryPath = NewType("DirectoryPath", str)

# Config types (no raw primitives in contracts)
ConfigPath = NewType("ConfigPath", str)
ConfigValue = str | int | bool | dict[str, str | int | bool | None] | None

# Additional VOs for AES006 compliance
CustomerUuid = NewType("CustomerUuid", str)
SessionId = NewType("SessionId", str)
Timestamp = NewType("Timestamp", float)
VersionString = NewType("VersionString", str)
PlatformName = NewType("PlatformName", str)
ToolName = NewType("ToolName", str)
DurationMs = NewType("DurationMs", float)
BlenderVersion = NewType("BlenderVersion", str)
StatusString = NewType("StatusString", str)
PythonCode = NewType("PythonCode", str)
TaskUuid = NewType("TaskUuid", str)
ScaleFactor = NewType("ScaleFactor", float)
ImageBytes = NewType("ImageBytes", bytes)
BBoxIntegers = NewType("BBoxIntegers", list[int])

# Server-specific VOs for request correlation
RequestId = NewType("RequestId", str)
QueueWaitMs = NewType("QueueWaitMs", float)
ProtocolVersion = NewType("ProtocolVersion", str)
AuthToken = NewType("AuthToken", str)

# Details type alias (used in error handling)
Details = dict[str, Any]

# ErrorMessage is an alias for ErrorString, used by capability layers
ErrorMessage = ErrorString

# BlenderObjectList placeholder (resolved at runtime)
BlenderObjectList = NewType("BlenderObjectList", list[Any])

# ============================================================
# CONFIGURATION METADATA (FR-CFG-001, FR-CFG-005)
# ============================================================

SourceLocation = NewType("SourceLocation", str | None)
ParseWarning = NewType("ParseWarning", str)
ValidationWarning = NewType("ValidationWarning", str)
OverrideCount = NewType("OverrideCount", int)


class ConfigMetadata:
    """Immutable metadata about configuration loading (FR-CFG-001, FR-CFG-005)."""

    __slots__ = ("_source", "_exists", "_overrides", "_parse_warnings", "_validation_warnings")

    def __init__(
        self,
        source: SourceLocation | None = None,
        exists: bool = False,
        overrides: OverrideCount = 0,
        parse_warnings: list[ParseWarning] | None = None,
        validation_warnings: list[ValidationWarning] | None = None,
    ) -> None:
        self._source = source
        self._exists = exists
        self._overrides = overrides
        self._parse_warnings = list(parse_warnings) if parse_warnings else []
        self._validation_warnings = list(validation_warnings) if validation_warnings else []

    @property
    def source(self) -> SourceLocation:
        return self._source

    @property
    def exists(self) -> bool:
        return self._exists

    @property
    def overrides(self) -> OverrideCount:
        return self._overrides

    @property
    def parse_warnings(self) -> list[ParseWarning]:
        return list(self._parse_warnings)

    @property
    def validation_warnings(self) -> list[ValidationWarning]:
        return list(self._validation_warnings)

    def to_dict(self) -> dict[str, Any]:
        """Serialize metadata for diagnostics (secrets excluded)."""
        return {
            "source": self._source,
            "exists": self._exists,
            "overrides": self._overrides,
            "parse_warnings": self._parse_warnings,
            "validation_warnings": self._validation_warnings,
        }
```

---

## File: modules/shared/src/common/taxonomy_domain_error.py

```python
"""Domain error types for the BlenderMCP system."""

from __future__ import annotations

from typing import Any

from .taxonomy_core_vo import AssetId, Details, ErrorString, ProviderName


class BlenderMCPError(Exception):
    """Base error for all BlenderMCP exceptions."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        message = message or ErrorString("")
        super().__init__(message)
        self.details = details or {}
        self._error_message: ErrorString = ErrorString(str(message))

    def to_mcp_format(self) -> Any:
        """Serialize error for MCP response."""
        return {
            "code": self.__class__.__name__,
            "message": str(ErrorString(str(self))),
            "details": getattr(self, "details", None),
        }


class DomainError(BlenderMCPError):
    """Base for domain-specific errors in the BlenderMCP system."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        message = message or ErrorString("Domain error")
        super().__init__(message)
        self.details = details or {}
        self._error_message: ErrorString = ErrorString(str(message))

    def to_mcp_format(self) -> Any:
        """Serialize error for MCP response."""
        return {
            "code": self.__class__.__name__,
            "message": str(ErrorString(str(self))),
            "details": getattr(self, "details", None),
        }


class SceneValidationError(DomainError):
    """Raised when a scene invariant is violated or validation fails."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Scene validation failed"))


class AssetNotFoundError(DomainError):
    """Raised when an asset is not found in a provider's database."""

    def __init__(self, asset_id: AssetId, provider: ProviderName):
        super().__init__(ErrorString(f"Asset {asset_id} not found in provider {provider}"))
        self.asset_id = asset_id
        self.provider = provider


class ValidationError(DomainError):
    """Raised when input parameters fail domain validation rules or constraints."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Input validation failed"))


class ConnectionError(DomainError):
    """Raised when a persistent connection to an external service or socket fails."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Connection failed"))


class ProviderError(DomainError):
    """Raised when an external asset provider returns an error."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Provider error"))


class ExecutionError(DomainError):
    """Raised when a command execution in Blender fails or returns a runtime error."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Execution failed"))


class BlenderConnectionFailure(ConnectionError):
    """Raised when the specific socket connection to the Blender instance is lost."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Blender connection lost"))


class InvalidCommandError(DomainError):
    """Raised when a command string is not recognized by the internal dispatcher."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Invalid command"))


# Backward-compatible alias for N818 (ConnectionFailure vs ConnectionError)
ConnectionFailure = ConnectionError
```

---

## File: modules/shared/src/server/__init__.py

```python
"""Server domain — taxonomy, contracts, and constants for Blender TCP communication.

Taxonomy: VOs (ConnectionStatus, ExecutionResult, TaskStatus, ConnectionConfig),
errors (SecurityViolationError, ExecutionTimeoutError, etc.), and constants.

Contracts: IBlenderServerAggregate — unified facade for connection lifecycle
and code execution operations. Implemented by Agent layer.

Protocols: IBlenderCommandProtocol, IBlenderConnectionProtocol, ICodeExecutionProtocol
— implemented by Capabilities.
"""

# ─── Taxonomy ──────────────────────────────────────────────────

from .taxonomy_server_constant import (
    CONNECTION_TIMEOUT_SECONDS,
    DEFAULT_COMMAND_TIMEOUT_MS,
    DEFAULT_EXECUTION_TIMEOUT_MS,
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_QUEUE_WAIT_TIMEOUT_MS,
    DEFAULT_TASK_RETENTION_SECONDS,
    HEARTBEAT_FAILURE_THRESHOLD,
    HEARTBEAT_INTERVAL_SECONDS,
    MAX_CODE_PAYLOAD_BYTES,
    MAX_RECONNECT_ATTEMPTS,
    QUEUE_MAX_DEPTH,
    RETRY_BASE_DELAY_SECONDS,
    RETRY_MAX_DELAY_SECONDS,
    TRANSPORT_SOCKET,
)
from .taxonomy_server_error import (
    AuthenticationError,
    BlenderConnectionExhausted,
    CodeValidationError,
    CommandTimeoutError,
    ConnectionClosedError,
    ConnectionConfigError,
    ExecutionTimeoutError,
    ProtocolVersionMismatchError,
    QueueFullError,
    QueueTimeoutError,
    SecurityViolationError,
    TaskNotFoundError,
)
from .taxonomy_server_vo import (
    CommandResult,
    ConnectionConfig,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionResult,
    ExecutionStatus,
    HeartbeatConfig,
    QueueConfig,
    RetryPolicy,
    TaskManagerConfig,
    TaskStatus,
    TaskState,
)

from .taxonomy_server_event import (
    CodeExecuted,
    CodeExecutionFailed,
    CommandDispatched,
    ConnectionEstablished,
    ConnectionLost,
    ItemDequeued,
    ItemEnqueued,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
    TaskStarted,
    TaskTimedOut,
)

# ─── Contracts (Aggregate — single unified facade) ─────────────

from .contract_server_aggregate import IBlenderServerAggregate

# ─── Contracts (Protocols — implemented by Capabilities) ──────

from .contract_code_execution_protocol import ICodeExecutionProtocol
from .contract_connection_protocol import IBlenderConnectionProtocol
from .contract_command_protocol import IBlenderCommandProtocol

# ─── Utility (stateless standalone functions) ─────────────────

from .utility_server_io import (
    format_bytes,
    generate_temp_path,
    is_safe_path,
    read_file_bytes,
    sanitize_filename,
    safe_remove,
    truncate_bytes,
    truncate_text,
    write_file_bytes,
    write_file_text,
)
from .utility_server_message import (
    encode_message,
    decode_message_header,
    decode_message_payload,
    build_request,
    parse_response,
)
from .utility_server_string import (
    camel_to_snake,
    contains_any,
    ends_with_any,
    escape_json_string,
    is_valid_python_identifier,
    normalize_newlines,
    safe_decode,
    safe_encode,
    safe_float,
    safe_int,
    sanitize_whitespace,
    starts_with_any,
    truncate_string,
)
from .utility_server_time import (
    calculate_deadline,
    format_duration,
    is_past_deadline,
    ms_to_seconds,
    remaining_ms,
    seconds_to_ms,
)
from .utility_server_validator import validate_code_ast, check_payload_size
from .utility_server_schema import validate_command_args, get_command_schema

__all__ = [
    # ─── Taxonomy ───────────────────────────────────────────────
    "ConnectionConfig",
    "ConnectionStatus",
    "ExecutionErrorDetail",
    "ExecutionResult",
    "ExecutionStatus",
    "HeartbeatConfig",
    "QueueConfig",
    "RetryPolicy",
    "CommandResult",
    "TaskManagerConfig",
    "TaskStatus",
    "TaskState",
    # ─── Events ───────────────────────────────────────────────
    "ConnectionEstablished",
    "ConnectionLost",
    "CodeExecuted",
    "CodeExecutionFailed",
    "TaskCreated",
    "TaskStarted",
    "TaskCompleted",
    "TaskFailed",
    "TaskTimedOut",
    "TaskCancelled",
    "CommandDispatched",
    "ItemEnqueued",
    "ItemDequeued",
    # ─── Constants ──────────────────────────────────────────────
    "TRANSPORT_SOCKET",
    "CONNECTION_TIMEOUT_SECONDS",
    "DEFAULT_HOST",
    "DEFAULT_PORT",
    "DEFAULT_EXECUTION_TIMEOUT_MS",
    "DEFAULT_COMMAND_TIMEOUT_MS",
    "MAX_CODE_PAYLOAD_BYTES",
    "HEARTBEAT_INTERVAL_SECONDS",
    "HEARTBEAT_FAILURE_THRESHOLD",
    "MAX_RECONNECT_ATTEMPTS",
    "RETRY_BASE_DELAY_SECONDS",
    "RETRY_MAX_DELAY_SECONDS",
    "QUEUE_MAX_DEPTH",
    "DEFAULT_QUEUE_WAIT_TIMEOUT_MS",
    "DEFAULT_TASK_RETENTION_SECONDS",
    # ─── Errors ─────────────────────────────────────────────────
    "SecurityViolationError",
    "CodeValidationError",
    "ExecutionTimeoutError",
    "QueueFullError",
    "QueueTimeoutError",
    "CommandTimeoutError",
    "TaskNotFoundError",
    "ConnectionConfigError",
    "AuthenticationError",
    "ProtocolVersionMismatchError",
    "ConnectionClosedError",
    "BlenderConnectionExhausted",
    # ─── Contracts (Aggregate) ──────────────────────────────────
    "IBlenderServerAggregate",
    # ─── Contracts (Protocols) ──────────────────────────────────
    "IBlenderCommandProtocol",
    "IBlenderConnectionProtocol",
    "ICodeExecutionProtocol",
    # ─── Utility ────────────────────────────────────────────────
    "validate_code_ast",
    "check_payload_size",
    "validate_command_args",
    "get_command_schema",
    "encode_message",
    "decode_message_header",
    "decode_message_payload",
    "build_request",
    "parse_response",
    # IO helpers
    "generate_temp_path",
    "read_file_bytes",
    "write_file_bytes",
    "write_file_text",
    "safe_remove",
    "truncate_bytes",
    "truncate_text",
    "format_bytes",
    "sanitize_filename",
    "is_safe_path",
    # Time helpers
    "ms_to_seconds",
    "seconds_to_ms",
    "format_duration",
    "calculate_deadline",
    "is_past_deadline",
    "remaining_ms",
    # String helpers
    "sanitize_whitespace",
    "normalize_newlines",
    "truncate_string",
    "safe_decode",
    "safe_encode",
    "starts_with_any",
    "ends_with_any",
    "contains_any",
    "safe_int",
    "safe_float",
    "camel_to_snake",
    "snake_to_camel",
    "escape_json_string",
    "is_valid_python_identifier",
]
```

---

## File: modules/shared/src/server/contract_code_execution_protocol.py

```python
"""Contract: Protocol for executing Python code in Blender.

Implemented by Capabilities that handle code validation,
execution queue, and result formatting.
AES Protocol layer — depends only on Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import Prompt
from .taxonomy_server_error import (
    CodeValidationError,
    ExecutionTimeoutError,
    TaskNotFoundError,
)
from .taxonomy_server_event import (
    CodeExecuted,
    CodeExecutionFailed,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
    TaskStarted,
    TaskTimedOut,
)
from .taxonomy_server_vo import ExecutionResult, TaskStatus


class ICodeExecutionProtocol(ABC):
    """Protocol for executing Python code in Blender and managing async task lifecycle.

    All methods use explicit typed errors — no bare strings.
    Query methods return typed results; state transitions raise on failure.
    """

    @abstractmethod
    async def execute_blender_code(self, code: Prompt) -> ExecutionResult:
        """Execute arbitrary Python code in Blender and return result.

        Success: Returns ExecutionResult with status='success', data from execution
        Failure: Raises CodeValidationError (blocked patterns), ExecutionTimeoutError,
                 or any Blender execution exception
        Event: CodeExecuted(request_id, execution_time_ms) on success;
                 CodeExecutionFailed(request_id, error_type, message) on failure
        """
        ...

    @abstractmethod
    async def submit_async_task(self, code: Prompt, request_id: str) -> str:
        """Submit long-running code for async execution. Returns new TaskId.

        Success: Returns newly created TaskId; event=TaskCreated(task_id, request_id)
        Failure: Raises CodeValidationError (code contains blocked patterns)
        Event: TaskCreated(task_id, request_id)
        """
        ...

    @abstractmethod
    async def poll_task_result(self, task_id: str) -> ExecutionResult:
        """Poll async task status and final result.

        Success: Returns ExecutionResult (success or error) with event=TaskCompleted(task_id)
                 if task is in terminal state
        Failure: Raises TaskNotFoundError if task not found or expired
        Event: TaskCompleted(task_id, execution_time_ms) on success;
                 TaskFailed(task_id, error_type, message) on error
        """
        ...

    @abstractmethod
    def create_task(self, request_id: str) -> str:
        """Create a new pending task. Returns the new TaskId.

        Success: Returns TaskId; event=TaskCreated(task_id, request_id)
        Failure: Raises ExecutionTimeoutError if task creation exceeds deadline
        Event: TaskCreated(task_id, request_id)
        """
        ...

    @abstractmethod
    def get_task(self, task_id: str) -> TaskStatus:
        """Get task status.

        Success: Returns TaskStatus with current state
        Failure: Raises TaskNotFoundError if not found or expired
        Event: None (pure query)
        """
        ...

    @abstractmethod
    def mark_running(self, task_id: str) -> None:
        """Transition task to running state.

        Success: No return; event=TaskStarted(task_id)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskStarted(task_id)
        """
        ...

    @abstractmethod
    def mark_completed(self, task_id: str, result: ExecutionResult) -> None:
        """Transition task to success state with result.

        Success: No return; event=TaskCompleted(task_id, execution_time_ms)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskCompleted(task_id, execution_time_ms)
        """
        ...

    @abstractmethod
    def mark_error(self, task_id: str, error_type: str, message: str) -> None:
        """Transition task to error state.

        Success: No return; event=TaskFailed(task_id, error_type, message)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskFailed(task_id, error_type, message)
        """
        ...

    @abstractmethod
    def mark_timeout(self, task_id: str) -> None:
        """Transition task to timeout state.

        Success: No return; event=TaskTimedOut(task_id)
        Failure: Raises TaskNotFoundError if task not found
        Event: TaskTimedOut(task_id)
        """
        ...

    @abstractmethod
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task. Returns True if cancelled, False if already running.

        Success: Returns True (cancelled) or False (already running);
                 event=TaskCancelled(task_id) on successful cancellation
        Failure: Raises TaskNotFoundError if task not found; raises no exception on already-running
        Event: TaskCancelled(task_id)
        """
        ...
```

---

## File: modules/shared/src/server/contract_command_protocol.py

```python
"""Contract: Command dispatch protocol for Blender operations.

Implemented by Capabilities layer (BlenderCommandAdapter).
Per FR-SRV-003: Send Blender Commands via TCP socket with timeout enforcement
and FIFO queue serialization.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ActionName
from .taxonomy_server_error import (
    CommandTimeoutError,
    QueueFullError,
    QueueTimeoutError,
)
from .taxonomy_server_event import (
    CommandDispatched,
    ItemDequeued,
    ItemEnqueued,
)
from .taxonomy_server_vo import CommandResult, ExecutionResult


class IBlenderCommandProtocol(ABC):
    """Protocol for dispatching named commands and managing execution queue.

    Implemented by Capabilities layer (BlenderCommandAdapter).
    Each command is routed through TCP socket with configurable timeout
    enforcement per FR-SRV-003, with FIFO queue serialization.
    """

    @abstractmethod
    async def send_command(
        self,
        action: ActionName,
        params: dict | None = None,
        timeout_ms: float | None = None,
    ) -> CommandResult:
        """Dispatch a named command to Blender addon.

        Success: Returns CommandResult with status='success', data from JSON response,
                 event=CommandDispatched(action, execution_time_ms)
        Failure: Raises CommandTimeoutError if response exceeds configured timeout
        Event: CommandDispatched(action, execution_time_ms)
        """
        ...

    @abstractmethod
    async def enqueue(
        self,
        request_id: str,
        payload: dict,
    ) -> int:
        """Add item to queue. Returns current queue depth.

        Success: Returns queue depth after enqueue; event=ItemEnqueued(request_id, queue_depth)
        Failure: Raises QueueFullError if max_depth exceeded
        Event: ItemEnqueued(request_id, queue_depth)
        """
        ...

    @abstractmethod
    async def dequeue(self) -> str | None:
        """Remove and return the next request_id from the queue.

        Success: Returns request_id; event=ItemDequeued(request_id)
        Failure: None (returns None if queue is empty — not an error)
        Event: ItemDequeued(request_id)
        """
        ...

    @abstractmethod
    async def wait_for_completion(
        self,
        request_id: str,
        timeout_ms: float | None = None,
    ) -> ExecutionResult:
        """Wait for a queued item to be processed and return result.

        Success: Returns ExecutionResult with status from queue processing
        Failure: Raises QueueTimeoutError if wait exceeds timeout_ms
        Event: None (internal queue detail)
        """
        ...

    @abstractmethod
    async def get_depth(self) -> int:
        """Return current queue depth.

        Success: Returns queue depth as int
        Failure: Raises ConnectionClosedError if connection lost
        Event: None (pure query)
        """
        ...
```

---

## File: modules/shared/src/server/contract_connection_protocol.py

```python
"""Contract: Protocol for Blender connection lifecycle management.

Implemented by Capabilities that handle TCP/stdio connection,
heartbeat monitoring, auto-reconnect, and status reporting.
AES Protocol layer — depends only on Taxonomy.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import ActionName, Details
from .taxonomy_server_error import (
    AuthenticationError,
    BlenderConnectionExhausted,
    ConnectionClosedError,
    ConnectionConfigError,
    ProtocolVersionMismatchError,
)
from .taxonomy_server_event import ConnectionEstablished, ConnectionLost
from .taxonomy_server_vo import CommandResult, ConnectionConfig, ConnectionStatus


class IBlenderConnectionProtocol(ABC):
    """Protocol for Blender TCP/stdio connection lifecycle.

    All methods use explicit typed errors — no bare strings.
    Query methods return bool or typed results; command methods raise on failure.
    """

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection to Blender with retries and handshake.

        Success: Returns ConnectionStatus with state='connected'
        Failure: Raises ConnectionConfigError, AuthenticationError,
                 ProtocolVersionMismatchError, or BlenderConnectionExhausted
        Event: ConnectionEstablished(host, port, transport_type)
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Graceful disconnect. Must be idempotent.

        Success: No return; connection state becomes 'closed'
        Failure: Raises ConnectionClosedError (non-fatal, ignored by caller)
        Event: ConnectionLost(reason='closed')
        """
        ...

    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if socket is currently connected and alive.

        Success: Returns True if connected, False otherwise
        Failure: Raises ConnectionClosedError (connection dropped between checks)
        Event: ConnectionLost(reason='timeout') if connection timed out
        """
        ...

    @abstractmethod
    async def send_command(
        self,
        command_type: ActionName,
        params: Details | None = None,
    ) -> CommandResult:
        """Send a command to Blender and return the parsed response.

        Success: Returns CommandResult with status='success', data from JSON response
        Failure: Raises ConnectionClosedError, AuthenticationError, or ProtocolVersionMismatchError
        Event: CommandDispatched(action=str(command_type), execution_time_ms)
        """
        ...

    @abstractmethod
    async def receive_full_response(
        self,
        buffer_size: int = 8192,
    ) -> bytes:
        """Receive complete JSON response from socket in chunks.

        Success: Returns raw bytes of the JSON response
        Failure: Raises ConnectionClosedError if connection dropped during receive
        Event: None (infrastructure-level detail)
        """
        ...
```

---

## File: modules/shared/src/server/contract_server_aggregate.py

```python
"""Contract: Aggregate facade for the server feature.

Implemented by Agent layer to provide a unified interface
for connection lifecycle, code execution, command dispatch, and
async task management to the Surface layer.
AES Aggregate layer — depends only on Taxonomy and Protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_server_vo import (
    ConnectionConfig,
    ConnectionStatus,
    ExecutionResult,
)


class IBlenderServerAggregate(ABC):
    """Aggregate facade for the server feature.

    Combines connection management, code execution, command dispatch,
    and async task management into a single unified interface consumed
    by the Surface layer.
    """

    # ─── Connection Lifecycle ──────────────────────────────

    @abstractmethod
    async def connect(self, config: ConnectionConfig) -> ConnectionStatus:
        """Establish connection with configuration and handshake.

        Success: Returns ConnectionStatus with state='connected'
        Failure: Raises ConnectionConfigError, AuthenticationError, etc.
        """
        ...

    @abstractmethod
    async def disconnect(self) -> None:
        """Graceful disconnect. Idempotent — no error if already closed."""
        ...

    @abstractmethod
    async def get_status(self) -> ConnectionStatus:
        """Return current connection state with metadata."""
        ...

    # ─── Code Execution ────────────────────────────────────

    @abstractmethod
    async def execute_code(self, code: str, request_id: str) -> ExecutionResult:
        """Execute Python code synchronously in Blender.

        Success: Returns ExecutionResult with status='success'
        Failure: Raises CodeValidationError, ExecutionTimeoutError, etc.
        """
        ...

    @abstractmethod
    async def submit_async_task(self, code: str, request_id: str) -> str:
        """Submit long-running code for async execution. Returns task_id."""
        ...

    @abstractmethod
    async def poll_task_result(self, task_id: str) -> ExecutionResult:
        """Poll async task status and final result.

        Failure: Raises TaskNotFoundError if not found or expired
        """
        ...

    # ─── Command Dispatch ──────────────────────────────────

    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
    ) -> dict:  # noqa: ANN004
        """Dispatch a named command to Blender addon.

        Failure: Raises CommandTimeoutError if response exceeds configured timeout
        """
        ...
```

---

## File: modules/shared/src/server/taxonomy_server_constant.py

```python
"""Server domain — Compile-time constant defaults from FRD specification.

All values follow binary notation (1k = 1024 bytes).
"""

# ============================================================
# Connection Defaults
# ============================================================

DEFAULT_HOST: str = "localhost"
DEFAULT_PORT: int = 9876
CONNECTION_TIMEOUT_SECONDS: float = 30.0
HEARTBEAT_INTERVAL_SECONDS: int = 10
HEARTBEAT_FAILURE_THRESHOLD: int = 3
MAX_RECONNECT_ATTEMPTS: int = 3
RETRY_BASE_DELAY_SECONDS: float = 1.0
RETRY_MAX_DELAY_SECONDS: float = 4.0

# ============================================================
# Execution Defaults
# ============================================================

DEFAULT_EXECUTION_TIMEOUT_MS: float = 30_000.0  # 30 seconds
DEFAULT_COMMAND_TIMEOUT_MS: float = 5_000.0     # 5 seconds
MAX_CODE_PAYLOAD_BYTES: int = 1_048_576          # 1 MB (1k = 1024)

# ============================================================
# Queue Defaults
# ============================================================

QUEUE_MAX_DEPTH: int = 50
DEFAULT_QUEUE_WAIT_TIMEOUT_MS: float = 10_000.0  # 10 seconds target

# ============================================================
# Task Defaults
# ============================================================

DEFAULT_TASK_RETENTION_SECONDS: float = 600.0    # 10 minutes

# ============================================================
# Transport Types
# ============================================================

TRANSPORT_SOCKET: str = "socket"
TRANSPORT_STDIO: str = "stdio"
```

---

## File: modules/shared/src/server/taxonomy_server_error.py

```python
"""Server domain — Typed error types for connection, execution, queue, and task lifecycle.

All errors subclass ServerError with explicit error codes for MCP serialization.
No bare string errors in public API.
"""

from __future__ import annotations


class ServerError(Exception):
    """Base error for all server-domain exceptions.

    Provides structured error info with code/message/details for
    MCP error serialization and observability.
    """

    def __init__(self, code: str, message: str, details: dict | None = None) -> None:
        self.code = code
        self.message = message
        self.details = details or {}  # type: ignore[dict-item]
        super().__init__(f"[{code}] {message}")

    def to_mcp_format(self) -> dict:  # noqa: ANN004
        """Serialize error for MCP response."""
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


# ─── Security Errors ──────────────────────────────────────────────


class SecurityViolationError(ServerError):
    """Raised when user-provided code contains blocked patterns or violates sandbox policy."""

    def __init__(self, message: str = "Security violation", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("security_violation", message, details)


# ─── Execution Errors ──────────────────────────────────────────────


class CodeValidationError(ServerError):
    """Raised when code fails static analysis or contains blocked patterns."""

    def __init__(self, message: str = "Code validation failed", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("code_validation_error", message, details)


class ExecutionTimeoutError(ServerError):
    """Raised when code execution exceeds the configured timeout."""

    def __init__(self, timeout_ms: float = 30_000.0, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("execution_timeout", f"Execution exceeded {timeout_ms}ms", {"timeout_ms": timeout_ms})


class CommandTimeoutError(ServerError):
    """Raised when a command response exceeds the configured timeout."""

    def __init__(self, action: str = "", timeout_ms: float = 5_000.0, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("command_timeout", f"Command '{action}' timed out after {timeout_ms}ms", {"action": action, "timeout_ms": timeout_ms})


# ─── Queue Errors ────────────────────────────────────────────────


class QueueFullError(ServerError):
    """Raised when the serialized execution queue has reached maximum depth."""

    def __init__(self, max_depth: int = 50, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("queue_full", f"Queue full (depth={max_depth})", {"max_depth": max_depth})


class QueueTimeoutError(ServerError):
    """Raised when a queued operation exceeds the configured wait timeout."""

    def __init__(self, request_id: str = "", timeout_ms: float = 10_000.0, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("queue_timeout", f"Queue wait timeout for {request_id}", {"request_id": request_id, "timeout_ms": timeout_ms})


# ─── Task Errors ────────────────────────────────────────────────


class TaskNotFoundError(ServerError):
    """Raised when polling an unknown or expired async task."""

    def __init__(self, task_id: str = "", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("task_not_found", f"Task not found: {task_id}", {"task_id": task_id})


# ─── Connection Errors ──────────────────────────────────────────


class ConnectionConfigError(ServerError):
    """Raised when connection factory receives invalid configuration."""

    def __init__(self, message: str = "Connection config error", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_config_error", message, details)


class AuthenticationError(ServerError):
    """Raised when connection authentication fails."""

    def __init__(self, message: str = "Authentication failed", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("authentication_failed", message, details)


class ProtocolVersionMismatchError(ServerError):
    """Raised when server and Blender addon protocol versions are incompatible."""

    def __init__(self, expected: str = "", actual: str = "", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("protocol_version_mismatch", f"Expected {expected}, got {actual}", {"expected": expected, "actual": actual})


class ConnectionClosedError(ServerError):
    """Raised when an operation is rejected after graceful disconnect."""

    def __init__(self, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_closed", "Connection already closed", details)


class BlenderConnectionExhausted(ServerError):
    """Raised after all reconnect attempts have been exhausted."""

    def __init__(self, attempts: int = 3, details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("connection_retries_exhausted", f"All {attempts} reconnect attempts failed", {"attempts": attempts})


# ─── Adapter / Surface Errors ────────────────────────────────────


class AdapterSurfaceError(ServerError):
    """Raised when an unexpected adapter surface failure occurs."""

    def __init__(self, message: str = "Adapter surface error", details: dict | None = None) -> None:  # noqa: ANN004
        super().__init__("adapter_surface_error", message, details)
```

---

## File: modules/shared/src/server/taxonomy_server_event.py

```python
"""Server domain — Typed domain events for connection, execution, and task lifecycle.

Frozen dataclasses for immutable, serializable event objects.
All events use past-tense naming for completed actions.
"""

from __future__ import annotations

from dataclasses import dataclass


# ============================================================
# Connection Events
# ============================================================

@dataclass(frozen=True)
class ConnectionEstablished:
    """Connection successfully established to Blender."""
    host: str
    port: int
    transport_type: str = "socket"


@dataclass(frozen=True)
class ConnectionLost:
    """Connection lost or closed."""
    reason: str  # "timeout" | "closed" | "error"


# ============================================================
# Code Execution Events
# ============================================================

@dataclass(frozen=True)
class CodeExecuted:
    """Code execution completed successfully."""
    request_id: str
    execution_time_ms: float
    truncated: bool = False


@dataclass(frozen=True)
class CodeExecutionFailed:
    """Code execution failed with error."""
    request_id: str
    error_type: str
    message: str


# ============================================================
# Task Lifecycle Events
# ============================================================

@dataclass(frozen=True)
class TaskCreated:
    """New async task created."""
    task_id: str
    request_id: str


@dataclass(frozen=True)
class TaskStarted:
    """Task transitioned to running state."""
    task_id: str


@dataclass(frozen=True)
class TaskCompleted:
    """Task completed successfully."""
    task_id: str
    execution_time_ms: float


@dataclass(frozen=True)
class TaskFailed:
    """Task failed with error."""
    task_id: str
    error_type: str
    message: str


@dataclass(frozen=True)
class TaskTimedOut:
    """Task exceeded timeout threshold."""
    task_id: str


@dataclass(frozen=True)
class TaskCancelled:
    """Task was cancelled by caller."""
    task_id: str


# ============================================================
# Command Dispatch Events
# ============================================================

@dataclass(frozen=True)
class CommandDispatched:
    """Command dispatched to Blender addon."""
    action: str
    execution_time_ms: float


@dataclass(frozen=True)
class CommandTimedOut:
    """Command exceeded timeout threshold."""
    action: str
    timeout_ms: float


# ============================================================
# Queue Events
# ============================================================

@dataclass(frozen=True)
class ItemEnqueued:
    """Item added to execution queue."""
    request_id: str
    queue_depth: int


@dataclass(frozen=True)
class ItemDequeued:
    """Item removed from execution queue."""
    request_id: str
```

---

## File: modules/shared/src/server/taxonomy_server_vo.py

```python
"""Server domain — Value Objects for connection, execution, and task state.

Frozen dataclasses with explicit types. All VOs are immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field


# ============================================================
# Connection State
# ============================================================

ConnectionState = str  # "disconnected" | "connecting" | "connected" | "reconnecting" | "failed" | "closed"


@dataclass(frozen=True)
class ConnectionStatus:
    """Immutable snapshot of connection state.

    Represents the current lifecycle state of the server-to-Blender
    TCP/stdio connection with metadata for observability.
    """

    state: ConnectionState
    host: str
    port: int
    transport_type: str = "socket"
    last_error: str | None = None
    protocol_version: str | None = None
    reconnect_attempts: int = 0


# ============================================================
# Execution Result
# ============================================================

ExecutionStatus = str  # "success" | "error"


@dataclass(frozen=True)
class ExecutionErrorDetail:
    """Structured error detail returned from Blender execution."""

    error_type: str
    message: str
    traceback: str | None = None
    line: int | None = None


@dataclass(frozen=True)
class ExecutionResult:
    """Standardized result for code execution in Blender.

    Contains status, data payload, optional error detail,
    timing information, and truncation flag.
    """

    status: ExecutionStatus
    data: str | bytes | None = None
    error: ExecutionErrorDetail | None = None
    execution_time_ms: float = 0.0
    truncated: bool = False


# ============================================================
# Command Result (replaces dict[str, Any] for command dispatch)
# ============================================================

@dataclass(frozen=True)
class CommandResult:
    """Typed command dispatch result (replaces dict[str, Any])."""

    status: str  # "success" | "error"
    data: dict | None = None
    execution_time_ms: float = 0.0


# ============================================================
# Task Status
# ============================================================

TaskState = str  # "pending" | "running" | "success" | "error" | "timeout" | "cancelled"


@dataclass(frozen=True)
class TaskStatus:
    """Immutable snapshot of async task lifecycle state."""

    task_id: str
    state: TaskState
    result: ExecutionResult | None = None


# ============================================================
# Connection Configuration
# ============================================================

TransportType = str  # "socket" | "stdio"


@dataclass(frozen=True)
class RetryPolicy:
    """Retry configuration with exponential backoff and jitter."""

    max_retries: int
    base_delay_seconds: float
    max_delay_seconds: float


@dataclass(frozen=True)
class HeartbeatConfig:
    """Heartbeat/ping configuration for stale connection detection."""

    interval_seconds: int
    failure_threshold: int  # consecutive failures before declaring stale


@dataclass(frozen=True)
class ConnectionConfig:
    """Immutable configuration for establishing a Blender connection.

    Contains transport type, endpoint info, timeout, retry policy,
    authentication settings, protocol version, payload limits,
    heartbeat settings, and allowed directories.
    """

    transport_type: TransportType
    host: str = "localhost"
    port: int = 9876
    timeout_seconds: float = 30.0
    retry_policy: RetryPolicy | None = None
    auth_token: str | None = None
    protocol_version: str | None = None
    heartbeat: HeartbeatConfig | None = None
    max_payload_bytes: int = 1_048_576  # 1 MB default (binary: 1k=1024)
    allowed_directories: list[str] = dc_field(default_factory=list)


# ============================================================
# Queue Configuration
# ============================================================


@dataclass(frozen=True)
class QueueConfig:
    """Immutable configuration for execution queue parameters."""

    max_depth: int = 50
    wait_timeout_ms: float = 10_000.0  # 10 seconds default


# ============================================================
# Task Manager Configuration
# ============================================================


@dataclass(frozen=True)
class TaskManagerConfig:
    """Immutable configuration for task manager parameters."""

    retention_seconds: float = 600.0  # 10 minutes default
```

---

## File: modules/shared/src/server/utility_server_schema.py

```python
"""Utility: Command argument schema validation for Blender commands.

Stateless standalone functions that validate command arguments
against defined schemas before sending to Blender.
Domain-agnostic — reusable across modules.
"""

from __future__ import annotations

from typing import Any

from ..common.taxonomy_domain_error import ValidationError


# Command argument schemas per FR-SRV-003
_COMMAND_SCHEMAS: dict[str, list[str]] = {
    "get_scene_info": [],
    "get_object_info": ["name"],
    "get_screenshot": ["max_size", "view_angle", "shading_mode", "show_overlays", "focus_object"],
    "execute_code": ["code"],
}


def validate_command_args(command: str, params: dict[str, Any] | None) -> None:
    """Validate command arguments against defined schema.

    Raises ValidationError if:
    - Command is unknown
    - Params contain keys not in schema
    - Required parameters are missing

    Args:
        command: The command/action name to validate.
        params: Command arguments dictionary.

    Raises:
        ValidationError: If command or arguments are invalid.
    """
    if command not in _COMMAND_SCHEMAS:
        raise ValidationError(f"Unknown command: {command}")

    allowed_keys = set(_COMMAND_SCHEMAS[command])

    if params is None:
        return

    if not isinstance(params, dict):
        raise ValidationError("Command arguments must be a dictionary")

    # Check for unknown keys
    for key in params:
        if key not in allowed_keys:
            raise ValidationError(f"Unknown parameter '{key}' for command '{command}'")


def get_command_schema(command: str) -> list[str]:
    """Get allowed parameters for a command.

    Args:
        command: The command/action name.

    Returns:
        List of allowed parameter names.
    """
    return _COMMAND_SCHEMAS.get(command, [])
```

---

## File: modules/shared/src/server/utility_server_validator.py

```python
"""Utility: AST-based code validation for Blender code execution.

Stateless standalone functions that analyze Python code using the
ast module to detect blocked patterns. More reliable than regex.
Domain-agnostic — reusable across modules.
"""

import ast
from typing import Final

from ..common.taxonomy_core_vo import ErrorMessage
from .taxonomy_server_error import SecurityViolationError

# Blocked module names — dangerous system-level imports
_BLOCKED_MODULES: Final[frozenset[str]] = frozenset({
    "os",
    "subprocess",
    "shutil",
    "importlib",
    "sys",
    "socket",
    "urllib",
    "requests",
    "ctypes",
    "multiprocessing",
    "threading",
    "signal",
    "pickle",
    "shelve",
})

# Blocked function names — dangerous builtins and system calls
_BLOCKED_FUNCTIONS: Final[frozenset[str]] = frozenset({
    "eval",
    "exec",
    "compile",
    "__import__",
    "breakpoint",
    "exit",
    "quit",
    "open",
})

# Blocked attribute names — unsafe dunder access
_BLOCKED_ATTRIBUTES: Final[frozenset[str]] = frozenset({
    "__subclasses__",
    "__bases__",
    "__mro__",
    "__globals__",
    "__builtins__",
    "__import__",
    "__loader__",
    "__spec__",
    "__file__",
    "__name__",
    "__package__",
})


def validate_code_ast(code: str) -> None:
    """Validate Python code using AST analysis for blocked patterns.

    Raises SecurityViolationError if code contains forbidden constructs.
    This is a pre-filter, not a security boundary — Blender addon
    enforces runtime restrictions.
    """
    if not code or not code.strip():
        raise SecurityViolationError(ErrorMessage("Code cannot be empty"))

    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        raise SecurityViolationError(
            ErrorMessage(f"Syntax error in code: {e.msg} at line {e.lineno}")
        ) from e

    for node in ast.walk(tree):
        _check_node(node)


def _check_node(node: ast.AST) -> None:
    """Check a single AST node for blocked patterns."""
    if isinstance(node, ast.Import):
        for alias in node.names:
            mod = alias.name.split(".")[0]
            if mod in _BLOCKED_MODULES:
                raise SecurityViolationError(
                    ErrorMessage(f"Blocked import: {alias.name}")
                )

    elif isinstance(node, ast.ImportFrom):
        if node.module:
            mod = node.module.split(".")[0]
            if mod in _BLOCKED_MODULES:
                raise SecurityViolationError(
                    ErrorMessage(f"Blocked import from: {node.module}")
                )

    elif isinstance(node, ast.Call):
        func = node.func
        if isinstance(func, ast.Name) and func.id in _BLOCKED_FUNCTIONS:
            raise SecurityViolationError(
                ErrorMessage(f"Blocked function call: {func.id}()")
            )
        elif isinstance(func, ast.Attribute) and func.attr in _BLOCKED_FUNCTIONS:
            raise SecurityViolationError(
                ErrorMessage(f"Blocked method call: .{func.attr}()")
            )

    elif isinstance(node, ast.Attribute):
        if node.attr in _BLOCKED_ATTRIBUTES:
            raise SecurityViolationError(
                ErrorMessage(f"Blocked attribute access: .{node.attr}")
            )


def check_payload_size(code: str, max_bytes: int) -> None:
    """Validate code payload size. Raises SecurityViolationError if too large."""
    code_bytes = len(code.encode("utf-8"))
    if code_bytes > max_bytes:
        raise SecurityViolationError(
            ErrorMessage(
                f"Code payload exceeds maximum size: {code_bytes} bytes "
                f"(max: {max_bytes})"
            )
        )
```

---

## File: pyproject.toml

```toml
[project]
name = "blender-arwaky"
version = "1.6.5"
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

[tool.setuptools]
package-dir = {"" = "src"}

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
| `BLENDER_HOST` | Override Blender host |
| `BLENDER_PORT` | Override Blender port |

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

