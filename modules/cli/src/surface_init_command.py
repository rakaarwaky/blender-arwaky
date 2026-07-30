"""CLI init command — Start Blender with a file.

FR-CLI-001: Routes to Dispatcher action launch_blender.
P0: Removes direct process spawn and registry usage per issue #91.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(args: Any, dispatcher: IDispatcherAggregate) -> dict[str, Any]:
    """Handle init command: start Blender with the given file via Dispatcher.

    P0: Replaces direct process spawn and registry logic.
    Routes to Launcher aggregate through Dispatcher.
    """
    params: dict[str, Any] = {
        "filepath": args.filepath,
        "mode": args.mode if args.mode else "headless",
        "port": args.port if args.port else 9876,
    }
    request = ActionCommandVO(action_name="launch_blender", parameters=params)
    result = dispatcher.execute_action(request)
    # Render from normalized envelope
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "warnings": result.warnings,
        "error_category": result.error_category if not result.success else None,
    }
