# Blender Arwaky

[![CI](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml/badge.svg?branch=develop)](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml) [![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-3776AB.svg)](https://www.python.org/downloads/) [![Blender 5.2+](https://img.shields.io/badge/Blender-5.2%2B-E87D0D.svg)](https://www.blender.org/download/) [![License: MIT](https://img.shields.io/badge/license-MIT-2ea44f.svg)](LICENSE)

**Blender Arwaky** is an open-source Blender automation runtime for MCP clients, agentic coding workflows, and technical artists. A validated dispatcher connects MCP and CLI clients to the same action catalog.

> Blender Python execution is powerful and is not a complete security sandbox. Use disposable workspaces, save important `.blend` files, and isolate untrusted workflows.

## Why use it?

Blender Arwaky is designed for **deterministic Blender automation, discoverable schemas, CLI/MCP parity, and governed local execution**. It is not a hosted SaaS product, bundled LLM, or complete wrapper for every Blender operator.

## Installation

### Requirements

Install Blender 5.2+, Python 3.10+, and [`uv`](https://docs.astral.sh/uv/). Blender 5.2 LTS is the supported runtime baseline for Arwaky.

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

## Canonical action catalog

The catalog below lists every valid CLI action and its action-specific parameters. Names use CLI `kebab-case`; MCP/API clients use the corresponding `snake_case` action name. Common flags are documented separately below the table. Optional Blender-Python providers are managed through the same catalog; they are not imported or executed implicitly.

| No. | Category | Action | Parameters | Description |
|---:|---|---|---|---|
| 1 | gateway | `execute-blender-code` | `--code` (string; required) | Execute validated Blender Python code |
| 2 | scene | `get-scene-info` | <none> | Full scene metadata — object count, frame range, resolution, render engine |
| 3 | scene | `cleanup-scene` | `--mode` (string; required; values: all, objects, meshes) | Remove objects from scene by mode |
| 4 | scene | `list-scene-objects` | `--include-hidden` (bool)<br>`--object-type` (string)<br>`--limit` (int) | List scene objects with optional visibility and type filters |
| 5 | scene | `get-object-hierarchy` | `--object-name` (string)<br>`--include-hidden` (bool)<br>`--max-depth` (int) | Inspect parent-child hierarchy for one object or the scene roots |
| 6 | scene | `undo` | <none> | Undo the most recent Blender edit operation |
| 7 | scene | `redo` | <none> | Redo the most recently undone Blender edit operation |
| 8 | object | `get-object-info` | `--object-name` (string; required) | Get details of a specific object — location, rotation, scale, modifiers, materials |
| 9 | object | `create-primitive` | `--primitive-type` (string; required; values: SPHERE, CUBE, CYLINDER, PLANE, CONE, TORUS)<br>`--location` (number[3])<br>`--scale` (number[3])<br>`--name` (string) | Create a new primitive mesh object |
| 10 | object | `set-object-transform` | `--object-name` (string; required)<br>`--location` (number[3])<br>`--rotation` (number[3])<br>`--scale` (number[3]) | Update object transform — location, rotation, or scale |
| 11 | object | `delete-object` | `--object-name` (string; required) | Remove an object from the scene |
| 12 | object | `set-material` | `--object-name` (string; required)<br>`--material-name` (string; required) | Assign a material to an object |
| 13 | object | `create-material` | `--material-name` (string; required)<br>`--base-color` (number[3])<br>`--metallic` (number)<br>`--roughness` (number)<br>`--reuse-existing` (bool) | Create or reuse a PBR material |
| 14 | object | `set-material-properties` | `--material-name` (string; required)<br>`--base-color` (number[3])<br>`--metallic` (number)<br>`--roughness` (number) | Update PBR properties of an existing material |
| 15 | object | `set-material-texture` | `--material-name` (string; required)<br>`--file-path` (string; required) | Assign a local image texture to a material base color |
| 16 | object | `apply-modifier` | `--object-name` (string; required)<br>`--modifier-name` (string; required) | Apply a modifier on an object |
| 17 | geometry_nodes | `inspect-geometry-node-group` | `--node-group-name` (string; required) | Inspect a Geometry Nodes group with bounded node, socket, and link metadata |
| 18 | geometry_nodes | `create-geometry-node-group` | `--node-group-name` (string; required)<br>`--object-name` (string) | Create or reuse a Geometry Nodes group and optionally bind it to an object modifier |
| 19 | geometry_nodes | `set-geometry-node-link` | `--node-group-name` (string; required)<br>`--from-node` (string; required)<br>`--from-socket` (string; required)<br>`--to-node` (string; required)<br>`--to-socket` (string; required) | Create a validated link between sockets in a Geometry Nodes group |
| 20 | geometry_nodes | `set-geometry-node-modifier` | `--object-name` (string; required)<br>`--node-group-name` (string; required) | Bind an existing Geometry Nodes group to an object modifier |
| 21 | animation | `get-animation-state` | `--object-name` (string; required)<br>`--limit` (int) | Inspect an object's bounded animation action, frame range, and F-curves |
| 22 | animation | `insert-object-keyframe` | `--object-name` (string; required)<br>`--frame` (int; required)<br>`--data-path` (string; required; values: location, rotation_euler, scale)<br>`--index` (int) | Insert a bounded keyframe for an object's location, rotation, or scale |
| 23 | animation | `set-timeline-range` | `--frame-start` (int; required)<br>`--frame-end` (int; required)<br>`--current-frame` (int) | Set the scene timeline frame range with bounded integer values |
| 24 | animation | `list-object-keyframes` | `--object-name` (string; required)<br>`--limit` (int) | List an object's bounded F-curve keyframe points |
| 25 | mesh | `get-mesh-statistics` | `--object-name` (string; required) | Inspect bounded mesh vertex, edge, polygon, normal, and UV statistics |
| 26 | mesh | `validate-mesh` | `--object-name` (string; required)<br>`--limit` (int) | Run bounded mesh validation for loose, degenerate, and non-manifold geometry |
| 27 | mesh | `perform-mesh-edit-operation` | `--object-name` (string; required)<br>`--operation` (string; required; values: recalculate_normals, triangulate, remove_doubles) | Perform one bounded edit-mode-independent mesh cleanup operation |
| 28 | mesh | `ensure-mesh-uv-layer` | `--object-name` (string; required)<br>`--uv-layer-name` (string) | Create or reuse a named UV layer on a mesh object |
| 29 | render | `configure-camera` | `--camera-ref` (string)<br>`--focal-length` (number)<br>`--sensor-fit` (string; values: AUTO, HORIZONTAL, VERTICAL)<br>`--framing-target` (string)<br>`--set-active` (bool)<br>`--depth-of-field-enabled` (bool)<br>`--focus-distance` (number)<br>`--focus-object` (string)<br>`--aperture` (number)<br>`--create-if-missing` (bool) | Configure a Blender camera and optional depth of field |
| 30 | render | `setup-environment` | `--hdri-id` (string; required)<br>`--strength` (number) | Configure HDRI lighting using a local file resolved by the Asset feature |
| 31 | render | `get-viewport-screenshot` | `--filepath` (string)<br>`--max-size` (int)<br>`--view-angle` (string; values: PERSPECTIVE, TOP, FRONT, SIDE)<br>`--shading-mode` (string; values: WIREFRAME, SOLID, MATERIAL, RENDERED)<br>`--show-overlays` (bool)<br>`--focus-object` (string) | Capture AI-optimized viewport screenshot |
| 32 | render | `render` | `--output-path` (string; required)<br>`--resolution-x` (int)<br>`--resolution-y` (int) | Execute a full frame render |
| 33 | render | `set-render-settings` | `--engine` (string)<br>`--resolution-x` (int)<br>`--resolution-y` (int)<br>`--resolution-percentage` (int)<br>`--samples` (int)<br>`--use-transparent` (bool) | Configure bounded scene render settings without rendering |
| 34 | compositor | `inspect-compositor-nodes` | `--limit` (int) | Inspect a bounded compositor node graph for the active scene |
| 35 | compositor | `configure-compositor` | `--use-nodes` (bool; required) | Enable or disable compositor nodes for the active scene |
| 36 | compositor | `create-compositor-node` | `--node-type` (string; required; values: CompositorNodeRGB, CompositorNodeMixRGB, CompositorNodeBlur, CompositorNodeComposite, CompositorNodeViewer)<br>`--node-name` (string) | Create one allow-listed compositor node in the active scene |
| 37 | compositor | `set-compositor-link` | `--from-node` (string; required)<br>`--from-socket` (string; required)<br>`--to-node` (string; required)<br>`--to-socket` (string; required) | Create a validated link between compositor node sockets |
| 38 | vse | `inspect-sequence-editor` | `--limit` (int) | Inspect bounded VSE strips and channels for the active scene |
| 39 | vse | `create-sequence-strip` | `--strip-type` (string; required; values: COLOR, IMAGE, MOVIE, SOUND)<br>`--strip-name` (string; required)<br>`--filepath` (string)<br>`--channel` (int; required)<br>`--frame-start` (int; required)<br>`--frame-end` (int) | Create an allow-listed VSE strip from a validated local media path |
| 40 | vse | `remove-sequence-strip` | `--strip-name` (string; required) | Remove one named VSE strip from the active scene |
| 41 | vse | `render-sequence` | `--output-path` (string; required)<br>`--frame-start` (int)<br>`--frame-end` (int) | Render a bounded VSE frame range to a validated local output path |
| 42 | physics | `get-physics-state` | `--object-name` (string; required) | Inspect bounded rigid body and cloth state for one object |
| 43 | physics | `configure-rigid-body` | `--object-name` (string; required)<br>`--enabled` (bool; required)<br>`--body-type` (string; values: ACTIVE, PASSIVE)<br>`--mass` (number)<br>`--kinematic` (bool) | Configure rigid body simulation settings for one mesh object |
| 44 | physics | `configure-cloth-simulation` | `--object-name` (string; required)<br>`--enabled` (bool; required)<br>`--quality` (int)<br>`--pin-group` (string) | Configure bounded cloth simulation settings for one mesh object |
| 45 | physics | `bake-physics-simulation` | `--frame-start` (int)<br>`--frame-end` (int) | Bake a bounded physics cache for the active scene |
| 46 | physics | `clear-physics-bake` | <none> | Clear cached physics simulation data for the active scene |
| 47 | physics | `get-simulation-state` | `--object-name` (string; required) | Inspect bounded advanced simulation modifiers for one object |
| 48 | physics | `get-simulation-cache-status` | <none> | Inspect bounded physics cache range and bake state for the active scene |
| 49 | physics | `configure-particle-system` | `--object-name` (string; required)<br>`--enabled` (bool; required)<br>`--count` (int)<br>`--frame-start` (int)<br>`--frame-end` (int)<br>`--lifetime` (number)<br>`--physics-type` (string; values: NEWTON, KEYED, BOIDS, FLUID) | Configure one bounded particle system on a mesh object |
| 50 | physics | `configure-force-field` | `--object-name` (string; required)<br>`--enabled` (bool; required)<br>`--field-type` (string; values: FORCE, WIND, VORTEX, MAGNET, TURBULENCE)<br>`--strength` (number)<br>`--noise` (number) | Configure a bounded force field on an existing object |
| 51 | physics | `configure-fluid-domain` | `--object-name` (string; required)<br>`--enabled` (bool; required)<br>`--domain-type` (string; values: LIQUID, GAS)<br>`--resolution` (int)<br>`--cache-type` (string; values: REPLAY, MODULAR, FINAL) | Configure a bounded fluid domain modifier baseline on a mesh object |
| 52 | rigging | `inspect-armature` | `--object-name` (string; required)<br>`--limit` (int) | Inspect a bounded armature bone hierarchy and pose summary |
| 53 | rigging | `set-pose-bone-transform` | `--armature-name` (string; required)<br>`--bone-name` (string; required)<br>`--location` (number[3])<br>`--rotation-euler` (number[3])<br>`--scale` (number[3]) | Set a bounded transform on one named pose bone |
| 54 | rigging | `configure-bone-constraint` | `--armature-name` (string; required)<br>`--bone-name` (string; required)<br>`--constraint-type` (string; required; values: COPY_LOCATION, COPY_ROTATION, LIMIT_LOCATION, LIMIT_ROTATION)<br>`--enabled` (bool; required)<br>`--constraint-name` (string)<br>`--target-object` (string)<br>`--subtarget` (string) | Create, update, or remove one allow-listed bone constraint |
| 55 | rigging | `configure-shape-key` | `--object-name` (string; required)<br>`--shape-key-name` (string; required)<br>`--enabled` (bool; required)<br>`--value` (number)<br>`--slider-min` (number)<br>`--slider-max` (number) | Create, update, or remove one bounded mesh shape key |
| 56 | rigging | `get-deformation-state` | `--object-name` (string; required) | Inspect bounded deformation modifiers, constraints, and shape keys |
| 57 | asset | `search-assets` | `--query` (string)<br>`--providers` (string[])<br>`--asset-type-filter` (string)<br>`--limit` (int)<br>`--page-token` (string) | Search configured asset providers |
| 58 | asset | `get-provider-metadata` | `--provider` (string; required)<br>`--asset-id` (string; required) | Get normalized metadata for a provider asset |
| 59 | asset | `download-asset` | `--provider` (string; required)<br>`--asset-id` (string; required)<br>`--asset-type` (string; required)<br>`--cache-dir` (string; required)<br>`--resolution` (string)<br>`--overwrite-policy` (string)<br>`--max-size` (int)<br>`--background` (bool) | Download a provider asset into the validated local cache |
| 60 | asset | `extract-asset` | `--artifact-path` (string; required)<br>`--destination` (string; required)<br>`--max-entries` (int)<br>`--max-extracted-size` (int)<br>`--allow-symlinks` (bool) | Safely extract a downloaded asset archive |
| 61 | asset | `import-asset` | `--file-path` (string; required)<br>`--asset-type` (string; required)<br>`--target-collection` (string)<br>`--scale-normalization` (bool)<br>`--duplicate-policy` (string)<br>`--format-hint` (string) | Import a locally cached asset into Blender |
| 62 | asset | `import-glb` | `--file-path` (string; required)<br>`--object-name` (string) | Import a GLB/GLTF file into the scene |
| 63 | asset | `export-model` | `--object-name` (string; required)<br>`--file-path` (string; required)<br>`--export-format` (string; values: glb, fbx, obj) | Export a model to a file |
| 64 | asset | `place-asset` | `--asset-id` (string; required)<br>`--location` (number[3])<br>`--rotation` (number[3])<br>`--scale` (number[3]) | Place an asset in the scene at a specific position |
| 65 | launcher | `launch-blender` | `--filepath` (string)<br>`--mode` (string; values: interface, headless)<br>`--port` (int) | Start Blender with integration component active |
| 66 | launcher | `shutdown-blender` | `--force` (bool) | Gracefully shut down Blender with force termination fallback |
| 67 | launcher | `get-runtime-status` | <none> | Verify true Blender process liveness and readiness |
| 68 | launcher | `register-executable` | `--path` (string) | Locate and register the Blender executable path |
| 69 | job | `submit-task` | `--operation-type` (string; required)<br>`--correlation-id` (string)<br>`--metadata` (value) | Register a background task through the shared job lifecycle |
| 70 | job | `list-tasks` | <none> | List current and retained background task snapshots |
| 71 | job | `get-capacity-status` | <none> | Return background task capacity and available slots |
| 72 | job | `get-task-status` | `--task-id` (string; required) | Query the progress and status of a background task |
| 73 | job | `cancel-task` | `--task-id` (string; required) | Cancel a running background task |
| 74 | config | `get-config` | `--key` (string) | Retrieve BlenderArwaky configuration settings |
| 75 | config | `set-config` | `--key` (string; required)<br>`--value` (value; required) | Update a configuration setting |
| 76 | plugin | `create-character` | `--plugin-id` (string; default: mpfb2)<br>`--name` (string; default: MPFB_Human) | Create one human through the explicitly mapped MPFB2 provider service |
| 77 | plugin | `randomize-character` | `--plugin-id` (string; default: mpfb2)<br>`--name` (string; default: MPFB_RandomHuman)<br>`--seed` (int; default: 0) | Create a deterministic MPFB2 human from a bounded seeded phenotype randomization |
| 78 | plugin | `remove-character` | `--plugin-id` (string; default: mpfb2)<br>`--object-name` (string; required)<br>`--confirm` (global; required for destructive actions) | Remove a verified MPFB2 basemesh and its parent-child closure |
| 79 | plugin | `list-plugins` | <none> | List registered optional providers and their runtime capability metadata |
| 80 | plugin | `download-plugin` | `--plugin-id` (string; required)<br>`--source-url` (HTTPS string; required)<br>`--sha256` (string; required)<br>`--cache-path` (absolute path; required) | Download a plugin package over HTTPS into the local cache |
| 81 | plugin | `verify-plugin` | `--plugin-id` (string; required)<br>`--sha256` (string; required)<br>`--cache-path` (absolute path; required) | Verify SHA-256 and ZIP safety before installation |
| 82 | plugin | `install-plugin` | `--plugin-id` (string; required)<br>`--sha256` (string; required)<br>`--cache-path` (absolute path; required)<br>`--blender-path` (absolute path; required)<br>`--repository-id` (string; default: user_default)<br>`--extension-id` (string; required)<br>`--enable` (bool; default: true) | Verify and install an optional plugin through Blender 5.2 Extension System |
| 83 | plugin | `enable-plugin` | `--plugin-id` (string; required)<br>`--sha256` (string; required)<br>`--cache-path` (absolute path; required)<br>`--blender-path` (absolute path; required)<br>`--repository-id` (string; default: user_default)<br>`--extension-id` (string; required) | Enable an installed Blender extension through its explicit extension id |
| 84 | plugin | `disable-plugin` | `--plugin-id` (string; required)<br>`--blender-path` (absolute path; required)<br>`--extension-id` (string; required)<br>`--confirm` (global; required for destructive actions) | Disable an installed Blender extension |
| 85 | plugin | `remove-plugin` | `--plugin-id` (string; required)<br>`--blender-path` (absolute path; required)<br>`--extension-id` (string; required)<br>`--confirm` (global; required for destructive actions) | Remove an installed Blender extension |

## Global and common flags

These flags are available across the CLI surface and are intentionally kept outside the action table:

| Flag | Purpose |
|---|---|
| `--json` | Emit machine-readable JSON. |
| `--quiet` | Suppress non-error output. |
| `--verbose` | Show masked structural diagnostics. |
| `--color auto|always|never` | Set output color policy. |
| `--no-progress` | Disable progress hints. |
| `--confirm` | Confirm a destructive action. |
| `--filepath` | Select the active `.blend` file or runtime session where applicable. |

Use `blender-arwaky <action-kebab-case> --help` for the complete help of one action. Global flags control output, runtime context, or confirmation; the Parameters column contains only flags declared by that action's own schema.

### Optional plugin packages

Plugin packages are optional and are never required for the core runtime. For a provider such as MPFB2, obtain a release archive and its published SHA-256 digest from the provider's official release channel, then run the following controlled sequence:

```bash
uv run blender-arwaky download-plugin --plugin-id mpfb2 --source-url https://example.org/mpfb2.zip --sha256 <sha256> --cache-path /absolute/cache/mpfb2.zip
uv run blender-arwaky verify-plugin --plugin-id mpfb2 --sha256 <sha256> --cache-path /absolute/cache/mpfb2.zip
uv run blender-arwaky install-plugin --plugin-id mpfb2 --sha256 <sha256> --cache-path /absolute/cache/mpfb2.zip --blender-path /absolute/path/to/blender-5.2 --extension-id mpfb --enable
uv run blender-arwaky enable-plugin --plugin-id mpfb2 --sha256 <sha256> --cache-path /absolute/cache/mpfb2.zip --blender-path /absolute/path/to/blender-5.2 --extension-id mpfb
uv run blender-arwaky create-character --plugin-id mpfb2 --name ArwakyHuman
```

The package boundary enforces HTTPS, SHA-256 verification, absolute traversal-free paths, ZIP traversal protection, symlink rejection, atomic installation, and Blender 5.2 Extension System lifecycle control. Provider operations remain explicitly mapped actions; character creation and seeded randomization use MPFB2's public service APIs and never accept arbitrary Python source.

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

The matrix below uses values and capabilities stated in each project's current public repository or official documentation. `√` means documented support, `×` means explicitly unavailable or outside the project's stated scope, and `?` means unknown or not published. `CLI` means the project documents a command-line interface as an access surface; it does not count the number of commands. Numeric values are kept only where the source publishes them. Counts are not perfectly equivalent because projects may expose one tool per operation or group many operations behind one tool.

| Project | MCP tools | Actions / operations | Namespaces | CLI | `.mcpb` | Min. Blender | Headless | Addon/bridge | Dashboard | Async jobs | Assets | 3D generation | Geometry Nodes | VSE | VRM | Gaussian splats | Safety controls |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Blender Arwaky** | 5 | 85 | 16 | √ | × | 5.2+ | ? | √ | × | √ | √ | × | √ | √ | × | × | √ |
| [BlenderMCP by ahujasid][1] | ? | ? | ? | ? | ? | ? | ? | √ | ? | ? | √ | √ | ? | ? | ? | ? | ? |
| [Blender MCP Server by djeada][3] | 27 | ? | 7 | ? | ? | ? | √ | √ | ? | √ | ? | ? | ? | ? | ? | ? | √ |
| [Blender MCP by sandraschi][4] | 41* | 150+ | ? | ? | √ | ? | √ | √ | √ | ? | √ | √ | √ | √ | √ | ? | ? |
| [Blender Lab MCP Server][2] | ? | ? | ? | ? | √ | 5.1+ | ? | √ | ? | ? | ? | ? | √ | ? | ? | ? | × |

* The sandraschi repository headline states 41 portmanteau tools and 150+ operations; another README section states 48+ MCP tools. The published values are shown as reported, not normalized. `MCP tools` and `Actions / operations` remain separate because they measure interface entries versus grouped operations.

## Contributing

Bug reports, feature requests, and code contributions are welcome. See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the developer workflow.

## License

Blender Arwaky is released under the [MIT License](LICENSE).

## References

[1]: https://github.com/ahujasid/blender-mcp "BlenderMCP by ahujasid"
[2]: https://www.blender.org/lab/mcp-server/ "Blender Lab MCP Server"
[3]: https://github.com/djeada/blender-mcp-server "Blender MCP Server by djeada"
[4]: https://github.com/sandraschi/blender-mcp "Blender MCP by sandraschi"
