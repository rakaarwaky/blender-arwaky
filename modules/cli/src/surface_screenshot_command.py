from typing import Any

from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(args: Any, dispatcher: IDispatcherAggregate | None = None) -> CliResultVo:
    if dispatcher is None:
        return CliResultVo(success=False, error="Dispatcher aggregate not available", category="configuration_error", ref="cli-500")
    try:
        params: dict[str, object] = {"filepath": args.output, "max_size": args.max_size, "view_angle": args.view_angle, "shading_mode": args.shading, "show_overlays": not args.no_overlays, "focus_object": args.focus_object}
        request = ActionCommandVO(action_name="get_viewport_screenshot", parameters=params)
        envelope = dispatcher.execute_action(request)
        if envelope.success:
            return CliResultVo(success=True, message="Screenshot saved", data={"filepath": args.output})
        return CliResultVo(success=False, error=envelope.message or "Screenshot failed", category=envelope.error_category or "unexpected", ref="cli-screenshot")
    except Exception as exc:
        return CliResultVo(success=False, error=str(exc), category="unexpected", ref="cli-screenshot")
