"""Capability: Code execution with AST-based validation, safety checks, and async task management.

Implements ICodeExecutionProtocol — handles Python code validation via
AST analysis, socket-based execution forwarding, payload size enforcement,
output truncation, result formatting, and async task lifecycle tracking per FR-SRV-002.
"""

from __future__ import annotations

import ast
import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ActionName, ErrorMessage, Prompt
from modules.shared.src.common.taxonomy_domain_error import ValidationError
from modules.shared.src.server import (
    DEFAULT_TASK_RETENTION_SECONDS,
    MAX_CODE_PAYLOAD_BYTES,
    ExecutionResult,
    ExecutionStatus,
    ExecutionTimeoutError,
    IBlenderConnectionProtocol,
    ICodeExecutionProtocol,
    SecurityViolationError,
    TaskManagerConfig,
    TaskNotFoundError,
    TaskState,
    TaskStatus,
    check_payload_size,
)

logger = logging.getLogger("BlenderMCPServer")

# Default AST-based blocked patterns for code validation (FRD-SRV-002)
_BLOCKED_ATTRS: set[str] = {
    "system",
    "popen",
    "exec_module",
    "load_module",
    "rmtree",
    "move",
    "unlink",
    "remove",
    "rmdir",
    "write_text",
    "write_bytes",
}

_BLOCKED_MODULES: set[str] = {
    "subprocess",
    "importlib",
    "socket",
    "requests",
    "urllib",
}


@dataclass
class TaskEntry:
    """Internal mutable state for a tracked task."""

    task_id: str
    state: TaskState
    result: ExecutionResult | None = None
    created_at: float = field(default_factory=time.monotonic)
    completed_at: float | None = None


class CodeExecutionAdapter(ICodeExecutionProtocol):
    """Code execution with AST-based validation, socket forwarding,
    and in-memory async task lifecycle management."""

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        connection_port: IBlenderConnectionProtocol,
        task_config: TaskManagerConfig | None = None,
    ) -> None:
        self._connection_port = connection_port
        self._task_config = task_config or TaskManagerConfig()
        self._tasks: dict[str, TaskEntry] = {}

    # ─── Block 2: ICodeExecutionProtocol Methods ─────────────

    async def execute_blender_code(self, code: Prompt) -> ExecutionResult:  # FR-SRV-002
        """Execute Python code in Blender via IPC.

        Validates code against AST-based denylist (FR-SRV-002),
        enforces payload size limits, enforces 30s timeout, and returns standardized ExecutionResult.

        Raises:
            SecurityViolationError: if code contains blocked patterns or exceeds size.
            ValidationError: if code is empty or syntax error.
            ExecutionTimeoutError: if execution exceeds 30s timeout.
        """
        code_str = str(code)

        # Enforce payload size limit (FR-SRV-002)
        check_payload_size(code_str, MAX_CODE_PAYLOAD_BYTES)

        # AST-based validation (FR-SRV-002 requirement)
        self._validate_code_ast(code_str)

        # Audit log — record all code execution attempts
        logger.info(
            "Executing Blender code (length=%d bytes): %.100s%s",
            len(code_str.encode("utf-8")),
            code_str,
            "..." if len(code_str) > 100 else "",
        )

        try:
            loop = asyncio.get_running_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(
                    None,
                    lambda: self._connection_port.send_command(
                        ActionName("execute_code"), {"code": code_str}
                    ),
                ),
                timeout=30.0,
            )

            # Truncate output if too large (FR-SRV-002)
            data = result.get("result", "")
            truncated = False
            max_output_bytes = 10_000  # 10KB max output

            if isinstance(data, str) and len(data.encode("utf-8")) > max_output_bytes:
                data = data[:max_output_bytes] + "\n...[truncated]"
                truncated = True

            return ExecutionResult(
                status=ExecutionStatus("success"),
                data=data,
                truncated=truncated,
            )
        except asyncio.TimeoutError:
            logger.warning("Code execution timed out after 30 seconds")
            raise ExecutionTimeoutError(
                ErrorMessage("Code execution timed out after 30 seconds")
            ) from None
        except SecurityViolationError:
            raise
        except ValidationError:
            raise
        except Exception as e:
            logger.exception("Error executing code in Blender")
            return ExecutionResult(
                status=ExecutionStatus("error"),
                error={"type": type(e).__name__, "message": str(e)},
            )

    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution. Returns task_id and status."""
        self._validate_code_ast(code)

        task_id = self.create_task(request_id)

        # Store code reference alongside the task entry
        entry = self._tasks[task_id]
        entry.code = code  # type: ignore[attr-defined]

        logger.info("Submitted async task %s for request %s", task_id, request_id)

        # Start async execution in background
        asyncio.ensure_future(self._run_async_task(task_id, code))

        return {"task_id": task_id, "status": "pending"}

    async def poll_task_result(self, task_id: str, request_id: str = "") -> ExecutionResult:
        """Poll async task status and final result."""
        task_status = self.get_task(task_id)

        if task_status.state == "success":
            return ExecutionResult(
                status=ExecutionStatus("success"),
                data=task_status.result,
            )
        elif task_status.state == "error":
            return ExecutionResult(
                status=ExecutionStatus("error"),
                error={"type": "ExecutionError", "message": str(task_status.result)},
            )
        else:
            # pending or running
            return ExecutionResult(
                status=ExecutionStatus("success"),
                data={"task_id": task_id, "state": task_status.state},
            )

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────

    def create_task(self, request_id: str) -> str:
        """Create a new task entry and return its unique task_id."""
        task_id = f"task_{request_id}_{int(time.monotonic() * 1000) % 1000000:06d}"
        self._tasks[task_id] = TaskEntry(task_id=task_id, state="pending")
        logger.info("Created task %s", task_id)
        self._cleanup_expired()
        return task_id

    def get_task(self, task_id: str) -> TaskStatus:
        """Retrieve task status; raises TaskNotFoundError if missing or expired."""
        entry = self._tasks.get(task_id)
        if entry is None:
            raise TaskNotFoundError(ErrorMessage(f"Task not found: {task_id}"))
        if entry.completed_at is not None:
            elapsed = time.monotonic() - entry.completed_at
            if elapsed > self._task_config.retention_seconds:
                del self._tasks[task_id]
                raise TaskNotFoundError(ErrorMessage(f"Task expired: {task_id}"))
        return TaskStatus(task_id=entry.task_id, state=entry.state, result=entry.result)

    def mark_running(self, task_id: str) -> None:
        """Transition task state to 'running'."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "running"

    def mark_completed(self, task_id: str, result: ExecutionResult) -> None:
        """Mark task as successfully completed with result."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "success"
            entry.result = result
            entry.completed_at = time.monotonic()

    def mark_error(self, task_id: str, error: str) -> None:
        """Mark task as failed with error message."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "error"
            entry.result = ExecutionResult(
                status="error",
                error={"type": "ExecutionError", "message": error},
            )
            entry.completed_at = time.monotonic()

    def mark_timeout(self, task_id: str) -> None:
        """Mark task as timed out."""
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "timeout"
            entry.result = ExecutionResult(
                status="error",
                error={"type": "ExecutionTimeoutError", "message": "Timed out"},
            )
            entry.completed_at = time.monotonic()

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending task. Returns True if cancelled, False otherwise."""
        entry = self._tasks.get(task_id)
        if entry is None:
            return False
        if entry.state == "pending":
            entry.state = "cancelled"
            entry.completed_at = time.monotonic()
            return True
        return False

    

    def __repr__(self) -> str:
        return (
            f"CodeExecutionAdapter(task_retention={self._task_config.retention_seconds}s)"
        )

    async def _run_async_task(self, task_id: str, code: str) -> None:
        """Execute async task in background, updating task state on completion."""
        self.mark_running(task_id)

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._connection_port.send_command(
                    ActionName("execute_code"), {"code": code}
                ),
            )
            self.mark_completed(
                task_id,
                ExecutionResult(status=ExecutionStatus("success"), data=result),
            )
        except Exception as e:
            self.mark_error(task_id, str(e))

    def _cleanup_expired(self) -> None:
        """Remove tasks that have exceeded their retention window."""
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

    @staticmethod
    def _validate_code_ast(code: str) -> None:
        """AST-based static analysis for blocked Python constructs.

        Implements FRD-SRV-002: code validated before sending using
        AST-based static analysis, not only regex or simple string matching.

        Raises SecurityViolationError if any blocked pattern is detected.
        Server-side validation is a pre-filter only; Blender addon must
        perform runtime enforcement as the final authority.
        """
        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            raise ValidationError(
                ErrorMessage(f"Invalid syntax in submitted code: {e}")
            ) from e

        for node in ast.walk(tree):
            # Check attribute calls (e.g., os.system, subprocess.Popen)
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr in _BLOCKED_ATTRS
            ):
                raise SecurityViolationError(
                    ErrorMessage(f"Blocked construct detected: {node.func.attr}")
                )

            # Check module imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in _BLOCKED_MODULES:
                            raise SecurityViolationError(
                                ErrorMessage(f"Blocked module import: {alias.name}")
                            )
                elif (
                    isinstance(node, ast.ImportFrom)
                    and node.module
                    and node.module in _BLOCKED_MODULES
                ):
                    raise SecurityViolationError(
                        ErrorMessage(f"Blocked module import: {node.module}")
                    )

            # Check eval/exec/compile/__import__ calls
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("eval", "exec", "compile", "__import__"):
                    raise SecurityViolationError(
                        ErrorMessage(f"Blocked function call: {node.func.id}")
                    )
                # Check open() calls for write/append modes (FR-SRV-002 file boundary check)
                if node.func.id == "open":
                    mode_val = ""
                    if len(node.args) >= 2 and isinstance(node.args[1], ast.Constant):
                        mode_val = str(node.args[1].value)
                    for kw in node.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            mode_val = str(kw.value.value)
                    if any(m in mode_val for m in ("w", "a", "x", "+")):
                        raise SecurityViolationError(
                            ErrorMessage(
                                f"Blocked file write operation with mode '{mode_val}'"
                            )
                        )