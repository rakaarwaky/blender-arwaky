"""Capabilities: Task lifecycle management for async Blender operations.

In-memory store for tracking async code execution tasks.
Implements ITaskManagerProtocol.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from uuid import uuid4

from modules.shared.src.server.contract_task_manager_protocol import ITaskManagerProtocol
from modules.shared.src.server.taxonomy_server_error import TaskNotFoundError
from modules.shared.src.server.taxonomy_server_vo import ExecutionResult, TaskManagerConfig, TaskState, TaskStatus

logger = logging.getLogger("BlenderMCPServer")


@dataclass
class TaskEntry:
    """Internal mutable state for a tracked task."""

    task_id: str
    state: TaskState
    result: ExecutionResult | None = None
    created_at: float = field(default_factory=time.monotonic)
    completed_at: float | None = None


class TaskManager(ITaskManagerProtocol):
    """In-memory store for async task lifecycle management."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, config: TaskManagerConfig | None = None) -> None:
        self._config = config or TaskManagerConfig()
        self._tasks: dict[str, TaskEntry] = {}

    # ─── Block 2: Protocol Method Implementation ─────────────
    def create_task(self, request_id: str) -> str:
        task_id = f"task_{request_id}_{uuid4().hex[:8]}"
        self._tasks[task_id] = TaskEntry(task_id=task_id, state="pending")
        logger.info("Created task %s", task_id)
        self._cleanup_expired()
        return task_id

    def get_task(self, task_id: str) -> TaskStatus:
        entry = self._tasks.get(task_id)
        if entry is None:
            raise TaskNotFoundError(f"Task not found: {task_id}")
        if entry.completed_at is not None:
            elapsed = time.monotonic() - entry.completed_at
            if elapsed > self._config.retention_seconds:
                del self._tasks[task_id]
                raise TaskNotFoundError(f"Task expired: {task_id}")
        return TaskStatus(task_id=entry.task_id, state=entry.state, result=entry.result)

    def mark_running(self, task_id: str) -> None:
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "running"

    def mark_completed(self, task_id: str, result: ExecutionResult) -> None:
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "success"
            entry.result = result
            entry.completed_at = time.monotonic()

    def mark_error(self, task_id: str, error: str) -> None:
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "error"
            entry.result = ExecutionResult(status="error", error={"type": "ExecutionError", "message": error})
            entry.completed_at = time.monotonic()

    def mark_timeout(self, task_id: str) -> None:
        entry = self._tasks.get(task_id)
        if entry:
            entry.state = "timeout"
            entry.result = ExecutionResult(status="error", error={"type": "ExecutionTimeoutError", "message": "Timed out"})
            entry.completed_at = time.monotonic()

    def cancel_task(self, task_id: str) -> bool:
        entry = self._tasks.get(task_id)
        if entry is None:
            return False
        if entry.state == "pending":
            entry.state = "cancelled"
            entry.completed_at = time.monotonic()
            return True
        return False

    # ─── Block 3: Dunder Methods, Factories & Helpers ────────
    def __repr__(self) -> str:
        return f"TaskManager(retention={self._config.retention_seconds}s)"

    def _cleanup_expired(self) -> None:
        now = time.monotonic()
        expired = [tid for tid, e in self._tasks.items() if e.completed_at is not None and (now - e.completed_at) > self._config.retention_seconds]
        for tid in expired:
            del self._tasks[tid]
            logger.info("Cleaned up expired task %s", tid)
