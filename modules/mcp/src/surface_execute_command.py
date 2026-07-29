"""MCP Tool 1: execute_command — Universal action executor.

FR-MCP-001: Expose MCP Tools — register_execute_command registers tool with MCP
FR-MCP-002: Route Tool Calls — dispatcher aggregate execute_action routes to owning feature
FR-MCP-003: Format MCP Responses — unified result envelope returned from orchestrator
"""

import json
import logging
from typing import Any

from modules.dispatcher.src.root_dispatcher_container import create_dispatcher_feature
from modules.shared.src.common.taxonomy_core_vo import ActionName, Details, Prompt

from .surface_action_registry import validate_action_args

logger = logging.getLogger("BlenderMCPServer")


class ExecuteCommandHandler:
    """Handler for the universal execute_command MCP tool."""

    @staticmethod
    def register_execute_command(mcp):
        """Register the execute_command tool (MCP Tool #1)."""

        @mcp.tool()
        async def execute_command(
            action: ActionName,
            args: Details | None = None,
        ) -> Any:
            """
            Execute ANY BlenderArwaky action via dispatcher aggregate.

            Args:
                action: Action name from catalog (shared identifier with CLI --action)
                args: Action-specific parameters as key-value dict

            Returns:
                Unified result envelope from execution
            """
            if args is None:
                args = {}

            errors = validate_action_args(str(action), args)
            if errors:
                return Prompt(json.dumps({"error": "; ".join(errors), "action": str(action)}, indent=2))

            try:
                orchestrator = create_dispatcher_feature()
                result = orchestrator.execute_action(action, args)
                return result
            except Exception as e:
                logger.error(f"Execution failed for '{action}': {e}", exc_info=True)
                return Prompt(json.dumps({"error": str(e), "action": str(action)}, indent=2))
