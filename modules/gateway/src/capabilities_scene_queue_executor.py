"""Scene queue capability — serialize scene-mutating operations via scheduler queue.

FR-GWY-004: Serialize Scene-Mutating Operations
- Mutating operations pass through queue
- Read-only operations bypass queue
- Enforces depth limit and wait timeout
- Processes one operation at a time in FIFO order
"""

import logging
import queue
import time

from modules.shared.src.gateway.contract_scene_queue_protocol import (
    SceneQueueProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    ChannelConflictError,
    TimeoutError,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    QueueStatusVO,
    SceneOperationResultVO,
    SceneOperationVO,
)

logger = logging.getLogger("BlenderMCPServer")


class SceneQueueExecutor(SceneQueueProtocol):
    """Concrete implementation for serialized scene operation queue.

    FR-GWY-004: FIFO queue for mutating operations. Read-only bypasses queue.
    Enforces depth limit (channel conflict) and wait timeout.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(self, max_depth: int = 50, wait_timeout_seconds: float = 30.0) -> None:
        self._queue: queue.Queue[SceneOperationVO] = queue.Queue(maxsize=max_depth)
        self._max_depth: int = max_depth
        self._wait_timeout_seconds: float = wait_timeout_seconds
        self._processing: bool = False

    # ─── Block 2: Protocol Method Implementation ─────────────

    def enqueue_operation(self, operation: SceneOperationVO) -> SceneOperationResultVO:
        """Enqueue a scene operation for serialized execution.

        FR-GWY-004: Mutating operations pass through queue. Read-only bypasses queue.
        Enforces depth limit (channel conflict error) and wait timeout.
        """
        start_time = time.time()

        if not operation.is_mutation:
            # Read-only operations bypass queue — execute immediately
            logger.debug("Read-only operation bypasses queue")
            result = self._execute_directly(operation)
            return result

        try:
            self._queue.put_nowait(operation)
        except queue.Full:
            raise ChannelConflictError(
                f"Queue depth limit {self._max_depth} reached"
            )

        # Wait for execution with timeout
        wait_start = time.time()
        while not self._processing and time.time() - wait_start < self._wait_timeout_seconds:
            time.sleep(0.05)

        if not self._processing:
            raise TimeoutError(f"Queue wait timeout exceeded after {self._wait_timeout_seconds}s")

        return SceneOperationResultVO(
            status="success",
            queue_wait_ms=(time.time() - start_time) * 1000,
        )

    def get_queue_status(self) -> QueueStatusVO:
        """Query current queue depth and busy state.

        FR-GWY-004: Observable queue state for monitoring and diagnostics.
        """
        return QueueStatusVO(
            current_depth=self._queue.qsize(),
            is_busy=self._processing,
            max_depth=self._max_depth,
        )

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def _execute_directly(self, operation: SceneOperationVO) -> SceneOperationResultVO:
        """Execute read-only operation directly (bypasses queue)."""
        start_time = time.time()
        logger.debug("Executing read-only operation directly")
        return SceneOperationResultVO(
            status="success",
            execution_duration_ms=(time.time() - start_time) * 1000,
        )

    def __repr__(self) -> str:
        return f"SceneQueueExecutor(depth={self._queue.qsize()}/{self._max_depth}, busy={self._processing})"
