"""Gateway domain contract: connection protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-GWY-001: Establish Connection to Blender.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import ConnectionResultVO


class ConnectionProtocol(ABC):
    """Protocol interface for establishing and managing transport connection."""

    @abstractmethod
    def establish_connection(self) -> ConnectionResultVO:
        """Establish transport channel to Blender with handshake and protocol check.

        FR-GWY-001: Idempotent when already connected. Validates protocol version.
        Rejects incompatible versions. Transports auth material only when enabled.
        """
        ...

    @abstractmethod
    def disconnect(self) -> None:
        """Graceful disconnect. Must be idempotent.

        FR-GWY-002: State transitions to closed. No-op if already disconnected.
        """
        ...
