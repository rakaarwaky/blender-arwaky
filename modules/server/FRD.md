# FRD — Server Feature Module

## System Overview

The server module manages TCP socket communication between the MCP server and the Blender addon. It handles connection lifecycle, code execution, and Blender-side operations. This module is the bridge between the AI agent layer and the Blender runtime.

## Functional Requirements

### FR-SRV-001: Manage Blender Socket Connection

- **Description**: Establish and maintain TCP socket connection to Blender addon
- **Input**: Host, port configuration
- **Output**: Active socket connection
- **Business Rules**: Auto-reconnect on failure; timeout after 30 seconds
- **Edge Cases**: Blender not running, connection refused, timeout, network error
- **Error Handling**: BlenderConnectionFailure with retry logic

### FR-SRV-002: Execute Blender Code

- **Description**: Send Python code to Blender for execution via TCP socket
- **Input**: Prompt (Python code string)
- **Output**: Execution result from Blender
- **Business Rules**: Code validated against blocked patterns; 30-second timeout
- **Edge Cases**: Code execution timeout, syntax error, Blender exception
- **Error Handling**: ExecutionError with error details from Blender

### FR-SRV-003: Send Blender Commands

- **Description**: Dispatch named commands to Blender addon
- **Input**: ActionName, command arguments
- **Output**: Command result dictionary
- **Business Rules**: Commands routed through TCP socket; response parsed as JSON
- **Edge Cases**: Unknown command, invalid arguments, Blender not responding
- **Error Handling**: ProviderError with command-specific error message

### FR-SRV-004: Connection Factory

- **Description**: Create new Blender connection instances
- **Input**: Connection configuration
- **Output**: BlenderConnectionPort instance
- **Business Rules**: Supports multiple connection strategies (socket, stdio)
- **Edge Cases**: Invalid configuration, unsupported transport
- **Error Handling**: ConnectionError for factory failures

### FR-SRV-005: Socket Adapter Surface

- **Description**: Surface layer for Blender socket operations
- **Input**: MCP tool calls
- **Output**: Delegated to Blender via connection
- **Business Rules**: Thin wrapper; no business logic in surface
- **Edge Cases**: Connection lost during operation
- **Error Handling**: Delegates to connection error handling

## API Contract

| Operation | Input | Output | Description |
|-----------|-------|--------|-------------|
| `send_command` | ActionName, dict | dict | Send command to Blender |
| `execute_blender_code` | Prompt | result | Execute Python code in Blender |
| `connect` | host, port | connection | Establish TCP connection |
| `disconnect` | — | — | Close TCP connection |

## Integration Points

- **Internal**: shared (taxonomy, contracts), config (server settings)
- **External**: Blender addon (TCP socket), Blender Python API (bpy)

## Non-functional Requirements

- Performance: Command response within 5 seconds
- Reliability: Auto-reconnect on connection loss (3 attempts)
- Security: Code execution validates against blocked patterns

## Test Scenarios / QA Checklist

- [ ] Connect to running Blender instance succeeds
- [ ] Connect to non-running Blender returns BlenderConnectionFailure
- [ ] Execute valid Python code returns result
- [ ] Execute code with syntax error returns ExecutionError
- [ ] Execute code exceeding timeout returns timeout error
- [ ] Send command to Blender returns response
- [ ] Connection loss triggers auto-reconnect
- [ ] Factory creates connection with valid config

## Assumptions & Constraints

- Blender addon must be running and listening on TCP socket
- Single connection per server instance
- Code execution has 30-second timeout

## Glossary

- **BlenderConnectionPort**: Contract for Blender TCP communication
- **CodeExecutionPort**: Contract for Python code execution in Blender
- **SocketAdapter**: Surface layer for Blender socket operations

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
