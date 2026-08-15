# FRD — Configuration & Workspace Feature

## Purpose

Single owner for loading, validating, and providing settings to all features. Loads from file, environment, and built-in defaults with deterministic precedence. Validates against schema, exposes immutable snapshots, resolves workspace directory, provides settings metadata, and supplies redaction rules. No other feature reads settings files directly or defines its own precedence.

## Scope

- Load settings from file, environment, built-in defaults
- Deterministic precedence across sources
- Type conversion for env values
- Schema validation enforcement
- Immutable settings snapshot after load
- Hierarchical retrieval (dot-separated paths)
- Project workspace resolution
- Settings metadata exposure
- Redaction policy for secret values
- Safe parsing (no arbitrary object instantiation)
- Cached singleton with thread-safe init
- Reload with atomic snapshot replacement
- Strict and permissive policy modes
- Settings size and encoding limits

## Out of Scope

Runtime process state, Blender connection state, background task state, feature business rules, command catalog, logging infrastructure, secret storage, remote settings sync, per-user profiles, redaction enforcement (owned by security + consumers).

## Depends On

Shared `config` taxonomy/contract module (constants, VOs, errors, events, contracts + 5 protocols, stateless helpers). Shared core VO (`ConfigMetadata`, `ConfigPath`, `OverrideCount`, `ParseWarning`, `ValidationWarning`, `SourceLocation`, `Timestamp`, `ErrorString`, `WorkspacePath`, `SettingsSnapshot`, `RedactionRule`). MCP bootstrap aggregator.

## Provides To

All features.

## Functional Requirements

### FR-CFG-001: Load and Apply Settings

- **Description**: Load from all sources, apply precedence, validate merged result, expose single immutable snapshot
- **Input**: Optional settings location override, optional runtime override mapping
- **Output**: Immutable settings snapshot
- **Rules**: Precedence: runtime overrides > environment > file > built-in defaults. Safe parsing only — no arbitrary object instantiation. UTF-8 encoding. Missing file → falls back to env+defaults (never fatal). Default path `<cwd>/config.yaml` when no explicit path and `BLENDERMCP_CONFIG_PATH` unset. Policy: strict (default) or permissive (opt-in). First load thread-safe (double-checked locking). Malformed content → ConfigError (strict) or warning+fallback (permissive). Schema violation → ValidationError (strict) or warning (permissive). Schema = Python-native mapping `SETTINGS_SCHEMA`; unknown keys warn, type/required violations error. Env values converted: bool-like→bool, int-like→int, float-like→float, null-like→empty, else string. Env values scalar-only (no list/map parsing). Prefix: `BLENDERMCP_` only; other prefixes are ignored. Snapshot immutable after load. Reload atomic under sync. Failed load never exposes partial state. Failed reload retains previous valid snapshot unless strict requires failure. Max source size: 1 MiB (`MAX_CONFIG_SIZE_BYTES`); oversized → ConfigError (strict) or skip file+warning (permissive, gated by `BLENDERMCP_STRICT`). Secrets never echoed in metadata/logs/diagnostics.
- **Edge Cases**: Missing/malformed/empty file, permission denied, duplicate keys, unsupported tags, oversized, non-UTF-8, env conflict, unsupported prefix, schema unavailable, secret values, symlinked location, location pointing to directory
- **Error Handling**: ConfigError (missing/unreadable/malformed), ValidationError (schema violation), LoadError (oversized/unsafe), permissive fallback warnings

### FR-CFG-002: Retrieve Settings Values

- **Description**: Retrieve via dot-separated paths with safe copy semantics
- **Input**: Dot-separated path, optional default, optional expected type
- **Output**: Resolved value or default
- **Rules**: Traverse nested structure by segments. Missing key/intermediate → default. Empty path → full snapshot. Returned values immutable or deep-copied. Numeric segments access list positions (out-of-range → default). `\.` escapes literal dot when `BLENDERMCP_STRICT` enabled. Thread-safe, lock-free after init. Never triggers file/env reads per request. Type mismatch → default (permissive) or TypeError (strict). Defaults never mutated by retrieval.
- **Edge Cases**: Empty/missing/leading/trailing/repeated path, whitespace, non-text path, list position on non-list, out-of-range, literal dot, type mismatch, mutable default, deeply nested path
- **Error Handling**: Default for missing keys; ValidationError for malformed path (strict); TypeError for type mismatch (strict); immutable/copy semantics prevent mutation

### FR-CFG-006: Mutate and Persist a Setting

- **Description**: Update one typed configuration value through the Config aggregate and atomically persist the resulting YAML document.
- **Input**: Non-empty dotted key and JSON/YAML-compatible typed value.
- **Output**: New immutable settings snapshot with the updated value.
- **Rules**: Mutation is available only through `IConfigAggregate.set_config`. The value is validated against `SETTINGS_SCHEMA` before any write. Writes use a temporary file, flush/fsync, and atomic replacement; a failed write leaves the previous file and snapshot intact. Secret-like keys matching the authoritative redaction rule are rejected rather than stored through the CLI mutation surface. A new ConfigContainer process reads the persisted value. CLI retrieval recursively redacts sensitive values and never prints the rejected secret value.
- **Edge Cases**: Missing config file, malformed existing file, unknown key, wrong scalar type, invalid dotted path, permission denied, concurrent writer, atomic replacement failure, secret-like key.
- **Error Handling**: ValidationError for invalid key/value or secret-like key; load/parse error for invalid existing source; write error with no partial success.

### FR-CFG-003: Resolve Project Workspace Directory

- **Description**: Resolve project root via deterministic strategies. Single trusted root for all file-based ops.
- **Input**: None (reads env + filesystem)
- **Output**: Workspace directory
- **Rules**: Resolution order: explicit override → `BLENDERMCP_ROOT` env → settings file parent dir → proximity markers (config.yaml, pyproject.toml, .git) → platform-standard user config → CWD. Normalized path. Symlinks resolved. Directory must exist+readable. Invalid env path logs warning, falls through. First valid candidate wins. Never creates directories by default. If no candidate → CWD. If CWD inaccessible → workspace resolution error. Result cached for process lifetime. All file-writing features derive allowed locations from this.
- **Edge Cases**: Multiple candidates, symlinks, non-existent candidate, permission denied, network fs, case-insensitive fs, settings location pointing to file vs dir, circular symlink, empty env value, relative path, deleted CWD, platform remote path
- **Error Handling**: Warning+fallthrough for invalid env path or non-existent/unreadable candidate; error only when all strategies fail + CWD inaccessible

### FR-CFG-004: Provide Settings Metadata

- **Description**: Expose diagnostic metadata about load/merge/validation without leaking secrets
- **Input**: None
- **Output**: Settings metadata (source, exists, overrides, parse_warnings, validation_warnings)
- **Rules**: Must include exactly: `source`, `exists`, `overrides` (env overrides only — excludes caller-scoped runtime overrides), `parse_warnings`, `validation_warnings`. No secret values. No raw settings content by default. Override names may be listed; sensitive values redacted. Safe for diagnostics, CLI, and MCP responses. Reflects current active snapshot. Never mutates state.
- **Edge Cases**: Settings file missing, unsupported overrides, sensitive override values, validation warnings present, permissive fallback, reload in progress, metadata before first load, oversized warning list
- **Error Handling**: Partial metadata when details unavailable; redaction failure → omit affected field

### FR-CFG-005: Provide Redaction Rules

- **Description**: Authoritative list of sensitive key patterns for masking. Config is default provider; security policy may extend via composition-root injection (`extra_redaction_patterns`).
- **Input**: None
- **Output**: Redaction rules (sensitive key patterns, detection rules, placeholder convention)
- **Rules**: Covers tokens, API keys, passwords, credentials, connection strings, signing/encryption material. Exact key + pattern-based match. Extensible via composition-root (not runtime settings). Placeholder convention defined. Rules contain key names/patterns only, never secret values. Consumers retrieve via `IConfigAggregate.get_redaction_rule()` and mask with `redact_dict()`. Matching: substring-based, case-insensitive (e.g. "auth" also matches "author" — accepted false positive). Full redaction only (`full_redact` always True). Lightweight for repeated use.
- **Edge Cases**: Empty list, conflicting patterns, unknown format, key matching multiple patterns, rule update after load, consumer bypass
- **Error Handling**: Missing/invalid rules → default sensitive key list; warning on parse failure; failure never causes secret exposure

## Error Categories

- configuration error — invalid/missing/unreadable source
- validation error — schema violation or malformed path
- load error — oversized/unsafe/rejected content
- type conversion error — type mismatch in strict mode
- workspace resolution error — cannot resolve from any strategy

## Events

- settings loaded (after successful load)
- settings reload (after successful replace)
- workspace resolved (after directory resolution)
- settings validation warning (in permissive mode)

Payloads: category, source summary, override count, warning count, policy mode, timestamp. Never: raw settings content, secret values, sensitive overrides.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| settings_source_location | Primary settings file | Resolved from workspace/platform |
| workspace_directory | Project root for file ops | Resolved via deterministic strategies |
| sensitive_key_list | Keys treated as secret | Common token/key/password/credential patterns |
| env_override_prefix | Env var prefix recognized | BLENDERMCP_ |
| unsupported_env_prefix | Accept only BLENDERMCP_ prefix | Other prefixes ignored |
| policy_mode | strict/permissive | strict |
| max_settings_size | Max source size | 1 MiB |
| default_values_source | Built-in defaults | Feature-defined safe defaults |

## QA Checklist

- [ ] Precedence: runtime overrides > env > file > defaults
- [ ] Default source: `<cwd>/config.yaml` when no explicit path and no BLENDERMCP_CONFIG_PATH
- [ ] Missing file → env+defaults, never fatal
- [ ] Malformed content → ConfigError (strict) or warning+fallback (permissive)
- [ ] Schema violation → ValidationError (strict) or warning (permissive)
- [ ] Unsafe content rejected without object instantiation
- [ ] Max 1 MiB enforced
- [ ] Env values scalar-only (no list/map parsing)
- [ ] Unsupported BLENDER_MCP_ prefix ignored
- [ ] Concurrent first access loads once
- [ ] Reload atomic; failed reload retains previous snapshot
- [ ] Immutable snapshot returned on retrieve
- [ ] Structured values deep-copied or immutable
- [ ] Missing key → default; empty path → full snapshot
- [ ] List position access works; out-of-range → default
- [ ] Workspace resolves via explicit→BLENDERMCP_ROOT→settings parent→markers→platform→CWD
- [ ] Symlinks handled safely; never creates directories
- [ ] Metadata reports source, overrides (env only), warnings
- [ ] Metadata never leaks secrets
- [ ] Redaction keys mask sensitive values in diagnostics, CLI, MCP
- [ ] Consumers derive masking from `get_redaction_rule()`/`redact_dict()`
- [ ] All events emitted
