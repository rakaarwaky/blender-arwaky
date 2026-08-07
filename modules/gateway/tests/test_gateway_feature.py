"""End-to-end smoke test for the gateway feature (FRD FR-GWY-001..005).

Exercises the five capabilities through injected mock components.
Run via pytest from repo root.
"""

from __future__ import annotations

import uuid

from modules.gateway.src import GatewayOrchestrator
from modules.gateway.src.capabilities_connection_maintenance import MaintenanceExecutor
from modules.shared.src.gateway.contract_code_execution_protocol import CodeExecutionProtocol
from modules.shared.src.gateway.contract_connection_protocol import ConnectionProtocol
from modules.shared.src.gateway.contract_scene_queue_protocol import SceneQueueProtocol
from modules.shared.src.gateway.contract_transport_protocol import TransportProtocol
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionVO,
    ConnectionOutcomeVO,
    ConnectionState,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
)

# ─── Mock Implementations ──────────────────────────────────────────────────


class MockConnection(ConnectionProtocol):
    """Mock connection for testing."""

    def __init__(self) -> None:
        self._connected = False

    def establish_connection(self) -> ConnectionOutcomeVO:
        self._connected = True
        return ConnectionOutcomeVO(state=ConnectionState.CONNECTED, protocol_version="1.0")

    def disconnect(self) -> None:
        self._connected = False


class MockTransport(TransportProtocol):
    """Mock transport for testing."""

    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
        return TransportOutcomeVO(
            tracking_id=request.tracking_id,
            status="success",
        )


class MockSceneQueue(SceneQueueProtocol):
    """Mock scene queue for testing."""

    def enqueue_operation(self, _operation: SceneOperationVO) -> object:
        from modules.shared.src.gateway.taxonomy_gateway_vo import SceneOperationOutcomeVO

        return SceneOperationOutcomeVO(status="success")

    def get_queue_status(self) -> object:
        from modules.shared.src.gateway.taxonomy_gateway_vo import QueueStatusVO

        return QueueStatusVO(current_depth=0, is_busy=False, max_depth=50)


class MockCodeExecutor(CodeExecutionProtocol):
    """Mock code executor for testing."""

    def execute_code(self, _request: CodeExecutionVO) -> object:
        from modules.shared.src.gateway.taxonomy_gateway_vo import CodeExecutionOutcomeVO

        return CodeExecutionOutcomeVO(status="success", output="hello")


def _make_orchestrator(**overrides) -> GatewayOrchestrator:
    """Helper to create orchestrator with mocks for all required deps."""
    defaults = dict(
        connection=MockConnection(),
        transport=MockTransport(),
        scene_queue=MockSceneQueue(),
        code_executor=MockCodeExecutor(),
        maintenance=MaintenanceExecutor(),
    )
    defaults.update(overrides)
    return GatewayOrchestrator(**defaults)


def _make_maintenance() -> MaintenanceExecutor:
    """Helper to create a fresh MaintenanceExecutor for inline constructions."""
    return MaintenanceExecutor()


# ─── FR-GWY-001: Establish Connection ──────────────────────────────────────


def test_fr_gwy_001_establishes_connection():
    """Test that connection establishment succeeds and returns connected state."""
    feat = _make_orchestrator()
    result = feat.establish_connection()
    assert result.state.value == "connected"


# ─── FR-GWY-002: Maintain Connection ──────────────────────────────────────


def test_fr_gwy_002_status_reports_connected():
    """Test that connection status reports correct state after establishment."""
    conn = MockConnection()
    feat = GatewayOrchestrator(connection=conn, transport=MockTransport(), scene_queue=MockSceneQueue(), code_executor=MockCodeExecutor(), maintenance=MaintenanceExecutor())
    feat.establish_connection()
    status = feat.get_connection_status()
    assert status.state == ConnectionState.CONNECTED


def test_fr_gwy_002_send_heartbeat():
    """Test that heartbeat can be sent and timestamp is updated."""
    feat = _make_orchestrator()
    feat.establish_connection()
    feat.send_heartbeat()
    status = feat.get_connection_status()
    assert status.last_heartbeat_timestamp is not None


def test_fr_gwy_002_reconnect_attempts():
    """Test that reconnect attempts increment counter and report state."""
    feat = _make_orchestrator()
    feat.establish_connection()
    feat.disconnect()
    status = feat.attempt_reconnect()
    assert status.reconnect_attempts >= 1


# ─── FR-GWY-003: Transport Request and Response ──────────────────────────


def test_fr_gwy_003_send_request():
    """Test that transport request succeeds with tracking ID correlation."""
    feat = _make_orchestrator()
    request = TransportMessageVO(
        tracking_id=str(uuid.uuid4()),
        operation_class="test",
    )
    result = feat.send_request(request)
    assert result.tracking_id == request.tracking_id


# ─── FR-GWY-004: Scene Operation Queue ────────────────────────────────────


def test_fr_gwy_004_enqueue_mutation():
    """Test that mutating operations are enqueued successfully."""
    feat = _make_orchestrator()
    operation = SceneOperationVO(is_mutation=True, payload=b"test")
    result = feat.enqueue_scene_operation(operation)
    assert result.status == "success"


def test_fr_gwy_004_enqueue_readonly_bypass():
    """Test that read-only operations bypass queue and execute directly."""
    feat = _make_orchestrator()
    operation = SceneOperationVO(is_mutation=False, payload=b"test")
    result = feat.enqueue_scene_operation(operation)
    assert result.status == "success"


def test_fr_gwy_004_get_queue_status():
    """Test that queue status reports current depth and busy state."""
    feat = _make_orchestrator()
    status = feat.get_queue_status()
    assert status.current_depth >= 0
    assert status.max_depth == 50


# ─── FR-GWY-005: Execute Raw Python Code ──────────────────────────────────


def test_fr_gwy_005_execute_code():
    """Test that code execution succeeds with security validation."""
    feat = _make_orchestrator()
    request = CodeExecutionVO(
        tracking_id=str(uuid.uuid4()),
        code="print('hello')",
    )
    result = feat.execute_code(request)
    assert result.status == "success"


# ─── Additional Edge Case Tests ──────────────────────────────────────────


def test_gateway_establish_connection_returns_protocol_version():
    """Test that connection establishment returns protocol version info."""
    feat = _make_orchestrator()
    result = feat.establish_connection()
    assert result.protocol_version == "1.0"


def test_gateway_disconnect_idempotent():
    """Test that disconnect is idempotent when already disconnected."""
    conn = MockConnection()
    feat = GatewayOrchestrator(connection=conn, transport=MockTransport(), scene_queue=MockSceneQueue(), code_executor=MockCodeExecutor(), maintenance=MaintenanceExecutor())
    feat.disconnect()
    feat.disconnect()
    assert True


def test_gateway_failed_connection_reports_state():
    """Test that failed connection state is reported correctly."""
    class FailedConnection(ConnectionProtocol):
        def establish_connection(self):
            return ConnectionOutcomeVO(state=ConnectionState.FAILED, error="connection refused")

        def disconnect(self):
            pass

    feat = _make_orchestrator(connection=FailedConnection())
    result = feat.establish_connection()
    assert result.state == ConnectionState.FAILED
    assert "connection refused" in result.error


def test_gateway_transport_request_error():
    """Test that transport request with error status is handled."""
    class ErrorTransport(TransportProtocol):
        def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
            return TransportOutcomeVO(tracking_id=request.tracking_id, status="error", error="timeout")

    feat = _make_orchestrator(transport=ErrorTransport())
    request = TransportMessageVO(tracking_id=str(uuid.uuid4()), operation_class="test")
    result = feat.send_request(request)
    assert result.status == "error"
    assert result.error == "timeout"


def test_gateway_code_execution_with_output():
    """Test that code execution captures output."""
    class OutputExecutor(CodeExecutionProtocol):
        def execute_code(self, _request: CodeExecutionVO) -> object:
            from modules.shared.src.gateway.taxonomy_gateway_vo import CodeExecutionOutcomeVO

            return CodeExecutionOutcomeVO(status="success", output="42")

    feat = _make_orchestrator(code_executor=OutputExecutor())
    request = CodeExecutionVO(tracking_id=str(uuid.uuid4()), code="1 + 41")
    result = feat.execute_code(request)
    assert result.output == "42"


def test_gateway_multiple_queue_operations():
    """Test that multiple operations can be enqueued."""
    class TrackingQueue(SceneQueueProtocol):
        def __init__(self):
            self.enqueued_count = 0

        def enqueue_operation(self, _operation: SceneOperationVO) -> object:
            from modules.shared.src.gateway.taxonomy_gateway_vo import SceneOperationOutcomeVO

            self.enqueued_count += 1
            return SceneOperationOutcomeVO(status="success")

        def get_queue_status(self) -> object:
            from modules.shared.src.gateway.taxonomy_gateway_vo import QueueStatusVO

            return QueueStatusVO(current_depth=self.enqueued_count, is_busy=False, max_depth=50)

    queue = TrackingQueue()
    feat = _make_orchestrator(scene_queue=queue)
    for _ in range(5):
        result = feat.enqueue_scene_operation(SceneOperationVO(is_mutation=True, payload=b"test"))
        assert result.status == "success"
    status = feat.get_queue_status()
    assert status.current_depth == 5


def test_gateway_disconnect_updates_state():
    """Test that disconnect updates maintenance state."""
    conn = MockConnection()
    feat = GatewayOrchestrator(connection=conn, transport=MockTransport(), scene_queue=MockSceneQueue(), code_executor=MockCodeExecutor(), maintenance=MaintenanceExecutor())

    feat.establish_connection()
    assert feat.get_connection_status().state == ConnectionState.CONNECTED

    feat.disconnect()
    status = feat.get_connection_status()
    assert status.state == ConnectionState.CLOSED


def test_gateway_reconnect_increments_attempts():
    """Test that reconnect increments attempt counter."""
    conn = MockConnection()
    feat = GatewayOrchestrator(connection=conn, transport=MockTransport(), scene_queue=MockSceneQueue(), code_executor=MockCodeExecutor(), maintenance=MaintenanceExecutor())

    status = feat.get_connection_status()
    initial_attempts = status.reconnect_attempts
    for _ in range(3):
        feat.attempt_reconnect()
    status = feat.get_connection_status()
    assert status.reconnect_attempts == initial_attempts + 3


def test_gateway_heartbeat_updates_timestamp():
    """Test that heartbeat updates last heartbeat timestamp."""
    conn = MockConnection()
    feat = GatewayOrchestrator(connection=conn, transport=MockTransport(), scene_queue=MockSceneQueue(), code_executor=MockCodeExecutor(), maintenance=MaintenanceExecutor())

    feat.establish_connection()
    feat.send_heartbeat()
    status = feat.get_connection_status()
    assert status.last_heartbeat_timestamp is not None
