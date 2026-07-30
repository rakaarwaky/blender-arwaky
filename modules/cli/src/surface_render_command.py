from typing import Any

from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO


def handle(args: Any, dispatcher: IDispatcherAggregate | None = None) -> CliResultVo:
    if dispatcher is None:
        return CliResultVo(success=False, error="Dispatcher aggregate not available", category="configuration_error", ref="cli-500")
    try:
        params: dict[str, object] = {"output_path": args.output, "resolution_x": args.resolution_x, "resolution_y": args.resolution_y}
        request = ActionCommandVO(action_name="render", parameters=params)
        envelope = dispatcher.execute_action(request)
        if envelope.success:
            return CliResultVo(success=True, message="Render started", data={"filepath": args.output})
        return CliResultVo(success=False, error=envelope.message or "Render failed", category=envelope.error_category or "unexpected", ref="cli-render")
    except Exception as exc:
        return CliResultVo(success=False, error=str(exc), category="unexpected", ref="cli-render")
