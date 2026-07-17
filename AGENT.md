# BlenderArwaky — AGENT.md

## Project Overview

BlenderArwaky connects **Blender 3D** to any **MCP client** (Claude Desktop, Cursor,
Continue.dev, or custom agents). It exposes a Universal Surface Layer with 4 MCP
tools that dispatch to a command catalog of 15+ actions: scene manipulation,
object ops, rendering, asset imports (Poly Haven, Sketchfab), and code execution.

**Stack:** Python 3.10+, FastMCP, Blender 5.1+, AES architecture

**Two entry points:**

- `surfaces.mcp_server_entry` — MCP stdio/SSE server
- `surfaces.cli_main_entry` — CLI standalone mode

---

## Architecture — AES 6-Domain Layering

```
surfaces/    → MCP tools, CLI entry points (4 tools only)
agent/       → DI container, orchestrators, experts
capabilities → Use cases: scene ops, rendering, import/export
infrastructure → Adapters: Blender socket, telemetry
contract/    → Ports & protocols (interfaces between layers)
taxonomy/    → Foundation: data structures, config, command catalog
```

**Layer rules:**

- surfaces → agent (never direct to infra/capabilities)
- agent → capabilities → infrastructure → contract → taxonomy
- taxonomy: pure data, no business logic

---

## Key Files & Directories

| Path | Purpose |
|------|---------|
| `src/surfaces/` | MCP tools (4 tools), CLI entry, barrel `__init__.py` |
| `src/agent/agent_di_container.py` | DI container — wires all layers |
| `src/agent/agent_factory_registry.py` | Factory methods for creating components |
| `src/agent/system_coordinator.py` | Config resolution, health checks, telemetry |
| `src/taxonomy/blender_command_vo.py` | Canonical `COMMAND_CATALOG` (15+ actions) |
| `src/capabilities/action_execute_actions.py` | Action dispatcher with auto-RequestVO |
| `src/capabilities/render_operate_executor.py` | Rendering + AI-optimized screenshots |
| `src/infrastructure/blender_socket_adapter.py` | TCP to Blender addon |
| `src/infrastructure/telemetry_signal_recorder.py` | Anonymous telemetry |
| `blender_mcp_addon/` | Blender addon (TCP server, auto-start) |

---

## File Naming — 3-Word AES Convention

```
{domain}_{concern}_{suffix}.py
```

Examples: `command_execute_handler.py`, `application_config_vo.py`,
`server_instance_handler.py`, `blender_socket_adapter.py`

**Suffix rules:**

- `_handler` — surfaces handlers (entry points for MCP tools)
- `_entry` — surface entry points (CLI, MCP server)
- `_adapter` — infrastructure adapters
- `_vo` — taxonomy value objects
- `_entity` — taxonomy entities
- `_port` — contract ports
- `_protocol` — contract protocols
- `_container` — agent containers
- `_orchestrator` — agent orchestrators
- `_executor` — capability executors (business logic)

---

## MCP Tools — The 4 Core Tools

| # | Tool | Purpose |
|---|------|---------|
| 1 | `execute_command` | Universal action executor |
| 2 | `list_commands` | Catalog discovery |
| 3 | `read_skill_context` | Read SKILL.md sections |
| 4 | `health_check` | System diagnostics |

All tools are registered in `tool_registry_handler.py` and implemented in
separate handler files under `surfaces/`.

---

## Command Catalog

Defined in `taxonomy/blender_command_vo.py` as `COMMAND_CATALOG`.

Domains: `scene`, `object`, `viewport`, `render`, `io`, `infrastructure`

Actions are dispatched through `ActionExecuteActions` (in `capabilities/`)
which auto-constructs RequestVO objects from raw dict args using signature
introspection.

---

## Common Operations

### Add a new action

1. Add entry in `taxonomy/blender_command_vo.py` `COMMAND_CATALOG`
2. Define RequestVO/ResponseVO in `taxonomy/blender_ops_vo.py`
3. Add abstract method to protocol in `contract/`
4. Implement in executor in `capabilities/`
5. Wire through DI container in `agent/agent_di_container.py`
6. Test with `execute_command(action="your_action")`

### Run the MCP server

```bash
uv run python -m surfaces.mcp_server_entry
```

### Run CLI mode

```bash
uv run python -m surfaces.cli_main_entry
```

### Run tests

```bash
uv run pytest
```

### Run linter

```bash
uv run ruff check src/
```

---

## Environment & Config

- `config.yaml` — server, blender path, storage, telemetry
- `.env.blendermcp` — API keys (Sketchfab)
- Env var `BLENDERMCP_CONFIG_PATH` — override config.yaml path

---

## Key Patterns

### Auto-RequestVO Construction

The dispatcher inspects method signatures to auto-construct typed RequestVO
objects from raw dict args:

```python
# Dispatcher detects GetScreenshotRequestVO is a BaseModel
# and constructs it from {"max_size": 800}
result = await method(GetScreenshotRequestVO(max_size=800))
```

### Async Safety

All Blender IPC calls use `asyncio.to_thread` + `asyncio.wait_for(30s)`:
- No event loop blocking
- Timeout protection
- UUID-based temp files to prevent collision

### Security

Code generation uses `_py_str()` and `_format_coord()` helpers to prevent
injection in generated Python scripts.

---

## Common Pitfalls

- **Circular imports:** surfaces/ modules must import from source files,
  never from the barrel (`__init__.py`)
- **Blender addon:** TCP server on port 9876, auto-started via persistent timer
  (30 retries, 2s interval)
- **API keys:** Never hardcode — use `.env.blendermcp` or scene properties
- **Telemetry:** Default `False` — set `telemetry.enabled` in config
