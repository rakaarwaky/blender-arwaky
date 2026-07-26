"""Server domain — Typed domain events for connection, execution, and task lifecycle.

Frozen dataclasses for immutable, serializable event objects.
All events use past-tense naming for completed actions.
"""

from __future__ import annotations

from dataclasses import dataclass


# ============================================================
# Connection Events
# ============================================================

@dataclass(frozen=True)
class ConnectionEstablished:
    """Connection successfully established to Blender."""
    host: str
    port: int
    transport_type: str = "socket"


@dataclass(frozen=True)
class ConnectionLost:
    """Connection lost or closed."""
    reason: str  # "timeout" | "closed" | "error"


# ============================================================
# Code Execution Events
# ============================================================

@dataclass(frozen=True)
class CodeExecuted:
    """Code execution completed successfully."""
    request_id: str
    execution_time_ms: float
    truncated: bool = False


@dataclass(frozen=True)
class CodeExecutionFailed:
    """Code execution failed with error."""
    request_id: str
    error_type: str
    message: str


# ============================================================
# Task Lifecycle Events
# ============================================================

@dataclass(frozen=True)
class TaskCreated:
    """New async task created."""
    task_id: str
    request_id: str


@dataclass(frozen=True)
class TaskStarted:
    """Task transitioned to running state."""
    task_id: str


@dataclass(frozen=True)
class TaskCompleted:
    """Task completed successfully."""
    task_id: str
    execution_time_ms: float


@dataclass(frozen=True)
class TaskFailed:
    """Task failed with error."""
    task_id: str
    error_type: str
    message: str


@dataclass(frozen=True)
class TaskTimedOut:
    """Task exceeded timeout threshold."""
    task_id: str


@dataclass(frozen=True)
class TaskCancelled:
    """Task was cancelled by caller."""
    task_id: str


# ============================================================
# Command Dispatch Events
# ============================================================

@dataclass(frozen=True)
class CommandDispatched:
    """Command dispatched to Blender addon."""
    action: str
    execution_time_ms: float


@dataclass(frozen=True)
class CommandTimedOut:
    """Command exceeded timeout threshold."""
    action: str
    timeout_ms: float


# ============================================================
# Queue Events
# ============================================================

@dataclass(frozen=True)
class ItemEnqueued:
    """Item added to execution queue."""
    request_id: str
    queue_depth: int


@dataclass(frozen=True)
class ItemDequeued:
    """Item removed from execution queue."""
    request_id: str
