# FRD — MCP Feature Module

## System Overview

The MCP module is the main entry point for the BlenderArwaky MCP server. It handles MCP protocol communication with AI agents (Claude Desktop, Cursor), registers the 4 core tools, and orchestrates server lifecycle. It delegates all business logic to the agent layer via aggregate contracts.

## Functional Requirements

### FR-MCP-001: Start MCP Server

- **Description**: Initialize and run the MCP server with stdio transport
- **Input**: None (reads config for host/port)
- **Output**: Running MCP server accepting AI agent connections
- **Business Rules**: Sets up logging, loads config, bootstraps DI container
- **Edge Cases**: Config missing, port already in use, Blender not running
- **Error Handling**: Logs startup failure and exits gracefully

### FR-MCP-002: Register Execute Command Tool

- **Description**: Register the universal `execute_command` tool that dispatches any Blender action
- **Input**: ActionName (action identifier), Details (optional args JSON)
- **Output**: Prompt (JSON result from Blender)
- **Business Rules**: Routes through agent layer → CLI → Blender addon; supports 15+ actions
- **Edge Cases**: Unknown action, Blender disconnected, execution timeout
- **Error Handling**: Returns error JSON with descriptive message

### FR-MCP-003: Register List Commands Tool

- **Description**: Register the `list_commands` tool that returns available actions
- **Input**: None
- **Output**: Command catalog with action names, descriptions, and parameters
- **Business Rules**: Returns full catalog from command catalog port
- **Edge Cases**: Catalog empty, catalog not loaded
- **Error Handling**: Returns empty catalog with error message

### FR-MCP-004: Register Read Skill Context Tool

- **Description**: Register the `read_skill_context` tool that serves SKILL.md documentation
- **Input**: SkillName (optional, defaults to root skill)
- **Output**: Skill documentation content
- **Business Rules**: Reads from `.agents/skills/` directory; returns markdown content
- **Edge Cases**: Skill not found, file not readable
- **Error Handling**: Returns error message for missing skill

### FR-MCP-005: Register Health Check Tool

- **Description**: Register the `health_check` tool that reports system status
- **Input**: None
- **Output**: Health status of all subsystems (Blender, providers, config)
- **Business Rules**: Checks TCP connection, config validity, provider availability
- **Edge Cases**: Subsystem degraded, partial failures
- **Error Handling**: Returns degraded status with specific failure details

### FR-MCP-006: Server Lifecycle Management

- **Description**: Handle server startup, shutdown, and signal handling
- **Input**: None
- **Output**: Server instance running until interrupted
- **Business Rules**: Graceful shutdown on SIGINT/SIGTERM; cleanup connections
- **Edge Cases**: Forced shutdown, zombie processes
- **Error Handling**: Timeout on graceful shutdown, force exit after 5s

## API Contract

| Tool | Input | Output | Description |
|------|-------|--------|-------------|
| `execute_command` | ActionName, Details? | Prompt | Universal action executor |
| `list_commands` | — | CommandCatalog | Available actions discovery |
| `read_skill_context` | SkillName? | SkillContent | Documentation reader |
| `health_check` | — | HealthStatus | System diagnostics |

## Integration Points

- **Internal**: shared (taxonomy, contracts, agent layer), config (server settings)
- **External**: MCP clients (Claude Desktop, Cursor), Blender addon (TCP socket)

## Non-functional Requirements

- Performance: Tool response within 5 seconds for standard operations
- Reliability: Server stays running until explicitly stopped
- Compatibility: MCP protocol compliant for any MCP client

## Test Scenarios / QA Checklist

- [ ] Server starts and accepts MCP client connection
- [ ] `execute_command` with valid action returns result JSON
- [ ] `execute_command` with unknown action returns error
- [ ] `list_commands` returns full command catalog
- [ ] `read_skill_context` returns skill documentation
- [ ] `read_skill_context` with missing skill returns error
- [ ] `health_check` returns subsystem status
- [ ] Server handles Blender disconnection gracefully
- [ ] Server shuts down cleanly on SIGINT

## Assumptions & Constraints

- MCP protocol over stdio transport
- Blender addon must be running for command execution
- Single-threaded tool execution (no concurrent Blender commands)

## Glossary

- **MCP**: Model Context Protocol — standard for AI agent tool integration
- **Tool**: MCP-exposed function that AI agents can call
- **Action**: Blender operation dispatched through command catalog

## Reference

- PRD: [../../PRD.md](../../PRD.md)
- FRD shared: [../shared/FRD.md](../shared/FRD.md)
