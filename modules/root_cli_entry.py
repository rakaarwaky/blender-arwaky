"""Bootstrap entry for blender-mcp CLI."""

import sys


def main() -> None:
    """Entry point for the blender-mcp CLI."""
    from modules.shared.src.common.surface_cli_command import CliCommandHandler

    sys.exit(CliCommandHandler.main())


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover
