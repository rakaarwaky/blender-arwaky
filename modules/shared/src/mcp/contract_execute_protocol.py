from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import ErrorString


class ServerExecuteProtocol(ABC):
    @abstractmethod
    async def execute_action(self, action: str, params: dict | None = None) -> dict:
        pass
