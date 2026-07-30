from modules.mcp.src import (
    surface_execute_command,
    surface_get_config,
    surface_health_check,
    surface_list_commands,
    surface_prompt_register,
    surface_read_skill,
    surface_scene_tools,
    surface_server_instance,
    surface_server_start,
    surface_tool_registry,
)

_surfaces = (
    surface_execute_command,
    surface_get_config,
    surface_health_check,
    surface_list_commands,
    surface_prompt_register,
    surface_read_skill,
    surface_scene_tools,
    surface_server_instance,
    surface_server_start,
    surface_tool_registry,
)


def main() -> None:
    """Entry point for the blender-mcp MCP server."""
    from modules.mcp.src.surface_server_start import ServerStartSurface

    ServerStartSurface.main()


if __name__ == "__main__":
    main()

