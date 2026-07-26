# FRD — MCP Surface

## Purpose

Provides MCP tools for AI clients. Surface only — no business logic.

## Scope

- MCP service lifecycle
- Tool schema exposure
- MCP protocol compliance
- Tool input parsing
- Tool output serialization
- Error formatting per MCP spec

## Out of Scope

- 3D execution logic (owner: `dispatcher` + domain features)
- Command catalog logic (owner: `dispatcher`)
- Health computation (owner: `diagnostics`)
- Config loading (owner: `config`)
- Task lifecycle (owner: `job`)
- Connection logic (owner: `gateway`)

## Depends On

- `dispatcher`
- `diagnostics`
- `config`
- `job`
- `security`

## Provides To

AI clients (MCP protocol).

## Functional Requirements

### FR-MCP-001: Expose MCP Tools

MCP displays tool schemas. Tool schemas retrieved from dispatcher, config, diagnostics, job.

### FR-MCP-002: Route Tool Calls

MCP forwards tool call to same aggregates as CLI.

### FR-MCP-003: Format MCP Responses

MCP returns structured response. MCP includes tracking_id. MCP does not carry oversized payloads.

## Tool Mapping

| MCP Tool             | Target Feature      |
| -------------------- | ------------------- |
| `execute_command`    | `dispatcher`        |
| `list_commands`      | `dispatcher`        |
| `health_check`       | `diagnostics`       |
| `get_config`         | `config`            |
| `read_skill_context` | static docs surface |
| `get_task_status`    | `job`               |
| `cancel_task`        | `job`               |

## Error Categories

- `ValidationError` — invalid tool input (surface-level)
- `UnsupportedError` — unknown tool name

## Events

None (surface layer does not emit domain events).

## Configuration Keys

- `mcp.server_name` — MCP server name
- `mcp.max_payload` — max response payload size

## QA Checklist

- [ ] Tool schemas exposed correctly
- [ ] Tool calls routed to correct aggregate
- [ ] Responses structured per MCP spec
- [ ] Tracking ID included in all responses
- [ ] Payload size limit enforced
- [ ] 1:1 parity with CLI (both use same aggregates)
- [ ] No business logic in MCP layer
