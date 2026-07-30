
.agents/issues/issue-launcher-config-integration-business-analyst-2026-07-30-150512.md

# Issue: launcher ↔ config — Cross-Feature Integration Review

## Summary
The launcher FRD explicitly declares a dependency on config for executable path, timeouts, search locations, and persistence location. The PRD data flow diagram shows `Config → workspace root → Launcher` and `Config → settings → Launcher`. However, **zero integration code exists between these two features**. The launcher container accepts a `LauncherConfigVO` that is never populated from `IConfigAggregate`, the config schema does not define launcher-specific settings, the launcher bypasses config's env override mechanism with its own `BLENDER_PATH` env var, workspace resolution is not consumed for state persistence, and redaction rules are not applied to launcher events. This means in production, the launcher operates entirely on hardcoded defaults, ignoring user configuration — a critical gap that defeats the purpose of the config feature's "single owner for settings" mandate.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Launcher FRD states "Depends On: config (executable path, timeout, search locations, persistence location)" but no code reads from `IConfigAggregate`. The `LauncherContainer.__init__` accepts `config: LauncherConfigVO | None = None` and defaults to `LauncherConfigVO()` with all hardcoded values. No composition root entry bridges config → launcher. | `modules/launcher/src/root_launcher_container.py:47-49` | Create a `root_composition_entry.py` (or extend existing entry) that: (1) builds `ConfigContainer`, (2) calls `config_aggregate.load()`, (3) reads launcher settings via `get_string/get_int/get_bool/get_float`, (4) constructs `LauncherConfigVO` from config values, (5) passes it to `LauncherContainer`. |
| 2 | 🔴 CRITICAL | Config's `SETTINGS_SCHEMA` only defines `blender.executable_path`, `blender.host`, `blender.port`, `server.transport`, `server.log_dir`. Launcher requires 10 config keys (`launch_timeout`, `shutdown_timeout`, `force_termination_enabled`, `search_locations`, `supported_version_range`, `state_persistence_location`, `default_launch_mode`, `stale_reconciliation_enabled`, `readiness_probe_interval_seconds`) that have no schema definition. Users cannot configure launcher behavior via `config.yaml`. | `modules/shared/src/config/taxonomy_config_constant.py:68-82` | Extend `SETTINGS_SCHEMA` with a `launcher` section containing all 10 keys with types and defaults. Add corresponding entries to `DEFAULT_SETTINGS`. |
| 3 | 🟡 WARNING | Launcher FRD FR-LAU-005 states "Location from config/workspace, never invented" for state persistence. But `LauncherContainer` accepts `state_path: str | None` as a raw string parameter. No code calls `config_aggregate.resolve_workspace()` to derive the persistence location. If `state_path` is None, persistence silently fails (returns `success=False`). | `modules/launcher/src/root_launcher_container.py:47` | In the composition root, derive `state_path` from `config_aggregate.resolve_workspace().path + "/.launcher_state.json"`. Never pass None in production wiring. |
| 4 | 🟡 WARNING | Config FRD FR-CFG-001 defines env override prefix `BLENDERMCP_` as the sole mechanism for environment-based settings. But `ExecutableLocator._build_candidate_order()` reads `os.environ.get("BLENDER_PATH")` directly — a completely separate env var that bypasses config's precedence, validation, and metadata tracking. | `modules/launcher/src/capabilities_executable_locator.py:82` | Remove direct `os.environ.get("BLENDER_PATH")` from the locator. Instead, the composition root should read `BLENDERMCP_BLENDER.EXECUTABLE_PATH` via config's env override mechanism and pass it as `override` or via `LauncherConfigVO.executable_path`. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🔴 CRITICAL | The PRD data flow shows `Config → settings → Launcher` but the actual runtime flow is: `LauncherContainer` → `LauncherConfigVO()` (hardcoded defaults) → capabilities. User's `config.yaml` values for `blender.executable_path` are loaded by config but never reach the launcher. A user who sets `blender.executable_path: "/opt/blender/blender"` in config.yaml will have it ignored by the launcher. | `modules/launcher/src/root_launcher_container.py:49` + `modules/shared/src/config/taxonomy_config_constant.py:57` | Wire the composition root to read `config_aggregate.get_string("blender.executable_path")` and inject it into `LauncherConfigVO.executable_path`. |
| 6 | 🟡 WARNING | Config supports `reload()` (FR-CFG-001). If a user changes `blender.executable_path` and triggers a config reload, the launcher has no notification mechanism. It continues using the stale `LauncherConfigVO` frozen at construction time. The FRD doesn't specify whether launcher should react to config changes, but the "single owner" mandate implies it should. | `modules/launcher/src/root_launcher_container.py:47-49` | Document in both FRDs that launcher config is read once at startup (snapshot semantics). If hot-reload is needed, add a `config_change_listener` callback or re-read mechanism. |
| 7 | 🟡 WARNING | Config FR-CFG-005 provides redaction rules. Launcher FRD events section states "Never: auth material, bridge secrets, full process env, sensitive filesystem details." But launcher events (`LauncherLifecycleEvent`) are emitted without passing through `IConfigAggregate.redact_dict()` or `get_redaction_rule()`. If `process_reference` or `reason_summary` ever contains a path with credentials, it will leak. | `modules/launcher/src/capabilities_process_launcher.py:95-100` | Inject `IRedactionRulesProtocol` into launcher capabilities (via DI at composition root). Apply `redact_dict()` to event payloads before emission, or at minimum redact `process_reference` and `reason_summary` fields. |
| 8 | 🟡 WARNING | Config's `DEFAULT_SETTINGS` defines `blender.executable_path: "blender"` (bare name, resolved via PATH). The launcher's `ExecutableLocator` also does `shutil.which("blender")` as its last discovery step. This creates a redundant dual-PATH-resolution: config resolves "blender" as a string, then the locator independently resolves it via `shutil.which`. If config's value is an absolute path, the locator's `os.path.exists()` check handles it, but the semantic overlap is confusing. | `modules/shared/src/config/taxonomy_config_constant.py:57` + `modules/launcher/src/capabilities_executable_locator.py:85-87` | Clarify in FRD: config provides the raw path string (may be bare name or absolute). Launcher's locator is responsible for resolution/validation. Config should NOT resolve the path — just store it. Document this boundary explicitly. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 9 | 🔴 CRITICAL | No composition root entry exists that wires config → launcher. The `root_launcher_container.py` has `create_launcher_feature(config, state_path)` but no caller passes config-derived values. The `pyproject.toml` entry points (`blender-mcp`, `blender-arwaky`) point to `root_mcp_entry` and `surface_cli_main` — neither imports the launcher container with config integration. | `modules/launcher/src/root_launcher_container.py:107-112` + `pyproject.toml:47-48` | Create or extend the application entry point to: (1) instantiate `ConfigContainer`, (2) call `build()` → `IConfigAggregate`, (3) call `load()`, (4) extract launcher settings, (5) build `LauncherConfigVO`, (6) call `create_launcher_feature(config=vo, state_path=derived)`. |
| 10 | 🟡 WARNING | `LauncherConfigVO` has `search_locations: tuple[str, ...]` defaulting to empty tuple. Config's `DEFAULT_SETTINGS` has no `launcher.search_locations` key. Platform-standard locations (FR-LAU-001 discovery step 4) are never populated from config. The locator falls through to `shutil.which("blender")` immediately after checking the empty search_locations tuple. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:195` + `modules/launcher/src/capabilities_executable_locator.py:83-84` | Add `launcher.search_locations` to config schema as a list type. In composition root, read via `config_aggregate.get("launcher.search_locations")` and convert to tuple. Provide platform-appropriate defaults in `DEFAULT_SETTINGS`. |
| 11 | 🟡 WARNING | Type conversion gap: Config's `get_float("launcher.launch_timeout", 30.0)` returns a Python float. `LauncherConfigVO.launch_timeout_seconds` expects `float`. This works. But `get_bool("launcher.force_termination_enabled", True)` returns Python bool, and `LauncherConfigVO.force_termination_enabled` expects `bool`. Also works. However, `get("launcher.search_locations")` returns `SettingsValue` which could be `list[str]` — but `LauncherConfigVO.search_locations` expects `tuple[str, ...]`. No conversion layer handles this. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:195` | In the composition root wiring code, explicitly convert: `tuple(config_aggregate.get("launcher.search_locations", []))`. Document that list→tuple conversion is the composition root's responsibility. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 12 | 🟡 WARNING | No integration test exists that verifies: "user sets `blender.executable_path` in config.yaml → launcher uses that path." The QA checklists in both FRDs test each feature in isolation. The launcher QA checklist item "Discovery: explicit→registered→env→platform→PATH" cannot pass for the "registered" step because "registered" means "from config/state store" but config is never wired. | `modules/launcher/FRD.md` (QA Checklist) + `modules/config/FRD.md` (QA Checklist) | Add a cross-feature integration test: (1) write a temp config.yaml with `blender.executable_path: /fake/blender`, (2) build ConfigContainer + load, (3) build LauncherConfigVO from config, (4) assert `vo.executable_path == "/fake/blender"`. |
| 13 | 🟡 WARNING | No test verifies that launcher events are redacted using config's redaction rules. The launcher FRD says "Never: auth material, bridge secrets" but no acceptance criterion tests this cross-feature behavior. | `modules/launcher/FRD.md` (Events section) | Add integration test: (1) configure redaction patterns via config, (2) emit a launcher event with a path containing "token", (3) assert the event payload has "***REDACTED***" in the relevant field. |
| 14 | 🟢 INFO | No test verifies workspace-derived state persistence location. FR-LAU-005 says "Location from config/workspace, never invented" but no test creates a workspace via config and asserts the launcher persists state there. | `modules/launcher/FRD.md` (FR-LAU-005) | Add integration test: (1) set `BLENDERMCP_ROOT=/tmp/test-ws`, (2) build config + resolve workspace, (3) derive state_path, (4) persist state, (5) assert file exists at `/tmp/test-ws/.launcher_state.json`. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 15 | 🔴 CRITICAL | PRD data flow diagram explicitly shows `Config -->|workspace root| Launcher` and `Config -->|settings| Launcher`. Neither arrow has a corresponding code path. The traceability chain PRD → FRD → Code is broken at the integration boundary. | `PRD.md` (Data Flow Diagram) | Implement the composition root wiring. Add a comment in `root_launcher_container.py` referencing the PRD data flow: `# PRD: Config → settings → Launcher (workspace root + executable path)`. |
| 16 | 🟡 WARNING | Config FRD "Provides To: All features" is untraceable for the launcher consumer. No code in `modules/launcher/` imports from `modules/shared/src/config/`. The dependency exists only in prose. | `modules/config/FRD.md` (Provides To) + `modules/launcher/src/` (all files) | The dependency should be realized at the composition root (Root layer), not via direct imports. But the composition root must exist. Add a traceability comment in the entry point. |
| 17 | 🟢 INFO | Launcher FRD "Depends On: config" lists 4 specific items (executable path, timeout, search locations, persistence location). Only `executable_path` has a corresponding key in config's `DEFAULT_SETTINGS`. The other 3 have no config schema entry, making the dependency partially fictional. | `modules/launcher/FRD.md` (Depends On) | Either (a) add all 4 to config schema, or (b) update launcher FRD to say "Depends On: config (executable path) + composition root defaults (timeout, search locations, persistence location)". |

## Violations
- **AES201 (Import Boundary) — Not violated**: The launcher correctly does NOT import from config's capabilities. The integration should happen at the Root layer (composition root), which is allowed to import all layers. The violation is the *absence* of this wiring, not an incorrect import.
- **AES503 (Capabilities Orphan) — Borderline**: `ExecutableLocator`, `ProcessLauncher`, etc. are wired in `LauncherContainer`, so they are not orphans within the launcher module. But the launcher module itself is effectively orphaned from the application because no entry point wires it with config.
- **AES505 (Agent Orphan) — Potential**: `LauncherOrchestrator` is constructed by `LauncherContainer.agent` property, but if no entry point ever calls `create_launcher_feature()`, the orchestrator is unreachable from any surface or entry point.

## Action Items (For Developer)
- [ ] 🔴 P0: Create composition root wiring that reads `IConfigAggregate` and populates `LauncherConfigVO` (Findings #1, #5, #9, #15)
- [ ] 🔴 P0: Extend `SETTINGS_SCHEMA` and `DEFAULT_SETTINGS` with `launcher.*` keys for all 10 launcher config fields (Finding #2)
- [ ] 🔴 P0: Derive `state_path` from `config_aggregate.resolve_workspace()` in the composition root (Finding #3)
- [ ] 🟡 P1: Remove direct `os.environ.get("BLENDER_PATH")` from `ExecutableLocator`; route through config's env mechanism (Finding #4)
- [ ] 🟡 P1: Inject `IRedactionRulesProtocol` into launcher event emission path (Finding #7)
- [ ] 🟡 P1: Add `launcher.search_locations` to config schema with platform defaults (Finding #10)
- [ ] 🟡 P1: Add cross-feature integration tests for config→launcher wiring (Findings #12, #13, #14)
- [ ] 🟡 P2: Document snapshot semantics for launcher config (no hot-reload) in both FRDs (Finding #6)
- [ ] 🟡 P2: Clarify config vs launcher responsibility for path resolution in FRDs (Finding #8)
- [ ] 🟢 P3: Add traceability comments in composition root referencing PRD data flow (Finding #16)

## Proposed Fixes / Reference Code

### File: `modules/shared/src/config/taxonomy_config_constant.py`

**Fix #2 — Extend schema and defaults with launcher settings:**
```python
# ─── Compile-Time Defaults (FR-CFG-001, Q4) ──────────────────
DEFAULT_SETTINGS: dict[str, Any] = {
    "blender": {"executable_path": "blender", "host": "localhost", "port": 9876},
    "server": {"transport": "stdio", "log_dir": "log"},
    "launcher": {
        "launch_timeout_seconds": 30.0,
        "shutdown_timeout_seconds": 10.0,
        "force_termination_enabled": True,
        "readiness_probe_interval_seconds": 0.5,
        "default_launch_mode": "interface",
        "stale_reconciliation_enabled": True,
        "supported_version_range": ">=3.0",
        "search_locations": [],
    },
}

# ─── Settings Schema (FR-CFG-001, Q3) ───────────────────────
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
    "launcher": {
        "type": "dict",
        "required": False,
        "children": {
            "launch_timeout_seconds": {"type": "float", "required": False},
            "shutdown_timeout_seconds": {"type": "float", "required": False},
            "force_termination_enabled": {"type": "bool", "required": False},
            "readiness_probe_interval_seconds": {"type": "float", "required": False},
            "default_launch_mode": {"type": "str", "required": False},
            "stale_reconciliation_enabled": {"type": "bool", "required": False},
            "supported_version_range": {"type": "str", "required": False},
            "search_locations": {"type": "list", "required": False},
        },
    },
}
```

### File: `modules/root_composition_entry.py` (NEW)

**Fix #1/#5/#9/#15 — Composition root wiring config → launcher:**
```python
"""Root: Application composition entry.
Wires all feature containers. PRD data flow:
  Config → settings → Launcher (executable path, timeouts, search locations)
  Config → workspace root → Launcher (state persistence location)
"""

from __future__ import annotations

from modules.config.src.root_config_container import ConfigContainer
from modules.launcher.src.root_launcher_container import create_launcher_feature
from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchMode,
)


def build_launcher_config(config_aggregate: IConfigAggregate) -> LauncherConfigVO:
    """Extract launcher settings from config aggregate into a frozen VO."""
    search_raw = config_aggregate.get("launcher.search_locations", [])
    search_locations = tuple(search_raw) if isinstance(search_raw, list) else ()

    mode_str = config_aggregate.get_string("launcher.default_launch_mode", "interface")
    try:
        mode = LaunchMode(mode_str)
    except ValueError:
        mode = LaunchMode.INTERFACE

    return LauncherConfigVO(
        executable_path=config_aggregate.get_string("blender.executable_path", "blender"),
        search_locations=search_locations,
        supported_version_range=config_aggregate.get_string("launcher.supported_version_range", ">=3.0"),
        launch_timeout_seconds=config_aggregate.get_float("launcher.launch_timeout_seconds", 30.0),
        shutdown_timeout_seconds=config_aggregate.get_float("launcher.shutdown_timeout_seconds", 10.0),
        force_termination_enabled=config_aggregate.get_bool("launcher.force_termination_enabled", True),
        readiness_probe_interval_seconds=config_aggregate.get_float("launcher.readiness_probe_interval_seconds", 0.5),
        state_persistence_location=None,  # derived below from workspace
        default_launch_mode=mode,
        stale_reconciliation_enabled=config_aggregate.get_bool("launcher.stale_reconciliation_enabled", True),
    )


def build_application() -> None:
    """Bootstrap all features with correct wiring."""
    # 1. Config feature (inner backbone)
    config_container = ConfigContainer()
    config_aggregate = config_container.build()
    config_aggregate.load()

    # 2. Derive workspace root for launcher state persistence
    workspace = config_aggregate.resolve_workspace()
    state_path = f"{workspace.path}/.launcher_state.json"

    # 3. Build launcher config from config aggregate
    launcher_config = build_launcher_config(config_aggregate)

    # 4. Wire launcher feature with config-derived settings
    launcher_aggregate = create_launcher_feature(
        config=launcher_config,
        state_path=state_path,
    )

    # 5. Pass aggregates to surfaces / MCP entry...
    # (surface wiring continues here)
```

### File: `modules/launcher/src/capabilities_executable_locator.py`

**Fix #4 — Remove direct env var bypass:**
```python
def _build_candidate_order(
    self, config: LauncherConfigVO, override: FilePath | None
) -> list[tuple[RegistrationSource, str]]:
    order: list[tuple[RegistrationSource, str]] = []
    if override:
        order.append((RegistrationSource.OVERRIDE, override))
    if config.executable_path:
        order.append((RegistrationSource.CONFIGURED, config.executable_path))
    # REMOVED: direct os.environ.get("BLENDER_PATH") — env overrides are
    # handled by config feature's BLENDERMCP_ prefix mechanism and flow
    # through LauncherConfigVO.executable_path at composition root.
    for loc in config.search_locations:
        order.append((RegistrationSource.PLATFORM, loc))
    sys_path = shutil.which("blender")
    if sys_path:
        order.append((RegistrationSource.SYSTEM_PATH, sys_path))
    return order
```

### File: `modules/launcher/src/root_launcher_container.py`

**Fix #7 — Inject redaction into event path:**
```python
class LauncherContainer:
    def __init__(
        self,
        config: LauncherConfigVO | None = None,
        state_path: str | None = None,
        redaction_rules: IRedactionRulesProtocol | None = None,  # NEW
    ) -> None:
        self._config = config or LauncherConfigVO()
        self._state_path = state_path
        self._redaction = redaction_rules
        self._orchestrator: LauncherOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        # ... existing wiring ...
        # Wrap event_sink with redaction:
        def _redacting_event_sink(event: LauncherLifecycleEvent) -> None:
            if self._redaction is not None:
                # Redact process_reference and reason_summary
                redacted_ref = self._redaction.redact_value("process_reference", event.process_reference)
                # Emit with redacted fields...
            # Forward to diagnostics event bus...
```

</parameter>
</function>
</tool_call>