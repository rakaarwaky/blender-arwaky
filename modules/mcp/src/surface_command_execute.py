"""
MCP Tool 1: execute_command — Thin wrapper delegating execution directly to the Agent container.

FR-MCP-001: Expose MCP Tools — register_execute_command registers tool with MCP
FR-MCP-002: Route Tool Calls — get_container().core_agent_orchestrator.execute_action routes to dispatcher
FR-MCP-003: Format MCP Responses — unified result envelope returned from the orchestrator

Direct delegation to the Agent container via its aggregate contract (AES compliant).
execute_action is a synchronous facade (FR-DSP-004); the tool wrapper is async for
MCP protocol compatibility but must NOT await the sync facade call.
"""

import json
import logging
from typing import Any

from modules.mcp.src.agent_mcp_orchestrator import get_container
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
        ) -> Any:
            """
            Execute ANY BlenderArwaky action via Agent aggregate contract.

            Args:
                action: Action name (must exist in COMMAND_CATALOG)
                args: Dictionary of arguments for the action

            Returns:
                Unified result envelope from execution
            """
            if args is None:
                args = {}
            try:
                orchestrator = get_container().core_agent_orchestrator
                # FR-MCP-002: route to the dispatcher aggregate facade.
                # execute_action is synchronous (FR-DSP-004) — do NOT await it.
                result = orchestrator.execute_action(action, args)
                return result
            except Exception as e:
                logger.error(f"Agent execution failed for '{action}': {e}", exc_info=True)
                return Prompt(json.dumps({"error": str(e), "action": str(action)}, indent=2))
