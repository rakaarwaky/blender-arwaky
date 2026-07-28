from __future__ import annotations

from abc import ABC, abstractmethod


class ServerExecuteProtocol(ABC):
    @abstractmethod
    async def execute_action(self, action: str, params: dict | None = None) -> dict:
        pass
