"""Job domain contract: job scheduler protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-JOB-005: Coordinate large downloads as background jobs.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import AssetId, ProviderName


class JobSchedulerProtocol(ABC):
    """Protocol for submitting background download jobs.

    Capability uses this to delegate large download coordination
    to the job subsystem.
    """

    @abstractmethod
    async def submit_download(
        self,
        provider: ProviderName,
        asset_id: AssetId,
        cache_path: str,
    ) -> str:
        """Submit a download task for background execution.

        Returns a task reference string.
        """
        ...
