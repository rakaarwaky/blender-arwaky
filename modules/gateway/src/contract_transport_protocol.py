"""Contract: Command dispatch protocol for Blender operations.

Implemented by Capabilities layer (BlenderCommandAdapter).
Per FR-SRV-003: Send Blender Commands via TCP socket with timeout enforcement.
Queue management moved to OperationQueue capability.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_server_vo import CommandResult


class IBlenderCommandProtocol(ABC):
    """Protocol for dispatching named commands to Blender.

    Implemented by Capabilities layer (BlenderCommandAdapter).
    Command routing via TCP socket with configurable timeout enforcement.
    Queue serialization is owned by the Agent layer orchestrator.
    """

    @abstractmethod
    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        timeout_ms: float | None = None,
        request_id: str | None = None,
    ) -> CommandResult:
        """Dispatch a named command to Blender addon.

        Success: Returns CommandResult with status='success'
        Failure: Raises CommandTimeoutError if response exceeds configured timeout
        Event: CommandDispatched(action, execution_time_ms)
        """
        ...
