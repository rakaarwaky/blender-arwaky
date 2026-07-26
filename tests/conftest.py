"""Shared test fixtures and configuration for all test suites.

Provides mocks, fakes, and reusable fixtures for server module testing.
"""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest


# ─── Fixtures ──────────────────────────────────────────────────────


@pytest.fixture
def anyio_backend():
    """Use asyncio backend for async tests."""
    return "asyncio"


@pytest.fixture
def event_loop():
    """Create an asyncio event loop for each test."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ─── Mock Event Bus ────────────────────────────────────────────────


class FakeEventBus:
    """Simple in-memory event bus for testing without real implementation."""

    def __init__(self) -> None:
        self.events: list[Any] = []

    async def publish(self, event: Any) -> None:
        self.events.append(event)

    def get_events(self) -> list[Any]:
        return list(self.events)

    def clear(self) -> None:
        self.events.clear()


@pytest.fixture
def fake_event_bus() -> FakeEventBus:
    """Provide a fake event bus for testing."""
    return FakeEventBus()


# ─── Mock Connection ──────────────────────────────────────────────


class FakeBlenderConnection:
    """Mock Blender connection for testing without real socket."""

    def __init__(self) -> None:
        self._state = "disconnected"
        self._active_operation = False
        self._responses: dict[str, Any] = {}
        self._send_command_calls: list[dict] = []

    @property
    def state(self) -> str:
        return self._state

    @property
    def active_operation(self) -> bool:
        return self._active_operation

    async def connect(self, config: Any) -> Any:
        self._state = "connected"
        from modules.shared.src.server import ConnectionStatus
        return ConnectionStatus(
            state="connected",
            host=config.host if hasattr(config, 'host') else "localhost",
            port=config.port if hasattr(config, 'port') else 9876,
        )

    async def disconnect(self) -> None:
        self._state = "closed"

    async def send_command(
        self,
        action: str,
        params: dict | None = None,
        request_id: str | None = None,
        timeout_ms: float | None = None,
    ) -> Any:
        self._send_command_calls.append({
            "action": action,
            "params": params,
            "request_id": request_id,
            "timeout_ms": timeout_ms,
        })

        if hasattr(self, '_responses') and action in self._responses:
            return self._responses[action]
        return {"status": "ok", "data": None}

    def set_active_operation_in_progress(self, active: bool) -> None:
        self._active_operation = active

    async def get_status(self) -> Any:
        from modules.shared.src.server import ConnectionStatus
        return ConnectionStatus(
            state=self._state,
            host="localhost",
            port=9876,
        )


@pytest.fixture
def fake_connection() -> FakeBlenderConnection:
    """Provide a fake Blender connection for testing."""
    return FakeBlenderConnection()


# ─── Mock Config ──────────────────────────────────────────────────


@pytest.fixture
def fake_server_config():
    """Provide a minimal ServerConfig for testing."""
    from modules.shared.src.server import ServerConfig
    return ServerConfig(
        host="localhost",
        port=9876,
        queue_max_depth=10,
        queue_wait_timeout_ms=5000.0,
        execution_default_timeout_ms=10000.0,
        max_code_payload_bytes=1024,
        max_execution_output_bytes=512,
        max_command_response_bytes=1024,
    )


# ─── Async Mocks ──────────────────────────────────────────────────


@pytest.fixture
def async_mock() -> AsyncMock:
    """Provide an async mock for testing."""
    return AsyncMock()


@pytest.fixture
def mock_lock() -> MagicMock:
    """Provide a mock asyncio.Lock context manager."""
    lock = MagicMock()
    lock.__aenter__ = AsyncMock(return_value=None)
    lock.__aexit__ = AsyncMock(return_value=None)
    return lock
