from typing import Any

from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.dispatcher.taxonomy_action_command_vo import ActionCommandVO
from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS


def _validate_action(action: str, params: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for domain_actions in DISPATCHER_ACTION_SCHEMAS.values():
        if action in domain_actions:
            schema = domain_actions[action]
            schema_params = schema.get("parameters", {})
            if isinstance(schema_params, dict):
                for param_name, param_spec in schema_params.items():
                    if isinstance(param_spec, dict) and param_spec.get("required", False) and (param_name not in params or params[param_name] is None):
                        errors.append(f"Missing required parameter: '{param_name}'")
                    if isinstance(param_spec, dict) and "enum" in param_spec and param_name in params:
                        allowed = param_spec["enum"]
                        if isinstance(allowed, list) and params[param_name] not in allowed:
                            errors.append(f"Invalid value for '{param_name}': '{params[param_name]}'. Allowed: {', '.join(allowed)}")
            return errors
    errors.append(f"Unknown action: {action}")
    return errors


def handle(args: Any, dispatcher: IDispatcherAggregate | None = None) -> CliResultVo:
    action = args.action
    params: dict[str, object] = args.params if isinstance(args.params, dict) else {}

    validation_errors = _validate_action(action, params)
    if validation_errors:
        return CliResultVo(success=False, error="; ".join(validation_errors), category="validation_error", ref="cli-400")

    if dispatcher is None:
        return CliResultVo(success=False, error="Dispatcher aggregate not available", category="configuration_error", ref="cli-500")
    try:
        request = ActionCommandVO(action_name=action, parameters=params)
        envelope = dispatcher.execute_action(request)
        return CliResultVo(success=envelope.success, message=envelope.message, error=None if envelope.success else envelope.message, category=envelope.error_category, warnings=list(envelope.warnings) if envelope.warnings else None, data=envelope.data)
    except Exception as exc:
        return CliResultVo(success=False, error=str(exc), category="unexpected", ref="cli-run")
