"""Gateway domain contract: scene operation queue protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-GWY-004: Serialize scene-mutating operations via scheduler queue.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import QueueStatusVO, SceneOperationResultVO, SceneOperationVO


class SceneQueueProtocol(ABC):
    """Protocol interface for serialized scene-mutating operation queue."""

    @abstractmethod
    def enqueue_operation(self, operation: SceneOperationVO) -> SceneOperationResultVO:
        """Enqueue a scene operation for serialized execution.

        FR-GWY-004: Mutating operations pass through queue. Read-only bypasses queue.
        Enforces depth limit (channel conflict error) and wait timeout.
        """
        ...

    @abstractmethod
    def get_queue_status(self) -> QueueStatusVO:
        """Query current queue depth and busy state.

        FR-GWY-004: Observable queue state for monitoring and diagnostics.
        """
        ...
