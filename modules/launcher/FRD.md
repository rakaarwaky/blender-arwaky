# FRD — Blender Runtime Launcher Feature

## System Overview
The Launcher is the single authority for operating on the Blender process itself. It finds/validates the executable, starts it with the integration component, confirms readiness, shuts it down safely with escalation, and persists runtime state with corruption safety.

## Functional Requirements

### FR-001: Locate, Register, and Launch Application
- **Description**: Discover usable Blender executable, validate it, and start Blender with the integration bridge active.
- **Input**: Optional explicit location override, mode preference, readiness timeout.
- **Output**: Registration result, Launch result (process ref, readiness state, endpoint summary).
- **Business Rules**: Discovery order: explicit > registered > env > platform > PATH. Must validate as genuine Blender. Idempotent when verified running instance exists. Distinguishes process spawned from integration ready.
- **Edge Cases**: Not found; multiple candidates; unsupported version; bridge endpoint conflict; crash during startup.
- **Error Handling**: `configuration_error` when no valid executable found; `validation_error` for failed checks; `timeout_error` for readiness.

### FR-002: Shut Down and Check Runtime Status
- **Description**: Graceful shutdown with force termination fallback, and verify true runtime status via actual process liveness.
- **Input**: Shutdown request (force preference), depth preference (lightweight vs full).
- **Output**: Shutdown result (termination method), Runtime status (state classification).
- **Business Rules**: Graceful shutdown via bridge channel. No exit within timeout escalates to force termination if allowed. Status verifies actual OS process liveness, guarding against PID reuse.
- **Edge Cases**: Process not running; unresponsive to graceful; lingering children; PID reuse; zombie process.
- **Error Handling**: `timeout_error` for graceful exceeds; `state_error` for persisted vs observed conflict; `termination_error` if force fails.

### FR-003: Persist Runtime State
- **Description**: Persist registered path, process ref, and bridge endpoint summary with corruption safety.
- **Input**: Runtime state to persist.
- **Output**: Persistence result (success, reconciliation warnings).
- **Business Rules**: Atomic/crash-safe writes. Corrupt/unreadable files fall back to empty state with warning. Stale process refs reconciled via liveness verification.
- **Edge Cases**: Corrupt content; partial write after crash; disk full; stale ref after reboot.
- **Error Handling**: `state_error` triggers empty-state fallback + warning.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `launch_blender` | `filepath`, `mode`, `port` | `UnifiedEnvelope` | Start Blender with integration active |
| `shutdown_blender` | `force` | `UnifiedEnvelope` | Graceful shutdown with force fallback |
| `get_runtime_status` | None | `UnifiedEnvelope` | Verify true process liveness |
| `register_executable` | `path` | `UnifiedEnvelope` | Locate and register Blender executable |

## Integration Points

- **3rd Party**: OS Process Management (spawn/kill signals).
- **Internal**: `config` (executable paths/timeouts), `security` (safe auth handling), `diagnostics` (health composition).

## Non-functional Requirements (Detailed)

- **Performance**: Readiness probes bounded by timeout to prevent indefinite blocking. Lightweight status checks avoid bridge round-trips.
- **Security**: Auth material passed to bridge without logging. No secrets persisted in state files.
- **Scalability**: Launch idempotency prevents duplicate Blender instances. Stale reconciliation handles unexpected OS reboots.

## Test Scenarios / QA Checklist

- [ ] Verify discovery order: explicit > registered > env > platform > PATH.
- [ ] Verify non-Blender executables are rejected during validation.
- [ ] Verify duplicate launch returns existing state without spawning a second process.
- [ ] Verify graceful shutdown escalates to force termination if unresponsive and policy allows.
- [ ] Verify corrupt state files fall back to empty state with warning, never crashing.

## Assumptions & Constraints

- Other features may consume launcher state but never spawn, terminate, or validate Blender directly.
- Multi-instance orchestration is out of scope; one active connection per instance.

## Glossary

- **Bridge Endpoint**: The socket/pipe configuration used by the Gateway to communicate with the Blender bridge addon.
- **PID Reuse Guard**: Logic to prevent false "alive" status when the OS reassigns a Process ID to a different application.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.

## Reference

- PRD: `./PRD.md`
- Depends On: `config`, `security`, `diagnostics`
