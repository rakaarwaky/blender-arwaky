"""Agent: Server feature orchestrator.

Coordinates Blender TCP connection and code execution.
"""

import logging
from typing import Any

from modules.shared.src.server.contract_connection import BlenderConnectionPort
from modules.shared.src.server.contract_code_execution import CodeExecutionPort
from modules.shared.src.common.taxonomy_core_vo import Prompt, PythonCode, StatusString

logger = logging.getLogger("BlenderMCPServer")


class ServerOrchestrator:
    """Orchestrates server operations."""

    def __init__(self, connection: BlenderConnectionPort, code_executor: CodeExecutionPort):
        self._connection = connection
        self._code_executor = code_executor

    def connect(self) -> None:
        """Connect to Blender."""
        self._connection.connect()

    def disconnect(self) -> None:
        """Disconnect from Blender."""
        self._connection.disconnect()

    async def execute_code(self, code: PythonCode) -> StatusString:
        """Execute Python code in Blender."""
        return await self._code_executor.execute_blender_code(code)
