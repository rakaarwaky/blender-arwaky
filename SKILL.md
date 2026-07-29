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

Complete action catalog. All actions available via:
- **CLI** — direct command per action (`blender-arwaky scene-info`, `blender-arwaky render`, dll.)
- **MCP** — single `execute_command` tool with `action` argument (`execute_command(action="get_scene_info")`)

### Scene

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `get_scene_info` | `scene-info` | (none) | Full scene metadata |
| `cleanup_scene` | `scene-cleanup` | `mode`: "all" \| "objects" \| "meshes" | Remove objects |
| `setup_environment` | `set-env` | `hdri_id`, `strength` | Setup HDRI lighting |

### Object

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `get_object_info` | `object-info` | `object_name` | Object details |
| `create_primitive` | `create` | `primitive_type`, `location`, `scale`, `name` | Create primitive |
| `set_object_transform` | `set-transform` | `object_name`, `location`, `rotation`, `scale` | Update transform |
| `delete_object` | `delete` | `object_name` | Remove object |
| `set_material` | `set-material` | `object_name`, `material_name` | Assign material |
| `apply_modifier` | `apply-modifier` | `object_name`, `modifier_name` | Apply modifier |
| `place_asset` | `place-asset` | `asset_id`, `location`, `rotation`, `scale` | Position asset |

### Viewport

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `get_viewport_screenshot` | `screenshot` | [screenshot params](#screenshot-parameters) | AI-optimized screenshot |

### Render

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `render` | `render` | `output_path`, `resolution_x`, `resolution_y` | Full frame render |

### Import / Export

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `import_glb` | `import` | `file_path`, `object_name` | Import GLB/GLTF |
| `export_model` | `export` | `object_name`, `file_path`, `export_format` | Export model |

### Job

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `get_task_status` | `task-status` | `task_id` | Query render/compute task progress |
| `cancel_task` | `cancel-task` | `task_id` | Cancel running task |

### Config

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `get_config` | `config` | `key` (optional) | Get config value or all settings |
| `set_config` | `set-config` | `key`, `value` | Update config setting |

### Code Execution

| Action | CLI | Parameters | Description |
|--------|-----|------------|-------------|
| `execute_blender_code` | `run-code` | `code` | Run Python in Blender |

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

All workflows use `execute_command(action=..., args=...)` for MCP. CLI uses the direct command (see [commands](#section-commands)).

### Scene Discovery

```python
execute_command(action="get_scene_info")
```

### Create and Position Object

```python
execute_command(action="create_primitive", args={"primitive_type": "SPHERE", "location": [0, 0, 0]})
execute_command(action="set_object_transform", args={"object_name": "Sphere", "location": [2, 0, 1]})
```

### AI-Optimized Viewport Analysis

```python
execute_command(action="get_viewport_screenshot", args={"view_angle": "TOP", "shading": "WIREFRAME", "focus_object": "Table"})
execute_command(action="get_viewport_screenshot", args={"view_angle": "FRONT", "shading": "MATERIAL"})
```

### Import and Place Asset

```python
execute_command(action="import_glb", args={"file_path": "/path/to/model.glb"})
execute_command(action="place_asset", args={"asset_id": "model", "location": [0, 0, 0]})
```

### Submit Render and Check Status

```python
execute_command(action="render", args={"output_path": "/tmp/frame.png", "resolution_x": 1920, "resolution_y": 1080})
execute_command(action="get_task_status", args={"task_id": "<returned_task_id>"})
```

### Custom Blender Code

```python
execute_command(action="execute_blender_code", args={"code": "import bpy; bpy.ops.mesh.primitive_monkey_add()"})
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
