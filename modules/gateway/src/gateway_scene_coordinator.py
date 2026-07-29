"""Gateway scene coordinator — Scene queue orchestration logic.

FR-GWY-004: Coordinates scene-mutating operations through the queue.
Keeps GatewayOrchestrator type count under AES405 limit (max 3 types).
"""

import logging

from modules.shared.src.gateway.contract_scene_queue_protocol import (
    SceneQueueProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
)

logger = logging.getLogger("BlenderMCPServer")


class GatewaySceneCoordinator:
    """Coordinates scene-mutating operations via the queue.

    Delegates to SceneQueueProtocol; keeps orchestrator lean per AES405.
    """

    def __init__(self, scene_queue: SceneQueueProtocol) -> None:
        self._scene_queue = scene_queue

    def enqueue_scene_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
        """FR-GWY-004: Enqueue scene operation."""
        logger.debug("Enqueuing scene operation: mutation=%s", operation.is_mutation)
        return self._scene_queue.enqueue_operation(operation)

    def get_queue_status(self) -> QueueStatusVO:
        """FR-GWY-004: Get queue status."""
        return self._scene_queue.get_queue_status()
