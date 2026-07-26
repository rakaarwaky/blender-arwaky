# Module: config (v1.6.5)

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

None (foundational feature).

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
  - Malformed settings content raises configuration error in strict mode
  - Malformed settings content logs warning and falls back safely in permissive mode
  - Schema violation raises validation error in strict mode
  - Schema violation logs warning and continues where safe in permissive mode
  - Environment values are converted to typed values when safely detectable:
    - boolean-like values become boolean
    - integer-like values become integer
    - float-like values become float
    - null-like values become empty value
    - list-like or mapping-like values may be parsed when safely detectable
    - otherwise values remain text
  - Environment overrides use product-specific prefix and deterministic nested key convention
  - Legacy environment prefix may be accepted as fallback for backward compatibility
  - Settings snapshot must be immutable after successful load
  - Settings snapshot must be cached after first successful load
  - Reload must replace snapshot atomically under synchronization
  - Failed load must not expose partial settings state
  - Failed reload must retain previous valid snapshot unless strict mode requires failure propagation
  - Settings source size must be limited to prevent excessive memory usage
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
    2. Product-specific workspace environment signal
    3. Legacy workspace environment signal when backward compatibility is enabled
    4. Settings file location, using its parent directory
    5. Upward proximity search for recognized project marker concepts
    6. Platform-standard user configuration location
    7. Current working directory
  - Project marker priority should be:
    1. Primary settings source
    2. Product-specific settings source
    3. Project manifest
    4. Version control metadata
  - Resolved path must be normalized
  - Symbolic links must be resolved safely without unnecessary failure
  - Candidate directory must exist and be readable to be accepted
  - Invalid environment-provided path logs warning and falls through to next strategy
  - First valid candidate according to resolution order wins
  - Workspace resolution must not create directories by default
  - If no valid candidate exists, fallback to current working directory
  - If current working directory is inaccessible, raise workspace resolution error
  - Resolution result should be cached and reused consistently across features
  - All file-writing features must derive allowed locations from this resolution rather than their own rules
- **Edge Cases**: Multiple candidate directories, symlinked directories, non-existent candidate, permission denied candidate, network-mounted filesystem, case-insensitive filesystem, settings location pointing to file versus directory, circular symbolic link, empty environment value, relative path, deleted working directory, platform-specific remote path
- **Error Handling**: Warning and fallthrough for invalid environment path; fallthrough for non-existent or unreadable candidate; workspace resolution error only when all strategies fail and working directory is inaccessible

### FR-CFG-004: Provide Settings Metadata

Config provides config source, override count, and warnings. Metadata must not leak secrets.

- **Description**: Expose diagnostic metadata about how settings were loaded, merged, and validated
- **Input**: None
- **Output**: Settings metadata concept containing source information, override information, warning list, and load timing information
- **Business Rules**:
  - Metadata should include:
    - resolved settings source location
    - whether settings file existed
    - whether environment overrides were applied
    - count of applied overrides
    - count of applied defaults
    - parse warning list
    - validation warning list
    - policy mode in effect, strict or permissive
    - snapshot load or reload timestamp
    - workspace directory resolution summary
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

- **Description**: Provide the authoritative list of sensitive key patterns and redaction rules used by consuming features to mask secret values
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
  - Rules may be extended through settings without code changes
  - Rules must define placeholder convention used during masking
  - Rules themselves contain key names and patterns only, never secret values
  - Consuming features must retrieve rules from config or security policy and must not hard-code their own lists
  - Rule updates must be reflected consistently across diagnostics, command-line output, and MCP-facing responses
  - Rules should distinguish between full redaction and partial masking where supported
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

| Configuration Concept | Description | Typical Default |
| --------------------- | ----------- | --------------- |
| Settings source location | Location of primary settings file used during load | Resolved from workspace or platform-standard location |
| Workspace directory | Project root directory used for file-based operations | Resolved through deterministic workspace strategies |
| Sensitive key list | List of key names and patterns treated as secret for redaction | Common token, key, password, and credential patterns |
| Environment override prefix | Product-specific prefix recognized for environment overrides | Product prefix with nested key convention |
| Legacy environment fallback | Whether legacy environment prefix is accepted | Enabled for backward compatibility |
| Policy mode | Strict or permissive behavior for parse and schema issues | Strict |
| Maximum settings size | Maximum allowed settings source size | Conservative size limit |
| Default values source | Built-in defaults applied when no other source provides value | Feature-defined safe defaults |

## QA Checklist

- [ ] Settings load from file, environment, and defaults with correct precedence
- [ ] Runtime override takes precedence over environment, file, and defaults
- [ ] Environment override takes precedence over file and defaults
- [ ] File values take precedence over built-in defaults
- [ ] Missing settings file falls back to environment and defaults without fatal error
- [ ] Malformed settings content raises configuration error in strict mode
- [ ] Malformed settings content falls back safely in permissive mode
- [ ] Schema violation raises validation error in strict mode
- [ ] Schema violation logs warning in permissive mode
- [ ] Unsafe settings content is rejected without object instantiation
- [ ] Oversized settings source raises load error
- [ ] Environment values convert to boolean, integer, float, null, list, and mapping types correctly
- [ ] Legacy environment prefix fallback works when enabled
- [ ] Immutable snapshot returned on retrieve
- [ ] Retrieved structured values are deep-copied or immutable
- [ ] Missing key returns provided default
- [ ] Empty path returns full settings snapshot safely
- [ ] List position access works and out-of-range returns default
- [ ] Expected type mismatch returns default in permissive mode
- [ ] Expected type mismatch raises type conversion error in strict mode
- [ ] Concurrent first access loads settings only once
- [ ] Reload replaces snapshot atomically
- [ ] Failed reload retains previous valid snapshot in non-fatal mode
- [ ] Project workspace resolves correctly through explicit override
- [ ] Project workspace resolves correctly through environment signal
- [ ] Project workspace resolves correctly through settings file location
- [ ] Project workspace resolves correctly through proximity markers
- [ ] Project workspace falls back to current working directory
- [ ] Project workspace handles symlinked directories safely
- [ ] Project workspace resolution does not create directories by default
- [ ] Asset and render derive root locations from workspace resolution instead of own rules
- [ ] Settings metadata reports source, override count, and warnings
- [ ] Settings metadata does not leak secret values
- [ ] Redaction keys mask sensitive values in diagnostics
- [ ] Redaction keys mask sensitive values in command-line output
- [ ] Redaction keys mask sensitive values in MCP-facing responses
- [ ] Redaction rules contain key patterns only, never secret values
- [ ] Custom redaction rules extend built-in defaults safely
- [ ] Settings loaded event emitted after successful load
- [ ] Settings reload event emitted after successful reload
- [ ] Workspace resolved event emitted after resolution
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
via protocol interfaces.
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
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

# ─── Block 2: Aggregate Method Implementation ─────────────

    def load(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Load settings and cache snapshot."""
        self._snapshot = self._loader.load_settings(path)
        return self._snapshot

    def reload(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot."""
        self._snapshot = self._loader.reload_settings(path)
        return self._snapshot

    def get_snapshot(self) -> SettingsSnapshot:
        """Return cached snapshot, lazy-loading if needed."""
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
        """Delegate workspace resolution."""
        return self._workspace_resolver.resolve()

    def get_metadata(self) -> ConfigMetadata | None:
        """Delegate metadata retrieval."""
        return self._metadata_provider.get_metadata()

    def get_redaction_rule(self) -> RedactionRule:
        """Delegate redaction rule retrieval."""
        return self._redaction_rules.get_redaction_rule()

    def redact_dict(self, data: dict[str, Any]) -> dict[str, Any]:
        """Delegate dictionary redaction."""
        return self._redaction_rules.redact_dict(data)

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

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
    Consuming features retrieve rules here — must not hard-code their own lists.
    """

    def __init__(self, extra_patterns: tuple[str, ...] = ()) -> None:
        self._rule = RedactionRule(
            key_patterns=SENSITIVE_KEY_PATTERNS + extra_patterns,
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
override application, typed conversion, size limits.
"""

from __future__ import annotations

import copy
import os
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata, ConfigPath, Timestamp
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.taxonomy_config_constant import (
    ENV_PREFIX_LEGACY,
    ENV_PREFIX_PRODUCT,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
)
from modules.shared.src.config.taxonomy_config_error import (
    ConfigLoadError,
    ConfigParseError,
    ConfigValidationError,
)
from modules.shared.src.config.taxonomy_config_event import SettingsLoadedEvent, SettingsReloadEvent
from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot

from modules.shared.src.config.utility_config_helpers import parse_env_value


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsLoaderCapability(ISettingsLoaderProtocol):
    """FR-CFG-001: Load and apply settings.

    Responsible for: YAML safe parsing, environment override application
    with typed conversion, precedence merging, size limits, immutable
    snapshot creation, and policy-mode error handling.
    """

    def __init__(
        self,
        config_file_loader: Any = None,
        policy_mode: str = POLICY_MODE_STRICT,
    ) -> None:
        self._file_loader = config_file_loader
        self._policy_mode = policy_mode
        self._cached: SettingsSnapshot | None = None

# ─── Block 2: Protocol Method Implementation ──────────────

    def load_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Load settings from sources, apply precedence, return immutable snapshot."""
        file_data = self._load_file(path)
        merged = self._apply_env_overrides(file_data)
        self._cached = SettingsSnapshot(_data=merged)
        return self._cached

    def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot. Retains previous on failure (permissive)."""
        previous = self._cached
        try:
            self._cached = None
            return self.load_settings(path)
        except Exception:
            if self._policy_mode == POLICY_MODE_PERMISSIVE and previous is not None:
                self._cached = previous
                return previous
            raise

    def emit_loaded_event(self, snapshot: SettingsSnapshot) -> SettingsLoadedEvent:
        """Build settings-loaded event from snapshot."""
        return SettingsLoadedEvent(
            source_summary="loaded",
            override_count=0,
            warning_count=0,
            policy_mode=self._policy_mode,
            timestamp=Timestamp(0.0),
        )

    def emit_reload_event(self, snapshot: SettingsSnapshot) -> SettingsReloadEvent:
        """Build settings-reload event from snapshot."""
        return SettingsReloadEvent(
            source_summary="reloaded",
            override_count=0,
            warning_count=0,
            policy_mode=self._policy_mode,
            timestamp=Timestamp(0.0),
        )

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def _load_file(self, path: ConfigPath | None) -> dict[str, Any]:
        """Load and parse YAML from file path."""
        if self._file_loader is None:
            return {}

        try:
            result = self._file_loader(path)
            if isinstance(result, dict):
                return result
            return {}
        except Exception as exc:
            if self._policy_mode == POLICY_MODE_STRICT:
                if isinstance(exc, (ConfigParseError, ConfigLoadError, ConfigValidationError)):
                    raise
                raise ConfigLoadError(f"Failed to load settings: {exc}") from exc
            return {}

    def _apply_env_overrides(self, config: dict[str, Any]) -> dict[str, Any]:
        """Apply environment variable overrides with typed scalar conversion."""
        if not isinstance(config, dict):
            return config

        result = copy.deepcopy(config)

        for key, value in os.environ.items():
            if key.startswith(ENV_PREFIX_PRODUCT) or key.startswith(ENV_PREFIX_LEGACY):
                prefix = (
                    ENV_PREFIX_PRODUCT if key.startswith(ENV_PREFIX_PRODUCT) else ENV_PREFIX_LEGACY
                )
                env_key = key[len(prefix):].lower()
                parsed = parse_env_value(value)

                if "." in env_key:
                    keys = env_key.split(".")
                    node = result
                    for k in keys[:-1]:
                        if k not in node or not isinstance(node[k], dict):
                            break
                        node = node[k]
                    if keys[-1] in node:
                        node[keys[-1]] = parsed
                else:
                    result[env_key] = parsed

        return result
```

---

## File: modules/config/src/capabilities_settings_metadata.py

```python
"""Capability: Settings metadata provider (FR-CFG-004).

Implements ISettingsMetadataProtocol — exposes diagnostic metadata
about settings loading without leaking secrets.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ConfigMetadata
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsMetadataCapability(ISettingsMetadataProtocol):
    """FR-CFG-004: Provide settings metadata.

    Exposes source, override count, warnings, policy mode, and timestamps.
    Must never include secret values or raw settings content.
    """

    def __init__(self, metadata: ConfigMetadata | None = None) -> None:
        self._metadata = metadata

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_metadata(self) -> ConfigMetadata:
        """Return current settings metadata."""
        if self._metadata is None:
            return ConfigMetadata()
        return self._metadata

    def to_safe_dict(self, metadata: ConfigMetadata) -> dict[str, Any]:
        """Serialize metadata for diagnostics output."""
        return {
            "source": metadata.source,
            "exists": metadata.exists,
            "overrides": metadata.overrides,
            "parse_warnings": metadata.parse_warnings,
            "validation_warnings": metadata.validation_warnings,
        }

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "SettingsMetadataCapability()"
```

---

## File: modules/config/src/capabilities_settings_retriever.py

```python
"""Capability: Settings retriever (FR-CFG-002).

Implements ISettingsRetrieverProtocol — hierarchical dot-separated
settings value retrieval with safe copy semantics.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.taxonomy_config_vo import SettingsSnapshot


# ─── Block 1: Class Definition & Constructor ───────────────
class SettingsRetrieverCapability(ISettingsRetrieverProtocol):
    """FR-CFG-002: Retrieve settings values.

    Thread-safe traversal, deep-copy returns, list indexing support.
    No I/O. No file or environment reads per request.
    """

    def __init__(self) -> None:
        pass

# ─── Block 2: Protocol Method Implementation ──────────────

    def get_value(
        self,
        snapshot: SettingsSnapshot,
        path: str,
        default: Any = None,
    ) -> Any:
        """Retrieve value by dot-separated path. Returns deep copy."""
        return snapshot.get(path, default)

    def has_value(self, snapshot: SettingsSnapshot, path: str) -> bool:
        """Check if a dot-separated path exists."""
        return snapshot.has(path)

    def get_string(self, snapshot: SettingsSnapshot, path: str, default: str = "") -> str:
        """Retrieve string value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, str) else default

    def get_int(self, snapshot: SettingsSnapshot, path: str, default: int = 0) -> int:
        """Retrieve integer value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, int) and not isinstance(value, bool) else default

    def get_bool(self, snapshot: SettingsSnapshot, path: str, default: bool = False) -> bool:
        """Retrieve boolean value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, bool) else default

    def get_float(self, snapshot: SettingsSnapshot, path: str, default: float = 0.0) -> float:
        """Retrieve float value. Returns default on type mismatch."""
        value = snapshot.get(path, default)
        return value if isinstance(value, float) else default

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

    def __repr__(self) -> str:
        return "SettingsRetrieverCapability()"
```

---

## File: modules/config/src/capabilities_workspace_resolver.py

```python
"""Capability: Workspace resolver (FR-CFG-003).

Implements IWorkspaceResolverProtocol — resolves project workspace
directory using deterministic strategies.
"""

from __future__ import annotations

import os
from pathlib import Path

from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import PROJECT_MARKERS
from modules.shared.src.config.taxonomy_config_error import ConfigRootResolutionError
from modules.shared.src.config.taxonomy_config_event import WorkspaceResolvedEvent
from modules.shared.src.config.taxonomy_config_vo import WorkspacePath

from modules.shared.src.config.utility_config_helpers import search_project_root


# ─── Block 1: Class Definition & Constructor ───────────────
class WorkspaceResolverCapability(IWorkspaceResolverProtocol):
    """FR-CFG-003: Resolve project workspace directory.

    Resolution order: explicit override > env signal > marker search
    > platform config > CWD.
    """

    def __init__(self, explicit_override: str | None = None) -> None:
        self._explicit_override = explicit_override

# ─── Block 2: Protocol Method Implementation ──────────────

    def resolve(self) -> WorkspacePath:
        """Resolve workspace using deterministic strategy order."""
        if self._explicit_override:
            candidate = Path(self._explicit_override).resolve()
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="explicit_override")

        env_root = os.environ.get("BLENDER_MCP_ROOT") or os.environ.get("BLENDERMCP_ROOT")
        if env_root:
            try:
                candidate = Path(env_root).resolve()
                if candidate.is_dir():
                    return WorkspacePath(path=str(candidate), strategy="env_signal")
            except (OSError, ValueError):
                pass

        marker_path = search_project_root(PROJECT_MARKERS)
        if marker_path:
            return WorkspacePath(path=str(marker_path), strategy="marker_search")

        xdg_config = os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))
        prod_path = Path(xdg_config) / "blender-arwaky"
        if prod_path.is_dir():
            return WorkspacePath(path=str(prod_path), strategy="platform_config")

        try:
            cwd = Path.cwd().resolve()
            if cwd.is_dir():
                return WorkspacePath(path=str(cwd), strategy="cwd_fallback")
        except OSError as exc:
            raise ConfigRootResolutionError("All workspace resolution strategies failed") from exc

        raise ConfigRootResolutionError("All workspace resolution strategies failed")

    def emit_resolved_event(self, workspace: WorkspacePath) -> WorkspaceResolvedEvent:
        """Build workspace-resolved event payload."""
        return WorkspaceResolvedEvent(
            source_summary=workspace.strategy,
            override_count=0,
            warning_count=0,
        )

# ─── Block 3: Dunder Methods, Factories, Helpers ──────────

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

import logging

from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
from modules.shared.src.config.contract_settings_loader_protocol import ISettingsLoaderProtocol
from modules.shared.src.config.contract_settings_metadata_protocol import ISettingsMetadataProtocol
from modules.shared.src.config.contract_settings_retriever_protocol import ISettingsRetrieverProtocol
from modules.shared.src.config.contract_workspace_resolver_protocol import IWorkspaceResolverProtocol
from modules.shared.src.config.taxonomy_config_constant import POLICY_MODE_STRICT

from .agent_config_orchestrator import ConfigOrchestrator
from .capabilities_redaction_rules import RedactionRulesCapability
from .capabilities_settings_loader import SettingsLoaderCapability
from .capabilities_settings_metadata import SettingsMetadataCapability
from .capabilities_settings_retriever import SettingsRetrieverCapability
from .capabilities_workspace_resolver import WorkspaceResolverCapability

logger = logging.getLogger("BlenderMCPServer")


class ConfigContainer:
    """DI container for the config feature.

    Wires capabilities to protocol interfaces and constructs the
    IConfigAggregate facade (ConfigOrchestrator).
    """

    def __init__(
        self,
        config_file_loader: object | None = None,
        policy_mode: str = POLICY_MODE_STRICT,
        explicit_workspace: str | None = None,
        extra_redaction_patterns: tuple[str, ...] = (),
    ) -> None:
        self._config_file_loader = config_file_loader
        self._policy_mode = policy_mode
        self._explicit_workspace = explicit_workspace
        self._extra_redaction_patterns = extra_redaction_patterns

        # Capabilities (wired to protocols)
        self._loader: ISettingsLoaderProtocol = SettingsLoaderCapability(
            config_file_loader=config_file_loader,
            policy_mode=policy_mode,
        )
        self._retriever: ISettingsRetrieverProtocol = SettingsRetrieverCapability()
        self._workspace_resolver: IWorkspaceResolverProtocol = WorkspaceResolverCapability(
            explicit_override=explicit_workspace,
        )
        self._metadata_provider: ISettingsMetadataProtocol = SettingsMetadataCapability()
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

# ─── Taxonomy: Value Objects ───────────────────────────────────
from .taxonomy_config_vo import (
    RedactionRule,
    SensitiveKeyPattern,
    SettingsSnapshot,
    WorkspacePath,
)

# ─── Taxonomy: Events ──────────────────────────────────────────
from .taxonomy_config_event import (
    SettingsLoadedEvent,
    SettingsReloadEvent,
    SettingsValidationWarningEvent,
    WorkspaceResolvedEvent,
)

# ─── Taxonomy: Constants ───────────────────────────────────────
from .taxonomy_config_constant import (
    DEFAULT_POLICY_MODE,
    ENV_PREFIX_LEGACY,
    ENV_PREFIX_PRODUCT,
    MAX_CONFIG_SIZE_BYTES,
    POLICY_MODE_PERMISSIVE,
    POLICY_MODE_STRICT,
    PROJECT_MARKERS,
    REDACTION_PLACEHOLDER,
    SENSITIVE_KEY_PATTERNS,
)

# ─── Utility ───────────────────────────────────────────────────
from .utility_config_helpers import parse_env_value, search_project_root

# ─── Taxonomy: Errors ──────────────────────────────────────────
from .taxonomy_config_error import (
    ConfigError,
    ConfigLoadError,
    ConfigParseError,
    ConfigPathError,
    ConfigProviderError,
    ConfigRootResolutionError,
    ConfigTypeError,
    ConfigValidationError,
)

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
    "SensitiveKeyPattern",
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
    "ENV_PREFIX_LEGACY",
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
    "ConfigProviderError",
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
from typing import Any

from ..common.taxonomy_core_vo import ConfigMetadata, ConfigPath
from .taxonomy_config_vo import RedactionRule, SettingsSnapshot, WorkspacePath


class IConfigAggregate(ABC):
    """Aggregate facade for the config feature.

    Surface layer delegates all config operations through this interface.
    """

    # ─── Lifecycle ──────────────────────────────────────────────

    @abstractmethod
    def load(self, path: ConfigPath | None = None) -> SettingsSnapshot:
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

from ..common.taxonomy_core_vo import ConfigPath
from .taxonomy_config_event import SettingsLoadedEvent, SettingsReloadEvent
from .taxonomy_config_vo import SettingsSnapshot


class ISettingsLoaderProtocol(ABC):
    """Protocol for loading and applying settings (FR-CFG-001)."""

    @abstractmethod
    def load_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Load settings from all sources, apply precedence, validate, return immutable snapshot."""
        ...

    @abstractmethod
    def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
        """Atomically replace cached snapshot. Retains previous valid snapshot on failure (permissive)."""
        ...

    @abstractmethod
    def emit_loaded_event(self, snapshot: SettingsSnapshot) -> SettingsLoadedEvent:
        """Build a settings-loaded event payload for the given snapshot."""
        ...

    @abstractmethod
    def emit_reload_event(self, snapshot: SettingsSnapshot) -> SettingsReloadEvent:
        """Build a settings-reload event payload for the given snapshot."""
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

# ─── Project Markers (FR-CFG-003) ─────────────────────────────

PROJECT_MARKERS: tuple[str, ...] = (
    "config.yaml",
    "config.yml",
    ".git",
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "requirements.txt",
)

# ─── Limits (FR-CFG-001) ──────────────────────────────────────

MAX_CONFIG_SIZE_BYTES: int = 1024 * 1024  # 1 MB

# ─── Environment Prefixes (FR-CFG-001) ────────────────────────

ENV_PREFIX_PRODUCT: str = "BLENDERMCP_"
ENV_PREFIX_LEGACY: str = "BLENDER_MCP_"

# ─── Redaction Placeholder (FR-CFG-005) ──────────────────────

REDACTION_PLACEHOLDER: str = "***REDACTED***"

# ─── Policy Modes (FR-CFG-001) ────────────────────────────────

POLICY_MODE_STRICT: str = "strict"
POLICY_MODE_PERMISSIVE: str = "permissive"

DEFAULT_POLICY_MODE: str = "strict"
```

---

## File: modules/shared/src/config/taxonomy_config_error.py

```python
"""Domain error types for the config domain."""

from __future__ import annotations

from typing import Any

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


class ConfigProviderError(ConfigError):
    """Raised when a configuration provider is not registered or invalid."""

    def __init__(self, message: ErrorString | None = None) -> None:
        super().__init__(message or ErrorString("Configuration provider error"))
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
- SensitiveKeyPattern: key-level sensitivity detection
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SettingsSnapshot:
    """Immutable snapshot of merged configuration values.

    Created after load/reload. Never mutated after construction.
    Supports deep traversal via get() without exposing internals.
    """

    _data: dict[str, Any] = field(repr=False, default_factory=dict)

    def get(self, path: str, default: Any = None) -> Any:
        """Retrieve value by dot-separated path. Returns deep copy."""
        if not path:
            return copy.deepcopy(self._data)

        keys = path.split(".")
        value: Any = self._data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    value = value[idx] if 0 <= idx < len(value) else default
                except (ValueError, IndexError):
                    return default
            else:
                return default

        return copy.deepcopy(value)

    def has(self, path: str) -> bool:
        """Check if a dot-separated path exists in the snapshot."""
        if not path:
            return True

        keys = path.split(".")
        value: Any = self._data

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            elif isinstance(value, list):
                try:
                    idx = int(key)
                    value = value[idx] if 0 <= idx < len(value) else None
                except (ValueError, IndexError):
                    return False
            else:
                return False

        return True

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
        """Check if a key matches any of the sensitive patterns."""
        key_lower = key.lower()
        return any(pattern.lower() in key_lower for pattern in self.key_patterns)


@dataclass(frozen=True)
class SensitiveKeyPattern:
    """Pattern for detecting sensitive configuration keys."""

    pattern: str
    description: str = ""
    full_redact: bool = True
```

---

## File: modules/shared/src/config/utility_config_helpers.py

```python
"""Utility: Config helper functions.

Stateless, domain-agnostic standalone functions extracted from capabilities.
No class, no protocol impl, pure functions only.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def parse_env_value(value: str) -> Any:
    """Parse environment value as typed scalar.

    boolean-like → bool, integer-like → int, float-like → float,
    null-like → None, otherwise → str.
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

