"""CLI status command — Show active Blender status.

FR-CLI-001: Routes to Dispatcher action get_runtime_status.
P0: Removes direct PID check and registry usage per issue #91.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(_args: Any, dispatcher: IDispatcherAggregate) -> dict[str, Any]:
    """Handle status command: get true runtime status via Launcher.

    P0: Replaces local registry and PID check with Launcher liveness verification.
    """
    request = ActionCommandVO(action_name="get_runtime_status", parameters={})
    result = dispatcher.execute_action(request)
    # Render from normalized envelope
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "warnings": result.warnings,
        "error_category": result.error_category if not result.success else None,
    }
