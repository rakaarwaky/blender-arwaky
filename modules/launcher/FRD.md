# FRD — Blender Runtime Launcher Feature

## Purpose

Manages Blender process lifecycle: locate, launch, shutdown, status, and runtime state persistence.

## Scope

- Locate Blender executable
- Register Blender path
- Launch Blender with integration component
- Graceful shutdown
- Force shutdown fallback
- Process status
- Runtime state persistence

## Out of Scope

- 3D scene actions
- Command catalog
- MCP protocol
- CLI formatting
- Blender socket connection
- Background task
- Telemetry

## Depends On

- `config`
- `diagnostics` (health composition)

## Provides To

- `cli`
- `mcp`
- `diagnostics`

## Functional Requirements

### FR-LAU-001: Locate and Register Application

Launcher searches for Blender executable. Launcher validates executable. Launcher stores path via config or state store.

### FR-LAU-002: Launch Application

Launcher starts Blender. Launcher ensures integration component is active. Launcher waits for Blender to be ready.

### FR-LAU-003: Shut Down Application

Launcher performs graceful shutdown. If unresponsive, launcher force terminates.

### FR-LAU-004: Check Runtime Status

Launcher checks whether process is actually alive. Launcher detects stale state.

### FR-LAU-005: Persist Runtime State

Launcher stores path and running status. State corruption must not crash the application.

## Error Categories

- `BlenderProcessNotRunningError` — Blender process not found
- `StateError` — invalid runtime state
- `ConfigurationError` — Blender path not configured
- `TimeoutError` — launch/shutdown timeout

## Events

- `launcher.started` — Blender process launched
- `launcher.stopped` — Blender process shutdown
- `launcher.status` — runtime status checked

## Configuration Keys

- `launcher.blender_path` — path to Blender executable
- `launcher.launch_timeout` — max wait for Blender to start
- `launcher.shutdown_timeout` — max wait for graceful shutdown

## QA Checklist

- [ ] Blender located and validated
- [ ] Blender launched with integration component active
- [ ] Graceful shutdown with force fallback
- [ ] Stale state detection
- [ ] Runtime state persisted and corruption-safe
