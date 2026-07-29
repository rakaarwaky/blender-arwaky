"""MCP job action schemas — parameter definitions for background task lifecycle."""

from typing import Any

JOB_ACTIONS: dict[str, dict[str, Any]] = {
    "get_task_status": {
        "description": "Query the progress and status of a background task",
        "parameters": {
            "task_id": {"type": "string", "required": True, "description": "Task identifier returned from a previous submit action"},
        },
    },
    "cancel_task": {
        "description": "Cancel a running background task",
        "parameters": {
            "task_id": {"type": "string", "required": True, "description": "Task identifier of the task to cancel"},
        },
    },
}
