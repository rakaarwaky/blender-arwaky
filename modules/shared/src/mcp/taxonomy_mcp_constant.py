"""Embedded help content shared by MCP and CLI-facing surfaces.

This module is deliberately filesystem-free. Runtime help must remain available
when the package is installed through PyPI/uvx or bundled as an addon artifact.
"""

from __future__ import annotations

HELP_TOPICS = ("overview", "mcp", "cli", "actions", "safety", "examples")
CORE_TOOLS = (
    "execute_command",
    "list_commands",
    "health_check",
    "get_config",
    "help",
)

_EMBEDDED_SECTIONS: dict[str, str] = {
    "overview": (
        "Blender Arwaky exposes five MCP tools. Use help for this guide, "
        "list_commands to discover canonical actions, execute_command to run an action, "
        "health_check to inspect runtime health, and get_config to read configuration."
    ),
    "mcp": (
        "MCP usage:\n"
        "1. Configure an MCP client to start `uv run blender-mcp`.\n"
        "2. Call `list_commands` to inspect action names, owners, schemas, and catalog_version.\n"
        '3. Call `execute_command` with `{"action": "<action>", "args": {...}}`.\n'
        "4. Use `health_check` before long operations and `get_config` for non-secret settings.\n"
        "Only the five core tools are exposed by the MCP server; feature actions are dispatched through execute_command."
    ),
    "cli": (
        "CLI usage:\n"
        "- Start the server: `uv run blender-mcp`.\n"
        "- Inspect the CLI: `uv run blender-arwaky --help`.\n"
        "- Run any action generically: `uv run blender-arwaky run --filepath scene.blend --action <action> --params '{...}'`.\n"
        "- Use dedicated action commands shown by `uv run blender-arwaky --help`.\n"
        "- Add `--json` for machine-readable output and `--confirm` for destructive actions.\n"
        "The CLI and MCP submit the same canonical action names to the dispatcher."
    ),
    "actions": (
        "Canonical actions are grouped by owner in list_commands. Each action is available "
        "through execute_command and the corresponding CLI command surface. The catalog is "
        "versioned deterministically so clients can detect schema drift."
    ),
    "safety": (
        "Safety contract:\n"
        "- File paths, archives, code, and secrets are validated or redacted by the shared security layer.\n"
        "- Responses use bounded envelopes with tracking_id and catalog metadata.\n"
        "- Destructive CLI commands require --confirm.\n"
        "- Do not send credentials or untrusted code unless the configured security policy permits the operation."
    ),
    "examples": (
        "Examples:\n"
        'MCP: execute_command(action="create_primitive", args={"primitive_type": "CUBE", "name": "DemoCube"}).\n'
        'MCP: execute_command(action="configure_camera", args={"focal_length": 50, "set_active": true}).\n'
        'MCP: execute_command(action="list_scene_objects", args={"object_type": "MESH", "limit": 20}).\n'
        'MCP: execute_command(action="create_geometry_node_group", args={"node_group_name": "ArwakyGeometry", "object_name": "Cube"}).\n'
        'MCP: execute_command(action="insert_object_keyframe", args={"object_name": "Cube", "frame": 24, "data_path": "location"}).\n'
        'MCP: execute_command(action="get_mesh_statistics", args={"object_name": "Cube"}).\n'
        'MCP: execute_command(action="create_compositor_node", args={"node_type": "CompositorNodeRGB", "node_name": "Wave3RGB"}).\n'
        'MCP: execute_command(action="create_sequence_strip", args={"strip_type": "COLOR", "strip_name": "Wave3Color", "channel": 1, "frame_start": 1, "frame_end": 24}).\n'
        'MCP: execute_command(action="configure_rigid_body", args={"object_name": "Cube", "enabled": true, "body_type": "ACTIVE", "mass": 1.0}).\n'
        'MCP: execute_command(action="configure_particle_system", args={"object_name": "Cube", "enabled": true, "count": 1000, "frame_start": 1, "frame_end": 120, "lifetime": 40, "physics_type": "NEWTON"}).\n'
        'MCP: execute_command(action="configure_force_field", args={"object_name": "Cube", "enabled": true, "field_type": "WIND", "strength": 10}).\n'
        'MCP: execute_command(action="configure_fluid_domain", args={"object_name": "Cube", "enabled": true, "domain_type": "LIQUID", "resolution": 64, "cache_type": "REPLAY"}).\n'
        'MCP: execute_command(action="get_simulation_cache_status", args={}).\n'
        'MCP: execute_command(action="inspect_armature", args={"object_name": "Rig", "limit": 100}).\n'
        'MCP: execute_command(action="set_pose_bone_transform", args={"armature_name": "Rig", "bone_name": "Bone", "rotation_euler": [0, 0, 0.5]}).\n'
        'MCP: execute_command(action="configure_bone_constraint", args={"armature_name": "Rig", "bone_name": "Bone", "constraint_type": "COPY_ROTATION", "enabled": true, "target_object": "Target"}).\n'
        'MCP: execute_command(action="configure_shape_key", args={"object_name": "Cube", "shape_key_name": "Smile", "enabled": true, "value": 0.5, "slider_min": 0, "slider_max": 1}).\n'
        'MCP: execute_command(action="get_deformation_state", args={"object_name": "Cube"}).\n'
        'MCP: execute_command(action="create_material", args={"material_name": "BlueMetal", "base_color": [0.05, 0.2, 0.8, 1], "metallic": 0.8}).\n'
        'MCP: execute_command(action="set_render_settings", args={"resolution_x": 1920, "resolution_y": 1080, "samples": 64}).\n'
        'MCP: execute_command(action="submit_task", args={"operation_type": "render", "metadata": {"scene": "demo"}}).\n'
        "CLI: `uv run blender-arwaky camera-config --focal-length 50 --set-active`.\n"
        "CLI: `uv run blender-arwaky search-assets --query chair --provider Polyhaven --json`.\n"
        "CLI: `uv run blender-arwaky run --filepath scene.blend --action get_scene_info --params '{}' --json`."
    ),
}


HELP_SECTIONS = _EMBEDDED_SECTIONS
"""MCP constants — tool names, default server values, envelope schema."""

DEFAULT_SERVER_NAME = "blender-arwaky"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8080

TOOL_EXECUTE_COMMAND = "execute_command"
TOOL_LIST_COMMANDS = "list_commands"
TOOL_HELP = "help"
TOOL_HEALTH_CHECK = "health_check"

# Envelope schema keys
MCP_KEY_TRACKING_ID = "tracking_id"
MCP_KEY_TOOL = "tool"
MCP_KEY_SUCCESS = "success"
MCP_KEY_DATA = "data"
MCP_KEY_ERROR_CATEGORY = "error_category"
MCP_KEY_MESSAGE = "message"
MCP_KEY_WARNINGS = "warnings"
MCP_KEY_METADATA = "metadata"
MCP_KEY_PROTOCOL_VERSION = "protocol_version"
MCP_KEY_CATALOG_VERSION = "catalog_version"
MCP_KEY_VALUE = "value"
MCP_KEY_TRUNCATED = "truncated"
MCP_KEY_NOTE = "note"

# Envelope defaults
MCP_PROTOCOL_VERSION = "1.0"
MCP_CATALOG_VERSION_UNKNOWN = "unknown"
MCP_EXECUTION_FAILED_MESSAGE = "Execution failed"

# Validation messages
MCP_ACTION_REQUIRED_ERROR = "action is required"

# Truncation messages
MCP_TRUNCATION_NOTE_TEMPLATE = "Response exceeded {max_size} bytes"
MCP_RESPONSE_TRUNCATED_MESSAGE = "Response truncated due to size limit"
