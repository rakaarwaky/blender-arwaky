# BlenderArwaky — Skill Guide

The skill guide for BlenderArwaky. Use `read_skill_context(section="...")` to
read specific sections. Sections: `setup`, `tools`, `commands`, `workflows`,
`addon`, `troubleshooting`.

---

## Section: setup

### 1. Prerequisites

- Blender 3.0+ (tested on 5.1)
- Python 3.10+

### 2. Install Project

```bash
cd /path/to/blender-arwaky
uv sync
```

### 3. Start Blender with Addon

1. Blender → Edit → Preferences → Add-ons
2. Install `blender_mcp_addon/` directory
3. Enable "Interface: Blender Arwaky"

The addon auto-starts a TCP server on port 9876 within 1-5 seconds.

### 4. Start MCP Server

```bash
cd /path/to/blender-arwaky
uv run python -m surfaces.mcp_server_entry
```

The server connects to the Blender addon and registers 4 MCP tools.

---

## Section: tools

BlenderArwaky exposes exactly **4 MCP tools** (Universal Surface Layer design):

### Tool 1: `execute_command`
Universal action executor. Dispatches any action from the command catalog.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `action` | string | yes | Action name from catalog |
| `args` | dict | no | Arguments for the action |

**Returns:** JSON string with result or error.

**Example:**
```json
{
  "action": "get_scene_info",
  "args": {}
}
```

### Tool 2: `list_commands`
Discovers available actions and their parameters.

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `domain` | string | no | Filter by domain: "scene", "object", "viewport", "render", "io", "infrastructure", or "all" |

### Tool 3: `read_skill_context`
Reads specific sections of this document (SKILL.md).

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `section` | string | no | Section name: "setup", "tools", "commands", "workflows", "addon", "troubleshooting". Default: all. |

### Tool 4: `health_check`
Verifies Blender connectivity and system health. No parameters.

**Returns:** JSON with Blender connection status, config info.

---

## Section: commands

### Commands Table

Actions available via `execute_command(action=..., args=...)`:

| Action | Domain | Parameters | Description |
|--------|--------|------------|-------------|
| `get_scene_info` | scene | (none) | Full scene metadata |
| `get_object_info` | object | `object_name` | Detailed info for a single object |
| `cleanup_scene` | scene | `mode` | Remove objects ("all", "objects", "meshes") |
| `setup_environment` | scene | `hdri_id`, `strength` | Setup HDRI + environment |
| `create_primitive` | object | `primitive_type`, `location`, `scale`, `name` | Create 3D primitive |
| `set_object_transform` | object | `object_name`, `location`, `rotation`, `scale` | Update transform |
| `delete_object` | object | `object_name` | Remove object |
| `set_material` | object | `object_name`, `material_name` | Assign material |
| `apply_modifier` | object | `object_name`, `modifier_name` | Apply modifier |
| `place_asset` | object | `asset_id`, `location`, `rotation`, `scale` | Position asset |
| `get_viewport_screenshot` | viewport | `max_size`, `view_angle`, `shading`, `show_overlays`, `focus_object` | AI-optimized screenshot |
| `render` | render | `output_path`, `resolution_x`, `resolution_y` | Full frame render |
| `import_glb` | io | `file_path`, `object_name` | Import GLB/GLTF |
| `export_model` | io | `object_name`, `file_path`, `export_format` | Export model |
| `execute_blender_code` | infrastructure | `code` | Run Python code |

### AI-Optimized Screenshots

The `get_viewport_screenshot` action supports parameters optimized for AI vision:

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `max_size` | int | 800 | Max dimension in pixels |
| `view_angle` | string | `PERSPECTIVE` | `PERSPECTIVE`, `TOP`, `FRONT`, `SIDE` |
| `shading` | string | `MATERIAL` | `WIREFRAME`, `SOLID`, `MATERIAL`, `RENDERED` |
| `show_overlays` | bool | `true` | Toggle grid, axes, origins |
| `focus_object` | string | null | Object name to frame |

---

## Section: workflows

### Workflow 1: Discover and Execute

```python
# Step 1: Discover scene commands
list_commands(domain="scene")

# Step 2: Get scene info
execute_command(action="get_scene_info")

# Step 3: Create a sphere
execute_command(
    action="create_primitive",
    args={"primitive_type": "SPHERE", "location": [0, 0, 0]}
)
```

### Workflow 2: AI-Optimized Viewport Analysis

```python
# Top-down wireframe view of a specific object
execute_command(
    action="get_viewport_screenshot",
    args={
        "view_angle": "TOP",
        "shading": "WIREFRAME",
        "show_overlays": false,
        "focus_object": "MyTable"
    }
)

# Front view with material shading
execute_command(
    action="get_viewport_screenshot",
    args={
        "view_angle": "FRONT",
        "shading": "MATERIAL",
        "max_size": 1200
    }
)
```

### Workflow 3: Asset Import

```python
# Import GLB model
execute_command(
    action="import_glb",
    args={"file_path": "/path/to/model.glb"}
)

# Place it in the scene
execute_command(
    action="place_asset",
    args={"asset_id": "model", "location": [0, 0, 0]}
)
```

### Workflow 4: Custom Blender Python

```python
execute_command(
    action="execute_blender_code",
    args={"code": "import bpy; bpy.ops.mesh.primitive_monkey_add()"}
)
```

---

## Section: addon

### Blender Addon — `blender_mcp_addon/`

The Blender-side plugin that runs a TCP socket server (port 9876) to receive
commands from the external MCP server.

**Key features:**
- Auto-starts on Blender load (persistent timer, 30 retries × 2s)
- Reads `config.yaml` (env var `BLENDERMCP_CONFIG_PATH` override)
- Injects environment variables from `.env.blendermcp`
- UI panel in View3D → Sidebar → BlenderArwaky

**Architecture:**
| File | Purpose |
|------|---------|
| `__init__.py` | Registration, auto-start timer |
| `server.py` | TCP server (BlenderArwakyServer) |
| `operators.py` | Operator buttons (start/stop) |
| `properties.py` | Scene properties (port, API keys) |
| `ui.py` | Panel and preferences UI |
| `utils.py` | Screenshot, GLB import, AABB helpers |
| `polyhaven.py` | Poly Haven integration |
| `sketchfab.py` | Sketchfab integration |

Install: zip `blender_mcp_addon/` and install via Blender Preferences,
or copy directory to `~/.config/blender/<version>/scripts/addons/`.

---

## Section: troubleshooting

### Blender connection refused
```
ERROR  Failed to connect to Blender after all retries
```
**Fix:** Ensure Blender is running AND the addon is enabled AND server is
connected (status shows "Running on port 9876" in sidebar panel).

### MCP server won't start
```
ImportError: cannot import name 'mcp' from partially initialized module
```
**Fix:** Circular import — modules should import directly from source files,
not from the barrel (`surfaces/__init__.py`).

### Config not found
```
Warning: BLENDERMCP_CONFIG_PATH=... not found
```
**Fix:** Set `BLENDERMCP_CONFIG_PATH` to absolute path of `config.yaml`:
```bash
export BLENDERMCP_CONFIG_PATH=/path/to/blender-arwaky/config.yaml
```

### Tools not showing up
**Fix:** Verify `surfaces/tool_registry_handler.py` has all 4 tools registered.
Run `health_check` to see tool count.

### No active camera for screenshot
```
RuntimeError: No active camera in scene
```
**Fix:** In headless mode, you must set an active camera before taking screenshots.
In GUI mode, screenshots use the current viewport view (no camera needed).
