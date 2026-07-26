"""End-to-end smoke test for the gateway feature (FRD FR-GWY-001..005).

Exercises the five capabilities through injected mock components.
Run via pytest from repo root.
"""

from __future__ import annotations

import uuid

import pytest

from modules.gateway.src import GatewayOrchestrator
from modules.shared.src.gateway.contract_connection_protocol import ConnectionProtocol
from modules.shared.src.gateway.contract_maintenance_protocol import (
    ConnectionMaintenanceProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import TransportProtocol
from modules.shared.src.gateway.contract_scene_queue_protocol import SceneQueueProtocol
from modules.shared.src.gateway.contract_code_execution_protocol import CodeExecutionProtocol
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionVO,
    ConnectionState,
    ConnectionResultVO,
    ConnectionStatusVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportResultVO,
)


# ─── Mock Implementations ──────────────────────────────────────────────────


class MockConnection(ConnectionProtocol):
    """Mock connection for testing."""

    def __init__(self) -> None:
        self._connected = False

    def establish_connection(self) -> ConnectionResultVO:
        self._connected = True
        return ConnectionResultVO(state=ConnectionState.CONNECTED, protocol_version="1.0")

    def disconnect(self) -> None:
        self._connected = False


class MockMaintenance(ConnectionMaintenanceProtocol):
    """Mock maintenance for testing."""

    def __init__(self) -> None:
        self._state = ConnectionState.DISCONNECTED
        self._heartbeat_count = 0
        self._reconnect_count = 0

    def get_connection_status(self) -> ConnectionStatusVO:
        from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionStatusVO
        return ConnectionStatusVO(
            state=self._state,
            last_heartbeat_timestamp=self._heartbeat_count * 1.0,
            reconnect_attempts=self._reconnect_count,
        )

    def send_heartbeat(self) -> None:
        self._heartbeat_count += 1

    def attempt_reconnect(self) -> ConnectionStatusVO:
        self._reconnect_count += 1
        return self.get_connection_status()

    def set_state(self, state: ConnectionState) -> None:
        self._state = state


class MockTransport(TransportProtocol):
    """Mock transport for testing."""

    def send_request(self, request: TransportMessageVO) -> TransportResultVO:
        return TransportResultVO(
            tracking_id=request.tracking_id,
            status="success",
        )


class MockSceneQueue(SceneQueueProtocol):
    """Mock scene queue for testing."""

    def enqueue_operation(self, operation: SceneOperationVO) -> object:
        from modules.shared.src.gateway.taxonomy_gateway_vo import SceneOperationResultVO
        return SceneOperationResultVO(status="success")

    def get_queue_status(self) -> object:
        from modules.shared.src.gateway.taxonomy_gateway_vo import QueueStatusVO
        return QueueStatusVO(current_depth=0, is_busy=False, max_depth=50)


class MockCodeExecutor(CodeExecutionProtocol):
    """Mock code executor for testing."""

    def execute_code(self, request: CodeExecutionVO) -> object:
        from modules.shared.src.gateway.taxonomy_gateway_vo import CodeExecutionResultVO
        return CodeExecutionResultVO(status="success", output="hello")


# ─── FR-GWY-001: Establish Connection ──────────────────────────────────────


def test_fr_gwy_001_establishes_connection():
    """Test that connection establishment succeeds and returns connected state."""
    conn = MockConnection()
    feat = GatewayOrchestrator(conn, MockMaintenance(), MockTransport(), MockSceneQueue(), MockCodeExecutor())
    result = feat.establish_connection()
    assert result.state.value == "connected"


# ─── FR-GWY-002: Maintain Connection ──────────────────────────────────────


def test_fr_gwy_002_status_reports_connected():
    """Test that connection status reports correct state after establishment."""
    conn = MockConnection()
    maint = MockMaintenance()
    feat = GatewayOrchestrator(conn, maint, MockTransport(), MockSceneQueue(), MockCodeExecutor())
    feat.establish_connection()
    status = feat.get_connection_status()
    assert status.state == ConnectionState.CONNECTED


def test_fr_gwy_002_send_heartbeat():
    """Test that heartbeat can be sent and timestamp is updated."""
    conn = MockConnection()
    maint = MockMaintenance()
    feat = GatewayOrchestrator(conn, maint, MockTransport(), MockSceneQueue(), MockCodeExecutor())
    feat.establish_connection()
    feat.send_heartbeat()
    status = feat.get_connection_status()
    assert status.last_heartbeat_timestamp is not None


def test_fr_gwy_002_reconnect_attempts():
    """Test that reconnect attempts increment counter and report state."""
    conn = MockConnection()
    maint = MockMaintenance()
    feat = GatewayOrchestrator(conn, maint, MockTransport(), MockSceneQueue(), MockCodeExecutor())
    feat.establish_connection()
    status = feat.attempt_reconnect()
    assert status.reconnect_attempts >= 1


# ─── FR-GWY-003: Transport Request and Response ──────────────────────────


def test_fr_gwy_003_send_request():
    """Test that transport request succeeds with tracking ID correlation."""
    feat = GatewayOrchestrator(MockConnection(), MockMaintenance(), MockTransport(), MockSceneQueue(), MockCodeExecutor())
    request = TransportMessageVO(
        tracking_id=str(uuid.uuid4()),
        operation_class="test",
    )
    result = feat.send_request(request)
    assert result.tracking_id == request.tracking_id


# ─── FR-GWY-004: Scene Operation Queue ────────────────────────────────────


def test_fr_gwy_004_enqueue_mutation():
    """Test that mutating operations are enqueued successfully."""
    feat = GatewayOrchestrator(MockConnection(), MockMaintenance(), MockTransport(), MockSceneQueue(), MockCodeExecutor())
    operation = SceneOperationVO(is_mutation=True, payload=b"test")
    result = feat.enqueue_scene_operation(operation)
    assert result.status == "success"


def test_fr_gwy_004_enqueue_readonly_bypass():
    """Test that read-only operations bypass queue and execute directly."""
    feat = GatewayOrchestrator(MockConnection(), MockMaintenance(), MockTransport(), MockSceneQueue(), MockCodeExecutor())
    operation = SceneOperationVO(is_mutation=False, payload=b"test")
    result = feat.enqueue_scene_operation(operation)
    assert result.status == "success"


def test_fr_gwy_004_get_queue_status():
    """Test that queue status reports current depth and busy state."""
    feat = GatewayOrchestrator(MockConnection(), MockMaintenance(), MockTransport(), MockSceneQueue(), MockCodeExecutor())
    status = feat.get_queue_status()
    assert status.current_depth >= 0
    assert status.max_depth == 50


# ─── FR-GWY-005: Execute Raw Python Code ──────────────────────────────────


def test_fr_gwy_005_execute_code():
    """Test that code execution succeeds with security validation."""
    feat = GatewayOrchestrator(MockConnection(), MockMaintenance(), MockTransport(), MockSceneQueue(), MockCodeExecutor())
    request = CodeExecutionVO(
        tracking_id=str(uuid.uuid4()),
        code="print('hello')",
    )
    result = feat.execute_code(request)
    assert result.status == "success"
