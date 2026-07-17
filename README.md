# BlenderArwaky

**Connect Blender to AI agents through the Model Context Protocol.**

BlenderArwaky bridges [Blender 3D](https://www.blender.org/) with any MCP-compatible client — Claude Desktop, Cursor, Continue.dev, or custom agents. Control scenes, import assets, render, and execute Blender Python — all through 4 universal MCP tools.

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Blender 3.0+](https://img.shields.io/badge/Blender-3.0%2B-orange.svg)](https://www.blender.org/)
[![CI](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml/badge.svg)](https://github.com/rakaarwaky/blender-arwaky/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/rakaarwaky/blender-arwaky/branch/main/graph/badge.svg)](https://codecov.io/gh/rakaarwaky/blender-arwaky)
[![Code style: ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

---

## Features

- **4 Universal MCP Tools** — Minimal surface, maximum power via command catalog dispatch
- **15+ Actions** — Scene ops, object manipulation, rendering, import/export, code execution
- **2 Asset Providers** — Poly Haven (HDRI/textures/models), Sketchfab
- **AI-Optimized Screenshots** — View presets, shading modes, overlay control, object focus
- **Blender Addon** — TCP server with auto-start, UI panel, and API key management
- **Clean Architecture** — AES 6-domain layering with full dependency inversion

---

## Architecture

```
surfaces/        → MCP tools & CLI entry points (4 tools only)
agent/           → DI container, orchestrators, experts
capabilities/    → Use cases: scene ops, asset search, rendering
infrastructure/  → Adapters: Blender socket, API clients, telemetry
contract/        → Ports & protocols (interfaces between layers)
taxonomy/        → Foundation: data structures, config, command catalog
```

> **Layer rule:** `surfaces → agent → capabilities → infrastructure → contract → taxonomy`
> Each layer only imports from layers below it. Taxonomy is pure data, no business logic.

---

## Quick Start

### Prerequisites

- **Blender 3.0+** (tested on 5.1)
- **Python 3.10+**

### 1. Install

```bash
git clone https://github.com/rakaarwaky/blender-arwaky.git
cd blender-arwaky
uv sync
```

### 2. Install Blender Addon

1. Open Blender → Edit → Preferences → Add-ons
2. Install `blender_mcp_addon/` directory
3. Enable **"Interface: Blender Arwaky"**

The addon auto-starts a TCP server on port `9876` within 1–5 seconds.

### 3. Start MCP Server

```bash
uv run python -m surfaces.mcp_server_entry
```

### 4. Configure Your MCP Client

Add to your client's MCP configuration:

```json
{
  "mcpServers": {
    "blender-arwaky": {
      "command": "uv",
      "args": [
        "--directory", "/path/to/blender-arwaky",
        "run", "blender-arwaky"
      ]
    }
  }
}
```

---

## MCP Tools

BlenderArwaky exposes exactly **4 MCP tools** (Universal Surface Layer design):

| Tool | Purpose |
|------|---------|
| `execute_command` | Universal action executor — dispatches any action from the command catalog |
| `list_commands` | Discover available actions and their parameters |
| `read_skill_context` | Read SKILL.md sections for agent guidance |
| `health_check` | Verify Blender connectivity and system health |

---

## Command Catalog

Actions available via `execute_command(action=..., args=...)`:

| Action | Domain | Description |
|--------|--------|-------------|
| `get_scene_info` | scene | Full scene metadata (objects, counts, engine) |
| `get_object_info` | object | Detailed info for a single object |
| `cleanup_scene` | scene | Remove all objects from scene |
| `setup_environment` | scene | Setup HDRI + environment lighting |
| `create_primitive` | object | Create basic 3D primitives (cube, sphere, etc.) |
| `set_object_transform` | object | Update object location/rotation/scale |
| `delete_object` | object | Remove an object from the scene |
| `set_material` | object | Assign a material to an object |
| `apply_modifier` | object | Apply modifiers (subsurf, bevel, etc.) |
| `place_asset` | object | Position an imported asset |
| `get_viewport_screenshot` | viewport | Capture 3D viewport (AI-optimized) |
| `render` | render | Execute full frame render to file |
| `import_glb` | io | Import GLB/GLTF model |
| `export_model` | io | Export model to file |
| `execute_blender_code` | infrastructure | Run Python code in Blender |

---

## AI-Optimized Screenshots

The `get_viewport_screenshot` action supports AI agent-specific parameters:

```json
{
  "action": "get_viewport_screenshot",
  "args": {
    "max_size": 800,
    "view_angle": "TOP",
    "shading": "WIREFRAME",
    "show_overlays": false,
    "focus_object": "MyTable"
  }
}
```

| Parameter | Options | Purpose |
|-----------|---------|---------|
| `view_angle` | `PERSPECTIVE`, `TOP`, `FRONT`, `SIDE` | Standard orthographic views |
| `shading` | `WIREFRAME`, `SOLID`, `MATERIAL`, `RENDERED` | Viewport shading mode |
| `show_overlays` | `true`/`false` | Toggle grid, axes, origins |
| `focus_object` | Object name | Frame specific object |

---

## Testing

```bash
# Full test suite
uv run pytest

# Only unit tests
uv run pytest -m unit

# With coverage
uv run pytest --cov=src --cov-report=term
```

455+ tests across unit, integration, and functional categories.

---

## Project Structure

```
blender-arwaky/
├── src/
│   ├── surfaces/          # MCP tools & entry points
│   ├── agent/             # DI container & orchestrators
│   ├── capabilities/      # Business logic (use cases)
│   ├── infrastructure/    # External adapters
│   ├── contract/          # Ports & protocol interfaces
│   └── taxonomy/          # Data structures & command catalog
├── blender_mcp_addon/     # Blender addon (TCP server)
├── tests/                 # Unit, integration, functional tests
├── AGENT.md               # Developer guide
├── SKILL.md               # MCP skill documentation
└── TEST.md                # Testing guide
```

---

## Configuration

```yaml
blender:
  executable_path: "/path/to/blender"
  host: "localhost"
  port: 9876

server:
  transport: "stdio"    # or "sse"
  log_dir: "log"
```

---

## License

[MIT License](LICENSE) — Originally by Siddharth Ahuja, extended by Raka Arwaky.
