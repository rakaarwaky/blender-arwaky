# FRD — cli (CLI Feature Module)

## System Overview

The CLI module provides a standalone command-line interface for managing Blender instances outside the MCP server context. It is fully independent of the AES architecture — no dependency on taxonomy, contracts, or other layers.

```
modules/cli/
├── cli_main.py            ← Argparse entry point
├── cli_commands.py        ← High-level CLI operations
├── cli_blender_manager.py ← Blender process management
├── cli_socket_client.py   ← Raw TCP socket client
├── cli_registry.py        ← Active Blender instance registry
└── __init__.py
```

## Functional Requirements

### FR-001: Initialize Blender Instance

- **Description**: Find and register a Blender executable path
- **Input**: Optional custom path
- **Output**: Registered Blender path in registry.json
- **Business Rules**: Auto-detect Blender on PATH; validate executable exists
- **Edge Cases**: Multiple Blender installations, no Blender found, invalid path
- **Error Handling**: FileNotFoundError for missing Blender

### FR-002: Launch Blender

- **Description**: Start Blender process with TCP server addon
- **Input**: Optional additional Blender arguments
- **Output**: Running Blender process
- **Business Rules**: Auto-start addon; wait for TCP connection ready
- **Edge Cases**: Blender already running, port in use, addon not installed
- **Error Handling**: ProcessError for launch failures

### FR-003: Capture Screenshot

- **Description**: Capture Blender viewport via TCP socket
- **Input**: Optional view angle, shading mode
- **Output**: Screenshot image file
- **Business Rules**: Use TCP socket client; save to specified path
- **Edge Cases**: Blender not running, socket timeout, invalid response
- **Error Handling**: ConnectionError for socket failures

### FR-004: Render Image

- **Description**: Trigger Blender render via TCP socket
- **Input**: Output path, resolution, samples
- **Output**: Rendered image file
- **Business Rules**: Use TCP socket client; wait for render completion
- **Edge Cases**: Render timeout, invalid output path, Blender error
- **Error Handling**: ExecutionError for render failures

### FR-005: Close Blender

- **Description**: Terminate Blender process gracefully
- **Input**: None
- **Output**: Process terminated, registry updated
- **Business Rules**: Send shutdown command before killing process; update registry
- **Edge Cases**: Process already terminated, unresponsive process
- **Error Handling**: ProcessError for termination failures

### FR-006: Check Status

- **Description**: Report status of registered Blender instance
- **Input**: None
- **Output**: Status information (running, PID, port, uptime)
- **Business Rules**: Check process existence; verify socket connectivity
- **Edge Cases**: Process died without cleanup, stale registry entry
- **Error Handling**: StatusError for check failures

### FR-007: Registry Management

- **Description**: Thread-safe singleton managing active Blender instances
- **Input**: Instance registration/deregistration
- **Output**: Updated registry state
- **Business Rules**: Registry persisted to registry.json; thread-safe access
- **Edge Cases**: Corrupted registry file, concurrent access, missing file
- **Error Handling**: RegistryError for persistence failures

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `init` | path (optional) | None | Register Blender path |
| `run` | args (optional) | None | Launch Blender |
| `screenshot` | params | image file | Capture viewport |
| `render` | params | image file | Render scene |
| `close` | None | None | Terminate Blender |
| `status` | None | status dict | Check instance status |

## Integration Points

- **Internal**: None (fully standalone)
- **External**: Blender process (subprocess), Blender addon (TCP socket)

## Non-functional Requirements (Detailed)

- Performance: CLI commands respond within 5 seconds
- Reliability: Graceful handling of Blender crashes
- Security: No arbitrary code execution; only predefined commands

## Test Scenarios / QA Checklist

- [ ] Init with valid path registers Blender
- [ ] Init with missing path raises FileNotFoundError
- [ ] Run starts Blender process successfully
- [ ] Run with Blender already running warns user
- [ ] Screenshot captures viewport image
- [ ] Screenshot with Blender not running raises ConnectionError
- [ ] Render produces image file
- [ ] Close terminates Blender process
- [ ] Status reports running process info
- [ ] Registry persists across CLI invocations

## Assumptions & Constraints

- Blender 3.0+ must be installed
- TCP port 9876 must be available
- CLI is standalone (no dependency on MCP server)

## Glossary

- **Registry**: JSON file tracking active Blender instances
- **SocketClient**: Raw TCP client for Blender addon communication
- **BlenderManager**: Process lifecycle management

## Reference

- PRD: [../../PRD.md](../../PRD.md)
