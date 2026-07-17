# BlenderArwaky — Skill Guide

Reference for AI agents using BlenderArwaky. Use `read_skill_context(section="...")` to read specific sections.

Sections: `tools`, `commands`, `workflows`, `addon`, `troubleshooting`.

---

## Section: tools

4 MCP tools available:

| Tool | Purpose |
|------|---------|
| `execute_command` | Universal action executor — dispatches any action from the catalog |
| `list_commands` | Discover available actions and parameters |
| `read_skill_context` | Read SKILL.md sections for guidance |
| `health_check` | Verify Blender connectivity and system health |

### `execute_command`

```json
{
  "action": "action_name",
  "args": {"param": "value"}
}
```

### `list_commands`

```json
{"domain": "scene"}  // or "object", "viewport", "render", "io", "infrastructure", "all"
```

---

## Section: commands

### Scene Operations

| Action | Parameters | Description |
|--------|------------|-------------|
| `get_scene_info` | (none) | Full scene metadata |
| `cleanup_scene` | `mode`: "all", "objects", "meshes" | Remove objects |
| `setup_environment` | `hdri_id`, `strength` | Setup HDRI lighting |

### Object Operations

| Action | Parameters | Description |
|--------|------------|-------------|
| `get_object_info` | `object_name` | Object details |
| `create_primitive` | `primitive_type`, `location`, `scale`, `name` | Create primitive |
| `set_object_transform` | `object_name`, `location`, `rotation`, `scale` | Update transform |
| `delete_object` | `object_name` | Remove object |
| `set_material` | `object_name`, `material_name` | Assign material |
| `apply_modifier` | `object_name`, `modifier_name` | Apply modifier |
| `place_asset` | `asset_id`, `location`, `rotation`, `scale` | Position asset |

### Viewport & Render

| Action | Parameters | Description |
|--------|------------|-------------|
| `get_viewport_screenshot` | See below | AI-optimized screenshot |
| `render` | `output_path`, `resolution_x`, `resolution_y` | Full frame render |

### Import/Export

| Action | Parameters | Description |
|--------|------------|-------------|
| `import_glb` | `file_path`, `object_name` | Import GLB/GLTF |
| `export_model` | `object_name`, `file_path`, `export_format` | Export model |

### Code Execution

| Action | Parameters | Description |
|--------|------------|-------------|
| `execute_blender_code` | `code` | Run Python in Blender |

### Screenshot Parameters

| Parameter | Type | Default | Options |
|-----------|------|---------|---------|
| `max_size` | int | 800 | Max dimension in pixels |
| `view_angle` | string | `PERSPECTIVE` | `PERSPECTIVE`, `TOP`, `FRONT`, `SIDE` |
| `shading` | string | `MATERIAL` | `WIREFRAME`, `SOLID`, `MATERIAL`, `RENDERED` |
| `show_overlays` | bool | `true` | Toggle grid, axes, origins |
| `focus_object` | string | null | Object name to frame |

---

## Section: workflows

### Scene Discovery

```python
list_commands(domain="scene")
execute_command(action="get_scene_info")
```

### Create and Position Object

```python
execute_command(
    action="create_primitive",
    args={"primitive_type": "SPHERE", "location": [0, 0, 0]}
)
execute_command(
    action="set_object_transform",
    args={"object_name": "Sphere", "location": [2, 0, 1]}
)
```

### AI-Optimized Viewport Analysis

```python
# Top-down wireframe of specific object
execute_command(
    action="get_viewport_screenshot",
    args={"view_angle": "TOP", "shading": "WIREFRAME", "focus_object": "Table"}
)

# Front view with materials
execute_command(
    action="get_viewport_screenshot",
    args={"view_angle": "FRONT", "shading": "MATERIAL"}
)
```

### Import and Place Asset

```python
execute_command(action="import_glb", args={"file_path": "/path/to/model.glb"})
execute_command(action="place_asset", args={"asset_id": "model", "location": [0, 0, 0]})
```

### Custom Blender Code

```python
execute_command(
    action="execute_blender_code",
    args={"code": "import bpy; bpy.ops.mesh.primitive_monkey_add()"}
)
```

---

## Section: addon

### Blender Addon Architecture

| File | Purpose |
|------|---------|
| `__init__.py` | Registration, auto-start timer |
| `server.py` | TCP server (port 9876) |
| `operators.py` | Start/stop operators |
| `properties.py` | Scene properties, API keys |
| `ui.py` | Sidebar panel UI |
| `utils.py` | Screenshot, GLB import helpers |
| `polyhaven.py` | Poly Haven integration |
| `sketchfab.py` | Sketchfab integration |

**Key points:**
- Auto-starts on Blender load (30 retries × 2s)
- TCP server on port 9876
- Headless mode requires active camera for screenshots

---

## Section: troubleshooting

### Blender connection refused

**Fix:** Ensure Blender is running, addon enabled, server shows "Running on port 9876".

### No active camera for screenshot

**Fix:** In headless mode, set an active camera before taking screenshots. GUI mode uses viewport view.

### MCP server won't start

**Fix:** Circular import — import from source files, not barrel (`__init__.py`).

### Tools not showing up

**Fix:** Run `health_check` to verify. Check `tool_registry_handler.py` has all 4 tools.
