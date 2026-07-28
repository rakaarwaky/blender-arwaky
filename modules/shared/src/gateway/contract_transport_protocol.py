"""Gateway domain contract: transport protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-GWY-003: Transport Request and Response with framing, correlation, and limits.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import TransportMessageVO, TransportOutcomeVO


class TransportProtocol(ABC):
    """Protocol interface for framed request/response transport with tracking."""

    @abstractmethod
    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
        """Send command to Blender and receive correlated response.

        FR-GWY-003: Every request carries unique tracking ID. Every response
        is correlated back. Enforces payload limits and transport timeout.
        Discards uncorrelated/orphan responses safely.
        """
        ...


from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import CommandResult


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
