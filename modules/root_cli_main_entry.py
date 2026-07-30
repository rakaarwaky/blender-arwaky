#!/usr/bin/env python3
"""Standalone CLI entry point for BlenderArwaky.

FR-CLI-001: Parse and Route Commands — argparse-based command parsing with subcommand routing
FR-CLI-002: Render Terminal Output — structured text output with JSON fallback support
FR-CLI-003: Display Errors — categorized, actionable errors with masked details

P0: Accepts injected IDispatcherAggregate for proper integration flow.
P0: Removes direct process/socket utility imports.

Usage:
  blender-arwaky init --filepath <path> [--mode gui|headless]
  blender-arwaky run --filepath <path> --action <action> [--params '<json>']
  blender-arwaky screenshot --filepath <path> --output <path> [--params '<json>']
  blender-arwaky render --filepath <path> --output <path> [--params '<json>']
  blender-arwaky close --filepath <path>
  blender-arwaky status
"""

from __future__ import annotations

import argparse
import json
import logging
import sys

from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate

logger = logging.getLogger(__name__)

# FRD-mapped exit codes per outcome class
EXIT_SUCCESS = 0
EXIT_VALIDATION = 2
EXIT_UPSTREAM = 3
EXIT_UNEXPECTED = 4

ERROR_CATEGORIES: dict[str, int] = {
    "validation_error": EXIT_VALIDATION,
    "configuration_error": EXIT_VALIDATION,
    "not_found": EXIT_UPSTREAM,
    "capacity": EXIT_UPSTREAM,
    "timeout": EXIT_UPSTREAM,
    "security_violation": EXIT_UPSTREAM,
    "connection": EXIT_UPSTREAM,
    "state": EXIT_UPSTREAM,
    "task": EXIT_UPSTREAM,
}


def _exit_code(result: dict[str, object]) -> int:
    """Map result category to deterministic exit code."""
    if result.get("success"):
        return EXIT_SUCCESS
    category = result.get("category", "unexpected")
    return ERROR_CATEGORIES.get(category, EXIT_UNEXPECTED)


def main(
    argv: list[str] | None = None,
    *,
    dispatcher: IDispatcherAggregate | None = None,
) -> int:
    """Main CLI entry point.

    P0: Accepts optional dispatcher injection for testing and composition.
    P0: Routes all commands through Dispatcher aggregate.
    """
    parser = argparse.ArgumentParser(
        prog="blender-arwaky",
        description="BlenderArwaky CLI — Blender lifecycle management",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # init command
    init_parser = subparsers.add_parser("init", help="Start Blender with a file")
    init_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    init_parser.add_argument("--mode", choices=["gui", "headless"], default="headless", help="Blender mode")
    init_parser.add_argument("--port", type=int, default=9876, help="TCP port for addon")

    # run command
    run_parser = subparsers.add_parser("run", help="Execute an action on active Blender")
    run_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    run_parser.add_argument("--action", required=True, help="Action name")
    run_parser.add_argument("--params", type=str, default="{}", help="JSON parameters")

    # screenshot command
    ss_parser = subparsers.add_parser("screenshot", help="Capture viewport screenshot")
    ss_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    ss_parser.add_argument("--output", required=True, help="Output image path")
    ss_parser.add_argument("--max-size", type=int, default=800, help="Max dimension in pixels")
    ss_parser.add_argument("--view-angle", default="PERSPECTIVE", help="View angle")
    ss_parser.add_argument("--shading", default="MATERIAL", help="Shading mode")
    ss_parser.add_argument("--no-overlays", action="store_true", help="Hide overlays")
    ss_parser.add_argument("--focus-object", help="Object name to frame")

    # render command
    render_parser = subparsers.add_parser("render", help="Execute full frame render")
    render_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    render_parser.add_argument("--output", required=True, help="Output image path")
    render_parser.add_argument("--resolution-x", type=int, default=1920, help="Render width")
    render_parser.add_argument("--resolution-y", type=int, default=1080, help="Render height")

    # close command
    close_parser = subparsers.add_parser("close", help="Close active Blender instance")
    close_parser.add_argument("--filepath", required=True, help="Path to .blend file")

    # status command
    subparsers.add_parser("status", help="Show active Blender status")

    # Global options
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output")

    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return EXIT_VALIDATION

    # Validate dispatcher is available — auto-wire if not provided
    if dispatcher is None:
        try:
            from modules.dispatcher.src.root_dispatcher_container import DispatcherContainer
            from modules.launcher.src.root_launcher_container import LauncherConfigVO, LauncherContainer

            launcher_config = LauncherConfigVO()
            launcher_container = LauncherContainer(config=launcher_config)
            launcher_container.wire()

            dispatcher_container = DispatcherContainer(
                launcher_action_router=launcher_container.agent,
            )
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
            if args.json or not sys.stdout.isatty():
                print(json.dumps(result, indent=2, default=str))
            else:
                print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)
            return EXIT_UNEXPECTED

    result: dict[str, object] = {}

    try:
        # Lazy imports — commands loaded only when dispatched (AES506 compliant)
        from modules.cli.src import cmd_close, cmd_init, cmd_render, cmd_run, cmd_screenshot, cmd_status

        if args.command == "init":
            result = cmd_init.handle(args, dispatcher)

        elif args.command == "run":
            try:
                args.params = json.loads(args.params)
            except json.JSONDecodeError as e:
                logger.debug("Invalid JSON params: %s", e)
                result = {
                    "success": False,
                    "error": "Invalid JSON parameters",
                    "category": "validation_error",
                    "ref": "cli-400",
                }
            else:
                result = cmd_run.handle(args, dispatcher)

        elif args.command == "screenshot":
            result = cmd_screenshot.handle(args, dispatcher)

        elif args.command == "render":
            result = cmd_render.handle(args, dispatcher)

        elif args.command == "close":
            result = cmd_close.handle(args, dispatcher)

        elif args.command == "status":
            result = cmd_status.handle(args, dispatcher)

        else:
            result = {
                "success": False,
                "error": f"Unknown command: {args.command}",
                "category": "validation_error",
                "ref": "cli-400",
            }

    except Exception:
        logger.exception("Unexpected CLI error")
        result = {
            "success": False,
            "error": "Unexpected error",
            "category": "unexpected",
            "ref": "cli-500",
        }

    # Output
    if args.json or not sys.stdout.isatty():
        print(json.dumps(result, indent=2, default=str))
    else:
        if result.get("success"):
            print(result.get("message", "OK"))
        else:
            print(f"Error: {result.get('error', 'Unknown error')}", file=sys.stderr)

    return _exit_code(result)


if __name__ == "__main__":
    sys.exit(main())
