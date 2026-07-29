#!/usr/bin/env python3
"""Standalone CLI entry point for BlenderArwaky.

FR-CLI-001: Parse and Route Commands — argparse-based command parsing with subcommand routing
FR-CLI-002: Render Terminal Output — structured text output with JSON fallback support
FR-CLI-003: Display Errors — categorized, actionable errors with masked details

Usage:
  blender-arwaky init --filepath <path> [--mode gui|headless]
  blender-arwaky run --filepath <path> --action <action> [--params '<json>']
  blender-arwaky screenshot --filepath <path> --output <path> [--params '<json>']
  blender-arwaky render --filepath <path> --output <path> [--params '<json>']
  blender-arwaky close --filepath <path>
  blender-arwaky status
"""

import argparse
import json
import logging
import sys
from typing import Any

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


def _exit_code(result: dict[str, Any]) -> int:
    """Map result category to deterministic exit code."""
    if result.get("success"):
        return EXIT_SUCCESS
    category = result.get("category", "unexpected")
    return ERROR_CATEGORIES.get(category, EXIT_UNEXPECTED)


def main() -> int:
    """Main CLI entry point."""
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

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return EXIT_VALIDATION

    # Import commands lazily
    from . import capabilities_cli_command as commands

    result: dict[str, Any] = {}

    try:
        if args.command == "init":
            result = commands.init(args.filepath, mode=args.mode, port=args.port)

        elif args.command == "run":
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                logger.debug("Invalid JSON params: %s", e)
                result = {
                    "success": False,
                    "error": "Invalid JSON parameters",
                    "category": "validation_error",
                    "ref": "cli-400",
                }
            else:
                result = commands.run(args.filepath, args.action, params)

        elif args.command == "screenshot":
            result = commands.screenshot(
                filepath=args.filepath,
                output=args.output,
                max_size=args.max_size,
                view_angle=args.view_angle,
                shading=args.shading,
                show_overlays=not args.no_overlays,
                focus_object=args.focus_object,
            )

        elif args.command == "render":
            result = commands.render(
                filepath=args.filepath,
                output=args.output,
                resolution_x=args.resolution_x,
                resolution_y=args.resolution_y,
            )

        elif args.command == "close":
            result = commands.close(args.filepath)

        elif args.command == "status":
            result = commands.status()

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
