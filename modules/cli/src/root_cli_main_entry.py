import argparse
import difflib
import json
import logging
import sys
from collections.abc import Sequence
from typing import Any

from modules.shared.src.cli.taxonomy_cli_constant import (
    ERROR_CATEGORY_MAP,
    EXIT_SUCCESS,
    EXIT_UNEXPECTED,
    EXIT_VALIDATION,
)
from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate
from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate
from modules.shared.src.security.contract_redact_sensitive_protocol import RedactSensitiveProtocol

logger = logging.getLogger(__name__)

_KNOWN_COMMANDS = sorted(["init", "run", "screenshot", "render", "close", "status"])


def _get_close_matches(unknown: str) -> list[str]:
    return difflib.get_close_matches(unknown, _KNOWN_COMMANDS, n=3, cutoff=0.4)


def _envelope(
    success: bool,
    message: str = "",
    error: str | None = None,
    category: str | None = None,
    ref: str | None = None,
    warnings: list[str] | None = None,
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {"success": success}
    if message:
        result["message"] = message
    if error:
        result["error"] = error
    if category:
        result["category"] = category
    if ref:
        result["ref"] = ref
    if warnings:
        result["warnings"] = warnings
    if data:
        result["data"] = data
    return result


def _envelope_from_cli_result(cli_result: CliResultVo) -> dict[str, Any]:
    return _envelope(
        success=cli_result.success,
        message=cli_result.message or "",
        error=cli_result.error,
        category=cli_result.category,
        ref=cli_result.ref,
        warnings=cli_result.warnings,
        data=cli_result.data,
    )


def _exit_code(result: dict[str, Any]) -> int:
    if result.get("success"):
        return EXIT_SUCCESS
    category = result.get("category", "unexpected")
    return ERROR_CATEGORY_MAP.get(category, EXIT_UNEXPECTED)


def _redact_result(result: dict[str, Any], redactor: RedactSensitiveProtocol | None) -> dict[str, Any]:
    if redactor is None:
        return result
    import asyncio

    text = json.dumps(result, default=str)
    try:
        redacted = asyncio.run(redactor.redact(text=text))
        return json.loads(redacted.redacted_text) if not redacted.failed else result
    except Exception:
        return result


def _render_output(result: dict[str, Any], json_mode: bool, is_tty: bool) -> str | None:
    if json_mode or not is_tty:
        return json.dumps(result, indent=2, default=str)
    if result.get("success"):
        message = result.get("message", "OK")
        warnings = result.get("warnings")
        output = message
        if warnings:
            output += "\n" + "\n".join(f"Warning: {w}" for w in warnings)
        data = result.get("data")
        if data and isinstance(data, dict):
            for key, value in data.items():
                output += f"\n  {key}: {value}"
        return output
    error = result.get("error", "Unknown error")
    category = result.get("category", "unexpected")
    ref = result.get("ref", "")
    lines = [f"Error ({category}): {error}"]
    if ref:
        lines.append(f"Reference: {ref}")
    return "\n".join(lines)


class _SuggestionParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise argparse.ArgumentError(None, message)


# Shared parent parser for root-level flags usable with any subcommand
def _make_shared_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--quiet", action="store_true", help="Suppress non-error output")


def main(
    argv: Sequence[str] | None = None,
    launcher: ILauncherOperateAggregate | None = None,
    dispatcher: IDispatcherAggregate | None = None,
    redactor: RedactSensitiveProtocol | None = None,
) -> int:
    parser = _SuggestionParser(
        prog="blender-arwaky", description="BlenderArwaky CLI — Blender lifecycle management", add_help=True
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Shared parent parser for common flags (--json, --quiet) on each subparser
    shared_parent: argparse.ArgumentParser | None = None

    init_parser = subparsers.add_parser("init", help="Start Blender with a file")
    _make_shared_parser(init_parser)
    init_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    init_parser.add_argument("--mode", choices=["gui", "headless"], default="headless", help="Blender mode")
    init_parser.add_argument("--port", type=int, default=9876, help="TCP port for addon")

    run_parser = subparsers.add_parser("run", help="Execute an action on active Blender")
    _make_shared_parser(run_parser)
    run_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    run_parser.add_argument("--action", required=True, help="Action name")
    run_parser.add_argument("--params", type=str, default="{}", help="JSON parameters")

    ss_parser = subparsers.add_parser("screenshot", help="Capture viewport screenshot")
    _make_shared_parser(ss_parser)
    ss_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    ss_parser.add_argument("--output", required=True, help="Output image path")
    ss_parser.add_argument("--max-size", type=int, default=800, help="Max dimension in pixels")
    ss_parser.add_argument("--view-angle", default="PERSPECTIVE", help="View angle")
    ss_parser.add_argument("--shading", default="MATERIAL", help="Shading mode")
    ss_parser.add_argument("--no-overlays", action="store_true", help="Hide overlays")
    ss_parser.add_argument("--focus-object", help="Object name to frame")

    render_parser = subparsers.add_parser("render", help="Execute full frame render")
    _make_shared_parser(render_parser)
    render_parser.add_argument("--filepath", required=True, help="Path to .blend file")
    render_parser.add_argument("--output", required=True, help="Output image path")
    render_parser.add_argument("--resolution-x", type=int, default=1920, help="Render width")
    render_parser.add_argument("--resolution-y", type=int, default=1080, help="Render height")

    close_parser = subparsers.add_parser("close", help="Close active Blender instance")
    _make_shared_parser(close_parser)
    close_parser.add_argument("--filepath", required=True, help="Path to .blend file")

    status_parser = subparsers.add_parser("status", help="Show active Blender status")
    _make_shared_parser(status_parser)

    try:
        args = parser.parse_args(argv)
    except (argparse.ArgumentError, SystemExit):
        if argv and len(argv) > 0 and argv[0] not in _KNOWN_COMMANDS and not argv[0].startswith("-"):
            suggestions = _get_close_matches(argv[0])
            msg = f"Unknown command: {argv[0]}"
            if suggestions:
                msg += f". Did you mean: {', '.join(suggestions)}?"
            fallback = _envelope(success=False, error=msg, category="validation_error", ref="cli-400")
            output = _render_output(fallback, "--json" in (argv or []), sys.stdout.isatty())
            if output:
                print(output)
            return EXIT_VALIDATION
        parser.print_help()
        return EXIT_VALIDATION

    if not args.command:
        parser.print_help()
        return EXIT_VALIDATION

    json_mode = getattr(args, "json", False)
    quiet = getattr(args, "quiet", False)
    is_tty = sys.stdout.isatty()

    from . import (
        surface_close_command,
        surface_init_command,
        surface_render_command,
        surface_run_command,
        surface_screenshot_command,
        surface_status_command,
    )

    result: dict[str, Any] = {}

    try:
        if args.command == "init":
            result = _envelope_from_cli_result(surface_init_command.handle(args, launcher=launcher))
        elif args.command == "run":
            try:
                params = json.loads(args.params)
            except json.JSONDecodeError as e:
                logger.debug("Invalid JSON params: %s", e)
                result = _envelope(
                    success=False, error="Invalid JSON parameters", category="validation_error", ref="cli-400"
                )
            else:
                args.params = params
                result = _envelope_from_cli_result(surface_run_command.handle(args, dispatcher=dispatcher))
        elif args.command == "screenshot":
            result = _envelope_from_cli_result(surface_screenshot_command.handle(args, dispatcher=dispatcher))
        elif args.command == "render":
            result = _envelope_from_cli_result(surface_render_command.handle(args, dispatcher=dispatcher))
        elif args.command == "close":
            result = _envelope_from_cli_result(surface_close_command.handle(args, launcher=launcher))
        elif args.command == "status":
            result = _envelope_from_cli_result(surface_status_command.handle(args, launcher=launcher))
    except Exception:
        logger.exception("Unexpected CLI error")
        result = _envelope(success=False, error="Unexpected error", category="unexpected", ref="cli-500")

    result = _redact_result(result, redactor)

    if not quiet:
        output = _render_output(result, json_mode, is_tty)
        if output:
            if json_mode or not is_tty:
                print(output)
            else:
                if result.get("success"):
                    print(output)
                else:
                    print(output, file=sys.stderr)

    return _exit_code(result)
