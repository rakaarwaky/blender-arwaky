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

- Shared `config` taxonomy/contract module (`modules.shared.src.config`): constants (`taxonomy_config_constant`), value objects (`taxonomy_config_vo`), errors (`taxonomy_config_error`), events (`taxonomy_config_event`), contracts (`contract_config_aggregate` + 5 protocols), and stateless helpers (`utility_config_helpers`).
- Shared core VO (`modules.shared.src.common.taxonomy_core_vo`): consumed symbols — `ConfigMetadata`, `ConfigPath`, `OverrideCount`, `ParseWarning`, `ValidationWarning`, `SourceLocation`, `Timestamp`, `ErrorString`, `WorkspacePath`, `SettingsSnapshot`, `RedactionRule`.
- The shared `mcp` bootstrap aggregator for module initialization.

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
  - Legacy environment prefix BLENDER_MCP_ was removed in v1.7.0 (BREAKING). Only the BLENDERMCP_ prefix is recognized. Legacy variables are ignored.
  - Settings snapshot must be immutable after successful load
  - Settings snapshot must be cached after first successful load
  - Reload must replace snapshot atomically under synchronization
  - Failed load must not expose partial settings state
  - Failed reload must retain previous valid snapshot unless strict mode requires failure propagation
  - Settings source size must be limited to prevent excessive memory usage: limit is 1 MiB (MAX_CONFIG_SIZE_BYTES); in strict mode an oversized source raises ConfigLoadError, in permissive mode it warns and skips the file source (flag-gated behind BLENDERMCP_STRICT)
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
  - `\.` resolves a literal dotted key when BLENDERMCP_STRICT is enabled
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
    - NOTE: `overrides` counts applied **environment** overrides only; caller-scoped runtime overrides (FR-CFG-001, A5) are intentionally excluded from this count.
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
  - Wiring point: consumers obtain the active rule via `IConfigAggregate.get_redaction_rule()` and mask payloads with `redact_dict()` — both exposed through the config aggregate facade (FR-CFG-005 end-to-end).
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
| Legacy environment fallback | Whether legacy BLENDER_MCP_ prefix is accepted                 | Disabled (v1.7.0 BREAKING change)                     |
| Policy mode                 | Strict or permissive behavior for parse and schema issues      | Strict                                                |
| Maximum settings size       | Maximum allowed settings source size                           | Conservative size limit                               |
| Default values source       | Built-in defaults applied when no other source provides value  | Feature-defined safe defaults                         |

## QA Checklist

### FR-CFG-001 — Load and Apply Settings

- [ ]  (FR-CFG-001) Settings load from file, environment, and defaults with correct precedence
- [ ]  (FR-CFG-001) Runtime override takes precedence over environment, file, and defaults (requires `BLENDERMCP_STRICT=on`; ignored with warning when off)
- [ ]  (FR-CFG-001) Default settings source resolves to `<cwd>/config.yaml` when no explicit path and no `BLENDERMCP_CONFIG_PATH` is set
- [ ]  (FR-CFG-001) Environment override takes precedence over file and defaults
- [ ]  (FR-CFG-001) File values take precedence over built-in defaults
- [ ]  (FR-CFG-001) Missing settings file falls back to environment and defaults without fatal error
- [ ]  (FR-CFG-001) Malformed settings content raises configuration error in strict mode
- [ ]  (FR-CFG-001) Malformed settings content falls back safely in permissive mode
- [ ]  (FR-CFG-001) Schema violation raises validation error in strict mode
- [ ]  (FR-CFG-001) Schema violation logs warning in permissive mode
- [ ]  (FR-CFG-001) Unsafe settings content is rejected without object instantiation
- [ ]  (FR-CFG-001) Oversized settings source raises load error
- [ ]  (FR-CFG-001) Environment values convert scalar values to boolean, integer, float, or null; list-like and mapping-like values remain strings (scalar-only per Q7)
- [ ]  (FR-CFG-001) Legacy BLENDER_MCP_ prefix variables are ignored (v1.7.0 BREAKING)
- [ ]  (FR-CFG-001) Concurrent first access loads settings only once
- [ ]  (FR-CFG-001) Reload replaces snapshot atomically
- [ ]  (FR-CFG-001) Failed reload retains previous valid snapshot in non-fatal mode
- [ ]  (FR-CFG-001) Built-in defaults tier is complete; settings file is optional override-only (Q6)
- [ ]  (FR-CFG-001) Schema validation, 1 MiB size limit, `\.` escaping, strict ConfigTypeError gated behind BLENDERMCP_STRICT
- [ ]  (FR-CFG-001) 32-thread first access performs exactly one load (Q19)

### FR-CFG-002 — Retrieve Settings Values

- [ ]  (FR-CFG-002) Immutable snapshot returned on retrieve
- [ ]  (FR-CFG-002) Retrieved structured values are deep-copied or immutable
- [ ]  (FR-CFG-002) Missing key returns provided default
- [ ]  (FR-CFG-002) Empty path returns full settings snapshot safely
- [ ]  (FR-CFG-002) List position access works and out-of-range returns default
- [ ]  (FR-CFG-002) Expected type mismatch returns default in permissive mode
- [ ]  (FR-CFG-002) Expected type mismatch raises type conversion error in strict mode

### FR-CFG-003 — Resolve Project Workspace Directory

- [ ]  (FR-CFG-003) Project workspace resolves correctly through explicit override
- [ ]  (FR-CFG-003) Project workspace resolves correctly through environment signal
- [ ]  (FR-CFG-003) Project workspace resolves correctly through settings file location
- [ ]  (FR-CFG-003) Project workspace resolves correctly through proximity markers
- [ ]  (FR-CFG-003) Project workspace falls back to current working directory
- [ ]  (FR-CFG-003) Project workspace handles symlinked directories safely
- [ ]  (FR-CFG-003) Project workspace resolution does not create directories by default
- [ ]  (FR-CFG-003) Legacy BLENDERMCP_* environment variables are ignored (Q8)

### FR-CFG-004 — Provide Settings Metadata

- [ ]  (FR-CFG-004) Settings metadata reports source, override count (environment overrides only; excludes caller-scoped runtime overrides, A5), and warnings
- [ ]  (FR-CFG-004) Settings metadata does not leak secret values

### FR-CFG-005 — Provide Redaction Rules

- [ ]  (FR-CFG-005) Redaction keys mask sensitive values in diagnostics
- [ ]  (FR-CFG-005) Redaction keys mask sensitive values in command-line output
- [ ]  (FR-CFG-005) Redaction keys mask sensitive values in MCP-facing responses
- [ ]  (FR-CFG-005) Redaction rules contain key patterns only, never secret values
- [ ]  (FR-CFG-005) Asset, render, and other consumers derive masking from `IConfigAggregate.get_redaction_rule()` / `redact_dict()` (composition-root extensible via `extra_redaction_patterns`)

### Cross-cutting

- [ ]  (A5) Runtime overrides are caller-scoped and not cached
- [ ]  Asset and render derive root locations from workspace resolution instead of own rules
- [ ]  Custom redaction rules extend built-in defaults safely
- [ ]  Settings loaded event emitted after successful load
- [ ]  Settings reload event emitted after successful reload
- [ ]  Workspace resolved event emitted after resolution
