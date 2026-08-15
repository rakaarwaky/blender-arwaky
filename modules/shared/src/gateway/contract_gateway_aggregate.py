"""Gateway domain contract: aggregate facade for gateway feature."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ConnectionOutcomeVO,
    ConnectionStatusVO,
    QueueStatusVO,
    SceneOperationOutcomeVO,
    SceneOperationVO,
    TransportMessageVO,
    TransportOutcomeVO,
)


class IGatewayAggregate(ABC):
    """Public gateway facade consumed by surfaces and composed by root."""

    @abstractmethod
    def establish_connection(self) -> ConnectionOutcomeVO: ...

    @abstractmethod
    def disconnect(self) -> None: ...

    @abstractmethod
    def get_connection_status(self) -> ConnectionStatusVO: ...

    @abstractmethod
    def send_heartbeat(self) -> None: ...

    @abstractmethod
    def attempt_reconnect(self) -> ConnectionStatusVO: ...

    @abstractmethod
    def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO: ...

    @abstractmethod
    def enqueue_scene_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO: ...

    @abstractmethod
    def get_queue_status(self) -> QueueStatusVO: ...

    @abstractmethod
    def execute_blender_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO: ...
