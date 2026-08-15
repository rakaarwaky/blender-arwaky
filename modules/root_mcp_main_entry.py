"""MCP server composition root."""

from modules.mcp.src import (
    surface_execute_command,
    surface_get_config,
    surface_health_check,
    surface_help,
    surface_list_commands,
    surface_prompt_register,
    surface_scene_tools,
    surface_server_instance,
    surface_server_start,
    surface_tool_registry,
)

_surfaces = (
    surface_execute_command,
    surface_get_config,
    surface_health_check,
    surface_help,
    surface_list_commands,
    surface_prompt_register,
    surface_scene_tools,
    surface_server_instance,
    surface_server_start,
    surface_tool_registry,
)


def main() -> None:
    """Start the MCP server with the composed feature container."""
    from modules.mcp.src.root_mcp_container import create_mcp_feature
    from modules.mcp.src.surface_server_start import ServerStartSurface

    mcp_container = create_mcp_feature()
    ServerStartSurface.main(container=mcp_container)


if __name__ == "__main__":
    main()
