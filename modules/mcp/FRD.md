# FRD — MCP Surface

## Purpose

Provides MCP tools for AI clients of **blender-arwaky**. Surface only — no business logic.

This feature is the machine-facing counterpart of the CLI surface. Where the CLI translates for human eyes, this feature translates for AI agents: it renders the system's capabilities as precise, discoverable tool schemas, routes tool calls into the exact same aggregates every other surface uses, and returns structured responses an agent can parse without guessing.

The governing discipline is parity. An AI client and a terminal user issue different syntax but exercise identical semantics, because both surfaces are thin projections of the dispatcher catalog and the diagnostics, config, and job features. Nothing an agent can do through this surface exceeds what the catalog declares, and nothing the surface returns invents state the system does not actually have.

## Scope

- MCP service lifecycle: initialization, protocol negotiation, and orderly shutdown
- Tool schema exposure derived from the dispatcher action catalog
- MCP protocol compliance for messages, tool calls, and errors
- Tool input parsing with surface-level shape validation
- Tool output serialization with bounded, agent-parseable payloads
- Error formatting per MCP specification with unified categories
- Tracking identifier injection and propagation on every call
- Oversized payload protection through summarization and reference substitution
- Skill context exposure as versioned static documentation
- Degraded capability indication in tool metadata

## Out of Scope

- 3D execution logic, owned by dispatcher and domain features
- Command catalog logic, owned by dispatcher feature
- Health computation, owned by diagnostics feature
- Config loading, owned by config feature
- Task lifecycle, owned by job feature
- Connection logic, owned by gateway feature
- Agent-side prompting strategy or tool selection behavior
- Streaming or push-based updates to clients
- Multi-tenant isolation and client authentication beyond transport policy

## Depends On

- dispatcher feature for action catalog, validation, routing, and normalized results
- diagnostics feature for health snapshots and lifecycle logging
- config feature for settings display and surface preferences
- job feature for task status and cancellation aggregates
- security policy feature for redaction rules applied to every serialized response

## Provides To

AI clients through the MCP protocol.

## Functional Requirements

### FR-MCP-001: Expose MCP Tools

MCP displays tool schemas. Tool schemas retrieved from dispatcher, config, diagnostics, job.

- **Description**: Publish the system's capabilities as MCP-compliant tool schemas, with the dispatcher action catalog as the single source of truth
- **Input**: Tool discovery request from an MCP client, within a negotiated protocol session
- **Output**: Tool schema list concept containing tool names, AI-readable descriptions, parameter schemas, examples, and capability indicators
- **Business Rules**:
  - The dispatcher action catalog is the only source of action semantics; this feature renders it, never redefines it
  - Tool schemas must be assembled from owning features:
    - action tools from the dispatcher catalog, including parameter schema, defaults, timeout class, and behavioral flags
    - settings tool from the config feature metadata shape
    - health tool from the diagnostics feature snapshot shape
    - task tools from the job feature status and cancellation shapes
    - skill context tool from the versioned static documentation surface
  - Descriptions must be written for AI consumption: precise capability statements, parameter meanings, units, and at least one usage example per tool
  - Schema exposure must be deterministic: identical catalog state produces identical schema output across sessions
  - Schema output carries catalog version so clients can detect capability drift
  - Tools whose owning feature is degraded remain listed with explicit degraded indication rather than disappearing silently
  - Schemas must never embed secrets, credential placeholders, or environment-specific paths
  - Protocol session must negotiate version during initialization; incompatible client protocol versions are rejected with clear unsupported indication
  - Service lifecycle must be orderly: initialization completes before tool calls are accepted, and shutdown stops accepting calls before terminating
  - Schema assembly must complete from in-memory catalog state without triggering domain execution
- **Edge Cases**: Empty catalog at exposure time, catalog version drift between client sessions, client requesting unsupported protocol version, degraded owning feature, oversized schema for clients with tight limits, schema requested mid hot re-registration, static documentation missing for skill context tool, client reconnecting with stale catalog version cached
- **Error Handling**: Unsupported error for incompatible protocol version; state error when catalog cannot be read safely; degraded tools surfaced with indicator rather than failing discovery; missing documentation degrades skill context tool to unavailable indication instead of serving empty content

### FR-MCP-002: Route Tool Calls

MCP forwards tool call to same aggregates as CLI.

- **Description**: Parse incoming tool calls, validate input shape at the surface, and route to the same feature aggregates the CLI surface uses
- **Input**: Tool call concept containing tool name, structured input payload, and client session context
- **Output**: Aggregate call dispatched to the owning feature, with tracking identifier attached
- **Business Rules**:
  - Every tool call routes to the same aggregate the equivalent CLI command uses; surface parity is structural, not aspirational
  - Routing is a direct mapping: no retries, no reordering, no composition of multiple aggregates, no result reinterpretation
  - Input parsing validates surface shape only:
    - tool name recognized
    - payload parses as structured data
    - required fields present
    - field shapes match declared schema
  - Semantic validation belongs to the dispatcher and owning features; the surface never judges whether an action is valid or a state permits it
  - Unknown tool name produces unsupported error per MCP specification
  - Malformed or shape-invalid input produces validation error with field-level detail an agent can act on
  - Unknown extra fields are rejected in strict mode and ignored with warning in tolerant mode, per configuration
  - Tracking identifier is generated when the client does not supply one and propagated through aggregate, result, and logs
  - Concurrent tool calls are accepted; serialization of Blender-mutating work is owned by the gateway queue, not this surface
  - The surface remains stateless across calls except protocol session context; no per-client memory of prior calls influences routing
  - Client disconnect mid-call does not cancel the underlying aggregate; result handling follows owning feature policy
  - Input payload size is bounded; oversized input is rejected at the surface with validation error
- **Edge Cases**: Unknown tool name, malformed input payload, missing required field, wrong field shape, unknown extra field, oversized input payload, concurrent calls from one client, call arriving during catalog hot re-registration, client disconnect mid-call, tracking identifier collision across clients, degraded owning feature at route time
- **Error Handling**: Validation error for surface-level input problems, raised before routing; unsupported error for unknown tools; upstream errors passed through unchanged in categorized form; routing never swallows an aggregate failure or converts it into success

### FR-MCP-003: Format MCP Responses

MCP returns structured response. MCP includes tracking ID. MCP does not carry oversized payloads.

- **Description**: Serialize aggregate outcomes into MCP-compliant structured responses with tracking identifiers, bounded payloads, and categorized errors
- **Input**: Aggregate result or error concept with tracking identifier
- **Output**: MCP response concept containing structured content, tracking identifier, and protocol-compliant status
- **Business Rules**:
  - Every response is structured per MCP specification; free-text-only responses are not produced for tool calls
  - Tracking identifier appears in every response, whether success or failure
  - Response content follows the unified result envelope produced by the dispatcher: success indicator, data, error category, message, warnings, and metadata
  - Payload size is bounded by configured maximum; oversized outcomes never transmit raw
  - Oversized data follows configured strategy:
    - summarize with counts and representative excerpt
    - substitute artifact or task reference for inline content
    - truncate with explicit truncation indicator
  - Binary content such as images is returned as reference or bounded encoded excerpt, never as unbounded inline payload
  - Non-serializable values are converted to safe textual representation before serialization
  - Errors are formatted per MCP specification with unified category, actionable message, and field-level detail when available
  - Secrets, tokens, credentials, raw code, and sensitive paths are masked through security policy rules before any response leaves the surface, in success and failure alike
  - Warning lists accompany results rather than being promoted to failures or dropped
  - Response shape is stable across versions within a protocol version; additive fields are permitted, silent reshaping is not
  - Masking or serialization failure suppresses the affected fragment entirely rather than risking exposure or crashing the response
- **Edge Cases**: Oversized data payload, non-serializable value in result, binary content in response, error without category from upstream, success with warnings, client protocol version constraining response shape, masking failure during serialization, truncation boundary splitting structured content, artifact reference pointing at expired task
- **Error Handling**: Serialization fallback to safe summarized envelope when construction fails; masking failure suppresses affected fragment with redaction marker; protocol-level error envelope returned when response cannot be constructed at all, still carrying tracking identifier

## Tool Mapping


| MCP Tool Concept       | Target Feature               |
| ------------------------ | ------------------------------ |
| Execute action         | dispatcher feature           |
| List available actions | dispatcher feature           |
| Health check           | diagnostics feature          |
| Get settings           | config feature               |
| Read skill context     | static documentation surface |
| Get task status        | job feature                  |
| Cancel task            | job feature                  |

Mapping discipline:

- One tool corresponds to one aggregate; the surface never composes cross-feature behavior
- Tool semantics are identical to their CLI counterparts because both project the same underlying aggregates; any divergence is a defect, not a feature
- Skill context is the single static surface: versioned documentation describing capabilities, recommended workflows, and known limitations, served without touching live system state
- New capabilities become agent-accessible by catalog registration alone; the surface gains them through schema exposure, not through surface code changes
- Tools must not expose internals the catalog does not declare: no hidden parameters, no undocumented modes, no surface-only shortcuts

## Error Categories

Owned by this feature:

- validation error — invalid tool input at the surface level: malformed payload, missing required field, wrong field shape, oversized input
- unsupported error — unknown tool name or incompatible protocol version

Displayed but owned elsewhere:

- not found, capacity, timeout, execution, security violation, connection, state, and task categories pass through from owning features in unified categorized form
- the surface attaches MCP-spec formatting to these categories without renaming, reinterpreting, or softening them

## Events

None. The surface layer does not emit domain events.

Session lifecycle, tool call routing, and response outcomes may appear in structured logs through the diagnostics logging policy, but the MCP surface contributes no events to the domain event stream and consumes none for its own behavior.

## Configuration Keys


| Configuration Concept         | Description                                                                   | Typical Default                     |
| ------------------------------- | ------------------------------------------------------------------------------- | ------------------------------------- |
| Server identity name          | Name and version advertised during MCP initialization                         | Product name with semantic version  |
| Maximum response payload      | Upper bound for serialized response content before oversized strategy applies | Conservative payload limit          |
| Protocol version              | MCP protocol version negotiated during initialization                         | Current supported version           |
| Input strictness policy       | Whether unknown extra input fields are rejected or ignored with warning       | Strict                              |
| Oversized payload strategy    | Summarize, substitute reference, or truncate when bound exceeded              | Substitute reference where possible |
| Skill context version         | Version of static documentation served by skill context tool                  | Matches product release             |
| Tracking identifier injection | Whether surface generates tracking identifier when client omits it            | Enabled                             |
| Schema exposure detail        | Depth of examples and metadata included in tool schemas                       | Full detail                         |

## QA Checklist

- [ ]  Tool schemas exposed correctly with names, descriptions, parameter schemas, and examples
- [ ]  Schema content derived from dispatcher catalog and owning feature shapes, never redefined at surface
- [ ]  Schema exposure deterministic for identical catalog state
- [ ]  Catalog version included in schema output
- [ ]  Degraded owning feature indicated in tool metadata rather than hidden
- [ ]  Protocol negotiation rejects incompatible client versions with unsupported error
- [ ]  Service accepts tool calls only after initialization completes
- [ ]  Tool calls routed to correct aggregate with identical semantics to CLI counterparts
- [ ]  Unknown tool name produces unsupported error per MCP specification
- [ ]  Malformed tool input produces validation error with field-level detail
- [ ]  Unknown extra fields handled according to strict or tolerant policy
- [ ]  Oversized tool input rejected at surface before routing
- [ ]  Tracking ID included in all responses, success and failure alike
- [ ]  Tracking identifier generated when client omits it
- [ ]  Responses structured per MCP specification with unified result envelope
- [ ]  Payload size limit enforced through summarize, reference substitution, or truncation
- [ ]  Binary content returned as reference or bounded excerpt, never unbounded inline
- [ ]  Non-serializable values converted to safe textual representation
- [ ]  Errors formatted per MCP specification with unified category and actionable message
- [ ]  Secrets masked in every response path before transmission
- [ ]  Masking failure suppresses affected fragment rather than exposing it
- [ ]  Warning lists preserved alongside results
- [ ]  Concurrent tool calls accepted with serialization delegated to gateway queue
- [ ]  Client disconnect mid-call does not corrupt aggregate execution
- [ ]  Skill context serves versioned static documentation without touching live state
- [ ]  1:1 parity with CLI verified: both surfaces use same aggregates and produce same semantics
- [ ]  No business logic in MCP layer: no retries, no composition, no result reinterpretation
- [ ]  New catalog capability reachable through schema exposure without surface code changes
