"""Gateway domain contract: event publisher protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
Decouples gateway capabilities from the diagnostics feature's contract layer.
All gateway capability files import from this local protocol instead of
modules.diagnostics.src.contract_audit_emission_protocol.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_event import ServerEvent


class IEventPublisher(ABC):
    """Publish server domain events to subscribers.

    Gateway-local abstraction that decouples capabilities from diagnostics.
    Capabilities publish events through this protocol without depending on
    the diagnostics feature's contract layer.
    """

    @abstractmethod
    async def publish(self, event: ServerEvent) -> None:
        """Publish an event to all subscribers. Subscriber exceptions are isolated."""
        ...
