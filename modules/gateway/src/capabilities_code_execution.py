"""Capability: Code execution with security validation and transport delegation.

FR-GWY-005: Execute Raw Python Code
- Validates code via security policy feature before transport
- Enforces execution timeout
- Truncates oversized output with truncation indicator
- Does not manage background task lifecycle
- Delegates security validation to gateway-local CodeValidationProtocol (wired to security validator)
- Delegates code transport to gateway transport feature (TransportProtocol)

Contains CodeExecutionAdapter (asyncio-based, ICodeExecutionProtocol)
and CodeExecutionExecutor (sync socket-based, CodeExecutionProtocol).
"""

from __future__ import annotations

import asyncio
import logging
import time
import uuid
from dataclasses import dataclass, field

from modules.shared.src.gateway.contract_code_execution_protocol import (
    CodeExecutionProtocol,
    ICodeExecutionProtocol,
)
from modules.shared.src.gateway.contract_code_validation_protocol import (
    CodeValidationProtocol,
)
from modules.shared.src.gateway.contract_connection_protocol import (
    IBlenderConnectionProtocol,
)
from modules.shared.src.gateway.contract_event_protocol import (
    IEventPublisher,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_constant import (
    DEFAULT_EXECUTION_TIMEOUT_MS,
    MAX_EXECUTION_OUTPUT_BYTES,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    ConnectionClosedError,
    ExecutionTimeoutError,
    SecurityViolationError,
    TimeoutError,
)
from modules.shared.src.gateway.taxonomy_gateway_event import (
    CodeExecuted,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    ExecutionResult,
    ExecutionStatus,
    TaskState,
    TransportMessageVO,
    TransportOutcomeVO,
)
from modules.shared.src.security.taxonomy_security_vo import (
    CodeValidationVO,
)

logger = logging.getLogger("BlenderMCPServer")


class CodeExecutionAdapter(ICodeExecutionProtocol):
    """Async code execution adapter delegating to connection and events."""

    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        event_publisher: IEventPublisher,
        default_timeout_ms: float = DEFAULT_EXECUTION_TIMEOUT_MS,
        max_output_bytes: int = MAX_EXECUTION_OUTPUT_BYTES,
    ) -> None:
        self._connection = connection_port
        self._event_publisher = event_publisher
        self._default_timeout_ms = default_timeout_ms
        self._max_output_bytes = max_output_bytes

    async def execute_blender_code(
        self,
        code: str,
        request_id: str | None = None,
    ) -> ExecutionResult:
        start = time.monotonic()
        try:
            result = await asyncio.wait_for(
                self._connection.send_command(
                    action="execute_code",
                    params={"code": code},
                    request_id=request_id,
                    timeout_ms=self._default_timeout_ms,
                ),
                timeout=self._default_timeout_ms / 1000.0,
            )
            elapsed_ms = (time.monotonic() - start) * 1000
            data = result.data if result.data is not None else ""
            truncated = False
            if isinstance(data, str) and len(data.encode("utf-8")) > self._max_output_bytes:
                data = data[: self._max_output_bytes] + "\n...[truncated]"
                truncated = True
            exec_result = ExecutionResult(
                status=ExecutionStatus("success"),
                data=data,
                truncated=truncated,
                execution_time_ms=elapsed_ms,
                request_id=request_id,
            )
            await self._event_publisher.publish(
                CodeExecuted(
                    request_id=request_id or "",
                    execution_time_ms=elapsed_ms,
                    truncated=truncated,
                )
            )
            return exec_result
        except asyncio.TimeoutError:
            elapsed_ms = (time.monotonic() - start) * 1000
            raise ExecutionTimeoutError(
                timeout_ms=self._default_timeout_ms,
                details={"request_id": request_id},
            ) from None
        except ConnectionClosedError:
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            raise RuntimeError(f"Code execution failed: {e}") from e

    async def execute_task(self, _task_id: str, _code: str, _request_id: str | None = None) -> ExecutionResult:
        raise RuntimeError("Task lifecycle management belongs to the Job feature")

    async def create_task(self, _request_id: str | None = None) -> str:
        raise RuntimeError("Task lifecycle management belongs to the Job feature")

    async def get_task(self, _task_id: str) -> object:
        raise RuntimeError("Task lifecycle management belongs to the Job feature")

    async def poll_task_result(self, _task_id: str, _request_id: str | None = None) -> object:
        raise RuntimeError("Task lifecycle management belongs to the Job feature")

    async def cancel_async_task(self, _task_id: str, _request_id: str | None = None) -> object:
        raise RuntimeError("Task lifecycle management belongs to the Job feature")

    def cleanup_expired(self) -> int:
        return 0

    def __repr__(self) -> str:
        return f"CodeExecutionAdapter(timeout={self._default_timeout_ms}ms)"


@dataclass
class TaskEntry:
    task_id: str
    state: TaskState
    result: ExecutionResult | None = None
    request_id: str | None = None
    created_at: float = field(default_factory=time.monotonic)
    completed_at: float | None = None
    cancel_requested: bool = False


class CodeExecutionExecutor(CodeExecutionProtocol):
    """Concrete implementation for raw Python code execution.

    FR-GWY-005: Validates via security policy before transport. Enforces timeout.
    Truncates oversized output. Does not manage background task lifecycle.
    Delegates security validation to CodeValidationProtocol (gateway-local).
    Delegates code transport to TransportProtocol.
    """

    def __init__(
        self,
        security_policy: CodeValidationProtocol | None = None,
        transport: TransportProtocol | None = None,
        max_output_bytes: int = 1_048_576,
        execution_timeout_seconds: float = 30.0,
    ) -> None:
        self._security_policy: CodeValidationProtocol | None = security_policy
        self._transport: TransportProtocol | None = transport
        self._max_output_bytes: int = max_output_bytes
        self._execution_timeout_seconds: float = execution_timeout_seconds

    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        if self._security_policy is None:
            return CodeExecutionOutcomeVO(
                status="error",
                error_message="Security policy not configured",
            )
        if self._transport is None:
            return CodeExecutionOutcomeVO(
                status="error",
                error_message="Transport not configured",
            )
        start_time = time.time()
        try:
            self._validate_code(request)
        except SecurityViolationError:
            logger.error("Code execution blocked by security policy")
            raise
        timeout = request.timeout_override_seconds or self._execution_timeout_seconds
        try:
            outcome = self._execute_via_transport(request, timeout)
            duration_ms = (time.time() - start_time) * 1000
            output = outcome.payload.decode("utf-8") if outcome.payload else ""
            truncated = False
            if len(output.encode("utf-8")) > self._max_output_bytes:
                output = output[: self._max_output_bytes]
                truncated = True
            logger.debug(
                "Code execution complete: status=%s, %.1fms, truncated=%s",
                outcome.status,
                duration_ms,
                truncated,
            )
            return CodeExecutionOutcomeVO(
                status=outcome.status,
                output=output[:500],
                truncated=truncated,
                duration_ms=duration_ms,
                error_category=outcome.error,
                error_message=outcome.error,
            )
        except TimeoutError:
            logger.error("Code execution timed out after %.1fs", timeout)
            return CodeExecutionOutcomeVO(
                status="timeout",
                error_message=f"Execution timed out after {timeout}s",
                duration_ms=(time.time() - start_time) * 1000,
            )
        except Exception as e:
            logger.error("Code execution failed: %s", e)
            return CodeExecutionOutcomeVO(
                status="error",
                error_category="runtime",
                error_message=str(e),
                duration_ms=(time.time() - start_time) * 1000,
            )

    def _validate_code(self, request: CodeExecutionVO) -> None:
        security_request = CodeValidationVO(
            code_text=request.code,
            max_code_size=100_000,
            strict_mode=True,
            execution_context="gateway_code_execution",
        )
        result = self._security_policy.validate_code(security_request)
        if not result.allowed:
            violation_descriptions = "; ".join(v.description for v in result.violations)
            raise SecurityViolationError(f"Code validation failed: {violation_descriptions}")

    def _execute_via_transport(self, request: CodeExecutionVO, timeout_seconds: float) -> TransportOutcomeVO:
        tracking_id = request.tracking_id or str(uuid.uuid4())
        transport_request = TransportMessageVO(
            tracking_id=tracking_id,
            operation_class="code_execution",
            payload=request.code.encode("utf-8"),
            timeout_override_seconds=timeout_seconds,
        )
        return self._transport.send_request(transport_request)

    def __repr__(self) -> str:
        return (
            f"CodeExecutionExecutor(security={self._security_policy!r}, "
            f"transport={self._transport!r}, "
            f"max_output={self._max_output_bytes}, "
            f"timeout={self._execution_timeout_seconds})"
        )
