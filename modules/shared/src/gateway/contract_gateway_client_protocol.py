"""Contract: Gateway client protocol for transport layer.

Defines the typed interface for gateway command execution.
Used by capabilities that need to send commands through the gateway.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class GatewayClientProtocol(ABC):
    """Protocol for gateway transport layer.

    Implemented by gateway socket client or mock implementations.
    Capabilities depend on this protocol instead of primitive `object` types.
    """

    @abstractmethod
    async def execute_command(self, command: dict[str, Any]) -> dict[str, Any]:
        """Execute a command through the gateway and return the result."""
        ...  # pragma: no cover
