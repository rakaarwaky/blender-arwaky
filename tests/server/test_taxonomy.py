"""Unit tests for server taxonomy value objects and constants.

Tests frozen dataclass immutability, type safety, and default values.
"""

from __future__ import annotations

import pytest

from modules.shared.src.server import (
    CodeSecurityPolicy,
    CommandResult,
    ConnectionConfig,
    ConnectionStatus,
    ExecutionErrorDetail,
    ExecutionResult,
    QueueConfig,
    QueuedOperation,
    RetryPolicy,
    ServerCommandSpec,
    ServerConfig,
    ServerMetrics,
    TaskManagerConfig,
    TaskStatus,
)


# ─── ConnectionStatus Tests ──────────────────────────────────────


class TestConnectionStatus:
    """Test ConnectionStatus VO."""

    def test_defaults(self) -> None:
        """Verify default values for ConnectionStatus."""
        status = ConnectionStatus(state="connected", host="localhost", port=9876)
        assert status.state == "connected"
        assert status.host == "localhost"
        assert status.port == 9876
        assert status.transport_type == "socket"
        assert status.protocol_version is None
        assert status.reconnect_attempts == 0

    def test_with_all_fields(self) -> None:
        """Verify ConnectionStatus with all fields set."""
        status = ConnectionStatus(
            state="reconnecting",
            host="192.168.1.1",
            port=9876,
            transport_type="socket",
            last_error="Connection refused",
            protocol_version="2.0.0",
            reconnect_attempts=2,
            session_id="test-session-uuid",
        )
        assert status.state == "reconnecting"
        assert status.last_error == "Connection refused"
        assert status.session_id == "test-session-uuid"

    def test_frozen_immutability(self) -> None:
        """Verify ConnectionStatus is immutable."""
        status = ConnectionStatus(state="connected", host="localhost", port=9876)
        with pytest.raises(Exception):  # dataclass frozen raises AttributeError
            status.state = "disconnected"


# ─── ExecutionResult Tests ──────────────────────────────────────


class TestExecutionResult:
    """Test ExecutionResult VO."""

    def test_success_result(self) -> None:
        """Verify success ExecutionResult creation."""
        result = ExecutionResult(
            status="success",
            data="output text",
            execution_time_ms=123.45,
            truncated=False,
            request_id="test-uuid",
        )
        assert result.status == "success"
        assert result.data == "output text"
        assert result.execution_time_ms == 123.45
        assert result.truncated is False

    def test_error_result(self) -> None:
        """Verify error ExecutionResult with detail."""
        error_detail = ExecutionErrorDetail(
            error_type="SyntaxError",
            message="invalid syntax",
            line=10,
        )
        result = ExecutionResult(
            status="error",
            error=error_detail,
            request_id="test-uuid",
        )
        assert result.status == "error"
        assert result.error.error_type == "SyntaxError"

    def test_default_values(self) -> None:
        """Verify default values for ExecutionResult."""
        result = ExecutionResult(status="success")
        assert result.data is None
        assert result.error is None
        assert result.execution_time_ms == 0.0
        assert result.truncated is False


# ─── TaskStatus Tests ──────────────────────────────────────────


class TestTaskStatus:
    """Test TaskStatus VO."""

    def test_pending_task(self) -> None:
        """Verify pending task status."""
        status = TaskStatus(task_id="task_001", state="pending")
        assert status.task_id == "task_001"
        assert status.state == "pending"
        assert status.result is None

    def test_completed_task(self) -> None:
        """Verify completed task with result."""
        exec_result = ExecutionResult(status="success", data="done")
        status = TaskStatus(
            task_id="task_002",
            state="success",
            result=exec_result,
            created_at=1000.0,
            completed_at=1050.0,
        )
        assert status.state == "success"
        assert status.result is exec_result

    def test_cancel_requested(self) -> None:
        """Verify task with cancel requested flag."""
        status = TaskStatus(
            task_id="task_003",
            state="running",
            cancel_requested=True,
        )
        assert status.cancel_requested is True


# ─── ServerMetrics Tests ────────────────────────────────────────


class TestServerMetrics:
    """Test ServerMetrics VO."""

    def test_default_metrics(self) -> None:
        """Verify default metrics are zero."""
        metrics = ServerMetrics()
        assert metrics.pending_operations == 0
        assert metrics.running_operations == 0
        assert metrics.code_execution_count == 0
        assert metrics.request_id is None

    def test_updated_metrics(self) -> None:
        """Verify metrics with updated counts."""
        import time
        metrics = ServerMetrics(
            pending_operations=5,
            running_operations=2,
            code_execution_count=100,
            command_count=50,
            reconnect_count=3,
            average_code_latency_ms=45.6,
            last_updated_at=time.monotonic(),
        )
        assert metrics.pending_operations == 5
        assert metrics.running_operations == 2
        assert metrics.code_execution_count == 100


# ─── ServerConfig Tests ────────────────────────────────────────


class TestServerConfig:
    """Test ServerConfig VO."""

    def test_defaults(self) -> None:
        """Verify default configuration values."""
        config = ServerConfig()
        assert config.host == "localhost"
        assert config.port == 9876
        assert config.queue_max_depth == 50
        assert config.queue_wait_timeout_ms == 10_000.0
        assert config.execution_default_timeout_ms == 30_000.0
        assert config.max_code_payload_bytes == 1_048_576

    def test_custom_config(self) -> None:
        """Verify custom configuration overrides."""
        config = ServerConfig(
            host="192.168.1.100",
            port=9877,
            queue_max_depth=100,
            execution_default_timeout_ms=60_000.0,
        )
        assert config.host == "192.168.1.100"
        assert config.port == 9877
        assert config.queue_max_depth == 100
        assert config.execution_default_timeout_ms == 60_000.0

    def test_frozen_immutability(self) -> None:
        """Verify ServerConfig is immutable."""
        config = ServerConfig()
        with pytest.raises(Exception):
            config.host = "0.0.0.0"


# ─── CodeSecurityPolicy Tests ──────────────────────────────────


class TestCodeSecurityPolicy:
    """Test CodeSecurityPolicy VO."""

    def test_defaults(self) -> None:
        """Verify default security policy."""
        policy = CodeSecurityPolicy()
        assert policy.allowed_directories == ()
        assert policy.max_payload_bytes == 1_048_576

    def test_custom_policy(self) -> None:
        """Verify custom security policy."""
        policy = CodeSecurityPolicy(
            allowed_directories=("/home/user/projects", "/tmp"),
            max_payload_bytes=2_097_152,
        )
        assert len(policy.allowed_directories) == 2
        assert policy.max_payload_bytes == 2_097_152


# ─── ServerCommandSpec Tests ──────────────────────────────────


class TestServerCommandSpec:
    """Test ServerCommandSpec VO and hashability."""

    def test_spec_defaults(self) -> None:
        """Verify default command spec values."""
        spec = ServerCommandSpec(name="test_command")
        assert spec.name == "test_command"
        assert spec.required_params == ()
        assert spec.optional_params == ()
        assert spec.idempotent is True
        assert spec.mutates_scene is False

    def test_spec_with_params(self) -> None:
        """Verify command spec with parameters."""
        spec = ServerCommandSpec(
            name="execute_code",
            required_params=("code",),
            optional_params=("timeout_ms",),
            default_timeout_ms=30_000.0,
            max_timeout_ms=120_000.0,
            idempotent=False,
            mutates_scene=True,
            background_allowed=True,
        )
        assert spec.name == "execute_code"
        assert spec.mutates_scene is True

    def test_hash_by_name(self) -> None:
        """Verify ServerCommandSpec hashes by name."""
        spec1 = ServerCommandSpec(name="test")
        spec2 = ServerCommandSpec(name="test")
        spec3 = ServerCommandSpec(name="other")
        assert hash(spec1) == hash(spec2)
        assert hash(spec1) != hash(spec3)

    def test_frozenset_usage(self) -> None:
        """Verify ServerCommandSpec can be used in frozenset."""
        specs = frozenset([
            ServerCommandSpec(name="cmd1"),
            ServerCommandSpec(name="cmd2"),
        ])
        assert len(specs) == 2
        assert ServerCommandSpec(name="cmd1") in specs


# ─── QueuedOperation Tests ──────────────────────────────────────


class TestQueuedOperation:
    """Test QueuedOperation VO."""

    def test_sync_operation(self) -> None:
        """Verify sync code operation."""
        op = QueuedOperation(
            request_id="req-001",
            operation_type="code_sync",
            payload={"code": "print('hello')"},
            timeout_ms=30_000.0,
        )
        assert op.request_id == "req-001"
        assert op.operation_type == "code_sync"

    def test_command_operation(self) -> None:
        """Verify command operation."""
        op = QueuedOperation(
            request_id="req-002",
            operation_type="command",
            payload={"action": "get_status", "params": {}},
            timeout_ms=5_000.0,
        )
        assert op.operation_type == "command"


# ─── QueueConfig Tests ────────────────────────────────────────


class TestQueueConfig:
    """Test QueueConfig VO."""

    def test_defaults(self) -> None:
        """Verify default queue config."""
        config = QueueConfig()
        assert config.max_depth == 50
        assert config.wait_timeout_ms == 10_000.0


# ─── TaskManagerConfig Tests ──────────────────────────────────


class TestTaskManagerConfig:
    """Test TaskManagerConfig VO."""

    def test_defaults(self) -> None:
        """Verify default task manager config."""
        config = TaskManagerConfig()
        assert config.retention_seconds == 600.0
