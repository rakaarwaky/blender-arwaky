# FRD — MCP Surface

## System Overview
The MCP Surface provides Model Context Protocol tools for AI clients. It is the machine-facing counterpart of the CLI surface, routing tool calls to the same aggregates CLI uses. It contains zero business logic and strictly adheres to MCP protocol specifications.

## Functional Requirements

### FR-001: Expose MCP Tools and Route Calls
- **Description**: Publish tool schemas derived from the dispatcher catalog and route incoming tool calls to the correct aggregate.
- **Input**: Tool discovery request, Tool call (name, structured payload, session context).
- **Output**: Tool schema list, Aggregate call dispatched with tracking ID.
- **Business Rules**: Five stable MCP tools exposed: `execute_command`, `list_commands`, `health_check`, `get_config`, `help`. Feature actions executed via `execute_command`. Surface validates shape only. Unknown tools return `unsupported`.
- **Edge Cases**: Empty catalog; degraded owning feature; malformed payload; unknown extra fields; oversized input.
- **Error Handling**: `unsupported` for incompatible protocol/unknown tools; `validation_error` for malformed input; upstream errors passed through.

### FR-002: Format MCP Responses
- **Description**: Serialize aggregate outcomes into MCP-compliant structured responses.
- **Input**: Aggregate result/error + tracking ID.
- **Output**: MCP response (structured content, tracking ID, protocol-compliant status).
- **Business Rules**: Every response structured per MCP spec. Tracking ID in every response. Payload size bounded; oversized outcomes summarized, substituted, or truncated. Secrets masked via `security`.
- **Edge Cases**: Oversized payload; binary content; non-serializable value; masking failure.
- **Error Handling**: Serialization failure falls back to safe summarized envelope; masking failure suppresses fragment.

## API Contract

| Operation | Input | Output | Description |
|---|---|---|---|
| `execute_command` | `action`, `args` | `MCPResponse` | Universal action executor |
| `list_commands` | `domain`, `format` | `MCPResponse` | Discover available actions |
| `health_check` | None | `MCPResponse` | Verify system health |
| `get_config` | `key` | `MCPResponse` | Retrieve configuration |
| `help` | `topic` | `MCPResponse` | Embedded documentation |

## Integration Points

- **3rd Party**: AI Clients (via Model Context Protocol).
- **Internal**: `dispatcher` (catalog/routing), `diagnostics` (health), `config` (settings), `security` (redaction).

## Non-functional Requirements (Detailed)

- **Performance**: Schema assembly from in-memory catalog. Concurrent calls accepted; serialization delegated to Gateway.
- **Security**: Secrets/tokens/credentials masked in every response path. Oversized input rejected before routing.
- **Scalability**: Client disconnect mid-call doesn't cancel aggregate execution. Binary content returned as bounded excerpt or reference.

## Test Scenarios / QA Checklist

- [ ] Verify tool schemas include names, descriptions, param schemas, and catalog version.
- [ ] Verify degraded features are indicated in schema, not hidden.
- [ ] Verify unknown tool returns `unsupported` error per MCP spec.
- [ ] Verify tracking ID is injected and present in all responses.
- [ ] Verify 1:1 parity with CLI (same aggregates, same semantics).

## Assumptions & Constraints

- MCP Surface contains zero business logic (no retries, composition, or reinterpretation).
- Help content is embedded in source code and does not read filesystem files at runtime.

## Glossary

- **MCP (Model Context Protocol)**: Standardized protocol for AI agents to interact with external tools.
- **MCPResponse**: Protocol-compliant structured response containing content, tracking ID, and status.
- **UnifiedEnvelope**: The internal standardized wrapper that MCPResponse wraps for transport.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: `dispatcher`, `diagnostics`, `config`, `job`, `security`
