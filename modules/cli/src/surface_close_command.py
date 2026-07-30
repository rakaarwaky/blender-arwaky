"""CLI close command — Close active Blender instance.

FR-CLI-001: Routes to Dispatcher action shutdown_blender.
P0: Removes direct process kill, socket client, and registry usage per issue #91.
P1: Removes implicit save-on-close behavior.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(args: Any, dispatcher: IDispatcherAggregate) -> dict[str, Any]:
    """Handle close command: shutdown Blender via Dispatcher.

    P0: Replaces direct process kill and registry cleanup.
    P1: No implicit save — graceful/force escalation handled by Launcher.
    """
    params: dict[str, Any] = {"force": False}
    request = ActionCommandVO(action_name="shutdown_blender", parameters=params)
    result = dispatcher.execute_action(request)
    # Render from normalized envelope
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "warnings": result.warnings,
        "error_category": result.error_category if not result.success else None,
    }
