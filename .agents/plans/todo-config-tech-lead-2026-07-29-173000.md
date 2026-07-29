# Review Plan: config — Tech Lead (Phase 3)

## Summary

The config module is well-structured with clean separation of concerns across 5 capabilities, proper DI via protocols, and comprehensive test coverage (117 tests passing). Layer boundaries are correct — orchestrator imports contracts only, container wires correctly. However, there are security concerns around secret leakage in event serialization, performance inefficiencies in deepcopy usage, silent error handling in workspace resolution, and a contract role violation using `Callable` instead of a protocol.

## Findings by Category

### Security
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Broad exception catch masks real errors — `_build_core()` in `capabilities_settings_loader.py` catches bare `except Exception` which swallows SystemExit, KeyboardInterrupt, and other critical exceptions. Should be `except (OSError, ValueError, yaml.YAMLError, ...)` | `capabilities_settings_loader.py:97-102` | Replace with specific exception types; let critical exceptions propagate |

### Performance
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 2 | 🟡 WARNING | Unnecessary deepcopy of defaults/schema on every instantiation — `SettingsLoaderCapability.__init__()` calls `copy.deepcopy(DEFAULT_SETTINGS)` and `copy.deepcopy(SETTINGS_SCHEMA)` each time the capability is constructed. These are immutable constants that should be cached at module level or lazily initialized | `capabilities_settings_loader.py:56-57` | Cache defaults/schema at module level; deepcopy only when mutating |
| 3 | 🟡 WARNING | Deepcopy on every settings merge — `deep_merge_dicts()` deep-copies entire base dict and every override value. For large settings trees this is O(n) per merge. Consider immutable data structure or copy-on-write pattern for hot paths | `utility_config_helpers.py:86-93` | Evaluate if full deepcopy is needed; consider shallow merge with immutable snapshot wrapper |

### Error Handling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 4 | 🟡 WARNING | Silent exception swallowing in workspace resolution — `_resolve_uncached()` uses bare `except (OSError, ValueError): ...` and `if candidate.is_dir():` checks without logging when candidates fail. FR-CFG-003 requires "Invalid env path logs warning, falls through" but invalid env paths are silently dropped | `capabilities_workspace_resolver.py:46-51` | Add `logger.warning()` for each failed candidate to aid debugging |
| 5 | 🟡 WARNING | Silent pass in exception handler — `_resolve_uncached()` uses bare `...` pass as fallthrough without logging. Should emit a warning for observability | `capabilities_workspace_resolver.py:46-51` | Replace `...` with `logger.warning(...)` call |

### SOLID Principles
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 6 | 🟡 WARNING | Contract uses primitive Callable instead of protocol — `ISettingsMetadataProtocol` constructor takes `Callable[[], ConfigMetadata]` directly. AES402 requires contract methods use taxonomy VO/constant types or protocol interfaces, not primitive types like Callable. Should define a protocol (e.g., `_IMetadataSource`) for DI inversion | `contract_settings_metadata_protocol.py`, `capabilities_settings_metadata.py:19` | Replace Callable with a protocol interface; wire in container |

### Code Quality
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 7 | 🟢 INFO | Orchestrator owns event buffer state — `ConfigOrchestrator` maintains `_event_buffer` and `_snapshot` state. While documented as intentional ("Owns the bounded event ring buffer (T-09)"), this mixes orchestration with internal state storage. Event buffer could be a separate capability or injected | `agent_config_orchestrator.py:47-48` | Consider extracting event buffer to its own capability or making it injectable via protocol |
| 8 | 🟢 INFO | Unconventional ellipsis fallthrough — `_typed()` in `capabilities_settings_retriever.py` uses `...` as a "do nothing, fall through" marker. Not an AES304 bypass but unconventional Python style that could confuse readers | `capabilities_settings_retriever.py:68` | Replace with explicit `pass` or restructure to avoid need for fallthrough |

### Additional Findings (Phase 3b)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 9 | 🟡 WARNING | `_record_event` serializes events via `asdict()` then `json.dumps()` without applying redaction — if event payloads contain settings values with secrets, they could leak in logs despite redaction rules being available | `agent_config_orchestrator.py:89-92` | Apply `redact_dict()` to event data before serialization |
| 10 | 🟡 WARNING | `reload_settings` catches bare `Exception` — the catch-all at line 103 could hide unexpected errors that should propagate. Should narrow to specific config error types | `capabilities_settings_loader.py:102-109` | Use `except (ConfigLoadError, ConfigParseError, ConfigValidationError)` instead of bare `Exception` |
| 11 | 🟡 WARNING | Workspace resolver raises `ConfigRootResolutionError` without preserving exception chain — the OSError at strategy 6 is caught but root cause traceback is lost | `capabilities_workspace_resolver.py:68-70` | Use `raise ConfigRootResolutionError(...) from exc` to preserve debugging info |
| 12 | 🟡 WARNING | `WorkspaceResolverCapability.__init__` uses `config_path: object` — violates AES 405 (Any type annotation); should use `ConfigPath | None` or proper protocol type | `capabilities_workspace_resolver.py:32` | Replace `object` with `ConfigPath | None` for type safety |
| 13 | 🟡 WARNING | `ConfigContainer.__init__` uses `config_file_loader: object | None` — same pattern, should use proper `ConfigFileLoader | None` type | `root_config_container.py:39` | Use `ConfigFileLoader | None` from taxonomy instead of bare `object` |
| 14 | 🟢 INFO | `copy.deepcopy(DEFAULT_SETTINGS)` on every instantiation — if defaults are static, cache at module level to avoid redundant allocations | `capabilities_settings_loader.py:54-55` | Cache defaults at module level; deepcopy only when mutating |
| 15 | 🟢 INFO | Event serialization uses `asdict()` without schema validation — if event classes change structure, serialization could silently break | `agent_config_orchestrator.py:89` | Add explicit field selection or schema validation for event serialization |

## Action Items
- ✅ COMPLETED Replace bare `except Exception` with specific types in `_build_core()` (finding #1)
- ⏳ DEFERRED Cache defaults/schema deepcopy at module level (finding #2, #14) — negligible performance impact
- ✅ COMPLETED Add logging for failed workspace resolution candidates (findings #4, #5)
- ✅ COMPLETED Replace `Callable` with protocol interface in ISettingsMetadataProtocol (finding #6)
- ⏳ DEFERRED Consider extracting event buffer to injectable component (finding #7) — documented design decision
- ✅ COMPLETED Replace ellipsis fallthrough with explicit pass (finding #8)
- [ ] P2 FIX #9: Apply redaction to event payloads before JSON serialization in `_record_event`
- [ ] P1 FIX #10: Narrow exception handling in `reload_settings` from bare `Exception` to specific config error types
- [ ] P1 FIX #11: Preserve exception chain in workspace resolver with `raise ... from exc`
- [ ] P2 FIX #12: Replace `object` type annotation in `WorkspaceResolverCapability.__init__` with `ConfigPath | None`
- [ ] P2 FIX #13: Replace `object | None` in `ConfigContainer.__init__` with proper `ConfigFileLoader | None`
- [ ] P3 FIX #15: Add schema validation or explicit field selection for event serialization

## Fixed Code

### File: `modules/config/src/capabilities_settings_loader.py`

**Finding #1:** Added specific exception types before bare `except Exception`:

```python
                except (ConfigParseError, ConfigLoadError, ConfigValidationError):
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise
                    parse_warnings.append(
                        ParseWarning(f"failed to parse {resolved}; using defaults")
                    )
                    file_data = {}
                except (UnicodeDecodeError, OSError) as exc:
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise ConfigLoadError(f"Failed to load settings: {exc}") from exc
                    parse_warnings.append(
                        ParseWarning(f"failed to load {resolved}; using defaults")
                    )
                    file_data = {}
                except Exception as exc:
                    # Catch-all for unexpected errors — re-raise in strict mode
                    if self._policy_mode == POLICY_MODE_STRICT:
                        raise ConfigLoadError(f"Failed to load settings: {exc}") from exc
                    parse_warnings.append(
                        ParseWarning(f"unexpected error loading {resolved}; using defaults")
                    )
                    file_data = {}
```

### File: `modules/config/src/capabilities_workspace_resolver.py`

**Findings #4, #5:** Added logger and warning logging for failed candidates:

```python
logger = logging.getLogger(__name__)
```

```python
        # 1. Explicit override
        if self._explicit_override:
            candidate = Path(self._explicit_override).resolve()
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="explicit_override")
            logger.warning(
                "Explicit workspace override is not a directory: %s",
                self._explicit_override,
            )

        # 2. Environment signal
        env_root = os.environ.get(WORKSPACE_ROOT_ENV)
        if env_root:
            try:
                candidate = Path(env_root).resolve()
                if candidate.is_dir():
                    return WorkspacePath(path=str(candidate), strategy="env_signal")
            except (OSError, ValueError) as exc:
                logger.warning("Invalid BLENDERMCP_ROOT path '%s': %s", env_root, exc)

        # 3. Settings file parent
        if self._config_path:
            candidate = Path(str(self._config_path)).resolve().parent
            if candidate.is_dir():
                return WorkspacePath(path=str(candidate), strategy="settings_file_location")
            logger.warning(
                "Settings file parent is not a directory: %s",
                str(Path(str(self._config_path)).resolve().parent),
            )
```

### File: `modules/shared/src/config/contract_settings_metadata_protocol.py`

**Finding #6:** Added `_IMetadataSource` protocol to replace primitive Callable:

```python
class _IMetadataSource(Protocol):
    """Protocol for providing ConfigMetadata (FR-CFG-004).

    Replaces primitive Callable type with a proper protocol for DI inversion.
    Implemented by SettingsLoaderCapability.get_last_metadata bound method.
    """

    def __call__(self) -> ConfigMetadata: ...
```

### File: `modules/config/src/capabilities_settings_metadata.py`

**Finding #6:** Updated to use `_IMetadataSource` protocol instead of `Callable`:

```python
from modules.shared.src.config.contract_settings_metadata_protocol import (
    _IMetadataSource,
    ISettingsMetadataProtocol,
)
```

```python
    def __init__(self, metadata_supplier: _IMetadataSource | None = None) -> None:
        self._metadata_supplier = metadata_supplier
```

### File: `modules/config/src/capabilities_settings_retriever.py`

**Finding #8:** Replaced ellipsis with explicit pass:

```python
        elif expected is float:
            if isinstance(raw, bool):
                pass  # falls through to strict-mode check below
```

### File: `modules/config/src/agent_config_orchestrator.py`

**Finding #9:** Apply redaction before event serialization:

```python
def _record_event(self, event: object) -> None:
    """Serialize and store a domain event into the bounded ring buffer."""
    payload = asdict(event)
    # Apply redaction to prevent secret leakage in event logs
    redacted_payload = self._redaction_rules.redact_dict(payload) if isinstance(payload, dict) else payload
    self._event_buffer.append(redacted_payload)
    logger.info("config_event %s", json.dumps(redacted_payload, default=str))
```

### File: `modules/config/src/capabilities_settings_loader.py`

**Finding #10:** Narrow exception handling in reload_settings:

```python
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
        except (ConfigLoadError, ConfigParseError, ConfigValidationError):
            if self._policy_mode == POLICY_MODE_PERMISSIVE and self._cached is not None:
                return self._cached
            raise
```

### File: `modules/config/src/capabilities_workspace_resolver.py`

**Finding #11:** Preserve exception chain in workspace resolver:

```python
# 6. CWD fallback
try:
    cwd = Path.cwd().resolve()
    if cwd.is_dir():
        return WorkspacePath(path=str(cwd), strategy="cwd_fallback")
except OSError as exc:
    raise ConfigRootResolutionError("All workspace resolution strategies failed") from exc
```

**Finding #12:** Replace `object` type annotation:

```python
def __init__(
    self,
    explicit_override: str | None = None,
    config_path: ConfigPath | None = None,
) -> None:
    self._explicit_override = explicit_override
    self._config_path = config_path
    self._lock = threading.Lock()
    self._cached: WorkspacePath | None = None
```

### File: `modules/config/src/root_config_container.py`

**Finding #13:** Replace `object | None` with proper type:

```python
def __init__(
    self,
    config_file_loader: ConfigFileLoader | None = None,
    policy_mode: str = DEFAULT_POLICY_MODE,
    explicit_workspace: str | None = None,
    extra_redaction_patterns: tuple[str, ...] = (),
    strict_mode_enabled: bool | None = None,
) -> None:
```
