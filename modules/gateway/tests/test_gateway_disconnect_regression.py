from __future__ import annotations

from modules.gateway.src.agent_gateway_orchestrator import GatewayOrchestrator
from modules.shared.src.gateway.taxonomy_gateway_vo import ConnectionState


class ConnectionStub:
    def __init__(self) -> None:
        self.disconnected = False

    def disconnect(self) -> None:
        self.disconnected = True


class QueueStub:
    def __init__(self) -> None:
        self.failed: list[Exception] = []

    def fail_pending(self, error: Exception) -> None:
        self.failed.append(error)


class MaintenanceStub:
    def __init__(self) -> None:
        self.states: list[object] = []

    def set_state(self, state: object) -> None:
        self.states.append(state)


class TransportStub:
    pass


class ExecutorStub:
    pass


def test_disconnect_fails_pending_queue_without_keyword_type_error() -> None:
    connection = ConnectionStub()
    queue = QueueStub()
    maintenance = MaintenanceStub()
    gateway = GatewayOrchestrator(
        connection=connection,
        transport=TransportStub(),
        scene_queue=queue,
        code_executor=ExecutorStub(),
        maintenance=maintenance,
    )

    gateway.disconnect()

    assert connection.disconnected is True  # nosec B101
    assert len(queue.failed) == 1  # nosec B101
    assert queue.failed[0].details["reason"] == "graceful_disconnect"  # nosec B101
    assert maintenance.states[-1] == ConnectionState.CLOSED  # nosec B101
