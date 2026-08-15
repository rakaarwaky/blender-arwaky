# Blender Arwaky

[![CI](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml) [![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/downloads/) [![Blender 4.2+](https://img.shields.io/badge/Blender-4.2%2B-E87D0D.svg)](https://www.blender.org/download/) [![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

**Blender Arwaky** is an open-source Blender automation runtime for MCP clients, agentic coding workflows, and technical artists. A validated dispatcher connects MCP and CLI clients to the same action catalog.

> Blender Python execution is powerful and is not a complete security sandbox. Use disposable workspaces, save important `.blend` files, and isolate untrusted workflows.

## Why use it?

Blender Arwaky is designed for **deterministic Blender automation, discoverable schemas, CLI/MCP parity, and governed local execution**. It is not a hosted SaaS product, bundled LLM, or complete wrapper for every Blender operator.

## Installation

### Requirements

Install Blender 4.2+, Python 3.10+, and [`uv`](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync
```

Build the Blender addon package with the repository's addon build command. Install the generated ZIP through **Edit → Preferences → Add-ons → Install…**, enable **Blender Arwaky Addon**, and start the MCP server:

```bash
uv run blender-mcp
```

The MCP server uses stdio for the client connection and communicates with the Blender addon through the local bridge. The default bridge port is `9876`.

### MCP client configuration

Use an absolute checkout path in the client configuration:

```json
{
  "mcpServers": {
    "blender-arwaky": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/blender-arwaky", "run", "blender-mcp"]
    }
  }
}
```

## MCP surface

The MCP registry intentionally exposes only five stable tools. Feature actions are not duplicated as separate MCP tools; they are dispatched through `execute_command`.

| Tool | Purpose |
|---|---|
| `execute_command` | Execute one canonical action with structured arguments. |
| `list_commands` | Discover action names, categories, descriptions, parameters, and catalog metadata. |
| `health_check` | Inspect server and Blender runtime health. |
| `get_config` | Retrieve non-secret or redacted configuration. |
| `help` | Return embedded MCP/CLI usage guidance and examples. |

Typical workflow:

```text
health_check()
list_commands()
execute_command(action="create_primitive", args={"primitive_type": "CUBE", "name": "DemoCube"})
```

## CLI surface

The CLI exposes every canonical action exactly once. Start with:

```bash
uv run blender-arwaky --help
uv run blender-arwaky create-primitive --help
```

Examples:

```bash
uv run blender-arwaky get-scene-info --json
uv run blender-arwaky create-primitive --primitive-type CUBE --name DemoCube
uv run blender-arwaky configure-camera --focal-length 50 --set-active
uv run blender-arwaky render --output-path /tmp/render.png
uv run blender-arwaky get-runtime-status --json
```

## CLI flag model

The CLI has three flag layers. **Common flags** are available across actions; **action flags** are generated from each action schema; and some parameter names are reused by related actions without becoming a separate category-level interface.

| Layer | Flags or examples | Applies to |
|---|---|---|
| Common output and safety flags | `--json`, `--quiet`, `--verbose`, `--color`, `--no-progress`, `--confirm` | All actions |
| Runtime context | `--filepath` | Actions that do not define their own `filepath` parameter |
| Action-specific flags | `--primitive-type`, `--material-name`, `--frame-start`, `--node-group-name`, `--task-id` | Only the action whose schema declares the parameter |

Common flags control presentation and operator confirmation; they do not change the Blender operation itself. Action flags are typed from the schema, so a boolean becomes a switch, an integer or number is parsed accordingly, enumerated values are restricted, and vector values accept three components.

There is **no separate inherited flag set for each category**. Categories organize the catalog. However, several parameter names are intentionally reused where the concepts overlap:

| Reused parameter family | Typical actions |
|---|---|
| `--object-name` | Scene, object, mesh, physics, rigging, asset actions |
| `--location`, `--rotation`, `--scale` | Primitive, transform, pose, and placement actions |
| `--frame-start`, `--frame-end` | Timeline, VSE, particle, and physics actions |
| `--resolution-x`, `--resolution-y` | Render actions |
| `--file-path`, `--filepath`, `--output-path` | Texture, asset, launcher, screenshot, render, and export actions |
| `--provider`, `--asset-id`, `--asset-type` | Asset provider and import actions |
| `--task-id` | Background task status and cancellation actions |

The same flag name is validated separately by each action schema. Use `blender-arwaky <action> --help` for the authoritative flags of one action, and `list_commands` or `help` through MCP for the corresponding API contract.

## Canonical action catalog

The catalog below lists the available CLI actions in `kebab-case`. MCP/API clients use the corresponding `snake_case` action name.

| No. | Category | Action | Description |
|---:|---|---|---|
| 1 | gateway | `execute-blender-code` | Execute validated Blender Python code |
| 2 | scene | `get-scene-info` | Full scene metadata — object count, frame range, resolution, render engine |
| 3 | scene | `cleanup-scene` | Remove objects from scene by mode |
| 4 | scene | `list-scene-objects` | List scene objects with optional visibility and type filters |
| 5 | scene | `get-object-hierarchy` | Inspect parent-child hierarchy for one object or the scene roots |
| 6 | scene | `undo` | Undo the most recent Blender edit operation |
| 7 | scene | `redo` | Redo the most recently undone Blender edit operation |
| 8 | object | `get-object-info` | Get details of a specific object — location, rotation, scale, modifiers, materials |
| 9 | object | `create-primitive` | Create a new primitive mesh object |
| 10 | object | `set-object-transform` | Update object transform — location, rotation, or scale |
| 11 | object | `delete-object` | Remove an object from the scene |
| 12 | object | `set-material` | Assign a material to an object |
| 13 | object | `create-material` | Create or reuse a PBR material |
| 14 | object | `set-material-properties` | Update PBR properties of an existing material |
| 15 | object | `set-material-texture` | Assign a local image texture to a material base color |
| 16 | object | `apply-modifier` | Apply a modifier on an object |
| 17 | geometry_nodes | `inspect-geometry-node-group` | Inspect a bounded Geometry Nodes group |
| 18 | geometry_nodes | `create-geometry-node-group` | Create a Geometry Nodes group |
| 19 | geometry_nodes | `set-geometry-node-link` | Create a validated Geometry Nodes link |
| 20 | geometry_nodes | `set-geometry-node-modifier` | Configure a Geometry Nodes modifier |
| 21 | animation | `get-animation-state` | Inspect bounded animation state |
| 22 | animation | `insert-object-keyframe` | Insert a keyframe for an object data path |
| 23 | animation | `set-timeline-range` | Set the scene timeline range and current frame |
| 24 | animation | `list-object-keyframes` | List keyframes for an object |
| 25 | mesh | `get-mesh-statistics` | Return bounded mesh statistics |
| 26 | mesh | `validate-mesh` | Validate mesh structure and bounded quality conditions |
| 27 | mesh | `perform-mesh-edit-operation` | Perform an allow-listed mesh edit operation |
| 28 | mesh | `ensure-mesh-uv-layer` | Ensure a named UV layer exists |
| 29 | render | `configure-camera` | Configure a Blender camera and optional depth of field |
| 30 | render | `setup-environment` | Configure HDRI lighting using a resolved local asset |
| 31 | render | `get-viewport-screenshot` | Capture an AI-optimized viewport screenshot |
| 32 | render | `render` | Execute a full frame render |
| 33 | render | `set-render-settings` | Configure bounded scene render settings without rendering |
| 34 | compositor | `inspect-compositor-nodes` | Inspect a bounded compositor node graph |
| 35 | compositor | `configure-compositor` | Enable or disable compositor nodes |
| 36 | compositor | `create-compositor-node` | Create an allow-listed compositor node |
| 37 | compositor | `set-compositor-link` | Create a validated compositor node link |
| 38 | vse | `inspect-sequence-editor` | Inspect bounded VSE strips and channels |
| 39 | vse | `create-sequence-strip` | Create an allow-listed VSE strip from a validated path |
| 40 | vse | `remove-sequence-strip` | Remove a named VSE strip |
| 41 | vse | `render-sequence` | Render a bounded VSE frame range |
| 42 | physics | `get-physics-state` | Inspect bounded rigid body and cloth state |
| 43 | physics | `configure-rigid-body` | Configure rigid body simulation settings |
| 44 | physics | `configure-cloth-simulation` | Configure bounded cloth simulation settings |
| 45 | physics | `bake-physics-simulation` | Bake a bounded physics cache |
| 46 | physics | `clear-physics-bake` | Clear cached physics simulation data |
| 47 | physics | `get-simulation-state` | Inspect bounded advanced simulation modifiers |
| 48 | physics | `get-simulation-cache-status` | Inspect physics cache range and bake state |
| 49 | physics | `configure-particle-system` | Configure a bounded particle system |
| 50 | physics | `configure-force-field` | Configure a bounded force field |
| 51 | physics | `configure-fluid-domain` | Configure a bounded fluid domain baseline |
| 52 | rigging | `inspect-armature` | Inspect an armature bone hierarchy and pose summary |
| 53 | rigging | `set-pose-bone-transform` | Set a transform on a named pose bone |
| 54 | rigging | `configure-bone-constraint` | Create, update, or remove an allow-listed bone constraint |
| 55 | rigging | `configure-shape-key` | Create, update, or remove a bounded mesh shape key |
| 56 | rigging | `get-deformation-state` | Inspect deformation modifiers, constraints, and shape keys |
| 57 | asset | `search-assets` | Search configured asset providers |
| 58 | asset | `get-provider-metadata` | Get normalized metadata for a provider asset |
| 59 | asset | `download-asset` | Download a provider asset into the validated local cache |
| 60 | asset | `extract-asset` | Safely extract a downloaded asset archive |
| 61 | asset | `import-asset` | Import a locally cached asset into Blender |
| 62 | asset | `import-glb` | Import a GLB/GLTF file into the scene |
| 63 | asset | `export-model` | Export a model to a file |
| 64 | asset | `place-asset` | Place an asset in the scene at a specific position |
| 65 | launcher | `launch-blender` | Start Blender with the integration component active |
| 66 | launcher | `shutdown-blender` | Gracefully shut down Blender with force fallback |
| 67 | launcher | `get-runtime-status` | Verify Blender process liveness and readiness |
| 68 | launcher | `register-executable` | Locate and register the Blender executable |
| 69 | job | `submit-task` | Register a background task through the shared job lifecycle |
| 70 | job | `list-tasks` | List current and retained background task snapshots |
| 71 | job | `get-capacity-status` | Return background task capacity and available slots |
| 72 | job | `get-task-status` | Query the progress and status of a background task |
| 73 | job | `cancel-task` | Cancel a running background task |
| 74 | config | `get-config` | Retrieve Blender Arwaky configuration settings |
| 75 | config | `set-config` | Update a configuration setting |

## Configuration

Configuration is loaded from project files and environment variables with the `BLENDERMCP_` prefix. Use the dispatcher or CLI to inspect redacted settings:

```bash
uv run blender-arwaky get-config --json
```

Do not commit credentials or local configuration files.

## Security and scope

Shared boundaries validate paths, archives, configuration, and response data. Secret-like values are redacted, and destructive CLI actions require confirmation. These controls reduce operational risk but do not sandbox arbitrary Blender Python. Use a disposable workspace and isolate workflows that handle untrusted code or sensitive data.

Current core scope is deterministic Blender automation. LLM providers, local Ollama/llama.cpp adapters, VRM workflows, and broad capability packs are not bundled core features unless explicitly represented in the catalog and tested through the project gates.

## Comparison with other Blender MCP projects

This is a trade-off summary, not a ranking. Tool counts are self-reported and are not directly comparable because projects may expose one tool per operation or group many operations behind one tool.

| Project | Stronger than Blender Arwaky | Blender Arwaky stronger or different |
|---|---|---|
| [BlenderMCP by ahujasid][1] | Larger public adoption, simpler `uvx` onboarding, Poly Haven, Sketchfab, Hunyuan3D, and Hyper3D integrations | A stable five-tool MCP boundary, one shared action contract, CLI parity, and explicit validation |
| [Blender MCP Server by djeada][3] | 27 named tools across 7 namespaces, async jobs, script library, headless workflows, and detailed runtime controls | One shared contract for 75 actions, unified CLI/MCP behavior, and consistent discovery and validation |
| [Blender MCP by sandraschi][4] | `.mcpb`, headless-first execution, dashboard, Docker/native options, and broader specialized coverage such as VRM, VSE, Geometry Nodes, and Gaussian splats | Smaller five-tool protocol boundary, 75 discoverable actions, CLI/MCP parity, and clearly stated scope boundaries |
| [Blender Lab MCP Server][2] | Official Blender provenance, Blender 5.1+ integration, and natural-language access to Blender's Python API/documentation | Blender 4.2+ declared compatibility, structured action catalog, CLI, shared validation/redaction, health/config/help, and explicit confirmation boundaries |

Choose Blender Arwaky for governed, deterministic automation with a stable contract. Choose a broader competitor when you need specialized capability breadth, a polished `.mcpb` installer, dashboard, or headless workflows that are outside Arwaky's current core scope.

## Contributing

Bug reports, feature requests, and code contributions are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the developer workflow.

## License

Blender Arwaky is released under the [MIT License](LICENSE).

## References

[1]: https://github.com/ahujasid/blender-mcp "BlenderMCP by ahujasid"
[2]: https://www.blender.org/lab/mcp-server/ "Blender Lab MCP Server"
[3]: https://github.com/djeada/blender-mcp-server "Blender MCP Server by djeada"
[4]: https://github.com/sandraschi/blender-mcp "Blender MCP by sandraschi"
