"""VSE agent orchestrator for the Wave 3 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class VseOrchestrator(IWaveFeatureAggregate):
    """Coordinate VSE operations without owning transport or job storage."""

    def __init__(self, executor: IWaveFeatureProtocol) -> None:
        self._executor = executor

    async def inspect(self, limit: int = 100):
        return await self._executor.inspect(limit)

    async def create_strip(
        self,
        strip_type: str,
        strip_name: ObjectName,
        filepath: str | None,
        channel: int,
        frame_start: int,
        frame_end: int | None = None,
    ):
        return await self._executor.create_strip(strip_type, strip_name, filepath, channel, frame_start, frame_end)

    async def remove_strip(self, strip_name: ObjectName):
        return await self._executor.remove_strip(strip_name)

    async def render(self, output_path: str, frame_start: int | None = None, frame_end: int | None = None):
        return await self._executor.render(output_path, frame_start, frame_end)
