"""Capability: Code execution with AST validation and async task management.

FR-GWY-005: Execute Raw Python Code
- Validates code via security policy feature before transport
- Enforces execution timeout
- Truncates oversized output with truncation indicator
- Does not manage background task lifecycle
- Delegates security validation to security policy feature (ValidateCodeProtocol)
- Delegates code transport to gateway transport feature (TransportProtocol)

Contains CodeExecutionAdapter (asyncio-based, ICodeExecutionProtocol)
and CodeExecutionExecutor (sync socket-based, CodeExecutionProtocol).
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field

from modules.diagnostics.src.contract_audit_emission_protocol import (
    IEventPublisher,
)
from modules.shared.src.gateway.contract_code_execution_protocol import (
    CodeExecutionProtocol,
    ICodeExecutionProtocol,
)
from modules.shared.src.gateway.contract_connection_protocol import (
    IBlenderConnectionProtocol,
)
from modules.shared.src.gateway.contract_transport_protocol import (
    TransportProtocol,
)
from modules.shared.src.gateway.taxonomy_gateway_constant import (
    DEFAULT_EXECUTION_TIMEOUT_MS,
    MAX_EXECUTION_OUTPUT_BYTES,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    ExecutionTimeoutError,
    SecurityViolationError,
    TaskNotFoundError,
    TimeoutError,
    ValidationError,
)
from modules.shared.src.gateway.taxonomy_gateway_event import (
    CodeExecuted,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
)
from modules.shared.src.gateway.taxonomy_gateway_vo import (
    CodeExecutionOutcomeVO,
    CodeExecutionVO,
    CodeSecurityPolicy,
    ExecutionErrorDetail,
    ExecutionResult,
    ExecutionStatus,
    TaskManagerConfig,
    TaskState,
    TaskStatus,
    TransportMessageVO,
    TransportOutcomeVO,
)
from modules.shared.src.gateway.utility.utility_validator_checker import (
    check_payload_size,
    code_fingerprint,
    validate_code_ast,
)
from modules.shared.src.security.contract_validate_code_protocol import (
    ValidateCodeProtocol,
)
from modules.shared.src.security.taxonomy_security_error import (
    CodeValidationError,
)
from modules.shared.src.security.taxonomy_security_vo import (
    CodeValidationVO,
)

logger = logging.getLogger("BlenderMCPServer")


class CodeExecutionAdapter(ICodeExecutionProtocol):
    """Code execution with centralized AST validation, socket forwarding,
    and in-memory async task lifecycle management.
    """

    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        event_publisher: IEventPublisher,
        security_policy: CodeSecurityPolicy,
        task_config: TaskManagerConfig | None = None,
        default_timeout_ms: float = DEFAULT_EXECUTION_TIMEOUT_MS,
        max_output_bytes: int = MAX_EXECUTION_OUTPUT_BYTES,
    ) -> None:
        self._connection = connection_port
        self._event_publisher = event_publisher
        self._security_policy = security_policy
        self._task_config = task_config or TaskManagerConfig()
        self._default_timeout_ms = default_timeout_ms
        self._max_output_bytes = max_output_bytes
        self._tasks: dict[str, TaskEntry] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    async def execute_blender_code(
        self,
        code: str,
        request_id: str | None = None,
    ) -> ExecutionResult:
        fingerprint = code_fingerprint(code)
        code_len = len(code.encode("utf-8"))
        logger.info(
            "Executing Blender code: fingerprint=%s, length=%d bytes, request_id=%s",
            fingerprint,
            code_len,
            request_id,
        )
        check_payload_size(code, self._security_policy.max_payload_bytes)
        try:
            validate_code_ast(code, self._security_policy)
        except Exception as e:
            logger.warning("Code validation failed: fingerprint=%s, error=%s", fingerprint, e)
            raise
        start = time.monotonic()
        try:
            loop = asyncio.get_running_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._connection.send_command(
                        action="execute_code",
                        params={"code": code},
                        request_id=request_id,
                        timeout_ms=self._default_timeout_ms,
                    ),
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
            logger.warning("Code execution timed out after %.1fms", elapsed_ms)
            raise ExecutionTimeoutError(
                timeout_ms=self._default_timeout_ms,
                details={"request_id": request_id},
            ) from None
        except SecurityViolationError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            elapsed_ms = (time.monotonic() - start) * 1000
            logger.error("Code execution failed: fingerprint=%s, error=%s", fingerprint, e)
            return ExecutionResult(
                status=ExecutionStatus("error"),
                error=ExecutionErrorDetail(
                    error_type=type(e).__name__,
                    message=str(e),
                ),
                execution_time_ms=elapsed_ms,
                request_id=request_id,
            )

    async def execute_task(self, task_id: str, code: str, request_id: str | None = None) -> ExecutionResult:
        async with self._lock:
            entry = self._tasks.get(task_id)
            if entry is None:
                raise TaskNotFoundError(task_id=task_id)
            entry.state = TaskState("running")
        try:
            result = await self.execute_blender_code(code, request_id)
        except Exception as e:
            async with self._lock:
                entry = self._tasks.get(task_id)
                if entry:
                    entry.state = TaskState("error")
                    entry.result = ExecutionResult(
                        status=ExecutionStatus("error"),
                        error=ExecutionErrorDetail(
                            error_type=type(e).__name__,
                            message=str(e),
                        ),
                    )
                    entry.completed_at = time.monotonic()
            raise
        async with self._lock:
            entry = self._tasks.get(task_id)
            if entry:
                entry.state = TaskState("success")
                entry.result = result
                entry.completed_at = time.monotonic()
        return result

    async def create_task(self, request_id: str | None = None) -> str:
        task_id = f"task_{request_id or 'unnamed'}_{int(time.monotonic() * 1000) % 1000000:06d}"
        try:
            await self._event_publisher.publish(TaskCreated(task_id=task_id, request_id=request_id or ""))
        except Exception as e:
            logger.error("Failed to emit TaskCreated: %s", e)
        async with self._lock:
            self._tasks[task_id] = TaskEntry(
                task_id=task_id,
                state=TaskState("pending"),
                request_id=request_id,
                created_at=time.monotonic(),
            )
        logger.info("Created task %s", task_id)
        self.cleanup_expired()
        return task_id

    async def get_task(self, task_id: str) -> TaskStatus:
        async with self._lock:
            entry = self._tasks.get(task_id)
            if entry is None:
                raise TaskNotFoundError(task_id=task_id)
            if entry.completed_at is not None:
                elapsed = time.monotonic() - entry.completed_at
                if elapsed > self._task_config.retention_seconds:
                    del self._tasks[task_id]
                    raise TaskNotFoundError(task_id=task_id)
            return TaskStatus(
                task_id=entry.task_id,
                state=entry.state,
                result=entry.result,
                request_id=entry.request_id,
                created_at=entry.created_at,
                completed_at=entry.completed_at,
                cancel_requested=entry.cancel_requested,
            )

    async def poll_task_result(self, task_id: str, request_id: str | None = None) -> TaskStatus:
        async with self._lock:
            entry = self._tasks.get(task_id)
            if entry is None:
                raise TaskNotFoundError(task_id=task_id)
            if entry.completed_at is not None:
                elapsed = time.monotonic() - entry.completed_at
                if elapsed > self._task_config.retention_seconds:
                    del self._tasks[task_id]
                    raise TaskNotFoundError(task_id=task_id)
            status = TaskStatus(
                task_id=entry.task_id,
                state=entry.state,
                result=entry.result,
                request_id=request_id,
                created_at=entry.created_at,
                completed_at=entry.completed_at,
                cancel_requested=entry.cancel_requested,
            )
        if entry.state == TaskState("success"):
            try:
                await self._event_publisher.publish(TaskCompleted(task_id=task_id, execution_time_ms=0))
            except Exception as e:
                logger.error("Failed to emit TaskCompleted: %s", e)
        elif entry.state == TaskState("error"):
            try:
                await self._event_publisher.publish(
                    TaskFailed(task_id=task_id, error_type="ExecutionError", message=str(entry.result))
                )
            except Exception as e:
                logger.error("Failed to emit TaskFailed: %s", e)
        return status

    async def cancel_async_task(self, task_id: str, request_id: str | None = None) -> TaskStatus:
        async with self._lock:
            entry = self._tasks.get(task_id)
            if entry is None:
                raise TaskNotFoundError(task_id=task_id)
            status = TaskStatus(
                task_id=entry.task_id,
                state=entry.state,
                result=entry.result,
                request_id=request_id,
                created_at=entry.created_at,
                completed_at=entry.completed_at,
                cancel_requested=entry.cancel_requested,
            )
            if entry.state == TaskState("pending"):
                entry.state = TaskState("cancelled")
                entry.completed_at = time.monotonic()
                status = TaskStatus(
                    task_id=task_id,
                    state=TaskState("cancelled"),
                    request_id=request_id,
                )
            elif entry.state == TaskState("running"):
                entry.cancel_requested = True
        try:
            await self._event_publisher.publish(TaskCancelled(task_id=task_id))
        except Exception as e:
            logger.error("Failed to emit TaskCancelled: %s", e)
        return status

    def cleanup_expired(self) -> int:
        now = time.monotonic()
        expired = [
            tid
            for tid, e in self._tasks.items()
            if e.completed_at is not None and (now - e.completed_at) > self._task_config.retention_seconds
        ]
        for tid in expired:
            del self._tasks[tid]
            logger.info("Cleaned up expired task %s", tid)
        return len(expired)

    def __repr__(self) -> str:
        return f"CodeExecutionAdapter(task_retention={self._task_config.retention_seconds}s, tasks={len(self._tasks)})"


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
    Delegates security validation to ValidateCodeProtocol.
    Delegates code transport to TransportProtocol.
    """

    def __init__(
        self,
        security_policy: ValidateCodeProtocol | None = None,
        transport: TransportProtocol | None = None,
        max_output_bytes: int = 1_048_576,
        execution_timeout_seconds: float = 30.0,
    ) -> None:
        self._security_policy: ValidateCodeProtocol | None = security_policy
        self._transport: TransportProtocol | None = transport
        self._max_output_bytes: int = max_output_bytes
        self._execution_timeout_seconds: float = execution_timeout_seconds

    def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
        # Guard required dependencies
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
        self._validate_code(request)
        start_time = time.time()
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
        except SecurityViolationError:
            logger.error("Code execution blocked by security policy")
            raise
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
        try:
            result = self._security_policy.validate_code(security_request)
            if not result.allowed:
                violation_descriptions = "; ".join(v.description for v in result.violations)
                raise SecurityViolationError(f"Code validation failed: {violation_descriptions}")
        except CodeValidationError as e:
            raise SecurityViolationError(f"Security policy validation error: {e}") from e

    def _execute_via_transport(self, request: CodeExecutionVO, timeout_seconds: float) -> TransportOutcomeVO:
        tracking_id = request.tracking_id or str(hash(request.code))
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
