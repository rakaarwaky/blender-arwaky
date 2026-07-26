# FRD — Blender Runtime Launcher Feature

## Purpose

Manages the Blender process lifecycle for **blender-arwaky**: locate, launch, shutdown, status, and runtime state persistence.

This feature is the single authority for operating on the Blender process itself. It finds and validates the Blender executable, starts Blender with the integration component active, confirms readiness, shuts the process down safely with escalation, verifies true liveness rather than assumed state, and persists runtime state in a corruption-safe way.

Other features may consume launcher state for health composition or user-facing control, but they never spawn, terminate, or validate the Blender process directly.

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

- 3D scene actions
- Command catalog
- MCP protocol behavior
- CLI formatting
- Blender socket connection and message transport, owned by gateway feature
- Background task lifecycle
- Telemetry
- Asset, render, object, or scene operations
- Blender file saving or scene persistence
- Multi-instance orchestration

## Depends On

- config feature for executable path, timeout, search locations, and persistence location settings
- security policy feature for safe handling of authentication material passed to the integration component
- diagnostics feature for health composition

## Provides To

- cli feature
- mcp layer
- diagnostics feature
- gateway feature, which consumes readiness and endpoint state before transport

## Functional Requirements

### FR-LAU-001: Locate and Register Application

Launcher searches for Blender executable. Launcher validates executable. Launcher stores path via config or state store.

- **Description**: Discover a usable Blender executable, validate it, and register its location as the authoritative runtime path
- **Input**: Optional explicit executable location override, otherwise search signals from configuration, environment, and platform-standard locations
- **Output**: Registration result concept containing validated executable reference, detected version summary, and registration source
- **Business Rules**:
  - Discovery follows deterministic order:
    1. Explicit override provided at runtime
    2. Registered path from configuration or state store
    3. Environment-provided location signal
    4. Platform-standard installation locations
    5. System executable search path
  - Candidate executable must exist and be executable by current user
  - Candidate must be validated as a genuine Blender runtime, not an unrelated executable
  - Detected version should be compared against supported compatibility range
  - Version outside supported range produces warning or rejection according to configured policy
  - Successful validation registers the path through config or state store
  - Registration must record source of discovery for diagnostics
  - Previously registered path must be re-validated before use when staleness is suspected
  - Multiple valid candidates resolve to first candidate in deterministic order
  - Discovery result should distinguish between configured, discovered, and overridden path sources
  - Executable reference must be normalized and symlink-safe
  - Registration must not store secrets or authentication material
- **Edge Cases**: Executable not found, multiple candidates, invalid executable, non-Blender executable with matching name, unsupported version, permission denied, symlinked executable, network-mounted installation, stale registered path, case-insensitive filesystem, platform-specific launcher wrapper, relocated installation
- **Error Handling**: Configuration error when no valid executable can be located or registered; validation error when candidate fails executable or authenticity checks; version compatibility warning when detected version is outside supported range

### FR-LAU-002: Launch Application

Launcher starts Blender. Launcher ensures integration component is active. Launcher waits for Blender to be ready.

- **Description**: Start the Blender process with the integration component active and confirm readiness before reporting success
- **Input**: Launch request concept containing optional mode preference such as interface or headless, bridge endpoint settings reference, and readiness timeout
- **Output**: Launch result concept containing success indicator, process reference, readiness state, bridge endpoint summary, and launch duration
- **Business Rules**:
  - Launch must use registered and validated executable path
  - Launch must activate the integration component during startup through supported startup mechanism
  - Launch must pass bridge endpoint settings and protocol information to the integration component
  - Authentication material required by the bridge must be handled through security policy guidance and never logged
  - Launch must be idempotent when a verified running instance already exists
  - Duplicate launch attempts against a live instance return existing runtime state instead of spawning a second process
  - Launcher must distinguish between process spawned and integration component ready
  - Readiness is confirmed only when process liveness and bridge readiness signal are both satisfied
  - Launcher waits for readiness within configured launch timeout
  - Process alive without bridge readiness within timeout is treated as launch failure or degraded state according to policy
  - Launch must not block indefinitely when the process exits during startup
  - Early process exit must surface exit reason summary when available
  - Launch mode preference may be honored where supported by platform and Blender runtime
  - Launch must emit lifecycle event after readiness confirmation or failure
- **Edge Cases**: Already running instance, bridge endpoint conflict, crash during startup, process exits immediately, readiness signal missed, launch timeout exceeded, missing executable at launch time, integration component fails to activate, insufficient system resources, permission denied during spawn, stale process reference from previous session, headless mode unsupported on platform
- **Error Handling**: Timeout error when readiness not confirmed within launch timeout; configuration error when executable path missing or invalid; launch error when process cannot be spawned; state error when runtime state conflicts with launch request

### FR-LAU-003: Shut Down Application

Launcher performs graceful shutdown. If unresponsive, launcher force terminates.

- **Description**: Stop the Blender process using graceful shutdown first, escalating to force termination when the process does not exit in time
- **Input**: Shutdown request concept containing optional force preference and confirmation flag for escalation
- **Output**: Shutdown result concept containing success indicator, termination method used, shutdown duration, and final process state
- **Business Rules**:
  - Graceful shutdown is attempted first through integration component shutdown channel or supported process signal
  - Launcher waits for process exit within configured shutdown timeout
  - If process does not exit within timeout, launcher escalates to force termination when policy allows
  - Force termination must be confirmed by subsequent liveness verification
  - Shutdown must be idempotent when process is already absent
  - Shutdown of absent process returns success with not-running indication rather than failure
  - Shutdown must update persisted runtime state to stopped
  - Shutdown must not modify or save Blender scene content unless explicitly requested by higher-level policy
  - Escalation to force termination should emit observability event
  - Shutdown during active launch sequence must resolve launch state deterministically before completing
  - Orphaned child processes directly spawned by launcher should be cleaned up where detectable and safe
  - Termination method must be reported for diagnostics
- **Edge Cases**: Process not running, process unresponsive to graceful shutdown, force termination also fails, partial termination with lingering child processes, shutdown during launch, shutdown requested concurrently, permission denied for process termination, process already exiting, stale process reference, unsaved work present
- **Error Handling**: Blender process not running error when shutdown targets unknown process and strict mode is enabled; timeout error when graceful shutdown exceeds timeout and force escalation is disallowed; state error when persisted state conflicts with observed process state

### FR-LAU-004: Check Runtime Status

Launcher checks whether process is actually alive. Launcher detects stale state.

- **Description**: Verify true runtime status by inspecting actual process liveness and integration component responsiveness, not only persisted state
- **Input**: Optional depth preference for lightweight liveness check or full readiness check
- **Output**: Runtime status concept containing state classification, process reference summary, readiness indicator, staleness indicator, and uptime summary when known
- **Business Rules**:
  - Status check must verify actual process liveness through operating system signals rather than trusting persisted state alone
  - Status check should classify runtime state as one of:
    - not running
    - starting
    - running and ready
    - running but unresponsive
    - stopping
    - stale
  - Process alive but bridge unresponsive is classified as unresponsive or stale according to configured threshold
  - Persisted process reference that no longer matches a live process is classified as stale
  - Stale detection must guard against process identifier reuse by unrelated processes
  - Status check must be read-only and must not mutate process or persisted state except stale-state reconciliation
  - Stale state reconciliation may correct persisted state and emit observability event
  - Lightweight check should avoid bridge round-trip; full readiness check may include bridge liveness exchange
  - Status result must be safe for health composition and user-facing diagnostics
  - Status check must complete quickly and must not block on unresponsive bridge beyond bounded probe timeout
- **Edge Cases**: Process identifier reuse, process alive but bridge dead, bridge responsive but persisted record missing, zombie process, status requested during launch transition, status requested during shutdown transition, clock skew affecting uptime, permission denied reading process information, concurrent status checks
- **Error Handling**: State error when persisted runtime state is invalid or unreadable; status result returns structured classification rather than failure for not-running and stale conditions; bounded probe timeout prevents unresponsive bridge from blocking status

### FR-LAU-005: Persist Runtime State

Launcher stores path and running status. State corruption must not crash the application.

- **Description**: Persist runtime state such as registered path, process reference, launch timestamp, bridge endpoint summary, and status, with corruption-safe read and write behavior
- **Input**: Runtime state concept to persist
- **Output**: Persistence result concept containing success indicator and reconciliation warnings
- **Business Rules**:
  - Persisted runtime state should include:
    - registered executable reference
    - process reference and launch timestamp
    - bridge endpoint summary
    - last known status classification
  - Persistence location must be derived from configuration or resolved workspace, never invented by launcher
  - State writes must be atomic or crash-safe so partial writes do not produce corrupt state
  - State reads must validate structure before use
  - Corrupt, unreadable, or malformed state must be treated as empty state with warning, never as application crash
  - Stale process reference detected at application startup must be reconciled through liveness verification
  - Persisted state must not contain secrets, authentication material, or raw credential values
  - Persistence failures must degrade gracefully with warning while launcher continues operating in-memory
  - State format should remain tolerant of future fields without breaking older readers
  - Concurrent access to persisted state must be safe within a single application instance
- **Edge Cases**: Corrupt state content, missing state file, partial write after crash, permission denied persistence location, disk full, stale process reference after system reboot, process identifier reuse after restart, concurrent state access, outdated state schema, persistence location moved or removed
- **Error Handling**: State error for invalid runtime state, recovered through empty-state fallback; warning emitted for corruption, reconciliation, and persistence failure; launcher continues operating with in-memory state when persistence is unavailable

## Error Categories

- blender process not running error — Blender process expected by operation but not found
- state error — invalid, corrupt, or conflicting runtime state
- configuration error — Blender path not configured, not locatable, or invalid
- timeout error — launch readiness timeout or shutdown timeout exceeded
- launch error — process could not be spawned or exited during startup
- validation error — candidate executable failed authenticity, permission, or version checks
- termination error — force termination attempted but process could not be stopped

## Events

- application started event — Blender process launched and readiness confirmed
- application launch failed event — launch attempt failed with categorized reason
- application stopped event — Blender process shut down and termination method recorded
- shutdown escalation event — graceful shutdown escalated to force termination
- runtime status checked event — status verification completed with state classification
- stale state detected event — persisted state reconciled against actual liveness
- executable registered event — Blender executable located, validated, and registered

Event payloads should include:

- event category
- state classification before and after transition
- process reference summary
- termination or launch method when applicable
- duration metadata
- redacted reason summary

Event payloads must avoid:

- authentication material
- bridge secrets
- full process environment content
- sensitive filesystem details beyond redacted executable reference

## Configuration Keys


| Configuration Concept        | Description                                                         | Typical Default                                                     |
| ------------------------------ | --------------------------------------------------------------------- | --------------------------------------------------------------------- |
| Blender executable path      | Registered location of validated Blender runtime                    | Resolved through discovery order                                    |
| Executable search locations  | Platform-standard locations consulted during discovery              | Platform-appropriate installation roots                             |
| Supported version range      | Blender version compatibility range for validation                  | Current and previous major supported releases                       |
| Launch timeout               | Maximum wait for process spawn plus bridge readiness                | Conservative startup limit                                          |
| Shutdown timeout             | Maximum wait for graceful shutdown before escalation                | Conservative shutdown limit                                         |
| Force termination enabled    | Whether shutdown may escalate to force termination                  | Enabled                                                             |
| Readiness probe interval     | Frequency of readiness checks during launch wait                    | Short probe interval                                                |
| State persistence location   | Where runtime state is stored                                       | Derived from resolved workspace or platform-standard state location |
| Default launch mode          | Interface or headless preference when supported                     | Interface mode                                                      |
| Stale reconciliation enabled | Whether stale persisted state is corrected automatically at startup | Enabled                                                             |

## QA Checklist

- [ ]  Blender located through explicit override
- [ ]  Blender located through registered path
- [ ]  Blender located through environment signal
- [ ]  Blender located through platform-standard locations
- [ ]  Blender located through system executable search path
- [ ]  Discovery order is deterministic across runs
- [ ]  Non-Blender executable with matching name is rejected
- [ ]  Executable validated for existence, permissions, and authenticity
- [ ]  Unsupported version produces warning or rejection according to policy
- [ ]  Registered path stored via config or state store
- [ ]  Stale registered path re-validated before use
- [ ]  Blender launched with integration component active
- [ ]  Launch passes bridge endpoint settings without leaking secrets
- [ ]  Launch distinguishes process spawned from bridge ready
- [ ]  Launch waits for readiness within configured timeout
- [ ]  Launch timeout produces timeout error with reason summary
- [ ]  Early process exit surfaces exit reason summary
- [ ]  Duplicate launch against live instance returns existing runtime state
- [ ]  Graceful shutdown completes within shutdown timeout
- [ ]  Unresponsive process escalates to force termination when enabled
- [ ]  Force termination verified through liveness check
- [ ]  Shutdown of absent process returns success with not-running indication
- [ ]  Shutdown during launch resolves launch state deterministically
- [ ]  Shutdown updates persisted runtime state to stopped
- [ ]  Shutdown escalation emits observability event
- [ ]  Status check verifies actual process liveness, not persisted state alone
- [ ]  Status classifies running and ready correctly
- [ ]  Status classifies running but unresponsive correctly
- [ ]  Status classifies stale state correctly
- [ ]  Process identifier reuse does not produce false alive result
- [ ]  Status check remains read-only except stale reconciliation
- [ ]  Status check bounded against unresponsive bridge
- [ ]  Runtime state persisted with registered path and running status
- [ ]  State write is atomic or crash-safe
- [ ]  Corrupt state falls back to empty state without crash
- [ ]  Missing state handled gracefully
- [ ]  Stale process reference reconciled at application startup
- [ ]  Persisted state contains no secrets or authentication material
- [ ]  Persistence failure degrades to in-memory operation with warning
- [ ]  Lifecycle events emitted for start, stop, escalation, and stale reconciliation
