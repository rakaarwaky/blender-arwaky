# Blender Arwaky

[![CI](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/downloads/)
[![Blender 4.2+](https://img.shields.io/badge/Blender-4.2%2B-E87D0D.svg)](https://www.blender.org/download/)
[![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

Blender Arwaky is an open-source Blender MCP addon and automation runtime for developers, technical artists, and agentic coding workflows. It supports scene inspection, object operations, camera and rendering workflows, asset pipelines, launcher lifecycle, background jobs, configuration, and validated Blender Python execution through the same dispatcher used by MCP and CLI clients.

## Why Blender Arwaky?

Most Blender MCP projects optimize first for the number of tools they expose. Blender Arwaky takes a different position: **a smaller public surface can be easier for an agent to reason about and safer for an operator to govern**. Five MCP tools expose the stable protocol boundary, while feature actions remain versioned in one canonical catalog and are available through `execute_command` or the CLI.

This makes Blender Arwaky a good fit when you care about:

- **Contract-first execution.** Action names, parameters, owners, and schemas come from a canonical catalog rather than speculative routing.
- **One protocol, two surfaces.** MCP clients and the standalone CLI submit the same canonical actions to the dispatcher.
- **Operational visibility.** Health checks, runtime status, configuration retrieval, tracking metadata, and bounded response envelopes are part of the design.
- **Security-aware automation.** Paths, archives, secrets, and code inputs pass through shared validation or redaction policies. This is not a promise of a perfect sandbox; arbitrary Blender Python remains powerful and must be governed.
- **A maintainable agent surface.** The MCP registry intentionally exposes exactly five tools, reducing tool sprawl while retaining a broader action catalog behind them.

## Honest project status

Blender Arwaky is an **active engineering runtime**, not a hosted SaaS product and not an all-in-one generative 3D platform. It does not bundle an LLM, Ollama adapter, Geometry Nodes capability pack, animation/VSE pack, compositor pack, physics pack, or VRM workflow as a current core feature. Those may be future scope. The current product is strongest at deterministic Blender automation through explicit actions and validated code execution.

Asset-provider availability depends on the configured provider and its credentials or network access. Heavy or provider-specific workflows should be treated as integration work rather than assumed to be universally available on every installation.

## Feature overview

| Area | Current capability | Boundary to understand |
|---|---|---|
| MCP | Five stable tools: `execute_command`, `list_commands`, `health_check`, `get_config`, `help` | Feature actions are not exposed as dozens of separate MCP tools; they are dispatched through `execute_command`. |
| Scene | Inspect scene metadata, list/filter objects, inspect hierarchy, clean objects or meshes, and request undo/redo | Undo/redo may return an explicit unavailable status when Blender runs without an editor context. |
| Objects | Inspect objects, create primitives, transform, delete, assign materials, create/update PBR materials, attach local textures, and apply modifiers | The primitive/material action catalog is intentionally finite; it is not a complete wrapper for every Blender operator. |
| Render | Configure camera, set render settings, set an HDRI environment from a resolved local asset, capture viewport screenshots, and render a frame | Background render orchestration and capability packs are not presented as complete current features. |
| Assets | Search providers, read metadata, download to validated cache, safely extract, import, export, and place assets | Provider credentials, network access, archive limits, and local paths still apply. |
| Launcher | Locate/register Blender, launch, inspect runtime readiness, and shut down | The launcher manages the runtime boundary; it does not replace Blender installation or process supervision for every deployment. |
| Jobs | Submit, list, inspect, cancel, and read capacity for shared background tasks | Job integration is available for defined flows; it is not a general distributed queue or automatic executor for every action. |
| Configuration | Read and update configuration through the dispatcher | Secrets are redacted; configuration policy and environment naming remain authoritative. |
| Code execution | Execute validated Blender Python through the gateway path | This is a powerful capability, not a security sandbox. Save important work and review policies before enabling it. |

## Installation

### Requirements

- **Blender 4.2 or newer.** This is the minimum declared by the addon manifest.
- **Python 3.10 or newer** for the MCP server and CLI.
- [`uv`](https://docs.astral.sh/uv/) for the recommended source installation.
- An MCP-compatible client such as Claude Desktop, Cursor, VS Code, Claude Code, or another client that can launch a local stdio server.

### 1. Clone and install the Python environment

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync
```

The repository exposes two console commands:

```bash
uv run blender-mcp --help
uv run blender-arwaky --help
```

### 2. Build and install the Blender addon

Build the canonical addon package:

```bash
uv run python scripts/build/build_addon_package.py
```

The command writes `dist/blender_mcp_addon.zip`. In Blender:

1. Open **Edit → Preferences → Add-ons**.
2. Choose **Install…** and select `dist/blender_mcp_addon.zip`.
3. Enable **Blender Arwaky Addon**.
4. Open the **BlenderArwaky** sidebar panel if you need to inspect the addon state.

The addon manifest declares Blender 4.2.0 as its minimum version. The addon starts the local bridge used by the MCP server according to the configured runtime settings; the default TCP port is `9876`.

### 3. Start the MCP server

From the repository directory, run:

```bash
uv run blender-mcp
```

Keep this process available to your MCP client. The server uses stdio for the client-facing MCP connection and communicates with the Blender addon through the configured local bridge.

### 4. Configure an MCP client

Use an absolute path to the checkout. A generic stdio configuration looks like this:

```json
{
  "mcpServers": {
    "blender-arwaky": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/blender-arwaky",
        "run",
        "blender-mcp"
      ]
    }
  }
}
```

If a graphical client cannot find `uv`, replace `"command": "uv"` with the absolute path returned by `which uv` on macOS/Linux or `where uv` on Windows. Restart the client after changing its MCP configuration.

## MCP surface

Blender Arwaky intentionally exposes exactly five MCP tools:

| Tool | Purpose |
|---|---|
| `execute_command` | Execute one canonical action with structured arguments. |
| `list_commands` | Discover action names, owners, descriptions, parameters, and catalog metadata. |
| `health_check` | Inspect server and Blender runtime health before or during an operation. |
| `get_config` | Retrieve non-secret configuration values or a redacted configuration snapshot. |
| `help` | Return embedded MCP/CLI guidance and action examples without reading repository files at runtime. |

A typical MCP workflow is:

1. Call `health_check` to confirm that the runtime boundary is available.
2. Call `list_commands` to discover the current canonical action and schema.
3. Call `execute_command` with the discovered action and arguments.
4. Use `get_config` for redacted configuration context and `help` when the client needs usage guidance.

Example action calls:

```text
execute_command(
  action="create_primitive",
  args={"primitive_type": "CUBE", "name": "DemoCube"}
)

execute_command(
  action="configure_camera",
  args={"focal_length": 50, "set_active": true}
)
```

The five-tool registry and embedded help contract are defined in [`surface_tool_registry.py`](modules/mcp/src/surface_tool_registry.py) and [`utility_help_content.py`](modules/shared/src/mcp/utility_help_content.py).

## Canonical action catalog

The current dispatcher catalog contains **40 actions across eight owners**. The number refers to canonical actions, not the number of MCP tools. Wave 1 adds bounded scene object listing and hierarchy inspection, explicit history navigation status, PBR material authoring, render settings configuration, and shared job submission/list/capacity actions.

| Owner | Actions |
|---|---|
| Gateway | `execute_blender_code` |
| Scene | `get_scene_info`, `cleanup_scene`, `list_scene_objects`, `get_object_hierarchy`, `undo`, `redo` |
| Object | `get_object_info`, `create_primitive`, `set_object_transform`, `delete_object`, `set_material`, `create_material`, `set_material_properties`, `set_material_texture`, `apply_modifier` |
| Render | `configure_camera`, `setup_environment`, `get_viewport_screenshot`, `render`, `set_render_settings` |
| Asset | `search_assets`, `get_provider_metadata`, `download_asset`, `extract_asset`, `import_asset`, `import_glb`, `export_model`, `place_asset` |
| Launcher | `launch_blender`, `shutdown_blender`, `get_runtime_status`, `register_executable` |
| Job | `submit_task`, `list_tasks`, `get_capacity_status`, `get_task_status`, `cancel_task` |
| Config | `get_config`, `set_config` |

The canonical source is [`taxonomy_dispatcher_constant.py`](modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py). Use `list_commands` rather than hard-coding schemas in an agent integration because the catalog is versioned and may evolve.

## CLI usage

The CLI is useful for local automation, CI checks, scripts, and debugging without requiring an MCP client. Start with:

```bash
uv run blender-arwaky --help
```

### Generic action execution

The generic `run` command submits a canonical action directly:

```bash
uv run blender-arwaky run \
  --filepath /absolute/path/to/scene.blend \
  --action get_scene_info \
  --params '{}' \
  --json
```

For a mutating action:

```bash
uv run blender-arwaky run \
  --filepath /absolute/path/to/scene.blend \
  --action create_primitive \
  --params '{"primitive_type":"CUBE","name":"DemoCube"}' \
  --json
```

### Useful dedicated commands

| Command | Example |
|---|---|
| Start Blender | `uv run blender-arwaky init --filepath scene.blend --mode headless --port 9876` |
| Runtime status | `uv run blender-arwaky status --json` |
| Scene inspection | `uv run blender-arwaky scene-info --json` |
| Object creation | `uv run blender-arwaky create --type CUBE --name DemoCube` |
| Camera setup | `uv run blender-arwaky camera-config --focal-length 50 --set-active` |
| Screenshot | `uv run blender-arwaky screenshot --filepath scene.blend --output /tmp/scene.png` |
| Render | `uv run blender-arwaky render --filepath scene.blend --output /tmp/render.png` |
| Asset search | `uv run blender-arwaky search-assets --query chair --provider Polyhaven --json` |
| Asset download | `uv run blender-arwaky download-asset --provider Polyhaven --asset-id chair --asset-type model --cache-dir .cache/assets` |
| Job status | `uv run blender-arwaky task-status --task-id task-001 --json` |
| Read config | `uv run blender-arwaky config --key default_output_format --json` |
| Validated code | `uv run blender-arwaky run-code --code 'print(bpy.context.scene.name)' --json` |

Common output and safety flags are available on the root command and dedicated commands:

```text
--json         Machine-readable JSON output
--confirm      Confirm a destructive action
--quiet        Suppress non-error output
--verbose      Show masked structural diagnostics
--color        Color policy: auto, always, or never
--no-progress  Disable progress hints
```

Commands such as scene cleanup, object deletion, Blender shutdown, task cancellation, and configuration mutation require explicit confirmation where the command contract marks them destructive. Treat `--confirm` as an operator decision, not as a bypass for validation or security policy.

## Configuration

Configuration is loaded from the project configuration sources and can be overridden by environment variables. The canonical prefix is `BLENDERMCP_`.

Example `config.yaml` shape:

```yaml
blender:
  executable_path: "/usr/bin/blender"
  host: "localhost"
  port: 9876

server:
  transport: "stdio"
  log_dir: "log"
```

Useful configuration controls include:

| Variable | Purpose |
|---|---|
| `BLENDERMCP_CONFIG_PATH` | Select an explicit configuration file. |
| `BLENDERMCP_SERVER.TRANSPORT` | Override the configured server transport. |
| `BLENDERMCP_STRICT` | Enable strict enforcement for configuration validation and size/path policies. |

Use `get_config` or `uv run blender-arwaky config --json` to inspect redacted settings. Do not place credentials in `config.yaml` or commit local configuration files.

## Security model

Blender automation can alter files, scenes, processes, and external resources. Review the following before connecting an agent to a production workspace:

- Blender Python execution is powerful and can perform any operation permitted by the configured policy and Blender process. It should not be described as a complete sandbox.
- File paths and archive extraction are validated at the shared security boundary, including traversal and size policies where applicable.
- Secret-like configuration values and diagnostic metadata are redacted before exposure through response surfaces.
- Destructive CLI commands require explicit confirmation flags.
- The MCP server exposes a bounded core surface, but a caller with permission to execute a mutating action can still change the Blender scene.
- Use a disposable project, version-control important `.blend` files, and avoid sending credentials or untrusted code unless the policy is understood.

## Architecture

Blender Arwaky follows an AES-style modular architecture: **Agents → Executors → Services**, with shared taxonomy and contract layers controlling dependencies. The root composition layer wires feature capabilities into the dispatcher and surfaces.

```text
MCP / CLI surface
        │
        ▼
dispatcher and action catalog
        │
        ▼
feature agents → capabilities → shared contracts/taxonomy
        │
        ▼
Blender addon / external providers / local runtime
```

Read [ARCHITECTURE.md](ARCHITECTURE.md) for the full boundary specification and [`modules/*/FRD.md`](modules/shared/FRD.md) for feature contracts.

## Honest comparison with other Blender MCP projects

The following comparison is intentionally about **trade-offs**, not a ranking. Competitor descriptions and tool counts come from their public repository or official documentation and can change between releases. A larger tool count may provide broader immediate coverage, but it can also create a larger contract surface for an agent to discover and maintain.

| Project | Public MCP shape | Installation / runtime model | Safety and governance posture | Where it is stronger than Blender Arwaky | Where Blender Arwaky is stronger or different |
|---|---|---|---|---|---|
| **Blender Arwaky** | **5 stable MCP tools** plus **40 canonical actions** dispatched through `execute_command` | Source checkout with `uv`; Blender addon package built to `dist/blender_mcp_addon.zip`; stdio MCP server plus local addon bridge | Shared validation/redaction, explicit confirmation for destructive CLI commands, bounded responses, health/config/help surfaces; arbitrary Blender Python is still powerful and not a full sandbox | — | Contract-first catalog, small stable MCP boundary, same actions through MCP and CLI, explicit runtime diagnostics, and a focused automation core |
| [BlenderMCP by ahujasid][2] | Feature-oriented MCP integration with scene/object/material tools, screenshots, arbitrary Python, and asset/3D-generation integrations described in its README | `uvx`/Python server plus Blender addon; supports Claude, Cursor, VS Code, and other clients | The README explicitly warns that arbitrary Python execution is powerful and dangerous; it also documents optional telemetry and external provider credentials | Larger public community footprint, more mature consumer onboarding, and more integrations such as Poly Haven, Sketchfab, Hunyuan3D, and Hyper3D described in its README | Smaller protocol surface and stronger emphasis on canonical schemas, CLI parity, and explicit contract governance rather than feature breadth |
| [Blender MCP Server by djeada][4] | Large named-tool surface covering scene/object/material/render/export, Python execution, undo/redo, and asynchronous jobs; its README advertises 27 tools across 7 namespaces | Python package with editable install, built addon ZIP, stdio MCP server, and direct bridge helpers | Documents safe mode, project-root file restrictions, tool whitelist, script-root restrictions, module blocklists, and automatic undo for many mutations | Broader named coverage, async job controls, script library, headless-oriented workflows, and more explicit per-tool safety controls | Smaller stable MCP boundary and a more centralized action catalog; current scope is intentionally narrower and does not claim complete physics, VSE, Geometry Nodes, or VRM coverage |
| [Blender MCP by sandraschi][5] | Its README advertises 48+ MCP tools; the repository page summarizes 41 portmanteau tools and 150+ operations, spanning mesh, VSE, Geometry Nodes, VRM, Gaussian splats, and more | `.mcpb` packaging for Claude Desktop, headless Blender by default, optional live bridge, dashboard, Docker/native options | Documents a broad operational surface with optional bridge, packaging, monitoring, and multiple execution modes; the exact security guarantees vary by mode and configuration | Much broader capability coverage, `.mcpb` distribution, headless-first workflows, web dashboard, and future-facing capability packs | More focused contract surface, fewer moving parts, CLI/MCP action parity, and clearer current non-goals for teams that prefer controlled scope |
| [Blender Lab MCP Server][3] | Official Blender Lab MCP server focused on natural-language access to Blender's Python API and documentation | Blender 5.1+ addon plus an MCP server and a separate LLM client; `.mcpb` or source setup is documented | The official page explicitly warns that LLM-generated code is executed **without guards** and recommends isolation such as a virtual machine | Official Blender Lab provenance, Blender 5.1+ integration, and natural-language exploration/documentation workflows | Declared Blender 4.2+ minimum, structured action catalog, CLI surface, shared validation/redaction, health/config/help tools, and explicit confirmation boundaries |

**How to read this table.** Tool counts are self-reported and may not be directly comparable: some projects expose one tool per operation, while Blender Arwaky groups operations behind a canonical dispatcher. “Safer” does not mean “safe by default”; all systems that can execute Blender Python or mutate a scene require operator review and isolation appropriate to the workload.

## What to choose

Choose Blender Arwaky if your priority is a **controlled automation runtime** with a small MCP boundary, discoverable schemas, a parallel CLI, and explicit contracts that can be tested in CI.

Choose a broader competitor if you need maximum ready-made operation coverage, a polished `.mcpb` installer, a web dashboard, headless-first batch workflows, or specialized Geometry Nodes/VSE/VRM/physics integrations today. Those are legitimate advantages, not gaps to hide.

## Testing and development

Install development dependencies and run the local gates:

```bash
uv sync --dev
uv run pytest -q
uv run ruff check modules blender_mcp_addon scripts
uv run ruff format --check modules blender_mcp_addon scripts
uv run bandit -r modules blender_mcp_addon -x '*/tests/*' -ll -ii
bash scripts/ci.sh
```

The repository CI validates Ruff, Python syntax, Bandit, the full test suite on Python 3.10–3.13, integration contracts, and distributable artifacts. See [TEST.md](TEST.md), [CONTRIBUTING.md](CONTRIBUTING.md), and [`scripts/README.md`](scripts/README.md) for contributor workflows.

## Documentation map

| Document | Purpose |
|---|---|
| [PRD.md](PRD.md) | Product requirements and intended scope |
| [ARCHITECTURE.md](ARCHITECTURE.md) | AES architecture and layer boundaries |
| [AGENT.md](AGENT.md) | Agent/developer operating guidance |
| [TEST.md](TEST.md) | Test strategy and verification workflow |
| [CHANGELOG.md](CHANGELOG.md) | Release and change history |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Contribution workflow |
| [`modules/*/FRD.md`](modules/shared/FRD.md) | Feature-level requirements |
| [`docs/`](docs/) | Historical plans, migration guides, and reference documentation |
| MCP `help` | Embedded runtime help topics: `overview`, `mcp`, `cli`, `actions`, `safety`, and `examples` |

## License

Blender Arwaky is released under the [MIT License](LICENSE).

## References

[1]: https://modelcontextprotocol.io/ "Model Context Protocol"
[2]: https://github.com/ahujasid/blender-mcp "BlenderMCP by ahujasid"
[3]: https://www.blender.org/lab/mcp-server/ "Blender Lab MCP Server"
[4]: https://github.com/djeada/blender-mcp-server "Blender MCP Server by djeada"
[5]: https://github.com/sandraschi/blender-mcp "Blender MCP by sandraschi"
[6]: modules/mcp/src/surface_tool_registry.py "Blender Arwaky five-tool registry"
[7]: modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py "Blender Arwaky canonical action catalog"
[8]: modules/shared/src/mcp/utility_help_content.py "Blender Arwaky embedded MCP/CLI help"
