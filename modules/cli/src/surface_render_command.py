"""CLI render command — Execute full frame render.

FR-CLI-001: Routes to Dispatcher action render.
P0: Removes direct socket client and registry usage per issue #91.
P1: Normalizes results into Dispatcher result envelope.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(args: Any, dispatcher: IDispatcherAggregate) -> dict[str, Any]:
    """Handle render command: execute full frame render via Dispatcher → Gateway.

    P0: Replaces direct socket client usage with Dispatcher routing.
    P1: Returns normalized result envelope instead of raw transport payload.
    """
    params: dict[str, Any] = {
        "output_path": args.output,
        "resolution_x": args.resolution_x,
        "resolution_y": args.resolution_y,
    }

    request = ActionCommandVO(action_name="render", parameters=params)
    result = dispatcher.execute_action(request)
    # Render from normalized envelope
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "warnings": result.warnings,
        "error_category": result.error_category if not result.success else None,
    }
