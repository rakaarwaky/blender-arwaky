from __future__ import annotations

from abc import ABC, abstractmethod


class ServerDiscoveryProtocol(ABC):
    @abstractmethod
    async def list_actions(self) -> dict:
        pass

    @abstractmethod
    async def read_skill_context(self, skill_name: str | None = None) -> dict:
        pass
