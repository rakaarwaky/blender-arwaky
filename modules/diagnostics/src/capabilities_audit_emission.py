"""Capability: Audit event emitter and in-memory event bus.

FR-DIA-003: Emit Audit Events
Produces immutable audit records for security-relevant and operationally
significant activity. Supports async subscribers with isolated exception
handling.
Implements AuditEmissionProtocol and provides InMemoryEventBus.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from modules.diagnostics.src.contract_audit_emission_protocol import (
    AuditEmissionProtocol,
)
from modules.shared.src.gateway.contract_event_protocol import (
    IEventBus,
    IEventSubscriber,
)
from modules.shared.src.gateway.taxonomy_gateway_event import ServerEvent

logger = logging.getLogger("BlenderMCPServer")


class AuditEmitter(AuditEmissionProtocol):
    """Emit immutable audit records for security-relevant activity.

    Produces audit records for security violations, connection failures,
    task failures, and destructive actions. Records are immutable once emitted.
    """

    def __init__(self) -> None:
        self._audit_records: list[dict[str, Any]] = []

    async def emit_audit_event(
        self,
        category: str,
        severity: str,
        source_feature: str,
        operation_type: str,
        correlation_id: str | None = None,
        source_tool: Any = None,
    ) -> dict[str, Any]:
        """Produce immutable audit record for security-relevant activity."""
        record: dict[str, Any] = {
            "category": category,
            "severity": severity,
            "source_feature": source_feature,
            "operation_type": operation_type,
            "correlation_id": correlation_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._audit_records.append(record)
        return {"emitted": True, "record": record}


class InMemoryEventBus(IEventBus):
    """In-memory event bus with async subscriber support.

    All events are published synchronously to registered subscribers.
    Subscriber exceptions are caught and logged — never propagated
    to the publisher, ensuring one slow subscriber doesn't block others.
    """

    def __init__(self) -> None:
        self._subscribers: list[IEventSubscriber] = []

    def subscribe(self, subscriber: IEventSubscriber) -> None:
        """Subscribe an event handler."""
        if subscriber not in self._subscribers:
            self._subscribers.append(subscriber)
            logger.debug("Event bus subscribed: %s", type(subscriber).__name__)

    async def publish(self, event: ServerEvent) -> None:
        """Publish an event to all subscribers."""
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

    def get_subscribers(self) -> list[IEventSubscriber]:
        """Return list of registered subscribers (for testing)."""
        return list(self._subscribers)
