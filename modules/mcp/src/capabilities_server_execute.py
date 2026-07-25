"""Capability: Server action executor.

Implements ServerExecuteProtocol — handles 3D action execution with 1:1 CLI parity
through the container's agent orchestrator.
"""

from __future__ import annotations

import json
import logging

from modules.shared.src.common.taxonomy_core_vo import ActionName, Details, Prompt
from modules.shared.src.mcp.contract_server_execute_protocol import ServerExecuteProtocol

logger = logging.getLogger("BlenderMCPServer")


class ServerExecuteCapability(ServerExecuteProtocol):
    """Business logic for executing 3D actions via CLI environment."""

    def __init__(self, container: object) -> None:
        """Initialize with a DI container from the server module.

        Args:
            container: A callable or server capability that provides access to
                the agent orchestrator and action catalog.
        """
        self._container = container

    async def execute_action(self, action: str, params: dict | None = None) -> dict:
        """Execute a 3D action with 1:1 CLI parity.

        FR-MCP-002: Translates AI request to exact CLI instruction.
        Enforces same constraints, priority, and sequential processing as CLI.
        Returns structured result with success status, data, or error details.

        Args:
            action: The action name to execute.
            params: Optional dictionary of parameters for the action.

        Returns:
            Dictionary with success status, result data, and message.
        """
        logger.info("Executing action: %s (params=%s)", action, params)

        try:
            if params is None:
                params = {}

            # Get orchestrator from container
            container_instance = self._get_container()
            orchestrator = container_instance.core_agent_orchestrator

            result = await orchestrator.execute_action(ActionName(action), params)
            return {
                "success": True,
                "action": action,
                "result": result,
                "message": "Action executed successfully",
            }
        except Exception as e:
            logger.error("Action execution failed for '%s': %s", action, e, exc_info=True)
            return {
                "success": False,
                "action": action,
                "result": None,
                "message": f"Action execution failed: {e}",
            }

    def _get_container(self):
        """Get the DI container."""
        from modules.mcp.src.container import get_container
        return get_container()
