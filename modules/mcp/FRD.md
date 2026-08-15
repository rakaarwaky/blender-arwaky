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
- Embedded help exposure for MCP and CLI usage without filesystem dependencies
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
  - Five stable MCP tools are exposed: execute_command, list_commands, health_check, get_config, and help
  - Feature actions come from the dispatcher catalog and are executed through execute_command; they are not registered as separate MCP tools
  - Help content is embedded in source code and documents MCP, CLI, actions, safety, and examples
  - Descriptions for AI consumption: precise capability statements, parameter meanings, units, ≥1 usage example per tool
  - Schema output carries catalog version for drift detection
  - Degraded owning features: tool listed with explicit degraded indicator, not hidden
  - No secrets, credential placeholders, or environment paths in schemas
  - Schema assembly from in-memory catalog — no domain execution triggered
  - Incompatible client protocol version → rejected with unsupported error
  - Deterministic output: identical catalog → identical schemas across sessions
- **Edge Cases**: Empty catalog, catalog version drift, degraded owning feature, oversized schema for client limits, schema during hot re-registration, unknown help topic, client reconnecting with stale catalog
- **Error Handling**: Unsupported error for incompatible protocol version; state error when catalog unreadable; degraded actions surfaced with indicator; unknown help topic → validation error with available topics

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

### execute_command

Universal action executor — dispatches any action from catalog. Action name = shared identifier dengan CLI `--action`.

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `action` | string | yes | Action name from catalog |
| `args` | dict | no | Action-specific parameters (lihat tabel per domain di bawah) |

Target feature: dispatcher feature. Routes to `IDispatcherAggregate.execute_action(action, args)`.

#### Scene

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `get_scene_info` | (none) | Full scene metadata |
| `cleanup_scene` | `mode`: "all" \| "objects" \| "meshes" | Remove objects |
| `setup_environment` | `hdri_id` (req), `strength` (opt) | Setup HDRI lighting |

#### Object

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `get_object_info` | `object_name` (req) | Object details |
| `create_primitive` | `primitive_type` (req), `location` (opt), `scale` (opt), `name` (opt) | Create primitive |
| `set_object_transform` | `object_name` (req), `location` (opt), `rotation` (opt), `scale` (opt) | Update transform |
| `delete_object` | `object_name` (req) | Remove object |
| `set_material` | `object_name` (req), `material_name` (req) | Assign material |
| `apply_modifier` | `object_name` (req), `modifier_name` (req) | Apply modifier |

#### Viewport & Render

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `get_viewport_screenshot` | `filepath` (opt), `max_size` (opt), `view_angle` (opt), `shading_mode` (opt), `show_overlays` (opt), `focus_object` (opt) | AI-optimized screenshot |
| `render` | `output_path` (req), `resolution_x` (opt), `resolution_y` (opt) | Full frame render |

#### Import / Export / Asset

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `import_glb` | `file_path` (req), `object_name` (opt) | Import GLB/GLTF |
| `export_model` | `object_name` (req), `file_path` (req), `export_format` (opt) | Export model |
| `place_asset` | `asset_id` (req), `location` (opt), `rotation` (opt), `scale` (opt) | Position asset |

#### Launcher

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `launch_blender` | `mode` (opt): "interface" \| "headless" | Start Blender with integration active |
| `shutdown_blender` | `force` (opt, bool) | Graceful shutdown with force fallback |
| `get_runtime_status` | (none) | Verify true process liveness and readiness |
| `register_executable` | `path` (opt) | Locate and register Blender executable |

#### Job

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `get_task_status` | `task_id` (req) | Query render/compute task progress |
| `cancel_task` | `task_id` (req) | Cancel running task |

#### Config

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `get_config` | `key` (opt) | Get config value or all settings |
| `set_config` | `key` (req), `value` (req) | Update config setting |

#### Code Execution

| Action | `args` Parameters | Description |
|--------|-------------------|-------------|
| `execute_blender_code` | `code` (req) | Run Python in Blender |

### list_commands

Discover available actions, parameters, and descriptions.

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `domain` | string | no | Filter by domain: `scene`, `object`, `viewport`, `render`, `io`, `infrastructure`, `asset`, `generation`. Omit for all. |
| `format` | string | no | Output format: `detailed` (full spec per action) or `summary` (names + descriptions). Default: `detailed`. |

Target feature: dispatcher feature. Routes to `IDispatcherAggregate.discover_actions()`.

### health_check

Verify Blender connectivity and system health.

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| (none) | — | — | Returns system health snapshot |

Target feature: diagnostics feature. Routes to `IDiagnosticsAggregate.get_snapshot()`.

### get_config

Retrieve BlenderArwaky configuration settings.

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `key` | string | no | Specific config key to retrieve. Omit for all settings. |

Target feature: config feature.

### help

Return embedded documentation for using the MCP and CLI surfaces. The content is compiled into the package and does not read `SKILL.md` or any repository-relative file at runtime.

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| `topic` | string | no | `overview`, `mcp`, `cli`, `actions`, `safety`, or `examples`. Defaults to `overview`. |

Target feature: MCP help surface. Action details come from the canonical dispatcher catalog.

### Summary

| MCP Tool | Arguments | Target Feature |
|----------|-----------|----------------|
| `execute_command` | `action` (req), `args` (opt) | dispatcher feature |
| `list_commands` | `domain` (opt), `format` (opt) | dispatcher feature |
| `health_check` | (none) | diagnostics feature |
| `get_config` | `key` (opt) | config feature |
| `help` | `topic` (opt) | embedded MCP/CLI help surface |

## Error Categories

- **Owned**: validation error (surface-level input: malformed payload, missing field, wrong shape, oversized), unsupported error (unknown tool, incompatible protocol)
- **Displayed but unowned**: not_found, capacity, timeout, execution, security_violation, connection, state, task — pass through from owning features with MCP formatting, no renaming/reinterpretation

## Events

None. Session lifecycle and tool calls appear in structured logs via diagnostics logging policy.

## Configuration Keys


| Key                   | Description                             | Default               |
| ----------------------- | ----------------------------------------- | ----------------------- |
| server_identity       | Name + version advertised at init       | Product name + semver |
| max_response_payload  | Upper bound before oversized strategy   | Conservative          |
| protocol_version      | Negotiated at handshake                 | Current               |
| input_strictness      | strict/tolerant for unknown fields      | strict                |
| oversized_strategy    | summarize/substitute/truncate           | substitute            |
| help_content_version | Embedded MCP/CLI help contract version | Release version       |
| tracking_id_injection | Generate when client omits              | enabled               |
| schema_detail         | Depth of examples + metadata in schemas | full                  |

## QA Checklist

- [ ]  Tool schemas exposed with names, descriptions, param schemas, examples
- [ ]  Schema content from dispatcher catalog + owning features, never redefined at surface
- [ ]  Deterministic schema output for identical catalog
- [ ]  Catalog version in schema output
- [ ]  Degraded features indicated, not hidden
- [ ]  Protocol negotiation rejects incompatible versions
- [ ]  Calls accepted only after init completes
- [ ]  Tool calls route to correct aggregate, identical semantics to CLI
- [ ]  Unknown tool → unsupported error
- [ ]  Malformed input → validation error with field detail
- [ ]  Unknown extra fields handled per strict/tolerant policy
- [ ]  Oversized input rejected before routing
- [ ]  Tracking ID in all responses
- [ ]  Responses structured per MCP spec with unified envelope
- [ ]  Payload size enforced (summarize/substitute/truncate)
- [ ]  Binary content as ref or bounded excerpt
- [ ]  Non-serializable values → safe text
- [ ]  Errors: MCP-spec format, unified category, actionable message
- [ ]  Secrets masked in every response path
- [ ]  Masking failure → suppress fragment, not expose
- [ ]  Warnings preserved alongside results
- [ ]  Concurrent calls accepted; mutation serialization delegated to gateway
- [ ]  Client disconnect doesn't corrupt execution
- [ ]  Help: embedded MCP/CLI usage content, no SKILL.md or filesystem dependency
- [ ]  1:1 parity with CLI verified — same aggregates, same semantics
- [ ]  No business logic in MCP layer — no retries, composition, reinterpretation
- [ ]  New catalog capability reachable via schema exposure, no surface code changes
