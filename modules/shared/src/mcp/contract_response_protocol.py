from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from modules.shared.src.common.taxonomy_core_vo import ErrorString


class ServerResponseProtocol(ABC):
    @abstractmethod
    async def format_response(
        self,
        result: dict[str, Any],
        tracking_id: str | None = None,
        max_payload_size: int | None = None,
    ) -> dict[str, Any]:
        pass
