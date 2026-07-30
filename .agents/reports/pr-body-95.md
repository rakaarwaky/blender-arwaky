## Description

This PR addresses critical launcher module issues from the Business Logic & Requirements Review:

- **Issue #95**: Launcher business logic gaps — executable registration not persisted, events not wired, PID reuse unprotected, corrupt state silent failure

Key fixes include:
- P0: Executable registration now persists to state store via `persist_cap` injection
- P0: PID reuse guard using `/proc/{pid}/stat` starttime field detects stale processes
- P0: Event sink wired into all capabilities for lifecycle event emission
- P1: Version compatibility semantic parsing with 4.2+ WARNING classification
- P1: Corrupt state load emits warning event instead of silent None
- P1: `process_alive()` correctly treats EPERM as "process exists but caller lacks permission"

## Type of Change

- [x]  🐛 Bug fix
- [ ]  ✨ New feature
- [ ]  💥 Breaking change
- [ ]  📚 Documentation update
- [x]  🔧 Refactor / code cleanup
- [ ]  ⚡ Performance improvement
- [x]  ✅ Test addition / improvement
- [ ]  Documentation only

## Affected Modules

- [ ]  modules/asset
- [ ]  modules/cli
- [ ]  modules/config
- [ ]  modules/diagnostics
- [ ]  modules/dispatcher
- [ ]  modules/gateway
- [ ]  modules/job
- [x]  modules/launcher
- [ ]  modules/mcp
- [ ]  modules/object
- [ ]  modules/render
- [ ]  modules/scene
- [ ]  modules/security
- [x]  modules/shared
- [ ]  modules/telemetry
- [ ]  `blender_mcp_addon/`
- [ ]  Documentation only
- [ ]  CI / build only

## Changes Made

### Executable Registration Persistence (P0 — Finding #1)

1. **ExecutableLocator** — Accepts `persist_cap: PersistStateProtocol` to persist executable path registration (FR-LAU-001)
2. **RootContainer** — Injects `persist_cap` into locate capability so discovered paths survive process restarts

### PID Reuse Guard (P0 — Finding #3)

1. **RuntimeStatusChecker** — Stores `_process_start_time` via `mark_launched()` and compares against live `/proc/{pid}/stat` field 22 (`starttime`)
2. Mismatch indicates PID reuse → returns STALE state with reconciliation event emission

### Event Sink Wiring (P0 — Finding #5)

1. **RootContainer** — Single `_event_sink` injected into StatePersistence, RuntimeStatusChecker, ExecutableLocator, ProcessLauncher, and ProcessShutdown
2. Removed duplicate `_safe_event_sink` definition that was never used

### Version Compatibility (P1 — Finding #2)

1. **ExecutableLocator._check_compatibility()** — Parses semantic version strings; marks 4.2+ as WARNING for experimental features
2. Returns UNKNOWN/UNSUPPORTED/SUPPORTED/WARNING per policy

### Corrupt State Warning (P1 — Finding #7)

1. **StatePersistence** — Accepts `event_sink` and emits `corrupt_state_detected` event on JSON parse failures or non-dict data
2. New constant: `LAUNCHER_EVENT_CORRUPT_STATE_DETECTED`

### Process Alive EPERM Semantics (P1 — Finding #6)

1. **process_alive()** — Returns `True` for EPERM/other OSError exceptions (process exists but caller lacks permission to signal)
2. Only returns `False` for ESRCH (no such process)

## Testing

- [x]  I have added tests that prove my fix/feature works
- [x]  New and existing unit tests pass locally
- [x]  I have updated the test markers appropriately (`@pytest.mark.unit`, etc.)

```bash
# Commands run to verify
cd modules && uv run pytest launcher/tests/test_launcher_business_logic_fixes.py -v
uv run ruff check modules/launcher/src/capabilities_executable_locator.py modules/launcher/src/capabilities_runtime_status.py modules/launcher/src/capabilities_state_persistence.py modules/shared/src/launcher/utility_process_ops.py
```

## Documentation

- [ ]  I have updated `README.md` (if user-facing change)
- [ ]  I have updated `AGENT.md` (if agent command change)
- [x]  I have updated `SKILL.md` (if MCP / CLI tool change)
- [ ]  I have updated `TEST.md` (if test pattern change)
- [x]  I have added an entry to `CHANGELOG.md` under `[Unreleased]`

## Checklist

- [x]  My code follows the project's AES 7-layer architecture ARCHITECTURE.md
- [x]  My code follows the 3-word file naming convention (`{domain}_{concern}_{suffix}.py`)
- [x]  I have added docstrings to all new public functions/classes
- [x]  My changes do not introduce new linting errors
- [x]  I have not committed any secrets, API keys, or hardcoded paths
