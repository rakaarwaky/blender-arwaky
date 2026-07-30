"""CLI screenshot command — Capture viewport screenshot.

FR-CLI-001: Routes to Dispatcher action get_viewport_screenshot.
P0: Removes direct socket client and registry usage per issue #91.
P1: Normalizes results into Dispatcher result envelope.
"""

from __future__ import annotations

from typing import Any

from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(args: Any, dispatcher: IDispatcherAggregate) -> dict[str, Any]:
    """Handle screenshot command: capture viewport via Dispatcher → Gateway.

    P0: Replaces direct socket client usage with Dispatcher routing.
    P1: Returns normalized result envelope instead of raw transport payload.
    """
    params: dict[str, Any] = {
        "filepath": args.output,
        "max_size": args.max_size,
        "view_angle": args.view_angle,
        "shading_mode": args.shading,
        "show_overlays": not args.no_overlays,
        "focus_object": args.focus_object,
    }

    request = ActionCommandVO(action_name="get_viewport_screenshot", parameters=params)
    result = dispatcher.execute_action(request)
    # Render from normalized envelope
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "warnings": result.warnings,
        "error_category": result.error_category if not result.success else None,
    }
