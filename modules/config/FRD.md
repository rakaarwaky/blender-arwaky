# FRD — Configuration & Workspace Feature

## System Overview
The Config module is the single owner for loading, validating, and providing settings to all features. It resolves settings from file, environment, and built-in defaults with deterministic precedence, exposes immutable snapshots, resolves the workspace directory, and supplies redaction rules.

## Functional Requirements

### FR-001: Load and Apply Settings
- **Description**: Load from all sources, apply precedence, validate merged result, and expose a single immutable snapshot.
- **Input**: Optional settings location override, optional runtime override mapping.
- **Output**: Immutable settings snapshot.
- **Business Rules**: Precedence: runtime > env > file > defaults. Safe parsing only (no arbitrary object instantiation). Schema violation triggers `ValidationError` (strict) or warning (permissive). Max source size 1 MiB.
- **Edge Cases**: Missing/malformed file; oversized file; env conflict; symlinked location.
- **Error Handling**: `configuration_error` for missing/unreadable source; `validation_error` for schema violation; `load_error` for oversized content.

### FR-002: Retrieve and Mutate Settings
- **Description**: Retrieve via dot-separated paths and atomically persist mutations.
- **Input**: Dot-separated path, optional default, typed value for mutation.
- **Output**: Resolved value, default, or new immutable snapshot.
- **Business Rules**: Traverse nested structure by segments. Missing key returns default. Mutations validate against schema before atomic write. Secret-like keys are rejected from CLI mutation.
- **Edge Cases**: Empty/missing path; out-of-range list position; type mismatch; concurrent writer.
- **Error Handling**: `validation_error` for malformed path or secret-like key; `type_conversion_error` for strict mode mismatches.

### FR-003: Resolve Workspace and Metadata
- **Description**: Resolve project root and expose diagnostic metadata without leaking secrets.
- **Input**: None (reads env + filesystem).
- **Output**: Workspace directory, settings metadata (source, overrides, warnings).
- **Business Rules**: Resolution order: explicit > `BLENDERMCP_ROOT` > settings parent > markers > platform > CWD. Metadata never leaks secrets.
- **Edge Cases**: Multiple candidates; circular symlink; deleted CWD; sensitive override values.
- **Error Handling**: `workspace_resolution_error` when all strategies fail and CWD is inaccessible.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `get_config` | `key` (opt) | `ConfigSnapshot` | Retrieve config value by dot-separated path or full immutable settings snapshot; raises `validation_error` on malformed path |
| `set_config` | `key`, `value` | `config_updated` | Update and atomically persist config setting after schema validation; raises `validation_error` for secret-like keys or schema violations, `type_conversion_error` in strict mode |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `shared` (taxonomy, VOs, errors), `security` (redaction rule composition).

## Non-functional Requirements (Detailed)

- **Performance**: First load uses double-checked locking. Retrieval is lock-free and never triggers file reads per request.
- **Security**: Secrets never echoed in metadata/logs. Secret-like keys rejected from mutation surface. Safe parsing prevents arbitrary object instantiation.
- **Scalability**: Reload is atomic under sync; failed reload retains previous valid snapshot.

## Test Scenarios / QA Checklist

- [ ] Verify precedence: runtime > env > file > defaults.
- [ ] Verify missing file falls back to env+defaults without fatal error.
- [ ] Verify max 1 MiB size limit is enforced.
- [ ] Verify workspace resolves via deterministic strategies and handles symlinks safely.
- [ ] Verify metadata never leaks secret values.

## Assumptions & Constraints

- No other feature reads settings files directly or defines its own precedence.
- Env values are scalar-only (no list/map parsing). Prefix `BLENDERMCP_` only.

## Glossary

- **Immutable Snapshot**: A read-only, deep-copied representation of the current configuration state.
- **WorkspacePath**: Absolute, normalized filesystem path derived from Config.
- **Redaction Rule**: Authoritative list of sensitive key patterns for masking.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `shared`
