"""Contract: Event bus protocol for server domain events.

Implemented by in-memory event bus capability.
AES Protocol layer — depends only on Taxonomy and this contract.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_server_event import ServerEvent


class IEventPublisher(ABC):
    """Publish events to subscribers."""

    @abstractmethod
    async def publish(self, event: ServerEvent) -> None:
        """Publish an event to all subscribers. Subscriber exceptions are isolated."""
        ...


class IEventSubscriber(ABC):
    """Handle server domain events."""

    @abstractmethod
    async def handle(self, event: ServerEvent) -> None:
        """Handle a published event."""
        ...


class IEventBus(IEventPublisher):
    """Event bus with subscriber management."""

    @abstractmethod
    def subscribe(self, subscriber: IEventSubscriber) -> None:
        """Subscribe an event handler. Subscribers receive all published events."""
        ...
