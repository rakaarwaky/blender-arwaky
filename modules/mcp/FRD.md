# FRD — MCP Surface

## Purpose

MCP tools for AI clients. Machine-facing counterpart of CLI surface. Routes tool calls to the same aggregates CLI uses. Surface only — zero business logic.

## Scope

- MCP service lifecycle (init, protocol negotiation, shutdown)
- Tool schema exposure from dispatcher catalog + owning feature shapes
- MCP protocol compliance (messages, tool calls, errors)
- Tool input parsing + surface-level shape validation
- Tool output serialization (bounded, agent-parseable)
- Error formatting per MCP spec with unified categories
- Tracking ID injection + propagation on every call
- Oversized payload protection (summarize / reference / truncate)
- Skill context exposure as versioned static docs
- Degraded capability indication in tool metadata

## Out of Scope

3D execution logic, command catalog logic, health computation, config loading, task lifecycle, connection logic, agent-side prompting/strategy, streaming/push updates, multi-tenant auth.

## Depends On

dispatcher (catalog, validation, routing, normalized results), diagnostics (health snapshots, lifecycle logging), config (settings, surface preferences), job (task status, cancellation), security policy (redaction on all responses).

## Provides To

AI clients via MCP protocol.

## Functional Requirements

### FR-MCP-001: Expose MCP Tools

Publish tool schemas derived from dispatcher catalog + owning feature shapes. Dispatcher catalog = single source of truth for action semantics.

- **Input**: Tool discovery request from MCP client (negotiated session)
- **Output**: Tool schema list (names, AI-readable descriptions, param schemas, examples, capability indicators, catalog version)
- **Business Rules**:
  - Schemas assembled from owning features: action tools from dispatcher catalog, settings from config, health from diagnostics, task tools from job, skill context from static docs
  - Descriptions for AI consumption: precise capability statements, parameter meanings, units, ≥1 usage example per tool
  - Schema output carries catalog version for drift detection
  - Degraded owning features: tool listed with explicit degraded indicator, not hidden
  - No secrets, credential placeholders, or environment paths in schemas
  - Schema assembly from in-memory catalog — no domain execution triggered
  - Incompatible client protocol version → rejected with unsupported error
  - Deterministic output: identical catalog → identical schemas across sessions
- **Edge Cases**: Empty catalog, catalog version drift, degraded owning feature, oversized schema for client limits, schema during hot re-registration, missing skill docs, client reconnecting with stale catalog
- **Error Handling**: Unsupported error for incompatible protocol version; state error when catalog unreadable; degraded tools surfaced with indicator; missing docs → unavailable indication

### FR-MCP-002: Route Tool Calls

Parse incoming tool call, validate surface shape, route to same aggregate as CLI.

- **Input**: Tool call (tool name, structured payload, session context)
- **Output**: Aggregate call dispatched with tracking ID
- **Business Rules**:
  - Every tool routes to same aggregate as equivalent CLI command — divergence = defect
  - Direct mapping: no retries, no reordering, no multi-aggregate composition, no result reinterpretation
  - Surface validates shape only: tool recognized, payload parses, required fields present, field shapes match schema
  - Semantic validation → dispatcher + owning features
  - Unknown tool → unsupported error per MCP spec
  - Malformed input → validation error with field-level detail
  - Unknown extra fields: strict mode → reject; tolerant mode → ignore with warning
  - Tracking ID generated when client omits; propagated through aggregate, result, logs
  - Concurrent calls accepted; serialization of Blender mutations owned by gateway queue
  - Surface is stateless across calls
  - Client disconnect mid-call doesn't cancel aggregate; result handling follows owning feature policy
  - Oversized input rejected at surface
- **Edge Cases**: Unknown tool, malformed payload, missing required field, wrong field shape, unknown extra field, oversized input, concurrent calls from one client, call during catalog hot-reload, client disconnect mid-call, tracking ID collision, degraded owning feature at route time
- **Error Handling**: Validation error before routing; unsupported for unknown tools; upstream errors passed through in categorized form; routing never converts failure to success

### FR-MCP-003: Format MCP Responses

Serialize aggregate outcomes into MCP-compliant structured responses.

- **Input**: Aggregate result/error + tracking ID
- **Output**: MCP response (structured content, tracking ID, protocol-compliant status)
- **Business Rules**:
  - Every response structured per MCP spec; no free-text-only responses for tool calls
  - Tracking ID in every response (success + failure)
  - Response shape = unified result envelope: success indicator, data, error category, message, warnings, metadata
  - Payload size bounded by configured max; oversized outcomes never transmit raw
  - Oversized strategy: summarize (counts + excerpt), substitute (artifact/task ref), or truncate (with indicator)
  - Binary content (e.g. images) → reference or bounded encoded excerpt, never unbounded inline
  - Non-serializable values → safe textual representation
  - Secrets/tokens/credentials/code/paths masked via security policy before any response leaves
  - Warnings preserved alongside results
  - Response shape stable across versions within protocol version; additive fields OK, silent reshaping not
  - Masking/serialization failure → suppress affected fragment, never expose or crash
- **Edge Cases**: Oversized payload, non-serializable value, binary content, error without category, success with warnings, client protocol version constraining shape, masking failure, truncation boundary splitting structured content, artifact ref pointing at expired task
- **Error Handling**: Serialization failure → safe summarized envelope; masking failure → redaction marker; total response failure → protocol-level error envelope with tracking ID

## Tool Mapping

| MCP Tool | Target Feature |
|---|---|
| execute_command | dispatcher feature |
| list_commands | dispatcher feature |
| health_check | diagnostics feature |
| get_config | config feature |
| read_skill_context | static documentation surface |
| get_task_status | job feature |
| cancel_task | job feature |

Mapping rules: 1 tool = 1 aggregate. Semantics identical to CLI counterparts — divergence = defect. New capabilities reachable via catalog registration alone, no surface code changes.

## Error Categories

- **Owned**: validation error (surface-level input: malformed payload, missing field, wrong shape, oversized), unsupported error (unknown tool, incompatible protocol)
- **Displayed but unowned**: not_found, capacity, timeout, execution, security_violation, connection, state, task — pass through from owning features with MCP formatting, no renaming/reinterpretation

## Events

None. Session lifecycle and tool calls appear in structured logs via diagnostics logging policy.

## Configuration Keys

| Key | Description | Default |
|---|---|---|
| server_identity | Name + version advertised at init | Product name + semver |
| max_response_payload | Upper bound before oversized strategy | Conservative |
| protocol_version | Negotiated at handshake | Current |
| input_strictness | strict/tolerant for unknown fields | strict |
| oversized_strategy | summarize/substitute/truncate | substitute |
| skill_context_version | Static docs version | Release version |
| tracking_id_injection | Generate when client omits | enabled |
| schema_detail | Depth of examples + metadata in schemas | full |

## QA Checklist

- [ ] Tool schemas exposed with names, descriptions, param schemas, examples
- [ ] Schema content from dispatcher catalog + owning features, never redefined at surface
- [ ] Deterministic schema output for identical catalog
- [ ] Catalog version in schema output
- [ ] Degraded features indicated, not hidden
- [ ] Protocol negotiation rejects incompatible versions
- [ ] Calls accepted only after init completes
- [ ] Tool calls route to correct aggregate, identical semantics to CLI
- [ ] Unknown tool → unsupported error
- [ ] Malformed input → validation error with field detail
- [ ] Unknown extra fields handled per strict/tolerant policy
- [ ] Oversized input rejected before routing
- [ ] Tracking ID in all responses
- [ ] Responses structured per MCP spec with unified envelope
- [ ] Payload size enforced (summarize/substitute/truncate)
- [ ] Binary content as ref or bounded excerpt
- [ ] Non-serializable values → safe text
- [ ] Errors: MCP-spec format, unified category, actionable message
- [ ] Secrets masked in every response path
- [ ] Masking failure → suppress fragment, not expose
- [ ] Warnings preserved alongside results
- [ ] Concurrent calls accepted; mutation serialization delegated to gateway
- [ ] Client disconnect doesn't corrupt execution
- [ ] Skill context: versioned static docs, no live state access
- [ ] 1:1 parity with CLI verified — same aggregates, same semantics
- [ ] No business logic in MCP layer — no retries, composition, reinterpretation
- [ ] New catalog capability reachable via schema exposure, no surface code changes
