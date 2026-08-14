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
    surface_run_command,
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
    "configuration_error": EXIT_VALIDATION,
    "not_found": EXIT_UPSTREAM,
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


def _build_parser() -> CliArgumentParser:
    parser = CliArgumentParser(
        prog="blender-arwaky",
        description="BlenderArwaky CLI — FRD feature command surface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n  blender-arwaky status\n  blender-arwaky scene-info --json\n  blender-arwaky run --action get_scene_info --params '{}'",
    )
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output")
    parser.add_argument("--verbose", action="store_true", help="Show masked structural diagnostics")
    parser.add_argument("--color", choices=["auto", "always", "never"], default="auto", help="Color policy")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress hints")
    parser.add_argument("--confirm", action="store_true", help="Confirm destructive action")
    subparsers = parser.add_subparsers(dest="command", title="commands", metavar="COMMAND")

    init_parser = subparsers.add_parser("init", help="Start Blender with a file", description="Start Blender runtime")
    init_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    init_parser.add_argument("--mode", choices=["gui", "headless"], default="headless", help="Blender mode")
    init_parser.add_argument("--port", type=int, default=9876, help="TCP port for addon")
    _add_common_flags(init_parser)
    _example(init_parser, "blender-arwaky init --filepath scene.blend --mode headless --port 9876")

    run_parser = subparsers.add_parser("run", help="Execute an action on active Blender")
    run_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    run_parser.add_argument("--action", required=True, help="Canonical action name")
    run_parser.add_argument("--params", type=str, default="{}", help="JSON object parameters")
    _add_common_flags(run_parser)
    _example(run_parser, "blender-arwaky run --action get_scene_info --params '{}'")

    ss_parser = subparsers.add_parser("screenshot", help="Capture viewport screenshot")
    ss_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    ss_parser.add_argument("--output", required=True, help="Output image path")
    ss_parser.add_argument("--max-size", type=int, default=800, help="Max dimension in pixels")
    ss_parser.add_argument("--view-angle", choices=["PERSPECTIVE", "TOP", "FRONT", "SIDE"], default="PERSPECTIVE")
    ss_parser.add_argument("--shading", choices=["WIREFRAME", "SOLID", "MATERIAL", "RENDERED"], default="MATERIAL")
    ss_parser.add_argument("--no-overlays", action="store_true", help="Hide overlays")
    ss_parser.add_argument("--focus-object", help="Object name to frame")
    _add_common_flags(ss_parser)
    _example(ss_parser, "blender-arwaky screenshot --filepath scene.blend --output /tmp/shot.png")

    render_parser = subparsers.add_parser("render", help="Execute full frame render")
    render_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    render_parser.add_argument("--output", required=True, help="Output image path")
    render_parser.add_argument("--resolution-x", type=int, default=1920, help="Render width")
    render_parser.add_argument("--resolution-y", type=int, default=1080, help="Render height")
    _add_common_flags(render_parser)
    _example(render_parser, "blender-arwaky render --filepath scene.blend --output /tmp/render.png")

    close_parser = subparsers.add_parser("close", help="Close active Blender instance")
    close_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    close_parser.add_argument("--force", action="store_true", help="Force termination fallback")
    _add_common_flags(close_parser)
    _example(close_parser, "blender-arwaky close --filepath scene.blend --force")

    status_parser = subparsers.add_parser("status", help="Show active Blender status")
    _add_common_flags(status_parser)
    _example(status_parser, "blender-arwaky status --json")

    def add_action(
        name: str, action: str, description: str, fields: list[tuple[str, dict[str, object]]], example: str
    ) -> None:
        command_parser = subparsers.add_parser(name, help=description, description=description)
        for flag, options in fields:
            command_parser.add_argument(flag, **options)
        command_parser.set_defaults(
            action_name=action,
            parameter_fields=[str(options.get("dest", flag.lstrip("-").replace("-", "_"))) for flag, options in fields],
        )
        _add_common_flags(command_parser)
        _example(command_parser, example)

    add_action(
        "register",
        "register_executable",
        "Register Blender executable",
        [("--path", {"dest": "path", "help": "Blender executable path"})],
        "blender-arwaky register --path /usr/bin/blender",
    )
    add_action("scene-info", "get_scene_info", "Inspect current scene", [], "blender-arwaky scene-info --json")
    add_action(
        "scene-cleanup",
        "cleanup_scene",
        "Clean objects or meshes from scene",
        [("--mode", {"choices": ["all", "objects", "meshes"], "required": True})],
        "blender-arwaky scene-cleanup --mode objects",
    )
    add_action(
        "set-env",
        "setup_environment",
        "Configure scene HDRI environment",
        [("--hdri-id", {"dest": "hdri_id", "required": True}), ("--strength", {"type": float, "default": None})],
        "blender-arwaky set-env --hdri-id studio.hdr --strength 1.0",
    )
    add_action(
        "object-info",
        "get_object_info",
        "Inspect an object",
        [("--name", {"dest": "object_name", "required": True})],
        "blender-arwaky object-info --name Cube",
    )
    add_action(
        "create",
        "create_primitive",
        "Create a primitive object",
        [
            (
                "--type",
                {
                    "dest": "primitive_type",
                    "choices": ["SPHERE", "CUBE", "CYLINDER", "PLANE", "CONE", "TORUS"],
                    "required": True,
                },
            ),
            ("--location", {"dest": "location", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
            ("--scale", {"dest": "scale", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
            ("--name", {"dest": "name"}),
        ],
        "blender-arwaky create --type CUBE --name Cube",
    )
    add_action(
        "set-transform",
        "set_object_transform",
        "Set object transform",
        [
            ("--name", {"dest": "object_name", "required": True}),
            ("--location", {"dest": "location", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
            ("--rotation", {"dest": "rotation", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
            ("--scale", {"dest": "scale", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
        ],
        "blender-arwaky set-transform --name Cube --location 1 2 3",
    )
    add_action(
        "delete",
        "delete_object",
        "Delete an object",
        [("--name", {"dest": "object_name", "required": True})],
        "blender-arwaky delete --name Cube",
    )
    add_action(
        "set-material",
        "set_material",
        "Assign a material",
        [
            ("--name", {"dest": "object_name", "required": True}),
            ("--material", {"dest": "material_name", "required": True}),
        ],
        "blender-arwaky set-material --name Cube --material Matte",
    )
    add_action(
        "apply-modifier",
        "apply_modifier",
        "Apply an object modifier",
        [
            ("--name", {"dest": "object_name", "required": True}),
            ("--modifier", {"dest": "modifier_name", "required": True}),
        ],
        "blender-arwaky apply-modifier --name Cube --modifier Bevel",
    )
    add_action(
        "import",
        "import_glb",
        "Import a GLB/GLTF file",
        [("--file", {"dest": "file_path", "required": True}), ("--name", {"dest": "object_name"})],
        "blender-arwaky import --file asset.glb --name Asset",
    )
    add_action(
        "export",
        "export_model",
        "Export an object",
        [
            ("--name", {"dest": "object_name", "required": True}),
            ("--output", {"dest": "file_path", "required": True}),
            ("--format", {"dest": "export_format", "choices": ["glb", "fbx", "obj"], "default": None}),
        ],
        "blender-arwaky export --name Cube --output cube.glb --format glb",
    )
    add_action(
        "place-asset",
        "place_asset",
        "Place an asset",
        [
            ("--asset-id", {"dest": "asset_id", "required": True}),
            ("--location", {"dest": "location", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
            ("--rotation", {"dest": "rotation", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
            ("--scale", {"dest": "scale", "nargs": 3, "type": float, "metavar": ("X", "Y", "Z")}),
        ],
        "blender-arwaky place-asset --asset-id asset-001",
    )
    add_action(
        "task-status",
        "get_task_status",
        "Show background task status",
        [("--task-id", {"dest": "task_id", "required": True})],
        "blender-arwaky task-status --task-id task-001",
    )
    add_action(
        "cancel-task",
        "cancel_task",
        "Cancel a background task",
        [("--task-id", {"dest": "task_id", "required": True})],
        "blender-arwaky cancel-task --task-id task-001",
    )
    add_action(
        "config",
        "get_config",
        "Read configuration",
        [("--key", {"dest": "key"})],
        "blender-arwaky config --key default_output_format",
    )
    add_action(
        "set-config",
        "set_config",
        "Update configuration",
        [("--key", {"dest": "key", "required": True}), ("--value", {"dest": "value", "required": True})],
        "blender-arwaky set-config --key color_policy --value never",
    )
    add_action(
        "run-code",
        "execute_blender_code",
        "Execute validated Blender code",
        [("--code", {"dest": "code", "required": True})],
        "blender-arwaky run-code --code 'print(bpy.context.scene.name)'",
    )
    return parser


def _collect_params(args: argparse.Namespace) -> dict[str, object]:
    fields = getattr(args, "parameter_fields", [])
    return {field: getattr(args, field) for field in fields if getattr(args, field, None) is not None}


def _normalize_result(result: dict[str, object]) -> dict[str, object]:
    """Normalize legacy surface results to the FRD machine-readable envelope."""
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
            from modules.cli.src.capabilities_cli_action_router import CliActionRouter
            from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer
            from modules.launcher.src.root_launcher_container import LauncherConfigVO, LauncherContainer

            launcher_container = LauncherContainer(config=LauncherConfigVO())
            launcher_container.wire()
            dispatcher_container = DispatcherContainer(launcher_action_router=CliActionRouter(launcher_container.agent))
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
        if args.command == "init":
            if dispatcher is not None:
                mode = "interface" if args.mode == "gui" else args.mode
                result = surface_action_command.handle(
                    "launch_blender",
                    {"filepath": args.filepath, "mode": mode, "port": args.port},
                    args,
                    dispatcher,
                )
                if result.get("success") and isinstance(result.get("result"), dict):
                    from modules.shared.src.cli.capabilities_cli_registry import Registry

                    process_id = result["result"].get("process_id") or 0
                    Registry().set_active(args.filepath, process_id, args.port)
            else:
                result = surface_init_command.handle(args, dispatcher)
        elif args.command == "run":
            try:
                args.params = json.loads(args.params)
            except json.JSONDecodeError:
                result = {
                    "success": False,
                    "error": "Invalid JSON parameters",
                    "category": "validation_error",
                    "ref": "cli-400",
                }
            else:
                result = surface_run_command.handle(args, dispatcher)
        elif args.command == "screenshot":
            if dispatcher is not None:
                result = surface_action_command.handle(
                    "get_viewport_screenshot",
                    {
                        "filepath": args.output,
                        "max_size": args.max_size,
                        "view_angle": args.view_angle,
                        "shading_mode": args.shading,
                        "show_overlays": not args.no_overlays,
                        "focus_object": args.focus_object,
                    },
                    args,
                    dispatcher,
                )
            else:
                result = surface_screenshot_command.handle(args, dispatcher)
        elif args.command == "render":
            if dispatcher is not None:
                result = surface_action_command.handle(
                    "render",
                    {"output_path": args.output, "resolution_x": args.resolution_x, "resolution_y": args.resolution_y},
                    args,
                    dispatcher,
                )
            else:
                result = surface_render_command.handle(args, dispatcher)
        elif args.command == "close":
            if dispatcher is not None:
                result = surface_action_command.handle("shutdown_blender", {"force": args.force}, args, dispatcher)
                if result.get("success"):
                    from modules.shared.src.cli.capabilities_cli_registry import Registry

                    Registry().clear()
            else:
                result = surface_close_command.handle(args, dispatcher)
        elif args.command == "status":
            if dispatcher is not None:
                result = surface_action_command.handle("get_runtime_status", {}, args, dispatcher)
            else:
                result = surface_status_command.handle(args, dispatcher)
        else:
            result = surface_action_command.handle(args.action_name, _collect_params(args), args, dispatcher)
    except Exception:
        logger.exception("Unexpected CLI error")
        result = {"success": False, "error": "Unexpected error", "category": "unexpected", "ref": "cli-500"}

    result = _normalize_result(result)
    _render_result(result, args)
    return _exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
