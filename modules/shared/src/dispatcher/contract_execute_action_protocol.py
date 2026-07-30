"""Dispatcher domain contract: execute action protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.

FR-DSP-004: Dispatch Synchronous Action — defines the execute action interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ExecuteActionProtocol(ABC):
    """Protocol for executing a single action by name with parameters."""

    @abstractmethod
    def execute_action(self, action_name: str, parameters: dict[str, Any]) -> Any:
        """Execute an action by name with the given parameters.

        FR-DSP-004: Routes to owning feature and returns normalized result.
        """
        ...
