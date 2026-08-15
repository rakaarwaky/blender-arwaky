"""Standalone CLI entry point for BlenderArwaky.

The CLI is a thin surface: it parses token shape, maps public flag names to
canonical action parameters, routes one action to the owning dispatcher, and
renders a safe result.
"""

from __future__ import annotations

import argparse
import difflib
import json
import logging
import re
import sys

from modules.cli.src import (
    surface_action_command,
    surface_close_command,
    surface_init_command,
    surface_render_command,
    surface_screenshot_command,
    surface_status_command,
)
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate

logger = logging.getLogger(__name__)

EXIT_SUCCESS = 0
EXIT_VALIDATION = 2
EXIT_UPSTREAM = 3
EXIT_UNEXPECTED = 4

ERROR_CATEGORIES: dict[str, int] = {
    "validation_error": EXIT_VALIDATION,
    "confirmation": EXIT_VALIDATION,
    "confirmation_error": EXIT_VALIDATION,
    "unsupported": EXIT_UPSTREAM,
    "unsupported_error": EXIT_UPSTREAM,
    "blocked": EXIT_UPSTREAM,
    "blocked_error": EXIT_UPSTREAM,
    "configuration_error": EXIT_VALIDATION,
    "not_found": EXIT_UPSTREAM,
    "not_found_error": EXIT_UPSTREAM,
    "capacity": EXIT_UPSTREAM,
    "timeout": EXIT_UPSTREAM,
    "security_violation": EXIT_UPSTREAM,
    "connection": EXIT_UPSTREAM,
    "state": EXIT_UPSTREAM,
    "task": EXIT_UPSTREAM,
    "upstream": EXIT_UPSTREAM,
    "execution_error": EXIT_UPSTREAM,
}


class CliArgumentParser(argparse.ArgumentParser):
    """Argument parser with a closest-command hint for invalid subcommands."""

    def error(self, message: str) -> None:
        match = re.search(r"invalid choice: '([^']+)'", message)
        if match and self._subparsers_action is not None:
            choices = list(self._subparsers_action.choices)
            suggestion = difflib.get_close_matches(match.group(1), choices, n=1, cutoff=0.5)
            if suggestion:
                message += f". Did you mean '{suggestion[0]}'?"
        super().error(message)

    @property
    def _subparsers_action(self) -> argparse._SubParsersAction | None:
        for action in self._actions:
            if isinstance(action, argparse._SubParsersAction):
                return action
        return None


def _exit_code(result: dict[str, object]) -> int:
    """Map result category to deterministic exit code."""
    if result.get("success"):
        return EXIT_SUCCESS
    return ERROR_CATEGORIES.get(str(result.get("category", "unexpected")), EXIT_UNEXPECTED)


def _add_common_flags(parser: argparse.ArgumentParser) -> None:
    """Add output flags to a parser without overriding root-level values."""
    parser.add_argument("--json", action="store_true", default=argparse.SUPPRESS, help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", default=argparse.SUPPRESS, help="Suppress non-error output")
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Show masked structural diagnostics",
    )
    parser.add_argument(
        "--color",
        choices=["auto", "always", "never"],
        default=argparse.SUPPRESS,
        help="Color policy for text output",
    )
    parser.add_argument(
        "--no-progress",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Disable progress hints",
    )
    parser.add_argument(
        "--confirm",
        action="store_true",
        default=argparse.SUPPRESS,
        help="Confirm destructive action",
    )


def _example(parser: argparse.ArgumentParser, text: str) -> None:
    parser.epilog = f"Example:\n  {text}"
    parser.formatter_class = argparse.RawDescriptionHelpFormatter


def _add_vector(parser: argparse.ArgumentParser, flag: str, dest: str, help_text: str) -> None:
    parser.add_argument(flag, dest=dest, nargs=3, type=float, metavar=("X", "Y", "Z"), help=help_text)


def _snake_to_kebab(value: str) -> str:
    """Convert canonical MCP/API names to their CLI command spelling."""
    return value.replace("_", "-")


def _schema_arg_options(name: str, spec: dict[str, object]) -> dict[str, object]:
    """Build argparse options from one canonical action parameter schema."""
    options: dict[str, object] = {
        "dest": name,
        "help": str(spec.get("description", name.replace("_", " "))),
    }
    if spec.get("required"):
        options["required"] = True
    if "enum" in spec:
        options["choices"] = list(spec["enum"])
    parameter_type = str(spec.get("type", "string"))
    if parameter_type == "boolean":
        options["action"] = "store_true"
        options["default"] = None
    elif parameter_type == "integer":
        options["type"] = int
    elif parameter_type == "number":
        options["type"] = float
    elif parameter_type == "array[number]":
        options["nargs"] = 3
        options["type"] = float
        options["metavar"] = ("X", "Y", "Z")
    elif parameter_type == "array[string]":
        options["action"] = "append"
    elif parameter_type == "any":
        options["type"] = str
    return options


def _snake_to_kebab(value: str) -> str:
    """Convert canonical MCP/API names to their CLI command spelling."""
    return value.replace("_", "-")


def _schema_arg_options(name: str, spec: dict[str, object]) -> dict[str, object]:
    """Build argparse options from one canonical action parameter schema."""
    options: dict[str, object] = {
        "dest": name,
        "help": str(spec.get("description", name.replace("_", " "))),
    }
    if spec.get("required"):
        options["required"] = True
    if "enum" in spec:
        options["choices"] = list(spec["enum"])
    parameter_type = str(spec.get("type", "string"))
    if parameter_type == "boolean":
        options["action"] = "store_true"
        options["default"] = None
    elif parameter_type == "integer":
        options["type"] = int
    elif parameter_type == "number":
        options["type"] = float
    elif parameter_type == "array[number]":
        options["nargs"] = 3
        options["type"] = float
        options["metavar"] = ("X", "Y", "Z")
    elif parameter_type == "array[string]":
        options["action"] = "append"
    elif parameter_type == "any":
        options["type"] = str
    return options


def _build_parser() -> CliArgumentParser:
    """Build one CLI command for every canonical dispatcher action."""
    from modules.shared.src.dispatcher.taxonomy_dispatcher_constant import DISPATCHER_ACTION_SCHEMAS

    parser = CliArgumentParser(
        prog="blender-arwaky",
        description="BlenderArwaky CLI — canonical action command surface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\\n"
            "  blender-arwaky get-scene-info --json\\n"
            "  blender-arwaky create-primitive --primitive-type CUBE --name DemoCube\\n"
            "  blender-arwaky execute-blender-code --code 'print(bpy.context.scene.name)'"
        ),
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output")
    parser.add_argument("--verbose", action="store_true", help="Show masked structural diagnostics")
    parser.add_argument("--color", choices=["auto", "always", "never"], default="auto", help="Color policy")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress hints")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive action")
    subparsers = parser.add_subparsers(dest="command", title="canonical actions", metavar="ACTION", required=True)

    for owner, actions in DISPATCHER_ACTION_SCHEMAS.items():
        for action_name, schema in actions.items():
            description = str(schema.get("description", action_name.replace("_", " ")))
            command_parser = subparsers.add_parser(
                _snake_to_kebab(action_name),
                help=f"[{owner}] {description}",
                description=f"[{owner}] {description}",
            )
            parameters = schema.get("parameters", {})
            if "filepath" not in parameters:
                command_parser.add_argument(
                    "--filepath",
                    help="Path to the active .blend file or runtime session",
                    default=argparse.SUPPRESS,
                )
            for parameter_name, parameter_spec in parameters.items():
                command_parser.add_argument(
                    f"--{_snake_to_kebab(parameter_name)}",
                    **_schema_arg_options(parameter_name, parameter_spec),
                )
            command_parser.set_defaults(
                action_name=action_name,
                action_availability="executable",
                parameter_fields=list(parameters.keys()),
            )
            _add_common_flags(command_parser)
            _example(command_parser, f"blender-arwaky {_snake_to_kebab(action_name)} --help")
    return parser


def _collect_params(args: argparse.Namespace) -> dict[str, object]:
    fields = getattr(args, "parameter_fields", [])
    return {field: getattr(args, field) for field in fields if getattr(args, field, None) is not None}


def _normalize_result(result: dict[str, object]) -> dict[str, object]:
    """Normalize surface results to the FRD machine-readable envelope."""
    normalized = dict(result)
    if normalized.get("success"):
        normalized.setdefault("data", normalized.get("result"))
        normalized.setdefault("warnings", [])
    else:
        category = str(normalized.get("category", "unexpected"))
        normalized.setdefault("message", normalized.get("error", "Operation failed"))
        normalized.setdefault(
            "hint",
            {
                "validation_error": "Review command syntax and required flags.",
                "blocked": "This capability is contract-blocked and is not routed.",
                "blocked_error": "This capability is contract-blocked and is not routed.",
                "unsupported": "This runtime does not support the requested execution mode.",
                "unsupported_error": "This runtime does not support the requested execution mode.",
                "state": "Start Blender or use the matching active filepath.",
                "connection": "Check that Blender and the addon TCP server are running.",
                "not_found": "Verify the action or resource identifier.",
                "security_violation": "Review the security policy and provide safe input.",
            }.get(category, "Inspect the command inputs and runtime diagnostics."),
        )
        normalized.setdefault("detail", None)
    normalized.setdefault("tracking_id", normalized.get("tracking_id", ""))
    return normalized


def _render_result(result: dict[str, object], args: argparse.Namespace) -> None:
    if bool(getattr(args, "json", False)) or not sys.stdout.isatty():
        print(json.dumps(result, indent=2, default=str))
        return
    if result.get("success"):
        if not getattr(args, "quiet", False):
            print(result.get("message", "OK"))
    else:
        print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)


def main(argv: list[str] | None = None, *, dispatcher: IDispatcherAggregate | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return EXIT_VALIDATION

    if dispatcher is None:
        try:
            from modules.asset.src.root_asset_container import create_asset_container
            from modules.cli.src.surface_cli_action_router import CliActionRouter
            from modules.config.src.root_config_container import ConfigContainer
            from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer
            from modules.job.src.root_job_container import create_job_feature
            from modules.launcher.src.root_launcher_container import LauncherConfigVO, LauncherContainer
            from modules.security.src.root_security_container import create_security_feature

            launcher_container = LauncherContainer(config=LauncherConfigVO())
            launcher_container.wire()
            config = ConfigContainer().build()
            security = create_security_feature()
            asset = create_asset_container(
                security_validator=security,
                security_supervisor=security,
                config_getter=config,
            ).get_orchestrator()
            action_router = CliActionRouter(
                launcher_container.agent,
                job=create_job_feature(),
                config=config,
                security=security,
                asset=asset,
            )
            dispatcher_container = DispatcherContainer(launcher_action_router=action_router)
            dispatcher_container.wire()
            dispatcher = dispatcher_container.agent
        except Exception:
            logger.exception("Failed to auto-wire dispatcher and launcher")
            result = {
                "success": False,
                "error": "Dispatcher not configured",
                "category": "configuration_error",
                "ref": "cli-500",
            }
            _render_result(result, args)
            return EXIT_UNEXPECTED

    try:
        action_name = args.action_name
        params = _collect_params(args)
        if action_name == "launch_blender" and dispatcher is None:
            result = surface_init_command.handle(args, dispatcher)
        elif action_name == "get_viewport_screenshot" and dispatcher is None:
            result = surface_screenshot_command.handle(args, dispatcher)
        elif action_name == "render" and dispatcher is None:
            result = surface_render_command.handle(args, dispatcher)
        elif action_name == "shutdown_blender" and dispatcher is None:
            result = surface_close_command.handle(args, dispatcher)
        elif action_name == "get_runtime_status" and dispatcher is None:
            result = surface_status_command.handle(args, dispatcher)
        else:
            result = surface_action_command.handle(action_name, params, args, dispatcher)
    except Exception:
        logger.exception("Unexpected CLI error")
        result = {"success": False, "error": "Unexpected error", "category": "unexpected", "ref": "cli-500"}

    result = _normalize_result(result)
    _render_result(result, args)
    return _exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
