"""Contract: Config event sink protocol (FR-CFG-001, T-09).

Defines the inbound behavior interface for recording config domain events
into a bounded ring buffer and exposing recent events to observers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_config_constant import EVENT_RING_BUFFER_SIZE


class IConfigEventSinkProtocol(ABC):
    """Protocol for recording and retrieving config domain events (T-09)."""

    @abstractmethod
    def record_event(self, event: Any) -> None:
        """Record a domain event (any dataclass) into the sink."""
        ...

    @abstractmethod
    def recent_events(self, limit: int = EVENT_RING_BUFFER_SIZE) -> tuple[dict[str, Any], ...]:
        """Return the most recent ``limit`` events, oldest → newest, asdict-serialized."""
        ...
