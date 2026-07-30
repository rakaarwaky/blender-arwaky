# Blender Arwaky — Pull Request

## Description

This PR addresses issue #101 — launcher business logic review findings:

**P0 (Critical):**
- Changed `ILauncherOperateAggregate.locate_and_register()` to accept only optional override; injected config internally
- Introduced `LaunchRequestVO` and `BridgeEndpointSettingsVO`; updated protocol, aggregate, orchestrator, and capability
- **Made launch/shutdown/registration persist runtime state internally** — injected `PersistStateProtocol` into ProcessLauncher, ProcessShutdown, and ExecutableLocator
  - ProcessLauncher persists after successful spawn (process_id, launch_timestamp, bridge_endpoint)
  - ProcessShutdown persists NOT_RUNNING status after termination
  - ExecutableLocator persists executable_path after registration
- Resolved configuration authority: single injected config provider consistently used

**P1 (High):**
- Introduced `LauncherErrorCode` enum replacing free-text error strings across all outcome VOs
- Introduced `ShutdownRequestVO` with explicit force/escalation confirmation semantics
- Added diagnostics metadata to `RuntimeStatusVO`: process_reference, probe_duration_ms
- Added `LoadOutcomeVO` for persistence load path with corruption/parse warnings
- Made event emission safe: wrapped in try/except, never fails status checks due to observability failures
- Populated event duration_ms, method, and redacted reason_summary consistently
- Integrated security/redaction policy for event reasons, persistence warnings, and endpoint summaries

**P2 (Low):**
- Used config-driven readiness probe interval instead of hardcoded 0.2 seconds
- Created process group/session on spawn to support orphan child cleanup
- Added comprehensive tests for contract alignment, error codes, event payloads, corrupt state warnings, and config authority

## Type of Change

- [ ]  🐛 Bug fix
- [ ]  ✨ New feature
- [ ]  💥 Breaking change
- [x]  📚 Documentation
- [x]  🔧 Refactor / code cleanup
- [ ]  ⚡ Performance improvement
- [x]  ✅ Test addition / improvement
- [ ]  🏗️ Build / CI / dependency change

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

### Launcher Contracts (modules/shared/src/launcher/)
1. **Request VOs**
   - Added `LaunchRequestVO` with mode, readiness timeout, and bridge endpoint settings
   - Added `ShutdownRequestVO` with force_requested and escalation_confirmed fields
   - Added `BridgeEndpointSettingsVO` for endpoint host/port/protocol info
   - Added `LoadOutcomeVO` replacing void load() return type

2. **Error Codes**
   - Introduced `LauncherErrorCode` enum mapping FRD categories to machine-readable codes
   - Added error_code fields to RegistrationOutcomeVO, LaunchOutcomeVO, ShutdownOutcomeVO
   - Replaced free-text error strings with structured error_code + error_message

3. **Runtime Status**
   - Extended RuntimeStatusVO with process_reference, bridge_endpoint_summary, probe_duration_ms
   - Added diagnostics-friendly metadata for observability integration

4. **Protocol Updates**
   - Updated ILauncherOperateAggregate to accept request VOs instead of primitive parameters
   - Fixed locate_and_register signature: override-only parameter, injected config provider
   - Updated LaunchProtocol, ShutdownProtocol, PersistStateProtocol signatures

### Capabilities (modules/launcher/src/)
1. **ExecutableLocator** — single config authority, categorized errors/warnings, **internal persistence on registration**
2. **ProcessLauncher** — configurable probe interval, error codes, event completeness, **internal persistence after spawn**
3. **ProcessShutdown** — request VO adoption, error codes, redacted reasons, **internal persistence after termination**
4. **RuntimeStatus** — safe event emission (try/except), diagnostics metadata
5. **StatePersistence** — LoadOutcomeVO with warnings, TypeError handling

## Testing

- [x]  I have added tests that prove my fix/feature works
- [x]  New and existing unit tests pass locally
- [x]  I have updated the test markers appropriately (`@pytest.mark.unit`, etc.)

```bash
# Commands run to verify
python -m pytest modules/launcher/tests/test_launcher_feature.py -v
python -m flake8 modules/launcher/src modules/shared/src/launcher --max-line-length=200
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
