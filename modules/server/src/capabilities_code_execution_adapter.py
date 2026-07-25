"""Capability: Code execution with AST-based validation and safety checks.

Implements ICodeExecutionProtocol — handles Python code validation via
AST analysis, socket-based execution forwarding, and result formatting
per FRD-SRV-002 / FRD-SRV-005.
"""

from __future__ import annotations

import ast
import asyncio
import logging
import time
from typing import Any
from uuid import uuid4

from modules.shared.src.server import (
    IBlenderConnectionProtocol,
    ICodeExecutionProtocol,
    ExecutionResult,
    ExecutionStatus,
    SecurityViolationError,
    TaskNotFoundError,
)
from modules.shared.src.common.taxonomy_core_vo import ActionName, ErrorMessage, Prompt
from modules.shared.src.common.taxonomy_domain_error import ValidationError

logger = logging.getLogger("BlenderMCPServer")

# Default AST-based blocked patterns for code validation (FRD-SRV-002)
_BLOCKED_ATTRS: set[str] = {
    "system", "popen", "exec_module", "load_module",
    "rmtree", "move", "unlink", "remove", "rmdir",
}

_BLOCKED_MODULES: set[str] = {
    "subprocess", "importlib", "socket", "requests", "urllib",
}

# Task retention TTL (seconds)
_TASK_RETENTION_SECONDS: float = 600.0  # 10 minutes


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
        raise ValidationError(ErrorMessage(f"Invalid syntax in submitted code: {e}"))

    for node in ast.walk(tree):
        # Check attribute calls (e.g., os.system, subprocess.Popen)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute):
                attr_name = node.func.attr
                if attr_name in _BLOCKED_ATTRS:
                    raise SecurityViolationError(
                        ErrorMessage(f"Blocked construct detected: {attr_name}")
                    )

        # Check module imports
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in _BLOCKED_MODULES:
                        raise SecurityViolationError(
                            ErrorMessage(f"Blocked module import: {alias.name}")
                        )
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module in _BLOCKED_MODULES:
                    raise SecurityViolationError(
                        ErrorMessage(f"Blocked module import: {node.module}")
                    )

        # Check eval/exec/compile/__import__ calls
        if isinstance(node.func, ast.Name) and node.func.id in ("eval", "exec", "compile", "__import__"):
            raise SecurityViolationError(
                ErrorMessage(f"Blocked function call: {node.func.id}")
            )


class CodeExecutionAdapter(ICodeExecutionProtocol):
    """Code execution with AST-based validation and socket forwarding.

    Implements ICodeExecutionProtocol with:
    - AST-based static analysis for blocked constructs (FRD-SRV-002)
    - Socket-based execution forwarding to Blender
    - Async task submission and polling (FRD-SRV-002)
    - Standardized ExecutionResult return values
    """

    def __init__(self, connection_port: IBlenderConnectionProtocol) -> None:
        self._connection_port = connection_port
        self._tasks: dict[str, dict[str, Any]] = {}

    async def execute_blender_code(self, code: Prompt) -> Prompt:
        """Execute Python code in Blender via IPC.

        Validates code against AST-based denylist (FRD-SRV-002),
        then forwards to Blender through the socket adapter.

        Raises:
            SecurityViolationError: if code contains blocked patterns.
            ValidationError: if code is empty or syntax error.
        """
        code_str = str(code)

        # AST-based validation (FRD-SRV-002 requirement)
        _validate_code_ast(code_str)

        # Audit log — record all code execution attempts
        logger.info(
            "Executing Blender code (length=%d chars): %.100s%s",
            len(code_str),
            code_str,
            "..." if len(code_str) > 100 else "",
        )

        try:
            # Offload synchronous IPC call to thread pool to avoid blocking event loop
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._connection_port.send_command(ActionName("execute_code"), {"code": code_str}),
            )
            return Prompt(f"Code executed successfully: {result.get('result', '')}")
        except SecurityViolationError:
            raise
        except ValidationError:
            raise
        except Exception:
            logger.exception("Error executing code in Blender")
            return Prompt("Internal server error during code execution.")

    async def submit_async_task(self, code: str, request_id: str) -> dict[str, Any]:
        """Submit long-running code for async execution. Returns task_id and status."""
        _validate_code_ast(code)

        task_id = f"task_{request_id}_{uuid4().hex[:8]}"
        self._tasks[task_id] = {
            "state": "pending",
            "code": code,
            "created_at": time.monotonic(),
            "result": None,
        }
        logger.info("Submitted async task %s", task_id)

        # Start async execution in background
        asyncio.ensure_future(self._run_async_task(task_id, code))

        return {"task_id": task_id, "status": "pending"}

    async def _run_async_task(self, task_id: str, code: str) -> None:
        """Execute async task in background."""
        task = self._tasks.get(task_id)
        if task:
            task["state"] = "running"

        try:
            loop = asyncio.get_running_loop()
            result = await loop.run_in_executor(
                None,
                lambda: self._connection_port.send_command(ActionName("execute_code"), {"code": code}),
            )
            task = self._tasks.get(task_id)
            if task:
                task["state"] = "success"
                task["result"] = result
                task["completed_at"] = time.monotonic()
        except Exception as e:
            task = self._tasks.get(task_id)
            if task:
                task["state"] = "error"
                task["result"] = {"error": str(e)}
                task["completed_at"] = time.monotonic()

    async def poll_task_result(self, task_id: str, request_id: str) -> ExecutionResult:
        """Poll async task status and final result."""
        task = self._tasks.get(task_id)
        if task is None:
            raise TaskNotFoundError(ErrorMessage(f"Task not found: {task_id}"))

        # Check TTL expiry
        if task.get("completed_at"):
            elapsed = time.monotonic() - task["completed_at"]
            if elapsed > _TASK_RETENTION_SECONDS:
                del self._tasks[task_id]
                raise TaskNotFoundError(ErrorMessage(f"Task expired: {task_id}"))

        state = task["state"]
        result_data = task.get("result")

        if state == "success":
            return ExecutionResult(
                status=ExecutionStatus("success"),
                data=result_data,
            )
        elif state == "error":
            return ExecutionResult(
                status=ExecutionStatus("error"),
                error={"type": "ExecutionError", "message": str(result_data)},
            )
        else:
            # pending or running
            return ExecutionResult(
                status=ExecutionStatus("success"),
                data={"task_id": task_id, "state": state},
            )
