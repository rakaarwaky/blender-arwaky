"""
MCP Tool 1: execute_command — Thin wrapper delegating execution directly to the Agent container.

Direct delegation to the Agent container via its aggregate contract (AES compliant).
"""

import json
import logging

from modules.mcp.src.container import get_container
from modules.shared.src.common.taxonomy_core_vo import ActionName, Details, Prompt

logger = logging.getLogger("BlenderMCPServer")


class CommandExecuteHandler:
    """Handler for executing MCP commands via DI container."""

    @staticmethod
    def register_execute_command(mcp):
        """Register the universal execute_command tool (MCP Tool #1)."""

        @mcp.tool()
        async def execute_command(
            action: ActionName,
            args: Details | None = None,
        ) -> Prompt:
            """
            Execute ANY BlenderArwaky action via Agent aggregate contract.

            Args:
                action: Action name (must exist in COMMAND_CATALOG)
                args: Dictionary of arguments for the action

            Returns:
                JSON string result from execution
            """

            if args is None:
                args = {}
            try:
                orchestrator = get_container().core_agent_orchestrator
                result = await orchestrator.execute_action(action, args)
                return result
            except Exception as e:
                logger.error(f"Agent execution failed for '{action}': {e}", exc_info=True)
                return Prompt(json.dumps({"error": str(e), "action": str(action)}, indent=2))


