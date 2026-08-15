"""Animation agent orchestrator implementing the Wave 2 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class AnimationOrchestrator(IWaveFeatureAggregate):
    """Coordinate animation operations without owning gateway transport."""

    def __init__(self, executor: IWaveFeatureProtocol) -> None:
        self._executor = executor

    async def get_state(self, object_name: ObjectName, limit: int = 100):
        return await self._executor.get_state(object_name, limit)

    async def insert_keyframe(self, object_name: ObjectName, frame: int, data_path: str, index: int | None = None):
        return await self._executor.insert_keyframe(object_name, frame, data_path, index)

    async def set_timeline(self, frame_start: int, frame_end: int, current_frame: int | None = None):
        return await self._executor.set_timeline(frame_start, frame_end, current_frame)

    async def list_keyframes(self, object_name: ObjectName, limit: int = 100):
        return await self._executor.list_keyframes(object_name, limit)
