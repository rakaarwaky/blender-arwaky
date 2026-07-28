"""MCP domain contract: mcp aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for MCP server lifecycle: start, register, shutdown.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class IMcpAggregate(ABC):
    @abstractmethod
    def start(self) -> None:
        ...

    @abstractmethod
    def register_tools(self, mcp: Any) -> None:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...
