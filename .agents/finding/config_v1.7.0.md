# Module: config (v1.7.0)

This document contains the source code for module `config` along with related and imported definitions from the `shared` module.

## File List

- [ARCHITECTURE.md](<ARCHITECTURE.md>)
- [modules/config/FRD.md](<modules/config/FRD.md>)
- [modules/config/pyproject.toml](<modules/config/pyproject.toml>)
- [modules/config/src/agent_config_orchestrator.py](<modules/config/src/agent_config_orchestrator.py>)
- [modules/config/src/capabilities_redaction_rules.py](<modules/config/src/capabilities_redaction_rules.py>)
- [modules/config/src/capabilities_settings_loader.py](<modules/config/src/capabilities_settings_loader.py>)
- [modules/config/src/capabilities_settings_metadata.py](<modules/config/src/capabilities_settings_metadata.py>)
- [modules/config/src/capabilities_settings_retriever.py](<modules/config/src/capabilities_settings_retriever.py>)
- [modules/config/src/capabilities_workspace_resolver.py](<modules/config/src/capabilities_workspace_resolver.py>)
- [modules/config/src/root_config_container.py](<modules/config/src/root_config_container.py>)
- [modules/shared/src/common/__init__.py](<modules/shared/src/common/__init__.py>)
- [modules/shared/src/common/taxonomy_core_vo.py](<modules/shared/src/common/taxonomy_core_vo.py>)
- [modules/shared/src/common/taxonomy_domain_error.py](<modules/shared/src/common/taxonomy_domain_error.py>)
- [modules/shared/src/config/__init__.py](<modules/shared/src/config/__init__.py>)
- [modules/shared/src/config/contract_config_aggregate.py](<modules/shared/src/config/contract_config_aggregate.py>)
- [modules/shared/src/config/contract_redaction_rules_protocol.py](<modules/shared/src/config/contract_redaction_rules_protocol.py>)
- [modules/shared/src/config/contract_settings_loader_protocol.py](<modules/shared/src/config/contract_settings_loader_protocol.py>)
- [modules/shared/src/config/contract_settings_metadata_protocol.py](<modules/shared/src/config/contract_settings_metadata_protocol.py>)
- [modules/shared/src/config/contract_settings_retriever_protocol.py](<modules/shared/src/config/contract_settings_retriever_protocol.py>)
- [modules/shared/src/config/contract_workspace_resolver_protocol.py](<modules/shared/src/config/contract_workspace_resolver_protocol.py>)
- [modules/shared/src/config/taxonomy_config_constant.py](<modules/shared/src/config/taxonomy_config_constant.py>)
- [modules/shared/src/config/taxonomy_config_error.py](<modules/shared/src/config/taxonomy_config_error.py>)
- [modules/shared/src/config/taxonomy_config_event.py](<modules/shared/src/config/taxonomy_config_event.py>)
- [modules/shared/src/config/taxonomy_config_vo.py](<modules/shared/src/config/taxonomy_config_vo.py>)
- [modules/shared/src/config/utility_config_helpers.py](<modules/shared/src/config/utility_config_helpers.py>)
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

## File: modules/config/FRD.md

```markdown
# FRD — Configuration & Workspace Feature

## Purpose

Single owner for loading, validating, and providing settings to all features of **blender-arwaky**.

This feature is the only authority for settings resolution. It loads settings from files, environment, and built-in defaults, applies deterministic precedence rules, validates settings against schema, exposes immutable settings snapshots, resolves the project workspace directory, provides settings metadata, and supplies redaction rules for sensitive values.

No other feature reads settings files directly, determines precedence rules, resolves the project workspace independently, or defines its own sensitive value masking rules.

## Scope

- Load settings from file, environment, and built-in defaults
- Deterministic precedence rules across settings sources
- Type conversion for environment-provided values
- Validation schema enforcement
- Immutable settings snapshot after load
- Hierarchical setting retrieval using dot-separated paths
- Project workspace resolution
- Settings metadata exposure
- Redaction policy for secret values
- Safe parsing without arbitrary object instantiation
- Cached singleton access with thread-safe initialization
- Reload support with atomic snapshot replacement
- Strict and permissive policy modes
- Settings size and encoding limits

## Out of Scope

- Runtime process state
- Blender connection state
- Background task state
- Feature-specific business rules
- Command catalog
- Logging infrastructure
- Secret storage or secret management infrastructure
- Remote settings synchronization
- Per-user profile management
- Enforcement of redaction in output, which belongs to security policy and consuming features

## Depends On

- shared taxonomy primitives (`ConfigMetadata`, `ConfigPath`) and the shared `mcp` bootstrap aggregator for module initialization

## Provides To

All features.

Typical consumers include gateway, asset, render, scene, object, job, security policy, diagnostics, command-line tooling, and the MCP layer.

## Functional Requirements

### FR-CFG-001: Load and Apply Settings

Config is the only feature that loads settings. No other feature reads config files directly.

- **Description**: Load settings from all supported sources, apply precedence rules, validate the merged result, and expose a single immutable snapshot
- **Input**: Optional explicit settings location override, optional runtime override mapping, otherwise environment and filesystem sources
- **Output**: Immutable settings snapshot concept containing merged settings values
- **Business Rules**:
  - Settings loading follows deterministic precedence order:
    1. Explicit runtime overrides when provided
    2. Environment-based overrides
    3. Settings file values
    4. Built-in default values
  - Settings file must be parsed using safe parsing mode only
  - Arbitrary object instantiation from settings content is forbidden
  - Settings file must be UTF-8 encoded
  - Missing settings file is not fatal by default and falls back to environment and defaults
  - Missing settings file is never fatal in any policy mode (Q6): a missing settings file falls back to environment and defaults without raising
  - When no explicit path and no `BLENDERMCP_CONFIG_PATH` is set, the loader resolves `<cwd>/config.yaml` as the default settings source
  - Default policy mode is strict; permissive mode is opt-in per feature (see Configuration Keys)
  - First load is thread-safe and performed exactly once under contention (double-checked locking)
  - Malformed settings content raises configuration error in strict mode
  - Malformed settings content logs warning and falls back safely in permissive mode
  - Schema violation raises validation error in strict mode
  - Schema violation logs warning and continues where safe in permissive mode
  - Schema is a Python-native mapping (SETTINGS_SCHEMA); unknown keys produce warnings; type/required violations are errors.
  - Environment values are converted to typed values when safely detectable:
    - boolean-like values become boolean
    - integer-like values become integer
    - float-like values become float
    - null-like values become empty value
    - otherwise values remain text
  - Environment values are scalar-only (Q7): list-like or mapping-like values are NOT parsed and remain strings
  - Environment overrides use product-specific prefix and deterministic nested key convention
  - Legacy environment prefix may be accepted as fallback for backward compatibility
  - Legacy environment prefix BLENDER_MCP_ was removed in v1.7.0 (BREAKING). Only the BLENDERMCP_ prefix is recognized.
  - Settings snapshot must be immutable after successful load
  - Settings snapshot must be cached after first successful load
  - Reload must replace snapshot atomically under synchronization
  - Failed load must not expose partial settings state
  - Failed reload must retain previous valid snapshot unless strict mode requires failure propagation
  - Settings source size must be limited to prevent excessive memory usage: limit is 1 MiB (MAX_CONFIG_SIZE_BYTES); in strict mode an oversized source raises ConfigLoadError, in permissive mode it warns and skips the file source (flag-gated behind BLENDERMCP_CONFIG_V2)
  - Secret values present in settings must never be echoed into metadata, logs, or diagnostics
- **Edge Cases**: Missing settings file, malformed settings content, permission denied, empty settings file, duplicate mapping keys, unsupported tags, oversized settings file, non-UTF-8 encoding, environment override conflict, legacy environment fallback, schema unavailable, secret values in settings, symlinked settings location, settings location pointing to directory instead of file
- **Error Handling**: Configuration error for missing, unreadable, or malformed settings source in strict mode; validation error for schema violation; load error for oversized or unsafe settings content; warning-level fallback behavior in permissive mode

### FR-CFG-002: Retrieve Settings Values

Features request settings through config. Config returns immutable values or deep copies.

- **Description**: Retrieve settings values through hierarchical dot-separated paths with safe copy semantics
- **Input**: Dot-separated settings path, optional default value, optional expected type
- **Output**: Resolved settings value or default
- **Business Rules**:
  - Retrieval traverses nested settings structure by dot-separated segments
  - Missing key returns provided default value
  - Missing intermediate container returns provided default value
  - Empty path returns full settings snapshot
  - Returned snapshot and structured values must be immutable or deep-copied to prevent caller mutation
  - Numeric path segments may access list positions when current node is a list
  - Out-of-range list position returns default
  - Escaped separator may resolve literal dotted key when supported
  - `\.` resolves a literal dotted key when BLENDERMCP_CONFIG_V2 is enabled
  - Retrieval must be thread-safe and lock-free after initialization where possible
  - Retrieval must not trigger file or environment reads per request
  - Expected type mismatch returns default in permissive mode
  - Expected type mismatch raises type conversion error in strict mode
  - Default values must never be mutated by retrieval
  - Retrieval behavior must be deterministic for identical snapshot state
- **Edge Cases**: Empty path, missing key, missing intermediate key, trailing separator, leading separator, repeated separators, whitespace in path, non-text path, list position on non-list, out-of-range list position, key containing literal dot, expected type mismatch, mutable default value, deeply nested path
- **Error Handling**: Default value returned for missing keys; validation error for malformed path in strict mode; type conversion error for expected type mismatch in strict mode; mutation disallowed through immutable snapshot or copy semantics

### FR-CFG-003: Resolve Project Workspace Directory

Config determines project root. Asset and render do not determine project root rules themselves.

- **Description**: Resolve the project workspace directory using deterministic strategies and expose it as the single trusted root for file-based operations
- **Input**: None; reads environment and filesystem signals
- **Output**: Workspace directory concept representing resolved project root
- **Business Rules**:
  - Resolution follows deterministic order:
    1. Explicit workspace override when provided at runtime
    2. Product-specific workspace environment signal (BLENDERMCP_ROOT)
    3. Settings file location, using its parent directory
    4. Upward proximity search for recognized project marker concepts
    5. Platform-standard user configuration location
    6. Current working directory
  - Project marker priority should be:
    1. Primary settings source (config.yaml, config.yml) — discovered by the settings-file-location strategy (rule 3), which then uses its parent directory
    2. Product-specific settings source
    3. Project manifest (pyproject.toml)
    4. Version control metadata (.git)
  - Note: "Primary settings source" under marker priority refers to *discovery of config.yaml*, not a separate resolution strategy; the six strategy-order items (explicit → env → settings-file-parent → markers → platform → cwd) are the authoritative resolution sequence.
  - Resolved path must be normalized
  - Symbolic links must be resolved safely without unnecessary failure
  - Candidate directory must exist and be readable to be accepted
  - Invalid environment-provided path logs warning and falls through to next strategy
  - First valid candidate according to resolution order wins
  - Workspace resolution must not create directories by default
  - If no valid candidate exists, fallback to current working directory
  - If current working directory is inaccessible, raise workspace resolution error
  - Resolution result is cached for process lifetime and reused consistently across features
  - All file-writing features must derive allowed locations from this resolution rather than their own rules
- **Edge Cases**: Multiple candidate directories, symlinked directories, non-existent candidate, permission denied candidate, network-mounted filesystem, case-insensitive filesystem, settings location pointing to file versus directory, circular symbolic link, empty environment value, relative path, deleted working directory, platform-specific remote path
- **Error Handling**: Warning and fallthrough for invalid environment path; fallthrough for non-existent or unreadable candidate; workspace resolution error only when all strategies fail and working directory is inaccessible

### FR-CFG-004: Provide Settings Metadata

Config provides config source, override count, and warnings. Metadata must not leak secrets.

- **Description**: Expose diagnostic metadata about how settings were loaded, merged, and validated
- **Input**: None
- **Output**: Settings metadata concept containing source information, override information, warning list, and load timing information
- **Business Rules**:
  - Metadata MUST include exactly these five fields:
    - resolved settings source location (`source`)
    - whether settings file existed (`exists`)
    - count of applied environment overrides (`overrides`)
    - parse warning list (`parse_warnings`)
    - validation warning list (`validation_warnings`)
  - Metadata must not include secret values
  - Metadata must not include raw settings content by default
  - Override names may be listed, but override values must be redacted when sensitive
  - Metadata should be safe for diagnostics, command-line output, and MCP-facing responses
  - Metadata must reflect the current active snapshot, not stale load state
  - Metadata exposure must not mutate settings state
- **Edge Cases**: Settings file missing, overrides applied from legacy prefix, sensitive override values, validation warnings present, permissive mode fallback active, reload in progress, metadata requested before first load, oversized warning list
- **Error Handling**: Metadata retrieval returns safe partial metadata when some details are unavailable; redaction failure falls back to omitting the affected field rather than exposing it

### FR-CFG-005: Provide Redaction Rules

Config or security provides list of sensitive keys. Diagnostics, CLI, and MCP use these rules for masking.

- **Description**: Provide the authoritative list of sensitive key patterns and redaction rules used by consuming features to mask secret values. Config is the **current authoritative provider**; a security policy module may override the rule set via composition-root injection (`extra_redaction_patterns`), but config remains the default source of truth.
- **Input**: None
- **Output**: Redaction rules concept containing sensitive key patterns, pattern-based detection rules, and placeholder convention
- **Business Rules**:
  - Redaction rules define which settings keys are considered sensitive
  - Sensitive key detection supports exact key match and pattern-based match
  - Rules should cover common secret categories:
    - tokens
    - API keys
    - passwords
    - credentials
    - connection strings containing secrets
    - signing or encryption material
  - Rules may be extended via composition-root injection (extra_redaction_patterns) — not from settings at runtime
  - Rules must define placeholder convention used during masking
  - Rules themselves contain key names and patterns only, never secret values
  - Consuming features must retrieve rules from config or security policy and must not hard-code their own lists
  - Rule updates must be reflected consistently across diagnostics, command-line output, and MCP-facing responses
  - Matching is substring-based (case-insensitive): e.g. the pattern `auth` also matches `author` — an accepted false positive (Q14)
  - Redaction is full-only: `full_redact` is always True; partial masking of values is not supported (Q15)
  - Rule retrieval must be lightweight and safe for repeated use
- **Edge Cases**: Empty rule list, conflicting patterns, unknown secret format, key matching multiple patterns, rule update after load, consumer feature bypassing rules, pattern accidentally matching non-sensitive key
- **Error Handling**: Missing or invalid rule definition falls back to built-in default sensitive key list; warning emitted when custom rules cannot be parsed; rule failure must never cause secret values to be exposed

## Error Categories

- configuration error — invalid, missing, or unreadable settings source
- validation error — settings schema violation or malformed settings path
- load error — oversized, unsafe, or rejected settings content
- type conversion error — settings value does not match expected type in strict mode
- workspace resolution error — project workspace cannot be resolved from any strategy

## Events

- settings loaded event — emitted after settings snapshot is successfully loaded
- settings reload event — emitted after settings snapshot is successfully replaced
- workspace resolved event — emitted after project workspace directory is resolved
- settings validation warning event — emitted when schema or parse warnings occur in permissive mode

Event payloads should include:

- event category
- source summary
- override count
- warning count
- policy mode
- timestamp

Event payloads must avoid:

- raw settings content
- secret values
- sensitive override values

## Configuration Keys


| Configuration Concept       | Description                                                    | Typical Default                                       |
| ----------------------------- | ---------------------------------------------------------------- | ------------------------------------------------------- |
| Settings source location    | Location of primary settings file used during load             | Resolved from workspace or platform-standard location |
| Workspace directory         | Project root directory used for file-based operations          | Resolved through deterministic workspace strategies   |
| Sensitive key list          | List of key names and patterns treated as secret for redaction | Common token, key, password, and credential patterns  |
| Environment override prefix | Product-specific prefix recognized for environment overrides   | Product prefix with nested key convention             |
| Legacy environment fallback | Whether legacy environment prefix is accepted                  | Enabled for backward compatibility                    |
| Policy mode                 | Strict or permissive behavior for parse and schema issues      | Strict                                                |
| Maximum settings size       | Maximum allowed settings source size                           | Conservative size limit                               |
| Default values source       | Built-in defaults applied when no other source provides value  | Feature-defined safe defaults                         |

## QA Checklist

- [ ]  Settings load from file, environment, and defaults with correct precedence
- [ ]  Runtime override takes precedence over environment, file, and defaults (requires `BLENDERMCP_CONFIG_V2=on`; ignored with warning when off)
- [ ]  Default settings source resolves to `<cwd>/config.yaml` when no explicit path and no `BLENDERMCP_CONFIG_PATH` is set
- [ ]  Environment override takes precedence over file and defaults
- [ ]  File values take precedence over built-in defaults
- [ ]  Missing settings file falls back to environment and defaults without fatal error
- [ ]  Malformed settings content raises configuration error in strict mode
- [ ]  Malformed settings content falls back safely in permissive mode
- [ ]  Schema violation raises validation error in strict mode
- [ ]  Schema violation logs warning in permissive mode
- [ ]  Unsafe settings content is rejected without object instantiation
- [ ]  Oversized settings source raises load error
- [ ]  Environment values convert to boolean, integer, float, null, list, and mapping types correctly
- [ ]  Legacy environment prefix fallback works when enabled
- [ ]  Immutable snapshot returned on retrieve
- [ ]  Retrieved structured values are deep-copied or immutable
- [ ]  Missing key returns provided default
- [ ]  Empty path returns full settings snapshot safely
- [ ]  List position access works and out-of-range returns default
- [ ]  Expected type mismatch returns default in permissive mode
- [ ]  Expected type mismatch raises type conversion error in strict mode
- [ ]  Concurrent first access loads settings only once
- [ ]  Reload replaces snapshot atomically
- [ ]  Failed reload retains previous valid snapshot in non-fatal mode
- [ ]  Project workspace resolves correctly through explicit override
- [ ]  Project workspace resolves correctly through environment signal
- [ ]  Project workspace resolves correctly through settings file location
- [ ]  Project workspace resolves correctly through proximity markers
- [ ]  Project workspace falls back to current working directory
- [ ]  Project workspace handles symlinked directories safely
- [ ]  Project workspace resolution does not create directories by default
- [ ]  Legacy BLENDERMCP_* environment variables are ignored (Q8)
- [ ]  Runtime overrides are caller-scoped and not cached (A5)
- [ ]  32-thread first access performs exactly one load (Q19)
- [ ]  Built-in defaults tier is complete; settings file is optional override-only (Q6)
- [ ]  Schema validation, 1 MiB size limit, `\.` escaping, strict ConfigTypeError gated behind BLENDERMCP_CONFIG_V2
- [ ]  Asset and render derive root locations from workspace resolution instead of own rules
- [ ]  Settings metadata reports source, override count, and warnings
- [ ]  Settings metadata does not leak secret values
- [ ]  Redaction keys mask sensitive values in diagnostics
- [ ]  Redaction keys mask sensitive values in command-line output
- [ ]  Redaction keys mask sensitive values in MCP-facing responses
- [ ]  Redaction rules contain key patterns only, never secret values
- [ ]  Custom redaction rules extend built-in defaults safely
- [ ]  Settings loaded event emitted after successful load
- [ ]  Settings reload event emitted after successful reload
- [ ]  Workspace resolved event emitted after resolution
```

---

## File: modules/config/pyproject.toml

```toml
[project]
name = "blender-arwaky-config"
version = "1.6.5"
description = "BlenderArwaky configuration feature module"
requires-python = ">=3.10"
license = {text = "MIT"}

[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"

[tool.setuptools]
packages = ["."]
```

---

## File: modules/config/src/agent_config_orchestrator.py

```python
"""Agent: Config orchestrator.

Coordinates configuration loading, retrieval, workspace resolution,
metadata, and redaction through IConfigAggregate.

Orchestration only — delegates all business logic to capabilities
via protocol interfaces. Owns the bounded event ring buffer (T-09)
since config has exactly 5 capabilities mapped 1:1 to FR-CFG-001..005.
"""

from __future__ import annotations

import json
import logging
from collections import deque
from collections.abc import Mapping
from dataclasses import asdict
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import EVENT_RING_BUFFER_SIZE
from modules.shared.src.config.taxonomy_config_vo import RedactionRule, SettingsSnapshot, WorkspacePath

logger = logging.getLogger("BlenderMCPServer")


# ─── Block 1: Class Definition & Constructor ───────────────
class ConfigOrchestrator(IConfigAggregate):
    """Orchestrator for the config feature.

    Coordinates capabilities through protocol interfaces.
    Zero I/O, zero business logic, zero domain computation.
    """

    def __init__(
        self,
        loader: ISettingsLoaderProtocol,
        retriever: ISettingsRetrieverProtocol,
        workspace_resolver: IWorkspaceResolverProtocol,
        metadata_provider: ISettingsMetadataProtocol,
        redaction_rules: IRedactionRulesProtocol,
    ) -> None:
        self._loader = loader
        self._retriever = retriever
        self._workspace_resolver = workspace_resolver
        self._metadata_provider = metadata_provider
        self._redaction_rules = redaction_rules
        self._snapshot: SettingsSnapshot | None = None
        self._event_buffer: deque[dict[str, Any]] = deque(maxlen=EVENT_RING_BUFFER_SIZE)

# ─── Block 2: Aggregate Method Implementation ─────────────

    def load(
        self,
        path: ConfigPath | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> SettingsSnapshot:
        """Load settings, record events, cache snapshot."""
        self._snapshot = self._loader.load_settings(path, overrides)
        self._record_event(self._loader.emit_loaded_event())
        validation_ev = self._loader.emit_validation_warning_event()
        if validation_ev is not None:
            self._record_event(validation_ev)
        return self._snapshot

    def reload(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot, record reload event."""
        self._snapshot = self._loader.reload_settings(path)
        self._record_event(self._loader.emit_reload_event())
        return self._snapshot

    def get_snapshot(self) -> SettingsSnapshot:
        """Return cached snapshot, lazy-loading if needed (now safe — loader locked)."""
        if self._snapshot is None:
            self._snapshot = self._loader.load_settings()
        return self._snapshot

    def get(self, path: ConfigPath = "", default: Any = None) -> Any:
        """Retrieve value by dot-separated path."""
        return self._retriever.get_value(self.get_snapshot(), path, default)

    def has(self, path: ConfigPath) -> bool:
        """Check if a path exists in settings."""
        return self._retriever.has_value(self.get_snapshot(), path)

    def get_string(self, path: ConfigPath, default: str = "") -> str:
        """Retrieve string value."""
        return self._retriever.get_string(self.get_snapshot(), path, default)

    def get_int(self, path: ConfigPath, default: int = 0) -> int:
        """Retrieve integer value."""
        return self._retriever.get_int(self.get_snapshot(), path, default)

    def get_bool(self, path: ConfigPath, default: bool = False) -> bool:
        """Retrieve boolean value."""
        return self._retriever.get_bool(self.get_snapshot(), path, default)

    def get_float(self, path: ConfigPath, default: float = 0.0) -> float:
        """Retrieve float value."""
        return self._retriever.get_float(self.get_snapshot(), path, default)

    def resolve_workspace(self) -> WorkspacePath:
        """Resolve and record workspace resolution event."""
        ws = self._workspace_resolver.resolve()
        self._record_event(self._workspace_resolver.emit_resolved_event(ws))
        return ws

    def get_metadata(self) -> ConfigMetadata | None:
        """Delegate metadata retrieval (reflects latest load)."""
        return self._metadata_provider.get_metadata()

    def recent_events(self, limit: int = EVENT_RING_BUFFER_SIZE) -> tuple[dict[str, Any], ...]:
        """Return the most recent config domain events, oldest → newest."""
        items = list(self._event_buffer)
        return tuple(items[-limit:])

    def get_redaction_rule(self) -> RedactionRule:
        """Delegate redaction rule retrieval."""
        return self._redaction_rules.get_redaction_rule()

    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Delegate dictionary redaction."""
        return self._redaction_rules.redact_dict(data)

# ─── Block 3: Event Recording ─────────────────────────────

    def _record_event(self, event: Any) -> None:
        """Serialize and store a domain event into the bounded ring buffer."""
        payload = asdict(event)
        self._event_buffer.append(payload)
        logger.info("config_event %s", json.dumps(payload, default=str))

# ─── Dunder ────────────────────────────────────────────────

    def __repr__(self) -> str:
        return "ConfigOrchestrator()"
```

---

## File: modules/config/src/capabilities_redaction_rules.py

```python
"""Capability: Redaction rules provider (FR-CFG-005).

Implements IRedactionRulesProtocol — provides sensitive key patterns
and redaction rules used by consuming features for masking.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    REDACTION_PLACEHOLDER,
    SENSITIVE_KEY_PATTERNS,
)
from modules.shared.src.config.taxonomy_config_vo import RedactionRule


# ─── Block 1: Class Definition & Constructor ───────────────
class RedactionRulesCapability(IRedactionRulesProtocol):
    """FR-CFG-005: Provide redaction rules.

    Rules contain key patterns only, never secret values.

    Substring matching semantics are intentional (PM Q14): a pattern such as
    ``auth`` also matches ``author`` — an accepted false positive. Matching is
    case-insensitive substring, so broad patterns catch variants.

    Redaction is full-only (PM Q15): ``full_redact`` is always True; partial
    masking of values is not supported. The placeholder is constant.

    Extension is via composition-root injection only (PM Q16): additional
    patterns are supplied through ``extra_patterns`` at construction time,
    never read from settings at runtime.
    """

    def __init__(self, extra_patterns: tuple[str, ...] = ()) -> None:
        self._rule = RedactionRule(
            key_patterns=SENSITIVE_KEY_PATTERNS + tuple(extra_patterns),
            placeholder=REDACTION_PLACEHOLDER,
            full_redact=True,
        )

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_redaction_rule(self) -> RedactionRule:
        """Return the authoritative redaction rule."""
        return self._rule

    def redact_value(self, key: str, value: Any) -> Any:
        """Redact a value if its key matches a sensitive pattern."""
        if self._rule.matches_key(key):
            return self._rule.placeholder
        return value

    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively redact all sensitive values in a dictionary."""
        result: dict[str, Any] = {}
        for key, value in data.items():
            if self._rule.matches_key(key):
                result[key] = self._rule.placeholder
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value)
            elif isinstance(value, list):
                result[key] = [
                    self.redact_dict(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "RedactionRulesCapability()"
```

---

## File: modules/config/src/capabilities_settings_loader.py

```python
"""Capability: Settings loader (FR-CFG-001).

Implements ISettingsLoaderProtocol — handles loading, validating, and
reloading application settings with deterministic precedence rules.

Business logic only: YAML parsing, precedence merging, environment
override application, schema validation, typed conversion, size limits,
runtime overrides, thread-safe single-load caching.
"""

from __future__ import annotations

import copy
import os
import threading
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import (
    ConfigMetadata,
    ConfigPath,
    OverrideCount,
    ParseWarning,
    SourceLocation,
    Timestamp,
    ValidationWarning,
)
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    DEFAULT_POLICY_MODE,
    DEFAULT_SETTINGS,
    ENV_PREFIX_PRODUCT,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    RESERVED_ENV_KEYS,
    SETTINGS_SCHEMA,
)
from modules.shared.src.config.taxonomy_config_error import (
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigValidationError,
)
from modules.shared.src.config.taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
)
from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot
from modules.shared.src.config.utility_config_helpers import (
    apply_env_overrides,
    deep_merge_dicts,
    load_yaml_safe,
    resolve_default_config_path,
    set_nested_value,
    validate_settings_schema,
)

ConfigFileLoader = Any  # Callable[[ConfigPath], dict[str, Any]]


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsLoaderCapability(ISettingsLoaderProtocol):
    """FR-CFG-001: Load and apply settings.

    Responsible for: YAML safe parsing, environment override application
    with typed conversion, precedence merging, schema validation, size
    limits, runtime overrides, immutable snapshot creation, policy-mode
    error handling, and thread-safe single-load caching.
    """

    def __init__(
        self,
        config_file_loader: ConfigFileLoader | None = None,
        policy_mode: str = DEFAULT_POLICY_MODE,
        defaults: Mapping[str, Any] | None = None,
        schema: Mapping[str, Any] | None = None,
        config_v2_enabled: bool = False,
    ) -> None:
        self._file_loader = config_file_loader or load_yaml_safe
        self._policy_mode = policy_mode
        self._defaults = dict(defaults) if defaults is not None else copy.deepcopy(DEFAULT_SETTINGS)
        self._schema = dict(schema) if schema is not None else copy.deepcopy(SETTINGS_SCHEMA)
        self._config_v2_enabled = config_v2_enabled
        self._lock = threading.Lock()
        # cached state
        self._cached: SettingsSnapshot | None = None
        self._cached_data: dict[str, Any] | None = None
        self._last_metadata: ConfigMetadata = ConfigMetadata()

# ─── Block 2: Protocol Method Implementation ──────────────

    def load_settings(
        self,
        path: ConfigPath | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> SettingsSnapshot:
        """Load settings from sources, apply precedence, validate, return immutable snapshot."""
        with self._lock:
            # Single-load guarantee (Q19): identical cached snapshot returned.
            if overrides is None and path is None and self._cached is not None:
                return self._cached

            if path is not None or self._cached is None:
                merged, filedata, metadata = self._build_core(path)
                self._cached_data = filedata
                self._cached = SettingsSnapshot(_data=merged)
                self._last_metadata = metadata

            # Runtime overrides are caller-scoped — never cached (A5).
            if overrides is not None and self._config_v2_enabled:
                structured: dict[str, Any] = {}
                for dotted_key, value in overrides.items():
                    segments = tuple(dotted_key.split("."))
                    set_nested_value(structured, segments, value)
                final = deep_merge_dicts(self._cached_data, structured)
                return SettingsSnapshot(_data=final)

            if overrides is not None and not self._config_v2_enabled:
                self._last_metadata = ConfigMetadata(
                    source=self._last_metadata.source,
                    exists=self._last_metadata.exists,
                    overrides=self._last_metadata.overrides,
                    parse_warnings=(
                        *self._last_metadata.parse_warnings,
                        ParseWarning("runtime overrides ignored; BLENDERMCP_CONFIG_V2 off"),
                    ),
                    validation_warnings=self._last_metadata.validation_warnings,
                )

            return self._cached

    def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot. Retains previous on failure (permissive)."""
        with self._lock:
            try:
                merged, filedata, metadata = self._build_core(path)
                # build-then-swap = atomic; never set cache to None before build
                self._cached_data = filedata
                self._cached = SettingsSnapshot(_data=merged)
                self._last_metadata = metadata
                return self._cached
            except Exception:
                if self._policy_mode == POLICY_MODE_PERMISSIVE and self._cached is not None:
                    return self._cached
                raise

    def get_last_metadata(self) -> ConfigMetadata:
        """Return metadata from the most recent successful load."""
        return self._last_metadata

    def emit_loaded_event(self) -> SettingsLoadedEvent:
        """Build a settings-loaded event from the most recent load metadata."""
        metadata = self._last_metadata
        return SettingsLoadedEvent(
            source_summary=str(metadata.source) if metadata.source is not None else "",
            override_count=int(metadata.overrides),
            warning_count=len(metadata.parse_warnings) + len(metadata.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

    def emit_reload_event(self) -> SettingsReloadEvent:
        """Build a settings-reload event from the most recent load metadata."""
        metadata = self._last_metadata
        return SettingsReloadEvent(
            source_summary=str(metadata.source) if metadata.source is not None else "",
            override_count=int(metadata.overrides),
            warning_count=len(metadata.parse_warnings) + len(metadata.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

    def emit_validation_warning_event(self) -> SettingsValidationWarningEvent | None:
        """Return warning event iff permissive mode and validation warnings exist."""
        if self._policy_mode != POLICY_MODE_PERMISSIVE:
            return None
        metadata = self._last_metadata
        if not metadata.validation_warnings:
            return None
        return SettingsValidationWarningEvent(
            source_summary=str(metadata.source) if metadata.source is not None else "",
            override_count=int(metadata.overrides),
            warning_count=len(metadata.validation_warnings),
            policy_mode=self._policy_mode,
            timestamp=Timestamp(time.time()),
        )

# ─── Block 3: Core Build ───────────────────────────────────

    def _build_core(
        self, path: ConfigPath | None
    ) -> tuple[dict[str, Any], dict[str, Any], ConfigMetadata]:
        """Build merged settings + raw file data + metadata.

        Returns (merged, filedata, metadata). ``filedata`` is what gets cached
        (used as base for caller-scoped runtime overrides).
        """
        resolved = resolve_default_config_path(path)
        p = Path(str(resolved))

        parse_warnings: list[ParseWarning] = []
        file_data: dict[str, Any] = {}

        # Directory path
        if p.is_dir():
            if self._policy_mode == POLICY_MODE_STRICT:
                raise ConfigPathError(f"{resolved} is a directory")
            parse_warnings.append(ParseWarning(f"{resolved} is a directory; using defaults"))
        elif not p.is_file():
            # Missing file: never fatal in any mode (Q6).
            parse_warnings.append(
                ParseWarning(f"settings file not found: {resolved}; using defaults")
            )
        else:
            # Size limit (flag-gated)
            if self._config_v2_enabled and p.stat().st_size > MAX_CONFIG_SIZE_BYTES:
                if self._policy_mode == POLICY_MODE_STRICT:
                    raise ConfigLoadError(
                        f"settings file too large: {resolved} exceeds {MAX_CONFIG_SIZE_BYTES} bytes"
                    )
                parse_warnings.append(ParseWarning(f"settings file too large: {resolved}; skipped"))
            else:
                try:
                    file_data = self._file_loader(ConfigPath(str(p)))
                except (ConfigParseError, ConfigLoadError, ConfigValidationError):
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise
                    parse_warnings.append(
                        ParseWarning(f"failed to parse {resolved}; using defaults")
                    )
                    file_data = {}
                except Exception as exc:
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise ConfigLoadError(f"Failed to load settings: {exc}") from exc
                    parse_warnings.append(
                        ParseWarning(f"failed to load {resolved}; using defaults")
                    )
                    file_data = {}

        # Merge precedence: defaults < file < env
        merged = deep_merge_dicts(dict(self._defaults), file_data)
        merged, env_count = apply_env_overrides(
            merged, os.environ, ENV_PREFIX_PRODUCT, RESERVED_ENV_KEYS
        )

        # Schema (flag-gated)
        validation_warnings: list[ValidationWarning] = []
        if self._config_v2_enabled:
            errors, warnings = validate_settings_schema(merged, self._schema)
            if errors and self._policy_mode == POLICY_MODE_STRICT:
                raise ConfigValidationError("; ".join(errors))
            validation_warnings.extend(warnings)
            validation_warnings.extend(errors)

        metadata = ConfigMetadata(
            source=SourceLocation(str(resolved)),
            exists=p.is_file(),
            overrides=OverrideCount(env_count),
            parse_warnings=tuple(parse_warnings),
            validation_warnings=tuple(validation_warnings),
        )
        return merged, file_data, metadata
```

---

## File: modules/config/src/capabilities_settings_metadata.py

```python
"""Capability: Settings metadata provider (FR-CFG-004).

Implements ISettingsMetadataProtocol — exposes diagnostic metadata
about settings loading without leaking secrets.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsMetadataCapability(ISettingsMetadataProtocol):
    """FR-CFG-004: Provide settings metadata.

    Exposes source, override count, warnings, policy mode, and timestamps.
    Must never include secret values or raw settings content.

    The metadata supplier is a bound method (e.g. loader.get_last_metadata)
    wired by the composition root — no capability-to-capability imports.
    """

    def __init__(self, metadata_supplier: Callable[[], ConfigMetadata] | None = None) -> None:
        self._metadata_supplier = metadata_supplier

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_metadata(self) -> ConfigMetadata:
        """Return current settings metadata (reflects latest load/reload)."""
        if self._metadata_supplier is None:
            return ConfigMetadata()
        return self._metadata_supplier()

    def to_safe_dict(self, metadata: ConfigMetadata) -> dict[str, Any]:
        """Serialize metadata for diagnostics output (secrets excluded)."""
        return metadata.to_dict()

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "SettingsMetadataCapability()"
```

---

## File: modules/config/src/capabilities_settings_retriever.py

```python
"""Capability: Settings retriever (FR-CFG-002).

Implements ISettingsRetrieverProtocol — hierarchical dot-separated
settings value retrieval with safe copy semantics, policy-mode typing,
and escaped-separator path support.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ErrorString
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.taxonomy_config_constant import POLICY_MODE_STRICT
from modules.shared.src.config.taxonomy_config_error import ConfigTypeError
from modules.shared.src.config.taxonomy_config_vo import _MISSING, SettingsSnapshot
from modules.shared.src.config.utility_config_helpers import parse_settings_path


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsRetrieverCapability(ISettingsRetrieverProtocol):
    """FR-CFG-002: Retrieve settings values.

    Thread-safe traversal, deep-copy returns, list indexing support,
    typed getters with policy-mode error handling, escaped separator support.
    No I/O. No file or environment reads per request.
    """

    def __init__(self, policy_mode: str = POLICY_MODE_STRICT, escape_enabled: bool = False) -> None:
        self._policy_mode = policy_mode
        self._escape_enabled = escape_enabled

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_value(
        self,
        snapshot: SettingsSnapshot,
        path: str,
        default: Any = None,
    ) -> Any:
        """Retrieve value by dot-separated path. Returns deep copy."""
        segments = parse_settings_path(path, self._escape_enabled)
        return snapshot.get_segments(segments, default)

    def has_value(self, snapshot: SettingsSnapshot, path: str) -> bool:
        """Check if a dot-separated path exists."""
        segments = parse_settings_path(path, self._escape_enabled)
        return snapshot.has_segments(segments)

    def get_string(self, snapshot: SettingsSnapshot, path: str, default: str = "") -> str:
        """Retrieve string value. Returns default on type mismatch."""
        return self._typed(snapshot, path, str, default)

    def get_int(self, snapshot: SettingsSnapshot, path: str, default: int = 0) -> int:
        """Retrieve integer value. Returns default on type mismatch. Bool excluded."""
        return self._typed(snapshot, path, int, default, exclude_bool=True)

    def get_bool(self, snapshot: SettingsSnapshot, path: str, default: bool = False) -> bool:
        """Retrieve boolean value. Returns default on type mismatch."""
        return self._typed(snapshot, path, bool, default)

    def get_float(self, snapshot: SettingsSnapshot, path: str, default: float = 0.0) -> float:
        """Retrieve float value. Returns default on type mismatch. Int coerced."""
        return self._typed(snapshot, path, float, default, coerce_int=True)

# ─── Block 3: Typed Helper ─────────────────────────────────

    def _typed(
        self,
        snapshot: SettingsSnapshot,
        path: str,
        expected: type,
        default: Any,
        exclude_bool: bool = False,
        coerce_int: bool = False,
    ) -> Any:
        segments = parse_settings_path(path, self._escape_enabled)
        raw = snapshot.get_segments(segments, _MISSING)
        if raw is _MISSING:
            return default  # missing key never raises in either mode

        if expected is int:
            if isinstance(raw, int) and not (exclude_bool and isinstance(raw, bool)):
                return raw
        elif expected is float:
            if isinstance(raw, bool):
                pass
            elif isinstance(raw, int):
                return float(raw) if coerce_int else default
            elif isinstance(raw, float):
                return raw
        elif isinstance(raw, expected):
            return raw

        if self._policy_mode == POLICY_MODE_STRICT:
            raise ConfigTypeError(
                ErrorString(f"{path}: expected {expected.__name__}, got {type(raw).__name__}")
            )
        return default

    def __repr__(self) -> str:
        return "SettingsRetrieverCapability()"
```

---

## File: modules/config/src/capabilities_workspace_resolver.py

```python
"""Capability: Workspace resolver (FR-CFG-003).

Implements IWorkspaceResolverProtocol — resolves project workspace
directory using deterministic strategies with result caching.
"""

from __future__ import annotations

import os
import threading
from pathlib import Path

from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    PROJECT_MARKERS,
    WORKSPACE_ROOT_ENV,
)
from modules.shared.src.config.taxonomy_config_error import ConfigRootResolutionError
from modules.shared.src.config.taxonomy_config_event import WorkspaceResolvedEvent
from modules.shared.src.config.taxonomy_config_vo import WorkspacePath
from modules.shared.src.config.utility_config_helpers import search_project_root


# ─── Block 1: Class Definition & Constructor ───────────────
class WorkspaceResolverCapability(IWorkspaceResolverProtocol):
    """FR-CFG-003: Resolve project workspace directory.

    Resolution order (per FRD minus legacy per Q8):
      explicit override > env BLENDERMCP_ROOT > settings-file parent >
      marker search > platform config > cwd fallback.
    Result is cached for process lifetime.
    """

    def __init__(
        self,
        explicit_override: str | None = None,
        config_path: object | None = None,
    ) -> None:
        self._explicit_override = explicit_override
        self._config_path = config_path
        self._lock = threading.Lock()
        self._cached: WorkspacePath | None = None

# ─── Block 2: Protocol Method Implementation ──────────────

    def resolve(self) -> WorkspacePath:
        """Resolve workspace using deterministic strategy order (cached)."""
        with self._lock:
            if self._cached is not None:
                return self._cached
            self._cached = self._resolve_uncached()
            return self._cached

    def emit_resolved_event(self, workspace: WorkspacePath) -> WorkspaceResolvedEvent:
        """Build a workspace-resolved event payload."""
        return WorkspaceResolvedEvent(
            source_summary=workspace.strategy,
            override_count=0,
            warning_count=0,
        )

# ─── Block 3: Resolution Strategy ─────────────────────────

    def _resolve_uncached(self) -> WorkspacePath:
        # 1. Explicit override
        if self._explicit_override:
            candidate = Path(self._explicit_override).resolve()
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="explicit_override")
            # invalid path logs warning and falls through

        # 2. Environment signal (BLENDERMCP_ROOT only — legacy removed, Q8)
        env_root = os.environ.get(WORKSPACE_ROOT_ENV)
        if env_root:
            try:
                candidate = Path(env_root).resolve()
                if candidate.is_dir():
                    return WorkspacePath(path=str(candidate), strategy="env_signal")
            except (OSError, ValueError):
                pass

        # 3. Settings file parent (NEW)
        if self._config_path:
            candidate = Path(str(self._config_path)).resolve().parent
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="settings_file_location")

        # 4. Marker search
        marker_path = search_project_root(PROJECT_MARKERS)
        if marker_path:
            return WorkspacePath(path=str(marker_path), strategy="marker_search")

        # 5. Platform config
        xdg_config = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        prod_path = Path(xdg_config) / "blender-arwaky"
        if prod_path.is_dir():
            return WorkspacePath(path=str(prod_path), strategy="platform_config")

        # 6. CWD fallback
        try:
            cwd = Path.cwd().resolve()
            if cwd.is_dir():
                return WorkspacePath(path=str(cwd), strategy="cwd_fallback")
        except OSError as exc:
            raise ConfigRootResolutionError("All workspace resolution strategies failed") from exc

        raise ConfigRootResolutionError("All workspace resolution strategies failed")

    def __repr__(self) -> str:
        return "WorkspaceResolverCapability()"
```

---

## File: modules/config/src/root_config_container.py

```python
"""Root: Config feature DI container.

Wires capabilities to contract protocols and bootstraps the config feature.
Single composition root for the config module.
"""

from __future__ import annotations

import os

from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    CONFIG_V2_FLAG_ENV,
    DEFAULT_POLICY_MODE,
)
from modules.shared.src.config.utility_config_helpers import (
    load_yaml_safe,
    parse_env_value,
    resolve_default_config_path,
)

from .agent_config_orchestrator import ConfigOrchestrator
from .capabilities_redaction_rules import RedactionRulesCapability
from .capabilities_settings_loader import SettingsLoaderCapability
from .capabilities_settings_metadata import SettingsMetadataCapability
from .capabilities_settings_retriever import SettingsRetrieverCapability
from .capabilities_workspace_resolver import WorkspaceResolverCapability


class ConfigContainer:
    """DI container for the config feature.

    Wires capabilities to protocol interfaces and constructs the
    IConfigAggregate facade (ConfigOrchestrator).
    """

    def __init__(
        self,
        config_file_loader: object | None = None,
        policy_mode: str = DEFAULT_POLICY_MODE,
        explicit_workspace: str | None = None,
        extra_redaction_patterns: tuple[str, ...] = (),
        config_v2_enabled: bool | None = None,
    ) -> None:
        # Flag read once at construction (None → resolve via env truthiness).
        if config_v2_enabled is None:
            v2 = parse_env_value(os.environ.get(CONFIG_V2_FLAG_ENV, ""))
            config_v2_enabled = v2 is True
        else:
            config_v2_enabled = bool(config_v2_enabled)

        default_config_path = resolve_default_config_path(None)

        self._loader: ISettingsLoaderProtocol = SettingsLoaderCapability(
            config_file_loader=config_file_loader or load_yaml_safe,
            policy_mode=policy_mode,
            config_v2_enabled=config_v2_enabled,
        )
        self._retriever: ISettingsRetrieverProtocol = SettingsRetrieverCapability(
            policy_mode=policy_mode,
            escape_enabled=config_v2_enabled,
        )
        self._workspace_resolver: IWorkspaceResolverProtocol = WorkspaceResolverCapability(
            explicit_override=explicit_workspace,
            config_path=default_config_path,
        )
        self._metadata_provider: ISettingsMetadataProtocol = SettingsMetadataCapability(
            metadata_supplier=self._loader.get_last_metadata,
        )
        self._redaction_rules: IRedactionRulesProtocol = RedactionRulesCapability(
            extra_patterns=extra_redaction_patterns,
        )

    def build(self) -> IConfigAggregate:
        """Construct and return the wired ConfigOrchestrator."""
        return ConfigOrchestrator(
            loader=self._loader,
            retriever=self._retriever,
            workspace_resolver=self._workspace_resolver,
            metadata_provider=self._metadata_provider,
            redaction_rules=self._redaction_rules,
        )
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

from dataclasses import dataclass, field
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


@dataclass(frozen=True)
class ConfigMetadata:
    """Immutable metadata about configuration loading (FR-CFG-001, FR-CFG-005).

    Frozen (hashable). Carries structural counts + source path only —
    never raw settings values or secrets.
    """

    source: SourceLocation | None = None
    exists: bool = False
    overrides: OverrideCount = 0
    parse_warnings: tuple[ParseWarning, ...] = field(default_factory=tuple)
    validation_warnings: tuple[ValidationWarning, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        # Normalize list inputs to immutable tuples.
        if isinstance(self.parse_warnings, list):
            object.__setattr__(self, "parse_warnings", tuple(self.parse_warnings))
        if isinstance(self.validation_warnings, list):
            object.__setattr__(self, "validation_warnings", tuple(self.validation_warnings))

    def to_dict(self) -> dict[str, Any]:
        """Serialize metadata for diagnostics (secrets excluded)."""
        return {
            "source": self.source,
            "exists": self.exists,
            "overrides": self.overrides,
            "parse_warnings": list(self.parse_warnings),
            "validation_warnings": list(self.validation_warnings),
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

## File: modules/shared/src/config/__init__.py

```python
"""Config domain: contracts, errors, events, VOs, constants, utilities for configuration management."""

from __future__ import annotations

# ─── Contracts (Protocols) ─────────────────────────────────────
from .contract_config_aggregate import IConfigAggregate
from .contract_redaction_rules_protocol import IRedactionRulesProtocol
from .contract_settings_loader_protocol import ISettingsLoaderProtocol
from .contract_settings_metadata_protocol import ISettingsMetadataProtocol
from .contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from .contract_workspace_resolver_protocol import IWorkspaceResolverProtocol

# ─── Taxonomy: Constants ───────────────────────────────────────
from .taxonomy_config_constant import (
    CONFIG_PATH_ENV,
    CONFIG_V2_FLAG_ENV,
    DEFAULT_CONFIG_FILENAME,
    DEFAULT_POLICY_MODE,
    DEFAULT_SETTINGS,
    ENV_PREFIX_PRODUCT,
    EVENT_RING_BUFFER_SIZE,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    PROJECT_MARKERS,
    REDACTION_PLACEHOLDER,
    RESERVED_ENV_KEYS,
    SENSITIVE_KEY_PATTERNS,
    SETTINGS_SCHEMA,
    WORKSPACE_ROOT_ENV,
)

# ─── Taxonomy: Errors ──────────────────────────────────────────
from .taxonomy_config_error import (
    ConfigError,
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigRootResolutionError,
    ConfigTypeError,
    ConfigValidationError,
)

# ─── Taxonomy: Events ──────────────────────────────────────────
from .taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
    WorkspaceResolvedEvent,
)

# ─── Taxonomy: Value Objects ───────────────────────────────────
from .taxonomy_config_vo import (
    RedactionRule,
    SettingsSnapshot,
    WorkspacePath,
)

# ─── Utility ───────────────────────────────────────────────────
from .utility_config_helpers import parse_env_value, search_project_root

__all__ = [
    # Contracts — Protocols
    "IConfigAggregate",
    "ISettingsLoaderProtocol",
    "ISettingsRetrieverProtocol",
    "IWorkspaceResolverProtocol",
    "ISettingsMetadataProtocol",
    "IRedactionRulesProtocol",
    # Taxonomy — Value Objects
    "SettingsSnapshot",
    "WorkspacePath",
    "RedactionRule",
    # Taxonomy — Events
    "SettingsLoadedEvent",
    "SettingsReloadEvent",
    "WorkspaceResolvedEvent",
    "SettingsValidationWarningEvent",
    # Taxonomy — Constants
    "SENSITIVE_KEY_PATTERNS",
    "PROJECT_MARKERS",
    "MAX_CONFIG_SIZE_BYTES",
    "ENV_PREFIX_PRODUCT",
    "CONFIG_PATH_ENV",
    "CONFIG_V2_FLAG_ENV",
    "WORKSPACE_ROOT_ENV",
    "DEFAULT_CONFIG_FILENAME",
    "RESERVED_ENV_KEYS",
    "EVENT_RING_BUFFER_SIZE",
    "DEFAULT_SETTINGS",
    "SETTINGS_SCHEMA",
    "REDACTION_PLACEHOLDER",
    "POLICY_MODE_STRICT",
    "POLICY_MODE_PERMISSIVE",
    "DEFAULT_POLICY_MODE",
    # Utility
    "parse_env_value",
    "search_project_root",
    # Taxonomy — Errors
    "ConfigError",
    "ConfigLoadError",
    "ConfigParseError",
    "ConfigPathError",
    "ConfigRootResolutionError",
    "ConfigTypeError",
    "ConfigValidationError",
]
```

---

## File: modules/shared/src/config/contract_config_aggregate.py

```python
"""Contract: Config aggregate facade.

Unified interface for the config feature consumed by the Surface layer.
Combines settings loading, retrieval, workspace resolution, metadata, and
redaction into a single entry point.

Implemented by Agent layer (ConfigOrchestrator).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from .taxonomy_config_constant import EVENT_RING_BUFFER_SIZE
from .taxonomy_config_vo import RedactionRule, SettingsSnapshot, WorkspacePath


class IConfigAggregate(ABC):
    """Aggregate facade for the config feature.

    Surface layer delegates all config operations through this interface.
    """

    # ─── Lifecycle ──────────────────────────────────────────────

    @abstractmethod
    def load(
        self,
        path: ConfigPath | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> SettingsSnapshot:
        """Load settings and return immutable snapshot."""
        ...

    @abstractmethod
    def reload(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached settings snapshot."""
        ...

    @abstractmethod
    def get_snapshot(self) -> SettingsSnapshot:
        """Return current cached settings snapshot (lazy-loads if needed)."""
        ...

    # ─── Retrieval (FR-CFG-002) ────────────────────────────────

    @abstractmethod
    def get(self, path: ConfigPath = "", default: Any = None) -> Any:
        """Retrieve value by dot-separated path from current snapshot."""
        ...

    @abstractmethod
    def has(self, path: ConfigPath) -> bool:
        """Check if a dot-separated path exists in the current snapshot."""
        ...

    @abstractmethod
    def get_string(self, path: ConfigPath, default: str = "") -> str:
        """Retrieve string value."""
        ...

    @abstractmethod
    def get_int(self, path: ConfigPath, default: int = 0) -> int:
        """Retrieve integer value."""
        ...

    @abstractmethod
    def get_bool(self, path: ConfigPath, default: bool = False) -> bool:
        """Retrieve boolean value."""
        ...

    @abstractmethod
    def get_float(self, path: ConfigPath, default: float = 0.0) -> float:
        """Retrieve float value."""
        ...

    # ─── Workspace (FR-CFG-003) ────────────────────────────────

    @abstractmethod
    def resolve_workspace(self) -> WorkspacePath:
        """Resolve project workspace directory."""
        ...

    # ─── Metadata (FR-CFG-004) ────────────────────────────────

    @abstractmethod
    def get_metadata(self) -> ConfigMetadata | None:
        """Return settings loading metadata (secrets excluded)."""
        ...

    # ─── Events (T-09) ─────────────────────────────────────────

    @abstractmethod
    def recent_events(self, limit: int = EVENT_RING_BUFFER_SIZE) -> tuple[dict[str, Any], ...]:
        """Return recent config domain events, oldest → newest."""
        ...

    # ─── Redaction (FR-CFG-005) ────────────────────────────────

    @abstractmethod
    def get_redaction_rule(self) -> RedactionRule:
        """Return authoritative redaction rule."""
        ...

    @abstractmethod
    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively redact sensitive values in a dictionary."""
        ...
```

---

## File: modules/shared/src/config/contract_redaction_rules_protocol.py

```python
"""Contract: Redaction rules protocol (FR-CFG-005).

Defines the inbound behavior interface for providing sensitive key
patterns and redaction rules used by consuming features for masking.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_config_vo import RedactionRule


class IRedactionRulesProtocol(ABC):
    """Protocol for providing redaction rules (FR-CFG-005)."""

    @abstractmethod
    def get_redaction_rule(self) -> RedactionRule:
        """Return the authoritative redaction rule for sensitive key detection."""
        ...

    @abstractmethod
    def redact_value(self, key: str, value: Any) -> Any:
        """Redact a value if its key matches a sensitive pattern."""
        ...

    @abstractmethod
    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Recursively redact all sensitive values in a dictionary."""
        ...
```

---

## File: modules/shared/src/config/contract_settings_loader_protocol.py

```python
"""Contract: Settings loader protocol (FR-CFG-001).

Defines the inbound behavior interface for loading, validating,
and reloading application settings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from ..common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from .taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
)
from .taxonomy_config_vo import SettingsSnapshot


class ISettingsLoaderProtocol(ABC):
    """Protocol for loading and applying settings (FR-CFG-001)."""

    @abstractmethod
    def load_settings(
        self,
        path: ConfigPath | None = None,
        overrides: Mapping[str, Any] | None = None,
    ) -> SettingsSnapshot:
        """Load settings from all sources, apply precedence, validate, return immutable snapshot."""
        ...

    @abstractmethod
    def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot. Retains previous valid snapshot on failure (permissive)."""
        ...

    @abstractmethod
    def get_last_metadata(self) -> ConfigMetadata:
        """Return metadata from the most recent successful load."""
        ...

    @abstractmethod
    def emit_loaded_event(self) -> SettingsLoadedEvent:
        """Build a settings-loaded event payload from the most recent load metadata."""
        ...

    @abstractmethod
    def emit_reload_event(self) -> SettingsReloadEvent:
        """Build a settings-reload event payload from the most recent load metadata."""
        ...

    @abstractmethod
    def emit_validation_warning_event(self) -> SettingsValidationWarningEvent | None:
        """Return warning event when permissive-mode warnings exist, else None."""
        ...
```

---

## File: modules/shared/src/config/contract_settings_metadata_protocol.py

```python
"""Contract: Settings metadata protocol (FR-CFG-004).

Defines the inbound behavior interface for exposing diagnostic metadata
about how settings were loaded, merged, and validated.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import ConfigMetadata


class ISettingsMetadataProtocol(ABC):
    """Protocol for providing settings metadata (FR-CFG-004)."""

    @abstractmethod
    def get_metadata(self) -> ConfigMetadata:
        """Return current settings metadata. Must not leak secret values."""
        ...

    @abstractmethod
    def to_safe_dict(self, metadata: ConfigMetadata) -> dict[str, Any]:
        """Serialize metadata for diagnostics. Secrets excluded, safe for MCP/CLI output."""
        ...
```

---

## File: modules/shared/src/config/contract_settings_retriever_protocol.py

```python
"""Contract: Settings retriever protocol (FR-CFG-002).

Defines the inbound behavior interface for hierarchical dot-separated
settings value retrieval with safe copy semantics.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..common.taxonomy_core_vo import ConfigPath
from .taxonomy_config_vo import SettingsSnapshot


class ISettingsRetrieverProtocol(ABC):
    """Protocol for retrieving settings values (FR-CFG-002)."""

    @abstractmethod
    def get_value(
        self,
        snapshot: SettingsSnapshot,
        path: ConfigPath,
        default: Any = None,
    ) -> Any:
        """Retrieve a value by dot-separated path. Returns deep copy to prevent mutation."""
        ...

    @abstractmethod
    def has_value(self, snapshot: SettingsSnapshot, path: ConfigPath) -> bool:
        """Check if a dot-separated path exists in the snapshot."""
        ...

    @abstractmethod
    def get_string(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: str = ""
    ) -> str:
        """Retrieve a string value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_int(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: int = 0
    ) -> int:
        """Retrieve an integer value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_bool(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: bool = False
    ) -> bool:
        """Retrieve a boolean value. Returns default on type mismatch."""
        ...

    @abstractmethod
    def get_float(
        self, snapshot: SettingsSnapshot, path: ConfigPath, default: float = 0.0
    ) -> float:
        """Retrieve a float value. Returns default on type mismatch."""
        ...
```

---

## File: modules/shared/src/config/contract_workspace_resolver_protocol.py

```python
"""Contract: Workspace resolver protocol (FR-CFG-003).

Defines the inbound behavior interface for resolving the project
workspace directory using deterministic strategies.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_config_event import WorkspaceResolvedEvent
from .taxonomy_config_vo import WorkspacePath


class IWorkspaceResolverProtocol(ABC):
    """Protocol for resolving project workspace directory (FR-CFG-003)."""

    @abstractmethod
    def resolve(self) -> WorkspacePath:
        """Resolve workspace using deterministic strategy order. Returns first valid candidate."""
        ...

    @abstractmethod
    def emit_resolved_event(self, workspace: WorkspacePath) -> WorkspaceResolvedEvent:
        """Build a workspace-resolved event payload."""
        ...
```

---

## File: modules/shared/src/config/taxonomy_config_constant.py

```python
"""Config domain constants.

Compile-time literal values for configuration management.
No classes, no functions — only ALL_CAPS declarations.
"""

from __future__ import annotations

from typing import Any

# ─── Sensitive Key Patterns (FR-CFG-005) ──────────────────────

SENSITIVE_KEY_PATTERNS: tuple[str, ...] = (
    "api_key",
    "apikey",
    "secret",
    "token",
    "password",
    "passwd",
    "credentials",
    "private",
    "auth",
    "access_key",
    "secret_key",
    "signing_key",
    "encryption_key",
    "connection_string",
)

# ─── Environment Variable Names (FR-CFG-001 / FR-CFG-003) ────

CONFIG_PATH_ENV: str = "BLENDERMCPCONFIGPATH"
WORKSPACE_ROOT_ENV: str = "BLENDERMCP_ROOT"      # replaces both legacy+product root lookup
CONFIG_V2_FLAG_ENV: str = "BLENDERMCPCONFIG_V2"
DEFAULT_CONFIG_FILENAME: str = "config.yaml"

# Environment keys that are control signals, never settings overrides.
RESERVED_ENV_KEYS: tuple[str, ...] = (
    "BLENDERMCPCONFIGPATH",
    "BLENDERMCP_ROOT",
    "BLENDERMCPCONFIG_V2",
)

# ─── Event Sink (FR-CFG-001 / T-09) ──────────────────────────

EVENT_RING_BUFFER_SIZE: int = 50

# ─── Project Markers (FR-CFG-003) ────────────────────────────
# Manifest markers precede version-control metadata per FR-CFG-003.

PROJECT_MARKERS: tuple[str, ...] = (
    "config.yaml",
    "config.yml",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
    ".git",
)

# ─── Compile-Time Defaults (FR-CFG-001, Q4) ──────────────────

DEFAULT_SETTINGS: dict[str, Any] = {
    "blender": {"executable_path": "blender", "host": "localhost", "port": 9876},
    "server": {"transport": "stdio", "log_dir": "log"},
}

# ─── Settings Schema (FR-CFG-001, Q3) ───────────────────────
# Python-native schema: node = {"type", "required", "children"}.

SETTINGS_SCHEMA: dict[str, Any] = {
    "blender": {
        "type": "dict",
        "required": False,
        "children": {
            "executable_path": {"type": "str", "required": False},
            "host": {"type": "str", "required": False},
            "port": {"type": "int", "required": False},
        },
    },
    "server": {
        "type": "dict",
        "required": False,
        "children": {
            "transport": {"type": "str", "required": False},
            "log_dir": {"type": "str", "required": False},
        },
    },
}

# ─── Limits (FR-CFG-001) ─────────────────────────────────────

MAX_CONFIG_SIZE_BYTES: int = 1024 * 1024  # 1 MiB

# ─── Environment Override Prefix (FR-CFG-001) ───────────────

ENV_PREFIX_PRODUCT: str = "BLENDERMCP_"  # legacy BLENDER_MCP_ prefix removed (v1.7.0 BREAKING)

# ─── Redaction Placeholder (FR-CFG-005) ──────────────────────

REDACTION_PLACEHOLDER: str = "***REDACTED***"

# ─── Policy Modes (FR-CFG-001) ───────────────────────────────

POLICY_MODE_STRICT: str = "strict"
POLICY_MODE_PERMISSIVE: str = "permissive"

DEFAULT_POLICY_MODE: str = "strict"

# ─── Scene Management Defaults (FR-SCN-001, FR-SCN-002) ──────────────

# Default preservation list — categories preserved during cleanup when request does not specify explicit preservation.
DEFAULT_PRESERVATION_LIST: tuple[str, ...] = (
    "camera",
    "light",
    "active_camera",
    "sole_camera",
    "protected",
)

# Default dry-run mode — whether cleanup defaults to preview-only mode.
DEFAULT_DRY_RUN_MODE: bool = False

# Include hidden objects in inspection — whether hidden objects are included by default.
DEFAULT_INCLUDE_HIDDEN_OBJECTS: bool = False

# Maximum inspection detail limit — limit for object detail returned during inspection.
MAX_INSPECTION_DETAIL_LIMIT: int = 1000

# Default cleanup timeout in seconds.
CLEANUP_TIMEOUT_SECONDS: float = 30.0

# Default inspection timeout in seconds.
INSPECTION_TIMEOUT_SECONDS: float = 15.0

# Cleanup confirmation required — whether destructive cleanup requires explicit confirmation when undo is unavailable.
CLEANUP_CONFIRMATION_REQUIRED: bool = True

# Default child handling policy — behavior for children of deleted objects.
DEFAULT_CHILD_HANDLING_POLICY: str = "detach"  # "delete", "detach", "reject"

# Default dependent handling policy — behavior for dependents such as constraints or references.
DEFAULT_DEPENDENT_HANDLING_POLICY: str = "reject"  # "ignore", "reject", "remove_safe"

# Protected object policy defaults.
PROTECTED_OBJECT_POLICY_ACTIVE_CAMERA: bool = True
PROTECTED_OBJECT_POLICY_SOLE_CAMERA: bool = True
PROTECTED_OBJECT_POLICY_LIGHTS: bool = True
PROTECTED_OBJECT_POLICY_PROTECTED: bool = True
```

---

## File: modules/shared/src/config/taxonomy_config_error.py

```python
"""Domain error types for the config domain."""

from __future__ import annotations

from ..common.taxonomy_core_vo import Details, ErrorString
from ..common.taxonomy_domain_error import BlenderMCPError


class ConfigError(BlenderMCPError):
    """Base for all configuration-related errors."""

    def __init__(self, message: ErrorString | None = None, details: Details | None = None) -> None:
        message = message or ErrorString("Configuration error")
        super().__init__(message)
        self.details = details or {}


class ConfigParseError(ConfigError):
    """Raised when YAML parsing fails (strict mode)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration parse error"))


class ConfigLoadError(ConfigError):
    """Raised when configuration loading fails (missing file, permission denied, oversized source)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration load error"))


class ConfigValidationError(ConfigError):
    """Raised when configuration fails schema validation (strict mode)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration validation error"))


class ConfigPathError(ConfigError):
    """Raised when a configuration path is invalid or malformed."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration path error"))


class ConfigTypeError(ConfigError):
    """Raised when a configuration value does not match expected type (strict mode)."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration type error"))


class ConfigRootResolutionError(ConfigError):
    """Raised when project root cannot be resolved from any strategy."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration root resolution error"))
```

---

## File: modules/shared/src/config/taxonomy_config_event.py

```python
"""Config domain events.

Domain events emitted by the configuration feature.
All payloads exclude raw settings content and secret values.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from ..common.taxonomy_core_vo import Timestamp


@dataclass(frozen=True)
class SettingsLoadedEvent:
    """Emitted after settings snapshot is successfully loaded."""

    category: str = "settings"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "strict"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))


@dataclass(frozen=True)
class SettingsReloadEvent:
    """Emitted after settings snapshot is successfully replaced."""

    category: str = "settings"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "strict"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))


@dataclass(frozen=True)
class WorkspaceResolvedEvent:
    """Emitted after project workspace directory is resolved."""

    category: str = "workspace"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "strict"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))


@dataclass(frozen=True)
class SettingsValidationWarningEvent:
    """Emitted when schema or parse warnings occur in permissive mode."""

    category: str = "validation"
    source_summary: str = ""
    override_count: int = 0
    warning_count: int = 0
    policy_mode: str = "permissive"
    timestamp: Timestamp = field(default_factory=lambda: Timestamp(0.0))
```

---

## File: modules/shared/src/config/taxonomy_config_vo.py

```python
"""Config domain value objects.

Immutable domain types for configuration management:
- SettingsSnapshot: merged, immutable settings container
- WorkspacePath: resolved project workspace directory
- RedactionRule: pattern-based sensitive value masking rule
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any

_MISSING = object()  # module-private sentinel for "no value"


@dataclass(frozen=True)
class SettingsSnapshot:
    """Immutable snapshot of merged configuration values.

    Created after load/reload. Never mutated after construction.
    Supports deep traversal via get()/get_segments() without exposing internals.
    """

    _data: dict[str, Any] = field(repr=False, default_factory=dict)

    # ─── Segment traversal (T-04) ───────────────────────────────
    # These operate on pre-split segment tuples so the retriever can pass
    # escape-aware segments. get()/has() delegate to them.

    def get_segments(self, segments: tuple[str, ...], default: Any = None) -> Any:
        """Retrieve value by pre-split segment tuple. Returns deep copy."""
        if not segments:
            return copy.deepcopy(self._data)

        value: Any = self._data
        for segment in segments:
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            elif isinstance(value, list):
                try:
                    idx = int(segment)
                except (ValueError, TypeError):
                    return default
                if not isinstance(idx, int) or isinstance(idx, bool):
                    return default
                if 0 <= idx < len(value):
                    value = value[idx]
                else:
                    return default  # out-of-range: stop, do not continue with default as node
            else:
                return default

        return copy.deepcopy(value)

    def has_segments(self, segments: tuple[str, ...]) -> bool:
        """Check if a pre-split segment tuple exists in the snapshot."""
        if not segments:
            return True

        value: Any = self._data
        for segment in segments:
            if isinstance(value, dict) and segment in value:
                value = value[segment]
            elif isinstance(value, list):
                try:
                    idx = int(segment)
                except (ValueError, TypeError):
                    return False
                if not isinstance(idx, int) or isinstance(idx, bool):
                    return False
                if 0 <= idx < len(value):
                    value = value[idx]
                else:
                    return False
            else:
                return False

        return True

    # ─── Dot-path delegation (T-04) ─────────────────────────────

    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve value by dot-separated path. Returns deep copy."""
        return self.get_segments(tuple(path.split(".")) if path else (), default)

    def has(self, path: str) -> bool:
        """Check if a dot-separated path exists in the snapshot."""
        return self.has_segments(tuple(path.split(".")) if path else ())

    def to_dict(self) -> dict[str, Any]:
        """Return deep copy of raw settings dict."""
        return copy.deepcopy(self._data)


@dataclass(frozen=True)
class WorkspacePath:
    """Resolved project workspace directory path."""

    path: str
    strategy: str

    def __post_init__(self) -> None:
        if not self.path:
            raise ValueError("WorkspacePath.path must not be empty")
        if not self.strategy:
            raise ValueError("WorkspacePath.strategy must not be empty")


@dataclass(frozen=True)
class RedactionRule:
    """Rule for redacting sensitive configuration values.

    Defines which keys are sensitive and how to mask them.
    """

    key_patterns: tuple[str, ...] = field(default_factory=tuple)
    placeholder: str = "***REDACTED***"
    full_redact: bool = True

    def matches_key(self, key: str) -> bool:
        """Check if a key matches any of the sensitive patterns.

        Substring semantics are intentional (PM Q14): e.g. ``auth`` also
        matches ``author`` — an accepted false positive.
        """
        key_lower = key.lower()
        return any(pattern.lower() in key_lower for pattern in self.key_patterns)
```

---

## File: modules/shared/src/config/utility_config_helpers.py

```python
"""Utility: Config helper functions.

Stateless, domain-agnostic standalone functions extracted from capabilities.
No class, no protocol impl, pure functions only.
Only depends on Taxonomy + stdlib + yaml.
"""

from __future__ import annotations

import copy
import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from modules.shared.src.common.taxonomy_core_vo import ConfigPath
from modules.shared.src.config.taxonomy_config_constant import (
    DEFAULT_CONFIG_FILENAME,
)
from modules.shared.src.config.taxonomy_config_error import ConfigParseError


def parse_env_value(value: str) -> Any:
    """Parse environment value as typed scalar (scalar-only per Q7).

    boolean-like → bool, integer-like → int, float-like → float,
    null-like → None, otherwise → str. Lists/mappings are intentionally
    NOT parsed — they remain strings (Q7).
    """
    if value.lower() in ("true", "yes", "on"):
        return True
    if value.lower() in ("false", "no", "off"):
        return False
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    if value.lower() in ("null", "none", ""):
        return None
    return value


def search_project_root(markers: tuple[str, ...]) -> Path | None:
    """Search upward from cwd for recognized project markers.

    Returns first parent containing any marker, or None.
    """
    current = Path.cwd().resolve()
    for parent in [current, *current.parents]:
        for marker in markers:
            candidate = parent / marker
            try:
                if candidate.exists():
                    return parent
            except OSError:
                continue
    return None


def resolve_default_config_path(explicit: ConfigPath | None = None) -> ConfigPath:
    """Resolve the config file path.

    Priority: explicit → env BLENDERMCPCONFIGPATH → cwd/config.yaml.
    """
    if explicit:
        return ConfigPath(str(explicit))
    env_path = os.environ.get("BLENDERMCPCONFIGPATH")
    if env_path:
        return ConfigPath(str(env_path))
    return ConfigPath(str(Path.cwd() / DEFAULT_CONFIG_FILENAME))


def load_yaml_safe(path: ConfigPath) -> dict[str, Any]:
    """Read a YAML file safely.

    Decode 'utf-8-sig' (BOM tolerated). UnicodeDecodeError → ConfigParseError.
    yaml.YAMLError → ConfigParseError. None → {}. Non-dict root → ConfigParseError.
    """
    raw = Path(str(path)).read_bytes()
    try:
        text = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ConfigParseError(f"Settings file is not valid UTF-8: {path}") from exc

    try:
        data = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ConfigParseError(f"Failed to parse settings YAML: {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ConfigParseError(f"Settings root must be a mapping, got {type(data).__name__}: {path}")
    return data


def deep_merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge ``override`` into a copy of ``base``.

    Dict + dict recurses; override wins otherwise. Inputs never mutated.
    """
    result: dict[str, Any] = copy.deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dicts(result[key], value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def set_nested_value(target: dict[str, Any], segments: tuple[str, ...], value: Any) -> None:
    """Set ``value`` at dotted ``segments`` inside ``target`` in place.

    Creates intermediate dicts for missing/non-dict nodes.
    """
    if not segments:
        return
    node = target
    for segment in segments[:-1]:
        existing = node.get(segment)
        if not isinstance(existing, dict):
            existing = {}
            node[segment] = existing
        node = existing
    node[segments[-1]] = copy.deepcopy(value)


def apply_env_overrides(
    config: dict[str, Any],
    environ: Mapping[str, str],
    prefix: str,
    reserved: tuple[str, ...],
) -> tuple[dict[str, Any], int]:
    """Apply environment variable overrides with nested key convention.

    Iterates sorted(environ.items()) for determinism. Skips reserved keys and
    keys whose remainder after prefix is empty. Lowercases remainder, splits on
    '.', creates intermediates (env may introduce new keys). Returns
    (newdict, applied_count). Inputs not mutated.
    """
    result = copy.deepcopy(config)
    applied = 0

    for key in sorted(environ.keys()):
        if key in reserved:
            continue
        if not key.startswith(prefix):
            continue
        remainder = key[len(prefix):]
        if not remainder:
            continue
        remainder = remainder.lower()
        segments = tuple(remainder.split("."))
        set_nested_value(result, segments, parse_env_value(environ[key]))
        applied += 1

    return result, applied


def validate_settings_schema(
    data: dict[str, Any],
    schema: dict[str, Any],
) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Validate ``data`` against a Python-native schema.

    Returns (errors, warnings). ``int`` type excludes bool.
    """
    errors: list[str] = []
    warnings: list[str] = []

    def walk(node: Any, node_schema: dict[str, Any], path: str) -> None:
        node_type = node_schema.get("type", "any")
        required = node_schema.get("required", False)

        if node is None:
            if required:
                errors.append(f"{path}: missing required value")
            return

        if node_type == "dict":
            if not isinstance(node, dict):
                errors.append(f"{path}: expected dict, got {type(node).__name__}")
                return
            children = node_schema.get("children", {})
            for child_key, child_node in node.items():
                child_schema = children.get(child_key)
                if child_schema is None:
                    warnings.append(f"{path}.{child_key}: unknown key")
                    continue
                walk(child_node, child_schema, f"{path}.{child_key}")
            return

        if node_type == "int":
            if isinstance(node, bool) or not isinstance(node, int):
                errors.append(f"{path}: expected int, got {type(node).__name__}")
            return

        if node_type == "str":
            if not isinstance(node, str):
                errors.append(f"{path}: expected str, got {type(node).__name__}")
            return

        if node_type == "float":
            if isinstance(node, bool) or not isinstance(node, (int, float)):
                errors.append(f"{path}: expected float, got {type(node).__name__}")
            return

        if node_type == "bool":
            if not isinstance(node, bool):
                errors.append(f"{path}: expected bool, got {type(node).__name__}")
            return

        if node_type == "list":
            if not isinstance(node, list):
                errors.append(f"{path}: expected list, got {type(node).__name__}")
            return

        # "any" or unknown: no type check
        return

    for key, value in data.items():
        key_schema = schema.get(key)
        if key_schema is None:
            warnings.append(f"{key}: unknown key")
            continue
        walk(value, key_schema, key)

    return tuple(errors), tuple(warnings)


def parse_settings_path(path: str, escape_enabled: bool) -> tuple[str, ...]:
    """Split a dotted path into segments.

    When ``escape_enabled``, '\\.' yields a literal '.' inside a segment.
    Empty path → (). Trailing/leading/repeated separators produce empty
    segments which resolve as missing keys (returns default).
    """
    if not path:
        return ()

    if not escape_enabled:
        return tuple(path.split("."))

    segments: list[str] = []
    current = ""
    i = 0
    while i < len(path):
        ch = path[i]
        if ch == "\\" and i + 1 < len(path) and path[i + 1] == ".":
            current += "."
            i += 2
            continue
        if ch == ".":
            segments.append(current)
            current = ""
            i += 1
            continue
        current += ch
        i += 1
    segments.append(current)
    return tuple(segments)
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

