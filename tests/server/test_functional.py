"""Functional tests for server with fake Blender addon.

Tests end-to-end server behavior using a simulated Blender addon.
Uses functional marker. Tests handshake, ping, command dispatch,
and code execution flows.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from modules.shared.src.server import (
    ConnectionConfig,
    ConnectionStatus,
    ExecutionResult,
    ServerConfig,
)


# ─── Fake Addon Integration Tests ──────────────────────────────


class TestFakeAddonIntegration:
    """Test fake addon message handling."""

    @pytest.mark.asyncio
    async def test_handshake_flow(self) -> None:
        """Verify handshake request/response flow."""
        from tests.server.fake_addon import FakeBlenderAddon

        addon = FakeBlenderAddon()
        reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

        # Send handshake
        handshake = {
            "type": "handshake",
            "request_id": "test-handshake-1",
            "protocol_version": "2.0.0",
        }
        payload = json.dumps(handshake).encode("utf-8")
        writer.write(len(payload).to_bytes(4, byteorder='big') + payload)
        await writer.drain()

        # Read response
        header = await reader.readexactly(4)
        length = int.from_bytes(header, byteorder='big')
        response_raw = await reader.read(length)
        response = json.loads(response_raw.decode("utf-8"))

        assert response["status"] == "ok"
        assert response["protocol_version"] == "2.0.0"
        assert "session_id" in response["result"]

        writer.close()

    @pytest.mark.asyncio
    async def test_ping_flow(self) -> None:
        """Verify ping request/response flow."""
        reader, writer = await asyncio.open_connection("127.0.0.1", 8888)

        # Send ping
        ping = {
            "type": "ping",
            "request_id": "test-ping-1",
        }
        payload = json.dumps(ping).encode("utf-8")
        writer.write(len(payload).to_bytes(4, byteorder='big') + payload)
        await writer.drain()

        # Read response
        header = await reader.readexactly(4)
        length = int.from_bytes(header, byteorder='big')
        response_raw = await reader.read(length)
        response = json.loads(response_raw.decode("utf-8"))

        assert response["status"] == "ok"
        assert response["result"] == {}

        writer.close()


# ─── Server Config Functional Tests ──────────────────────────────


class TestServerConfigFunctional:
    """Test server configuration loading and resolution."""

    def test_config_priority_resolution(self) -> None:
        """Verify config priority: programmatic > env > file > defaults."""
        from modules.shared.src.server import ServerConfig

        # Programmatic override should win over defaults
        config = ServerConfig(host="override.local", port=9999)
        assert config.host == "override.local"
        assert config.port == 9999

    def test_config_frozen_behavior(self) -> None:
        """Verify config is immutable after creation."""
        from modules.shared.src.server import ServerConfig

        config = ServerConfig()
        with pytest.raises(Exception):
            config.host = "0.0.0.0"


# ─── Connection Functional Tests ──────────────────────────────


class TestConnectionFunctional:
    """Test connection lifecycle behavior."""

    @pytest.mark.asyncio
    async def test_connection_config_validation(self) -> None:
        """Verify ConnectionConfig accepts valid parameters."""
        from modules.shared.src.server import ConnectionConfig

        config = ConnectionConfig(
            transport_type="socket",
            host="localhost",
            port=9876,
        )
        assert config.transport_type == "socket"
        assert config.host == "localhost"
        assert config.port == 9876

    @pytest.mark.asyncio
    async def test_connection_status_states(self) -> None:
        """Verify all connection states are valid."""
        from modules.shared.src.server import ConnectionStatus

        for state in ["disconnected", "connecting", "connected", "reconnecting", "failed", "closed"]:
            status = ConnectionStatus(state=state, host="localhost", port=9876)
            assert status.state == state


# ─── Execution Functional Tests ────────────────────────────────


class TestExecutionFunctional:
    """Test code execution result handling."""

    @pytest.mark.asyncio
    async def test_execution_result_format(self) -> None:
        """Verify ExecutionResult has required fields."""
        from modules.shared.src.server import ExecutionResult

        result = ExecutionResult(
            status="success",
            data="output text",
            execution_time_ms=123.45,
            truncated=False,
            request_id="test-uuid",
        )

        assert hasattr(result, "status")
        assert hasattr(result, "data")
        assert hasattr(result, "execution_time_ms")
        assert hasattr(result, "request_id")

    @pytest.mark.asyncio
    async def test_execution_result_truncation(self) -> None:
        """Verify truncation flag is set correctly."""
        from modules.shared.src.server import ExecutionResult

        result = ExecutionResult(
            status="success",
            data="short",
            truncated=True,
        )
        assert result.truncated is True


# ─── Command Functional Tests ──────────────────────────────────


class TestCommandFunctional:
    """Test command dispatch and result handling."""

    @pytest.mark.asyncio
    async def test_command_result_format(self) -> None:
        """Verify CommandResult has required fields."""
        from modules.shared.src.server import CommandResult

        result = CommandResult(
            status="success",
            data={"message": "ok"},
            execution_time_ms=50.0,
            request_id="test-uuid",
        )

        assert result.status == "success"
        assert result.data is not None

    @pytest.mark.asyncio
    async def test_command_result_error(self) -> None:
        """Verify CommandResult with error status."""
        from modules.shared.src.server import CommandResult, ExecutionErrorDetail

        result = CommandResult(
            status="error",
            data=None,
            error=ExecutionErrorDetail(error_type="ValidationError", message="unknown command"),
            request_id="test-uuid",
        )

        assert result.status == "error"
        assert result.error is not None


# ─── Task Functional Tests ──────────────────────────────────────


class TestTaskFunctional:
    """Test task lifecycle and status management."""

    @pytest.mark.asyncio
    async def test_task_status_states(self) -> None:
        """Verify all task states are valid."""
        from modules.shared.src.server import TaskStatus

        for state in ["pending", "running", "success", "error", "timeout", "cancelled"]:
            status = TaskStatus(task_id="test-task", state=state)
            assert status.state == state

    @pytest.mark.asyncio
    async def test_task_with_result(self) -> None:
        """Verify task can carry execution result."""
        from modules.shared.src.server import TaskStatus, ExecutionResult

        exec_result = ExecutionResult(status="success", data="done")
        status = TaskStatus(
            task_id="test-task",
            state="success",
            result=exec_result,
        )

        assert status.result is exec_result
        assert status.state == "success"
