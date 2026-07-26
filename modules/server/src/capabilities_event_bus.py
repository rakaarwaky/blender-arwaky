"""Capability: In-memory event bus for server domain events.

Implements IEventBus — supports async subscribers, isolates subscriber
exceptions, and logs subscriber failures without stopping publish flow.
"""

from __future__ import annotations

import logging
from typing import List

from modules.shared.src.server import IEventBus, IEventSubscriber, ServerEvent

logger = logging.getLogger("BlenderMCPServer")


class InMemoryEventBus(IEventBus):
    """In-memory event bus with async subscriber support.

    All events are published synchronously to registered subscribers.
    Subscriber exceptions are caught and logged — never propagated
    to the publisher, ensuring one slow subscriber doesn't block others.
    """

    def __init__(self) -> None:
        self._subscribers: List[IEventSubscriber] = []
        self._lock = False  # Not using threading; asyncio handles concurrency

    def subscribe(self, subscriber: IEventSubscriber) -> None:
        """Subscribe an event handler.

        Args:
            subscriber: An async event subscriber implementing handle().
        """
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
            logger.debug("Event bus subscribed: %s", type(subscriber).__name__)

    async def publish(self, event: ServerEvent) -> None:
        """Publish an event to all subscribers.

        Each subscriber is called in sequence. Exceptions are caught,
        logged, and do not prevent subsequent subscribers from receiving
        the event.

        Args:
            event: The server domain event to publish.
        """
        for subscriber in self._subscribers:
            try:
                await subscriber.handle(event)
            except Exception as e:
                logger.error(
                    "Event subscriber %s failed: %s",
                    type(subscriber).__name__,
                    e,
                    exc_info=True,
                )
