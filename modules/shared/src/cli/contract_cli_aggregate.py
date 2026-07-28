"""CLI domain contract: cli aggregate (ABC).

Agent implements this aggregate. Surface layers depend on it.
Facade for CLI lifecycle operations: init, run, close, status.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ToolName


class ICliAggregate(ABC):
    @abstractmethod
    async def init(self, config_path: str | None = None) -> dict[str, Any]: ...

    @abstractmethod
    async def run(self, extra_args: list[str] | None = None) -> dict[str, Any]: ...

    @abstractmethod
    async def close(self) -> dict[str, Any]: ...

    @abstractmethod
    async def status(self) -> dict[str, Any]: ...
