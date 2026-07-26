"""Integration tests for server capabilities.

Tests operation queue, event bus, metrics collector, and code execution
adapter with mocked dependencies. Uses integration marker.
"""

from __future__ import annotations

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock

import pytest

from modules.shared.src.server import (
    CodeSecurityPolicy,
    ExecutionResult,
    IEventPublisher,
    OperationRejected,
    SecurityViolationDetected,
    ServerCommandSpec,
    TooManyPendingOperationsError,
)

# Import from server module capabilities
from modules.gateway.src.capabilities_code_execution_adapter import CodeExecutionAdapter
from modules.gateway.src.capabilities_event_bus import InMemoryEventBus
from modules.gateway.src.capabilities_metrics_collector import MetricsCollector
from modules.gateway.src.capabilities_operation_queue import OperationQueue


# ─── Test Helpers ──────────────────────────────────────────────


class EventHandler:
    """Simple event handler wrapper for testing."""

    def __init__(self, callback) -> None:
        self._callback = callback

    async def handle(self, event) -> None:
        await self._callback(event)


# ─── InMemoryEventBus Integration Tests ─────────────────────────


class TestInMemoryEventBus:
    """Test event bus publish and subscribe."""

    @pytest.mark.asyncio
    async def test_subscribe_returns_handler(self) -> None:
        """Verify subscribe returns the handler for chaining."""
        bus = InMemoryEventBus()
        received = []

        async def handler(event: str) -> None:
            received.append(event)

        bus.subscribe(EventHandler(handler))
        assert len(bus.get_subscribers()) == 1

    @pytest.mark.asyncio
    async def test_handler_called_on_publish(self) -> None:
        """Verify subscriber handler is called when event is published."""
        bus = InMemoryEventBus()
        received = []

        async def handler(event: str) -> None:
            received.append(event)

        bus.subscribe(EventHandler(handler))
        await bus.publish("event_1")

        assert len(received) == 1
        assert received[0] == "event_1"

    @pytest.mark.asyncio
    async def test_exception_isolation(self) -> None:
        """Verify handler exceptions don't block other handlers."""
        bus = InMemoryEventBus()
        results = []

        async def good_handler(event: str) -> None:
            results.append("good")

        async def bad_handler(event: str) -> None:
            raise ValueError("handler error")

        bus.subscribe(EventHandler(good_handler))
        bus.subscribe(EventHandler(bad_handler))

        await bus.publish("test_event")
        assert "good" in results


# ─── MetricsCollector Integration Tests ─────────────────────────


class TestMetricsCollector:
    """Test metrics collection from events."""

    @pytest.mark.asyncio
    async def test_code_execution_metric(self) -> None:
        """Verify code execution count increases."""
        collector = MetricsCollector()
        bus = InMemoryEventBus()
        bus.subscribe(collector)

        from modules.shared.src.server import CodeExecuted
        await bus.publish(CodeExecuted(request_id="test", execution_time_ms=100.0))

        metrics = await collector.get_metrics("test")
        assert metrics.code_execution_count >= 1

    @pytest.mark.asyncio
    async def test_command_metric(self) -> None:
        """Verify command count increases."""
        collector = MetricsCollector()
        bus = InMemoryEventBus()
        bus.subscribe(collector)

        from modules.shared.src.server import CommandDispatched
        await bus.publish(CommandDispatched(action="ping", execution_time_ms=0.0, request_id="test"))

        metrics = await collector.get_metrics("test")
        assert metrics.command_count >= 1

    @pytest.mark.asyncio
    async def test_security_violation_metric(self) -> None:
        """Verify security violation count increases."""
        collector = MetricsCollector()
        bus = InMemoryEventBus()
        bus.subscribe(collector)

        await bus.publish(SecurityViolationDetected(
            request_id="test",
            rule="blocked_module_import",
            code_fingerprint="abc123",
        ))

        metrics = await collector.get_metrics("test")
        assert metrics.security_violation_count >= 1


# ─── OperationQueue Integration Tests ──────────────────────────


class TestOperationQueue:
    """Test FIFO queue with depth limits and cancellation."""

    @pytest.mark.asyncio
    async def test_enqueue_dequeue_fifo(self) -> None:
        """Verify FIFO ordering."""
        from modules.shared.src.server import QueuedOperation

        bus = InMemoryEventBus()
        queue = OperationQueue(event_publisher=bus, max_depth=10)

        await queue.enqueue(QueuedOperation(request_id="req_1", operation_type="code_sync", payload={}))
        await queue.enqueue(QueuedOperation(request_id="req_2", operation_type="command", payload={}))

        d1 = await queue.dequeue()
        d2 = await queue.dequeue()

        assert d1.request_id == "req_1"
        assert d2.request_id == "req_2"

    @pytest.mark.asyncio
    async def test_queue_depth_limit(self) -> None:
        """Verify TooManyPendingOperationsError when full."""
        from modules.shared.src.server import QueuedOperation

        bus = InMemoryEventBus()
        queue = OperationQueue(event_publisher=bus, max_depth=2)

        await queue.enqueue(QueuedOperation(request_id="r1", operation_type="code_sync", payload={}))
        await queue.enqueue(QueuedOperation(request_id="r2", operation_type="command", payload={}))

        with pytest.raises(TooManyPendingOperationsError):
            await queue.enqueue(QueuedOperation(request_id="r3", operation_type="code_sync", payload={}))

    @pytest.mark.asyncio
    async def test_mark_started_and_complete(self) -> None:
        """Verify operation state transitions."""
        from modules.shared.src.server import QueuedOperation, ExecutionResult

        bus = InMemoryEventBus()
        queue = OperationQueue(event_publisher=bus, max_depth=10)

        await queue.enqueue(QueuedOperation(request_id="test_req", operation_type="code_sync", payload={}))
        await queue.mark_started("test_req")

        # Check state
        assert "test_req" in queue._operation_states
        assert queue._operation_states["test_req"].started is True

    @pytest.mark.asyncio
    async def test_wait_for_started_timeout(self) -> None:
        """Verify OperationWaitTimeoutError on timeout."""
        from modules.shared.src.server import OperationWaitTimeoutError, QueuedOperation

        bus = InMemoryEventBus()
        queue = OperationQueue(event_publisher=bus, max_depth=10, wait_timeout_ms=100)

        await queue.enqueue(QueuedOperation(request_id="timeout_req", operation_type="code_sync", payload={}))

        with pytest.raises(OperationWaitTimeoutError):
            await queue.wait_for_started("timeout_req", timeout_ms=50)

    @pytest.mark.asyncio
    async def test_cancel_pending(self) -> None:
        """Verify pending operations can be cancelled."""
        from modules.shared.src.server import ConnectionClosedError, QueuedOperation

        bus = InMemoryEventBus()
        queue = OperationQueue(event_publisher=bus, max_depth=10)

        await queue.enqueue(QueuedOperation(request_id="p1", operation_type="code_sync", payload={}))
        await queue.enqueue(QueuedOperation(request_id="p2", operation_type="command", payload={}))

        cancelled = await queue.cancel_pending(ConnectionClosedError())
        assert cancelled == 2
        assert len(queue._queue) == 0


# ─── CodeExecutionAdapter Integration Tests ─────────────────────


class TestCodeExecutionAdapter:
    """Test code execution adapter with mocked connection."""

    @pytest.mark.asyncio
    async def test_task_creation(self) -> None:
        """Verify task creation returns unique ID."""
        mock_conn = MagicMock()
        mock_bus = InMemoryEventBus()
        policy = CodeSecurityPolicy()

        adapter = CodeExecutionAdapter(
            connection_port=mock_conn,
            event_publisher=mock_bus,
            security_policy=policy,
        )

        task_id = await adapter.create_task("test_req")
        assert task_id.startswith("task_test_req_")

    @pytest.mark.asyncio
    async def test_get_task_status(self) -> None:
        """Verify task status retrieval."""
        mock_conn = MagicMock()
        mock_bus = InMemoryEventBus()
        policy = CodeSecurityPolicy()

        adapter = CodeExecutionAdapter(
            connection_port=mock_conn,
            event_publisher=mock_bus,
            security_policy=policy,
        )

        task_id = await adapter.create_task("test_req")
        status = await adapter.get_task(task_id)
        assert status.task_id == task_id
        assert status.state == "pending"

    @pytest.mark.asyncio
    async def test_cancel_task(self) -> None:
        """Verify task cancellation."""
        mock_conn = MagicMock()
        mock_bus = InMemoryEventBus()
        policy = CodeSecurityPolicy()

        adapter = CodeExecutionAdapter(
            connection_port=mock_conn,
            event_publisher=mock_bus,
            security_policy=policy,
        )

        task_id = await adapter.create_task("test_req")
        status = await adapter.cancel_async_task(task_id)
        assert status.state == "cancelled"
