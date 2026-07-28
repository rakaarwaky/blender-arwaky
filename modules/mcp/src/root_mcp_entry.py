"""Bootstrap entry for blender-mcp MCP server."""


def main() -> None:
    """Entry point for the blender-mcp MCP server."""
    from modules.mcp.src.surface_server_start import ServerStartHandler

    ServerStartHandler.main()


if __name__ == "__main__":
    main()
