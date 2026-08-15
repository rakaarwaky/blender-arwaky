# Blender Arwaky

[![CI](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml) [![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/downloads/) [![Blender 4.2+](https://img.shields.io/badge/Blender-4.2%2B-E87D0D.svg)](https://www.blender.org/download/) [![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

**Blender Arwaky** is an open-source Blender automation runtime for MCP clients, agentic coding workflows, and technical artists. A validated dispatcher presents the same catalog through two surfaces: five stable MCP protocol tools and 75 CLI actions exposed once as `kebab-case` commands. MCP/API actions use `snake_case` and are routed through `execute_command`.

The same action contract is used by both surfaces, with shared validation, diagnostics, response handling, and confirmation for destructive operations.

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

Common flags include `--json`, `--confirm`, `--quiet`, `--verbose`, `--color auto|always|never`, and `--no-progress`. Destructive actions require explicit confirmation where defined by the command contract.

## Canonical action catalog

The catalog below lists the available actions. The `Action` column is the MCP/API `snake_case` name; the CLI spelling is obtained by replacing underscores with hyphens.

| No. | Category | Action | Description |
|---:|---|---|---|
| 1 | gateway | `execute_blender_code` | Execute validated Blender Python code |
| 2 | scene | `get_scene_info` | Full scene metadata — object count, frame range, resolution, render engine |
| 3 | scene | `cleanup_scene` | Remove objects from scene by mode |
| 4 | scene | `list_scene_objects` | List scene objects with optional visibility and type filters |
| 5 | scene | `get_object_hierarchy` | Inspect parent-child hierarchy for one object or the scene roots |
| 6 | scene | `undo` | Undo the most recent Blender edit operation |
| 7 | scene | `redo` | Redo the most recently undone Blender edit operation |
| 8 | object | `get_object_info` | Get details of a specific object — location, rotation, scale, modifiers, materials |
| 9 | object | `create_primitive` | Create a new primitive mesh object |
| 10 | object | `set_object_transform` | Update object transform — location, rotation, or scale |
| 11 | object | `delete_object` | Remove an object from the scene |
| 12 | object | `set_material` | Assign a material to an object |
| 13 | object | `create_material` | Create or reuse a PBR material |
| 14 | object | `set_material_properties` | Update PBR properties of an existing material |
| 15 | object | `set_material_texture` | Assign a local image texture to a material base color |
| 16 | object | `apply_modifier` | Apply a modifier on an object |
| 17 | geometry_nodes | `inspect_geometry_node_group` | Inspect a bounded Geometry Nodes group |
| 18 | geometry_nodes | `create_geometry_node_group` | Create a Geometry Nodes group |
| 19 | geometry_nodes | `set_geometry_node_link` | Create a validated Geometry Nodes link |
| 20 | geometry_nodes | `set_geometry_node_modifier` | Configure a Geometry Nodes modifier |
| 21 | animation | `get_animation_state` | Inspect bounded animation state |
| 22 | animation | `insert_object_keyframe` | Insert a keyframe for an object data path |
| 23 | animation | `set_timeline_range` | Set the scene timeline range and current frame |
| 24 | animation | `list_object_keyframes` | List keyframes for an object |
| 25 | mesh | `get_mesh_statistics` | Return bounded mesh statistics |
| 26 | mesh | `validate_mesh` | Validate mesh structure and bounded quality conditions |
| 27 | mesh | `perform_mesh_edit_operation` | Perform an allow-listed mesh edit operation |
| 28 | mesh | `ensure_mesh_uv_layer` | Ensure a named UV layer exists |
| 29 | render | `configure_camera` | Configure a Blender camera and optional depth of field |
| 30 | render | `setup_environment` | Configure HDRI lighting using a resolved local asset |
| 31 | render | `get_viewport_screenshot` | Capture an AI-optimized viewport screenshot |
| 32 | render | `render` | Execute a full frame render |
| 33 | render | `set_render_settings` | Configure bounded scene render settings without rendering |
| 34 | compositor | `inspect_compositor_nodes` | Inspect a bounded compositor node graph |
| 35 | compositor | `configure_compositor` | Enable or disable compositor nodes |
| 36 | compositor | `create_compositor_node` | Create an allow-listed compositor node |
| 37 | compositor | `set_compositor_link` | Create a validated compositor node link |
| 38 | vse | `inspect_sequence_editor` | Inspect bounded VSE strips and channels |
| 39 | vse | `create_sequence_strip` | Create an allow-listed VSE strip from a validated path |
| 40 | vse | `remove_sequence_strip` | Remove a named VSE strip |
| 41 | vse | `render_sequence` | Render a bounded VSE frame range |
| 42 | physics | `get_physics_state` | Inspect bounded rigid body and cloth state |
| 43 | physics | `configure_rigid_body` | Configure rigid body simulation settings |
| 44 | physics | `configure_cloth_simulation` | Configure bounded cloth simulation settings |
| 45 | physics | `bake_physics_simulation` | Bake a bounded physics cache |
| 46 | physics | `clear_physics_bake` | Clear cached physics simulation data |
| 47 | physics | `get_simulation_state` | Inspect bounded advanced simulation modifiers |
| 48 | physics | `get_simulation_cache_status` | Inspect physics cache range and bake state |
| 49 | physics | `configure_particle_system` | Configure a bounded particle system |
| 50 | physics | `configure_force_field` | Configure a bounded force field |
| 51 | physics | `configure_fluid_domain` | Configure a bounded fluid domain baseline |
| 52 | rigging | `inspect_armature` | Inspect an armature bone hierarchy and pose summary |
| 53 | rigging | `set_pose_bone_transform` | Set a transform on a named pose bone |
| 54 | rigging | `configure_bone_constraint` | Create, update, or remove an allow-listed bone constraint |
| 55 | rigging | `configure_shape_key` | Create, update, or remove a bounded mesh shape key |
| 56 | rigging | `get_deformation_state` | Inspect deformation modifiers, constraints, and shape keys |
| 57 | asset | `search_assets` | Search configured asset providers |
| 58 | asset | `get_provider_metadata` | Get normalized metadata for a provider asset |
| 59 | asset | `download_asset` | Download a provider asset into the validated local cache |
| 60 | asset | `extract_asset` | Safely extract a downloaded asset archive |
| 61 | asset | `import_asset` | Import a locally cached asset into Blender |
| 62 | asset | `import_glb` | Import a GLB/GLTF file into the scene |
| 63 | asset | `export_model` | Export a model to a file |
| 64 | asset | `place_asset` | Place an asset in the scene at a specific position |
| 65 | launcher | `launch_blender` | Start Blender with the integration component active |
| 66 | launcher | `shutdown_blender` | Gracefully shut down Blender with force fallback |
| 67 | launcher | `get_runtime_status` | Verify Blender process liveness and readiness |
| 68 | launcher | `register_executable` | Locate and register the Blender executable |
| 69 | job | `submit_task` | Register a background task through the shared job lifecycle |
| 70 | job | `list_tasks` | List current and retained background task snapshots |
| 71 | job | `get_capacity_status` | Return background task capacity and available slots |
| 72 | job | `get_task_status` | Query the progress and status of a background task |
| 73 | job | `cancel_task` | Cancel a running background task |
| 74 | config | `get_config` | Retrieve Blender Arwaky configuration settings |
| 75 | config | `set_config` | Update a configuration setting |

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
