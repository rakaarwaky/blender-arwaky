from __future__ import annotations

from abc import ABC, abstractmethod


class ServerHealthProtocol(ABC):
    @abstractmethod
    async def check_health(self) -> dict:
        pass

    @abstractmethod
    async def get_config(self) -> dict:
        pass
