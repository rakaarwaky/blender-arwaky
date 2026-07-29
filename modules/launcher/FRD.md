# FRD — Blender Runtime Launcher Feature

## Purpose

Single authority for operating on the Blender process itself. Finds/validates executable, starts with integration component, confirms readiness, shuts down safely with escalation, verifies true liveness, persists runtime state with corruption safety. Other features may consume launcher state but never spawn, terminate, or validate Blender directly.

## Scope

- Locate Blender executable across platform-standard locations
- Register and validate Blender executable path
- Launch Blender with integration component active
- Readiness detection after launch
- Graceful shutdown with force termination fallback
- Process status and true liveness verification
- Stale state detection and recovery
- Runtime state persistence with corruption safety
- Launch idempotency and duplicate-launch prevention
- Version compatibility awareness
- Lifecycle observability events

## Out of Scope

3D scene actions, command catalog, MCP protocol, CLI formatting, socket connection/message transport (gateway), background task lifecycle, telemetry, asset/render/object/scene operations, scene persistence, multi-instance orchestration.

## Depends On

config (executable path, timeout, search locations, persistence location), security policy (safe auth material handling), diagnostics (health composition).

## Provides To

CLI, MCP, diagnostics, gateway (readiness + endpoint state before transport).

## Functional Requirements

### FR-LAU-001: Locate and Register Application

- **Description**: Discover usable Blender executable, validate, register as authoritative runtime path
- **Input**: Optional explicit location override
- **Output**: Registration result (validated executable ref, version summary, source)
- **Rules**: Discovery order: explicit override → registered path from config/state store → env signal → platform-standard locations → system PATH. Executable must exist + be executable by current user. Must validate as genuine Blender runtime. Version compared against supported range; outside → warning or rejection per policy. Successful validation registers path. Source recorded for diagnostics. Previously registered path re-validated if staleness suspected. Multiple valid candidates → first in order. Normalized + symlink-safe. No secrets/auth material stored.
- **Edge Cases**: Not found, multiple candidates, invalid executable, matching name non-Blender, unsupported version, permission denied, symlinked, network-mounted, stale path, case-insensitive fs, platform-specific wrapper, relocated installation
- **Error Handling**: Config error when no valid executable found; validation error for failed checks; version compatibility warning for out-of-range

### FR-LAU-002: Launch Application

- **Description**: Start Blender with integration component active, confirm readiness
- **Input**: Launch request (mode preference, bridge endpoint settings, readiness timeout)
- **Output**: Launch result (success, process ref, readiness state, endpoint summary, duration)
- **Rules**: Uses registered validated executable. Activates integration component during startup. Passes bridge endpoint settings + protocol info. Auth material through security policy, never logged. Idempotent when verified running instance exists → returns existing state. Distinguishes process spawned from integration ready. Readiness = process liveness + bridge readiness signal. Waits within configured launch timeout. Process alive without bridge readiness → launch failure or degraded per policy. Never blocks indefinitely. Early exit → surface exit reason. Mode preference honored where supported. Emits lifecycle event.
- **Edge Cases**: Already running, bridge endpoint conflict, crash during startup, process exits immediately, readiness signal missed, timeout, missing executable at launch, integration fails to activate, insufficient resources, permission denied, stale process ref from previous session, headless unsupported on platform
- **Error Handling**: Timeout error (readiness not confirmed); config error (missing/invalid path); launch error (process not spawned); state error (runtime conflict)

### FR-LAU-003: Shut Down Application

- **Description**: Graceful shutdown → force termination when unresponsive
- **Input**: Shutdown request (optional force preference, confirmation flag for escalation)
- **Output**: Shutdown result (success, termination method, duration, final process state)
- **Rules**: Graceful shutdown via integration component shutdown channel or supported signal. Waits within configured shutdown timeout. No exit within timeout → escalate to force termination if policy allows. Force termination verified by subsequent liveness check. Idempotent when process already absent → success with not-running indication. Persisted state updated to stopped. Never modifies/saves Blender scene content unless explicitly requested. Escalation emits event. Shutdown during launch → resolve launch state first. Orphaned child processes cleaned up where detectable+ safe. Termination method reported.
- **Edge Cases**: Process not running, unresponsive to graceful, force also fails, lingering children, shutdown during launch, concurrent shutdown, permission denied, already exiting, stale ref, unsaved work
- **Error Handling**: Not running error (strict mode only); timeout error (graceful exceeds timeout + force disallowed); state error (persisted vs observed conflict)

### FR-LAU-004: Check Runtime Status

- **Description**: Verify true runtime status via actual process liveness + integration responsiveness, not just persisted state
- **Input**: Optional depth preference (lightweight liveness vs full readiness)
- **Output**: Runtime status (state classification, process ref summary, readiness, staleness, uptime)
- **Rules**: Verifies actual process liveness via OS signals. Classification: not running/starting/running+ready/running but unresponsive/stopping/stale. Process alive but bridge unresponsive → unresponsive or stale per configured threshold. Stale: persisted ref no longer matches live process + guard against PID reuse. Read-only except stale reconciliation (may correct persisted state + emit event). Lightweight avoids bridge round-trip; full includes bridge liveness. Safe for health composition + user-facing diagnostics. Completes quickly within bounded probe timeout.
- **Edge Cases**: PID reuse, alive but bridge dead, bridge responsive but record missing, zombie, status during launch/shutdown transition, clock skew, permission denied reading process info, concurrent checks
- **Error Handling**: State error (invalid/unreadable persisted state); structured classification for not-running/stale conditions (not failure); bounded probe timeout prevents unresponsive bridge from blocking

### FR-LAU-005: Persist Runtime State

- **Description**: Persist registered path, process ref, launch timestamp, bridge endpoint summary, status — corruption-safe
- **Input**: Runtime state to persist
- **Output**: Persistence result (success, reconciliation warnings)
- **Rules**: Persisted: executable ref, process ref + launch timestamp, bridge endpoint summary, last known status. Location from config/workspace, never invented. Atomic/crash-safe writes. Reads validate structure before use. Corrupt/unreadable/malformed → empty state with warning, never crash. Stale process ref at startup → reconciled via liveness verification. No secrets/auth material/credentials. Failures degrade gracefully with warning, continue in-memory. Format tolerant of future fields. Concurrent access safe within single instance.
- **Edge Cases**: Corrupt content, missing file, partial write after crash, permission denied, disk full, stale ref after reboot, PID reuse after restart, concurrent access, outdated schema, location moved/removed
- **Error Handling**: State error → empty-state fallback + warning; corruption/reconciliation/persistence warning emitted; continues in-memory when persistence unavailable

## Error Categories

- blender process not running — expected but not found
- state error — invalid/corrupt/conflicting runtime state
- configuration error — path not configured/locatable/invalid
- timeout error — launch readiness or shutdown timeout
- launch error — could not spawn or exited during startup
- validation error — failed authenticity/permission/version checks
- termination error — force termination attempted but failed

## Events

- application started (launched + readiness confirmed)
- application launch failed (categorized reason)
- application stopped (termination method recorded)
- shutdown escalation (graceful → force)
- runtime status checked (state classification)
- stale state detected (reconciled against liveness)
- executable registered (located, validated, registered)

Payloads: category, state before/after, process ref summary, termination/launch method, duration, redacted reason. Never: auth material, bridge secrets, full process env, sensitive filesystem details.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| blender_executable_path | Registered validated runtime | Resolved via discovery |
| executable_search_locations | Platform-standard installation roots | Platform-appropriate |
| supported_version_range | Compatibility range | Current + previous major |
| launch_timeout | Wait for spawn + bridge readiness | Conservative |
| shutdown_timeout | Wait before force escalation | Conservative |
| force_termination_enabled | May escalate to force | Enabled |
| readiness_probe_interval | Frequency during launch wait | Short |
| state_persistence_location | Where runtime state stored | Derived from workspace |
| default_launch_mode | interface/headless | interface |
| stale_reconciliation_enabled | Auto-correct stale state at startup | Enabled |

## QA Checklist

- [ ] Discovery: explicit→registered→env→platform→PATH (deterministic)
- [ ] Non-Blender executable rejected; version range enforced
- [ ] Stale path re-validated before use
- [ ] Launched with integration active; bridge settings passed without leaks
- [ ] Distinguishes spawned from ready; waits within timeout
- [ ] Early exit → exit reason surfaced
- [ ] Duplicate launch → existing state returned
- [ ] Graceful shutdown within timeout; unresponsive → force if enabled
- [ ] Force verified by liveness; absent process → success with not-running
- [ ] Shutdown during launch → deterministic resolution
- [ ] Status verifies actual liveness (not just persisted state)
- [ ] Classification: not running/starting/running+ready/unresponsive/stopping/stale
- [ ] PID reuse guard prevents false alive; read-only except stale reconciliation
- [ ] Bounded probe against unresponsive bridge
- [ ] State persisted: path, ref, timestamp, endpoint, status
- [ ] Atomic crash-safe writes; corrupt → empty state + warning (never crash)
- [ ] Missing state → graceful; secrets never persisted
- [ ] Failure → in-memory fallback with warning
- [ ] All lifecycle events emitted
