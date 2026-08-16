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

    async def list_actions(self, armature_name: str | None = None, limit: int = 100):
        return await self._executor.list_actions(armature_name, limit)

    async def inspect_rigify_controls(self, armature_name: str, limit: int = 1000):
        return await self._executor.inspect_rigify_controls(armature_name, limit)

    async def import_animation_file(self, source_path: str, importer: str | None = None):
        return await self._executor.import_animation_file(source_path, importer)

    async def link_action_to_armature(self, armature_name: str, action_name: str):
        return await self._executor.link_action_to_armature(armature_name, action_name)
