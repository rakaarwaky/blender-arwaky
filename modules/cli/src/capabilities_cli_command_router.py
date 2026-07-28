"""Capability: CLI command parser and router.

Implements CliCommandProtocol — parses terminal input and routes to
owning feature aggregates. Surface only; no business logic.

FR-CLI-001: Parse and Route Commands
"""

from __future__ import annotations

import logging
from typing import Any

from modules.shared.src.cli.contract_cli_command_protocol import CliCommandProtocol
from modules.shared.src.common.taxonomy_core_vo import (
    ActionName,
    ExitCode,
)
from modules.shared.src.common.taxonomy_domain_error import ValidationError

logger = logging.getLogger("BlenderMCPServer")

# Command-to-action mapping (surface-level only; semantics in catalog)
COMMAND_MAP: dict[str, ActionName] = {
    "launch": ActionName("launcher.launch"),
    "shutdown": ActionName("launcher.shutdown"),
    "status": ActionName("diagnostics.status"),
    "health": ActionName("diagnostics.health"),
    "execute": ActionName("dispatcher.execute"),
    "actions": ActionName("dispatcher.list_actions"),
    "settings": ActionName("config.settings"),
    "task": ActionName("job.status"),
    "cancel": ActionName("job.cancel"),
}


class CliCommandCapability(CliCommandProtocol):
    """Business logic for parsing CLI commands and routing to aggregates."""

    def __init__(
        self,
        container: object,
        strict_mode: bool = True,
    ) -> None:
        """Initialize with DI container and validation mode.

        Args:
            container: DI container providing access to dispatcher/catalog.
            strict_mode: Whether unknown commands produce errors vs warnings.
        """
        self._container = container
        self._strict_mode = strict_mode

    async def parse_and_route(
        self,
        command: str,
        args: list[str] | None = None,
        _flags: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Parse terminal input and route to owning feature aggregate.

        FR-CLI-001: Each CLI command maps to exactly one owning feature aggregate.
        Parsing validates surface shape only; semantic validation belongs to owning feature.

        Args:
            command: The command name from terminal input.
            args: Optional positional arguments.
            flags: Optional flags and options.

        Returns:
            Dict with success indicator, result data, message, and exit code.
        """
        if command == "help" or command == "--help":
            return self._show_help(args)

        action = COMMAND_MAP.get(command)
        if action is None:
            suggestions = self._suggest_commands(command)
            if self._strict_mode:
                raise ValidationError(
                    f"Unknown command '{command}'. Did you mean: {', '.join(suggestions)}?"
                )
            return {
                "success": False,
                "exit_code": ExitCode(1),
                "message": f"Unknown command '{command}'",
                "suggestions": suggestions,
            }

        logger.info("Routing CLI command '%s' to action %s", command, action)

        try:
            container_instance = self._get_container()
            dispatcher = container_instance.dispatcher if hasattr(container_instance, "dispatcher") else None
            result = await dispatcher.execute_action(action, args or {})
            return {
                "success": True,
                "command": command,
                "exit_code": ExitCode(0),
                "result": result,
            }
        except Exception as e:
            logger.error("CLI command '%s' failed: %s", command, e)
            return {
                "success": False,
                "command": command,
                "exit_code": ExitCode(1),
                "message": f"Command failed: {e}",
            }

    def _show_help(self, args: list[str] | None) -> dict[str, Any]:
        """Show CLI help overview or per-command usage."""
        if args and args[0] in COMMAND_MAP:
            action = COMMAND_MAP[args[0]]
            return {
                "success": True,
                "command": "help",
                "message": f"Usage for '{args[0]}': routes to {action}",
                "usage": f"blender-mcp {args[0]} [options]",
            }
        return {
            "success": True,
            "command": "help",
            "message": "Blender MCP CLI — available commands:",
            "commands": list(COMMAND_MAP.keys()),
            "usage": "blender-mcp <command> [options]",
        }

    def _suggest_commands(self, unknown: str) -> list[str]:
        """Suggest closest recognized commands for a typo."""
        suggestions: list[str] = []
        for cmd in COMMAND_MAP:
            if cmd.startswith(unknown[:2]) or len(unknown) < 4:
                suggestions.append(cmd)
        return suggestions[:3]

    def _get_container(self) -> object:
        """Get the DI container."""
        from modules.cli.src.container import get_container
        return get_container()
