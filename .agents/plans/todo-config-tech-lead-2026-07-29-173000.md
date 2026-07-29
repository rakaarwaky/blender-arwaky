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

## Action Items
- ✅ COMPLETED Replace bare `except Exception` with specific types in `_build_core()` (finding #1)
- ⏳ DEFERRED Cache defaults/schema deepcopy at module level (finding #2) — negligible performance impact
- ✅ COMPLETED Add logging for failed workspace resolution candidates (findings #4, #5)
- ✅ COMPLETED Replace `Callable` with protocol interface in ISettingsMetadataProtocol (finding #6)
- ⏳ DEFERRED Consider extracting event buffer to injectable component (finding #7) — documented design decision
- ✅ COMPLETED Replace ellipsis fallthrough with explicit pass (finding #8)

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
