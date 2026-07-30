.agents/issues/issue-config-business-analyst-2026-07-30-143022.md

# Issue: config — Business Logic & Requirements Review

## Summary

The config feature (v1.7.0) implements all five FR-CFG requirements with correct layer separation and DI wiring. However, analysis reveals a critical discrepancy between the FRD's schema validation policy (tied to `policy_mode`) and the implementation (gated by a separate `strict_mode_enabled` flag), a type-safety gap in the agent's event recording pipeline, and several missing edge-case behaviors specified in the FRD (double-checked locking, reload event emission on validation warnings). The feature is functionally operational but deviates from its specification in ways that will cause confusion during integration testing and v1.8.0 strict-mode migration.

## Findings by Category

### Requirements Clarity


| # | Severity   | Issue                                                                                                                                                                                                                                                                                                                                                                                                                                                          | Location (File:Line)                                          | Recommendation                                                                                                                                                                                           |
| --- | ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | 🟡 WARNING | FRD states "Schema violation → ValidationError (strict) or warning (permissive)" implying`policy_mode` controls schema enforcement. Implementation gates schema validation on a separate `strict_mode_enabled` flag (BLENDERMCP_STRICT env), meaning schema validation is skipped entirely when `strict_mode_enabled=False` regardless of `policy_mode`. The two concepts (policy_mode vs strict_mode_enabled) are conflated in the FRD but distinct in code. | `modules/config/src/capabilities_settings_loader.py:168-175`  | Clarify FRD to explicitly document the two-axis model:`policy_mode` (strict/permissive error handling) AND `strict_mode_enabled` (v1.7.0 feature gate). Or unify them if the intent is a single control. |
| 2 | 🟡 WARNING | FRD states "First load thread-safe (double-checked locking)" but implementation uses a simple`threading.Lock()` with the cache check inside the lock. True double-checked locking checks the cache outside the lock first (for read performance), then acquires the lock and re-checks. Current implementation is correct for safety but doesn't match the specified pattern.                                                                                  | `modules/config/src/capabilities_settings_loader.py:107-110`  | Either implement actual double-checked locking (check`self._cached` before acquiring lock) or update FRD to say "thread-safe (mutex-protected)" to match implementation.                                 |
| 3 | 🟢 INFO    | FRD FR-CFG-001 lists "duplicate keys" as an edge case but neither the FRD rules nor the implementation define behavior for YAML duplicate keys.`yaml.safe_load` silently takes the last value.                                                                                                                                                                                                                                                                 | `modules/shared/src/config/utility_config_helpers.py:100-113` | Document in FRD that duplicate keys follow YAML spec (last-wins) or add a warning in permissive mode.                                                                                                    |

### Business Flow


| # | Severity   | Issue                                                                                                                                                                                                                                                                                                                                                                                                                                          | Location (File:Line)                                          | Recommendation                                                                                                                                |
| --- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| 4 | 🟡 WARNING | FRD FR-CFG-001 states "Failed reload retains previous valid snapshot unless strict requires failure." Implementation in`reload_settings` catches `(ConfigLoadError, ConfigParseError, ConfigValidationError)` and returns cached in permissive mode. However, `ConfigPathError` (directory path) and `ConfigTypeError` are NOT caught — they propagate unhandled in both modes, potentially crashing a reload that should degrade gracefully. | `modules/config/src/capabilities_settings_loader.py:130-139`  | Add`ConfigPathError` and `ConfigTypeError` to the except tuple in `reload_settings`, or catch `ConfigError` (base class) for permissive mode. |
| 5 | 🟡 WARNING | FRD FR-CFG-003 states workspace resolution emits "workspace resolved" event. The`WorkspaceResolverCapability.emit_resolved_event` creates `WorkspaceResolvedEvent(timestamp=time.time())` passing a raw `float` where the dataclass field type is `Timestamp` (NewType). While Python won't enforce this at runtime, it breaks type-checker contracts and the event's `timestamp` field won't be wrapped in the `Timestamp` brand.             | `modules/config/src/capabilities_workspace_resolver.py:72-78` | Change to`timestamp=Timestamp(time.time())` to match the dataclass field type and maintain VO consistency.                                    |
| 6 | 🟢 INFO    | FRD FR-CFG-001 states "Secrets never echoed in metadata/logs/diagnostics." The`_build_core` method includes file paths in `ParseWarning` messages (e.g., `f"settings file not found: {resolved}; using defaults"`). If the config path itself is sensitive (e.g., contains a username), this could leak.                                                                                                                                       | `modules/config/src/capabilities_settings_loader.py:155-200`  | Consider redacting or truncating paths in warning messages, or document that paths are not considered secrets.                                |

### Logic Implementation


| #  | Severity    | Issue                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              | Location (File:Line)                                         | Recommendation                                                                                                                                                                                                                |
| ---- | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 7  | 🔴 CRITICAL | Agent`_record_event` calls `asdict(event)` producing `dict[str, Any]`, then passes it to `self._redaction_rules.redact_dict(payload)` which expects `SettingsData` (`dict[str, SettingsValue]`). The `asdict` output contains nested dataclass fields (e.g., `Timestamp` objects, tuples) that are NOT `SettingsValue` types. `redact_dict` iterates values and checks `isinstance(value, dict)` / `isinstance(value, list)` — tuples from `asdict` won't match `list`, so nested structures may pass through unredacted.                         | `modules/config/src/agent_config_orchestrator.py:119-125`    | Either (a) serialize with`json.loads(json.dumps(asdict(event), default=str))` before redaction to normalize to JSON-safe types, or (b) create a dedicated `redact_event_payload` method that handles dataclass-derived dicts. |
| 8  | 🟡 WARNING  | Agent`_record_event` performs `logger.info("config_event %s", json.dumps(...))` which is stdout/stderr I/O. Per AES agent rules: "Forbidden ops: stdout/stderr write." While logging is often exempted as infrastructure, the AES skill explicitly lists it as forbidden for the agent layer.                                                                                                                                                                                                                                                      | `modules/config/src/agent_config_orchestrator.py:126`        | Move logging to a capability or inject a logging callback. Alternatively, document an explicit exception for structured observability logging in the agent layer.                                                             |
| 9  | 🟡 WARNING  | FRD FR-CFG-002 states "Returned values immutable or deep-copied." The`SettingsSnapshot.get_segments` method calls `copy.deepcopy(value)` on the final resolved value. However, if the value is a primitive (str, int, float, bool, None), `deepcopy` is unnecessary overhead. More importantly, if the value is a list containing mutable objects, `deepcopy` correctly protects. But the `to_dict()` method also deep-copies the entire data dict — callers who use `to_dict()` then modify the result are safe, but this is O(n) on every call. | `modules/shared/src/config/taxonomy_config_vo.py:72-95`      | Acceptable as-is for correctness. Consider documenting the performance implication for large configs, or short-circuit deepcopy for known-immutable types.                                                                    |
| 10 | 🟢 INFO     | `SettingsLoaderCapability._build_core` catches bare `Exception` as a final fallback (line ~195). In strict mode this wraps as `ConfigLoadError`. In permissive mode it produces a warning. This catch-all could mask programming errors (e.g., `TypeError`, `AttributeError`) that should surface during development.                                                                                                                                                                                                                              | `modules/config/src/capabilities_settings_loader.py:190-198` | Narrow the catch to`(OSError, UnicodeDecodeError, yaml.YAMLError, ConfigError)` and let unexpected exceptions propagate, or add a `logger.exception()` call before swallowing.                                                |

### Testability & Acceptance Criteria


| #  | Severity   | Issue                                                                                                                                                                                                                                                                                                                                                           | Location (File:Line)                                          | Recommendation                                                                                                                                                         |
| ---- | ------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| 11 | 🟡 WARNING | FRD QA Checklist item "Concurrent first access loads once" cannot be verified without a multi-threaded test. No test infrastructure for concurrent access is evident in the module. The single-load guarantee depends on`threading.Lock` but race conditions under GIL release (I/O operations) need explicit testing.                                          | `modules/config/FRD.md` (QA Checklist)                        | Add an integration test that spawns N threads calling`load_settings()` simultaneously and asserts the file is read exactly once (mock the file loader with a counter). |
| 12 | 🟡 WARNING | FRD FR-CFG-003 edge case "circular symlink" is listed but no handling exists in`WorkspaceResolverCapability`. `Path.resolve()` in Python follows symlinks and will raise `OSError` on circular links, which is caught by the general `except (OSError, ValueError)` in the env-signal branch but NOT in the explicit-override or settings-file-parent branches. | `modules/config/src/capabilities_workspace_resolver.py:82-95` | Wrap all`Path(...).resolve()` calls in try/except OSError and fall through to next strategy. Add a test with a circular symlink fixture.                               |
| 13 | 🟢 INFO    | FRD FR-CFG-005 edge case "rule update after load" is listed but the implementation creates the`RedactionRule` once at construction and never updates it. The FRD doesn't specify HOW rules would update, making this edge case untestable.                                                                                                                      | `modules/config/src/capabilities_redaction_rules.py:30-35`    | Either remove this edge case from FRD (rules are immutable by design) or specify a reload mechanism.                                                                   |

### Traceability (FRD → Code)


| #  | Severity | Issue                                                                                                                                                                                                                                                                                                                                                              | Location (File:Line)                                          | Recommendation                                                                                                                                                  |
| ---- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 14 | 🟢 INFO  | FR-CFG-001 specifies "Unsupported tags → warning" (YAML tags like`!!python/object`). `yaml.safe_load` rejects these with `yaml.YAMLError` which is caught and handled. Traceability is satisfied but the specific "unsupported tag" case is handled implicitly rather than explicitly.                                                                            | `modules/shared/src/config/utility_config_helpers.py:107-109` | Add a comment in`load_yaml_safe` noting that `yaml.safe_load` rejects arbitrary tags by design, satisfying the "no arbitrary object instantiation" requirement. |
| 15 | 🟢 INFO  | FR-CFG-004 specifies metadata "Reflects current active snapshot." The`SettingsMetadataCapability` delegates to `loader.get_last_metadata()` which returns metadata from the most recent `_build_core` call. If `reload` fails in permissive mode (returning cached snapshot), the metadata still reflects the FAILED load attempt, not the active cached snapshot. | `modules/config/src/capabilities_settings_loader.py:130-139`  | On failed reload in permissive mode, either preserve the previous metadata or add a`reload_failed` warning to the returned metadata.                            |

## Violations

- **AES405 (Agent Role) — Borderline**: `ConfigOrchestrator` mutates `self._snapshot` and `self._event_buffer` outside `__init__`. This is caching/event-buffering (orchestration state), not business computation. The FRD explicitly requires snapshot caching. Recommend documenting an explicit exception for agent-layer caching in AES rules.
- **AES Agent I/O — Borderline**: `ConfigOrchestrator._record_event` calls `logger.info(...)` which writes to stderr. Strictly forbidden per agent rules. See Finding #8.

## Action Items (For Developer)

- [ ]  🔴 P0: Fix `_record_event` type mismatch — normalize `asdict()` output before passing to `redact_dict()` (Finding #7)
- [ ]  🟡 P1: Add `ConfigPathError`/`ConfigTypeError` to reload exception handling in permissive mode (Finding #4)
- [ ]  🟡 P1: Fix `WorkspaceResolvedEvent` timestamp to use `Timestamp(time.time())` (Finding #5)
- [ ]  🟡 P1: Clarify FRD on `policy_mode` vs `strict_mode_enabled` two-axis model (Finding #1)
- [ ]  🟡 P1: Add circular symlink handling to all `Path.resolve()` calls in workspace resolver (Finding #12)
- [ ]  🟡 P2: Move agent logging to injected callback or document exception (Finding #8)
- [ ]  🟡 P2: Narrow bare `Exception` catch in `_build_core` (Finding #10)
- [ ]  🟢 P3: Update FRD double-checked locking description or implement pattern (Finding #2)
- [ ]  🟢 P3: Add concurrent-load integration test (Finding #11)

## Proposed Fixes / Reference Code

### File: `modules/config/src/agent_config_orchestrator.py`

**Fix #7#7#7#7 — Normalize event payload before redaction:**

```python
# ─── Block 3: Event Recording ─────────────────────────────
def _record_event(self, event: object) -> None:
    """Serialize and store a domain event into the bounded ring buffer."""
    import json as _json

    # Normalize to JSON-safe dict (resolves dataclass fields, tuples, NewTypes)
    raw = asdict(event)
    payload: EventPayload = _json.loads(_json.dumps(raw, default=str))

    # Apply redaction to prevent secret leakage in event logs
    redacted_payload = self._redaction_rules.redact_dict(payload)
    self._event_buffer.append(redacted_payload)
    logger.info("config_event %s", _json.dumps(redacted_payload, default=str))
```

### File: `modules/config/src/capabilities_settings_loader.py`

**Fix #4#4#4#4 — Broaden reload exception handling:**

```python
def reload_settings(self, path: ConfigPath | None = None) -> SettingsSnapshot:
    """Atomically replace cached snapshot. Retains previous on failure (permissive)."""
    with self._lock:
        try:
            merged, filedata, metadata = self._build_core(path)
            self._cached_data = filedata
            self._cached = SettingsSnapshot(_data=merged)
            self._last_metadata = metadata
            return self._cached
        except (ConfigLoadError, ConfigParseError, ConfigValidationError, ConfigPathError, ConfigTypeError):
            if self._policy_mode == POLICY_MODE_PERMISSIVE and self._cached is not None:
                return self._cached
            raise
```

### File: `modules/config/src/capabilities_workspace_resolver.py`

**Fix #5#5#5#5 — Correct timestamp type:**

```python
from modules.shared.src.common.taxonomy_core_vo import ConfigPath, Timestamp


def emit_resolved_event(self, workspace: WorkspacePath) -> WorkspaceResolvedEvent:
    """Build a workspace-resolved event payload."""
    return WorkspaceResolvedEvent(
        source_summary=workspace.strategy,
        override_count=0,
        warning_count=0,
        timestamp=Timestamp(time.time()),
    )
```

**Fix #12#12#12#12 — Circular symlink safety:**

```python
def _resolve_uncached(self) -> WorkspacePath:
    # 1. Explicit override
    if self._explicit_override:
        try:
            candidate = Path(self._explicit_override).resolve()
        except OSError:
            candidate = None
        if candidate and candidate.is_dir():
            return WorkspacePath(path=str(candidate), strategy="explicit_override")
        logger.warning(
            "Explicit workspace override is not a directory: %s",
            self._explicit_override,
        )
    # ... (apply same try/except pattern to all Path.resolve() calls)
```

</parameter>
</function>
</tool_call>
