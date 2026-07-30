"""CLI run command — Execute any action on active Blender via Dispatcher.

FR-CLI-001: Routes all actions through Dispatcher → Gateway transport.
P0: Removes direct socket client and registry usage per issue #91.
P1: Normalizes results into Dispatcher result envelope.
"""

from __future__ import annotations

import json
from typing import Any

from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(args: Any, dispatcher: IDispatcherAggregate) -> dict[str, Any]:
    """Handle run command: execute action via Dispatcher → Gateway → Blender.

    P0: Replaces direct socket client usage with Dispatcher routing.
    P1: Returns normalized result envelope instead of raw transport payload.
    """
    action = args.action
    params = args.params if isinstance(args.params, dict) else json.loads(args.params)

    request = ActionCommandVO(action_name=action, parameters=params)
    result = dispatcher.execute_action(request)
    # Render from normalized envelope
    return {
        "success": result.success,
        "message": result.message,
        "data": result.data,
        "warnings": result.warnings,
        "error_category": result.error_category if not result.success else None,
    }
