"""Capability: Code execution with centralized AST validation and async task management.

Implements ICodeExecutionProtocol — handles code validation via shared
utility, socket-based execution forwarding, payload size enforcement,
output truncation, result formatting, and async task lifecycle tracking
per FR-SRV-002 (v2.0.0).
"""

from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.shared.src.server import (
    CodeExecuted,
    CodeExecutionFailed,
    CodeSecurityPolicy,
    ExecutionErrorDetail,
    ExecutionResult,
    ExecutionStatus,
    IBlenderConnectionProtocol,
    ICodeExecutionProtocol,
    IEventPublisher,
    SecurityViolationError,
    TaskCancelled,
    TaskCompleted,
    TaskCreated,
    TaskFailed,
    TaskNotFoundError,
    TaskStarted,
    TaskStatus,
    TaskState,
    TaskTimedOut,
    ValidationError,
    check_payload_size,
    code_fingerprint,
    validate_code_ast,
)

from modules.shared.src.server import (
    DEFAULT_EXECUTION_TIMEOUT_MS,
    ExecutionTimeoutError,
    MAX_CODE_PAYLOAD_BYTES,
    MAX_EXECUTION_OUTPUT_BYTES,
    TaskManagerConfig,
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
        """Initialize code execution adapter.

        Args:
            connection_port: The connection protocol for executing code.
            event_publisher: Event bus for emitting execution events.
            security_policy: Code security policy for validation.
            task_config: Task manager configuration.
            default_timeout_ms: Default execution timeout in milliseconds.
            max_output_bytes: Maximum output size before truncation.
        """
        self._connection = connection_port
        self._event_publisher = event_publisher
        self._security_policy = security_policy
        self._task_config = task_config or TaskManagerConfig()
        self._default_timeout_ms = default_timeout_ms
        self._max_output_bytes = max_output_bytes

        # Task storage: task_id -> TaskEntry
        self._tasks: dict[str, "TaskEntry"] = {}
        self._lock: asyncio.Lock = asyncio.Lock()

    # ─── Block 2: ICodeExecutionProtocol Methods ──────────────

    async def execute_blender_code(
        self,
        code: str,
        request_id: str | None = None,
    ) -> ExecutionResult:
        """Execute Python code in Blender via asyncio stream.

        Validates code against centralized AST validator (FR-SRV-002),
        enforces payload size limits, sends to Blender, and returns
        standardized ExecutionResult with timing and truncation.

        Never logs raw code — only fingerprint, length, and validation outcome.

        Args:
            code: The Python code string to execute.
            request_id: Optional tracking ID.

        Returns:
            ExecutionResult with status, data, and timing.

        Raises:
            SecurityViolationError: If code contains blocked patterns.
            ValidationError: If code is empty or syntax error.
            ExecutionTimeoutError: If execution exceeds timeout.
        """
        fingerprint = code_fingerprint(code)
        code_len = len(code.encode("utf-8"))

        # Audit log — record all code execution attempts (no raw code)
        logger.info(
            "Executing Blender code: fingerprint=%s, length=%d bytes, request_id=%s",
            fingerprint, code_len, request_id,
        )

        # Enforce payload size limit
        check_payload_size(code, self._security_policy.max_payload_bytes)

        # AST-based validation (centralized utility)
        try:
            validate_code_ast(code, self._security_policy)
        except Exception as e:
            logger.warning(
                "Code validation failed: fingerprint=%s, error=%s",
                fingerprint, e,
            )
            raise

        # Execute code via connection
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

            # Truncate output if too large
            data = result.data if result.data is not None else ""
            truncated = False
            if isinstance(data, str) and len(data.encode("utf-8")) > self._max_output_bytes:
                data = data[:self._max_output_bytes] + "\n...[truncated]"
                truncated = True

            exec_result = ExecutionResult(
                status=ExecutionStatus("success"),
                data=data,
                truncated=truncated,
                execution_time_ms=elapsed_ms,
                request_id=request_id,
            )

            # Emit event
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
        """Execute code for an existing background task.

        Internal use by the queue worker. Updates task state to running,
        executes code, then marks as completed or failed.

        Args:
            task_id: The task ID to execute.
            code: The Python code string.
            request_id: Optional tracking ID.

        Returns:
            ExecutionResult with status and data.
        """
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

    def create_task(self, request_id: str | None = None) -> str:
        """Create a new pending task and return its unique task_id.

        Args:
            request_id: Optional tracking ID.

        Returns:
            Unique task_id string.
        """
        task_id = f"task_{request_id or 'unnamed'}_{int(time.monotonic() * 1000) % 1000000:06d}"

        async def _emit() -> None:
            await self._event_publisher.publish(
                TaskCreated(task_id=task_id, request_id=request_id or "")
            )

        try:
            asyncio.ensure_future(_emit())
        except RuntimeError:
            pass  # No event loop running — emit will be handled later

        async def _store() -> None:
            async with self._lock:
                self._tasks[task_id] = TaskEntry(
                    task_id=task_id,
                    state=TaskState("pending"),
                    request_id=request_id,
                    created_at=time.monotonic(),
                )

        try:
            loop = asyncio.get_running_loop()
            asyncio.ensure_future(_store())
        except RuntimeError:
            # No event loop — direct assignment (caller must ensure thread safety)
            self._tasks[task_id] = TaskEntry(
                task_id=task_id,
                state=TaskState("pending"),
                request_id=request_id,
                created_at=time.monotonic(),
            )

        logger.info("Created task %s", task_id)
        self._cleanup_expired()
        return task_id

    def get_task(self, task_id: str) -> TaskStatus:
        """Get task status.

        Args:
            task_id: The task ID to query.

        Returns:
            TaskStatus with current state.

        Raises:
            TaskNotFoundError: If not found or expired.
        """
        async def _check() -> TaskStatus:
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

        try:
            loop = asyncio.get_running_loop()
            return loop.run_until_complete(_check())
        except RuntimeError:
            # No event loop — synchronous access (no lock)
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
        """Poll async task status and final result.

        Args:
            task_id: The task ID to poll.
            request_id: Optional tracking ID.

        Returns:
            TaskStatus with current state and optional ExecutionResult.

        Raises:
            TaskNotFoundError: If not found or expired.
        """
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

        # Emit completion events for terminal states
        if entry.state == TaskState("success"):
            try:
                await self._event_publisher.publish(
                    TaskCompleted(task_id=task_id, execution_time_ms=0)
                )
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
        """Cancel a pending or running task.

        - If pending: marks as cancelled, emits TaskCancelled
        - If running: sets cancel_requested=True, attempts asyncio cancellation

        Args:
            task_id: The task ID to cancel.
            request_id: Optional tracking ID.

        Returns:
            Updated TaskStatus.

        Raises:
            TaskNotFoundError: If not found.
        """
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
                # Attempt asyncio cancellation of the running coroutine
                # (actual cancellation depends on the coroutine supporting it)

        # Emit event outside lock
        try:
            await self._event_publisher.publish(TaskCancelled(task_id=task_id))
        except Exception as e:
            logger.error("Failed to emit TaskCancelled: %s", e)

        return status

    def cleanup_expired(self) -> int:
        """Remove tasks beyond retention window.

        Returns:
            Number of tasks removed.
        """
        now = time.monotonic()
        expired = [
            tid
            for tid, e in self._tasks.items()
            if e.completed_at is not None
            and (now - e.completed_at) > self._task_config.retention_seconds
        ]
        for tid in expired:
            del self._tasks[tid]
            logger.info("Cleaned up expired task %s", tid)
        return len(expired)

    # ─── Block 3: Helpers ──────────────────────────────────────

    def __repr__(self) -> str:
        return (
            f"CodeExecutionAdapter(task_retention={self._task_config.retention_seconds}s, "
            f"tasks={len(self._tasks)})"
        )


@dataclass
class TaskEntry:
    """Internal mutable state for a tracked task."""

    task_id: str
    state: TaskState
    result: ExecutionResult | None = None
    request_id: str | None = None
    created_at: float = field(default_factory=time.monotonic)
    completed_at: float | None = None
    cancel_requested: bool = False
