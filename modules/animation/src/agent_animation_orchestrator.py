"""Animation agent orchestrator implementing the Wave 2 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class AnimationOrchestrator(IWaveFeatureAggregate):
    """Coordinate animation operations without owning gateway transport."""

    def __init__(
        self,
        executor: IWaveFeatureProtocol,
        nla_executor: IWaveFeatureProtocol | None = None,
    ) -> None:
        self._executor = executor
        self._nla_executor = nla_executor or executor

    async def get_state(self, object_name: ObjectName, limit: int = 100):
        return await self._executor.get_state(object_name, limit)

    async def insert_keyframe(self, object_name: ObjectName, frame: int, data_path: str, index: int | None = None):
        return await self._executor.insert_keyframe(object_name, frame, data_path, index)

    async def set_timeline(self, frame_start: int, frame_end: int, current_frame: int | None = None):
        return await self._executor.set_timeline(frame_start, frame_end, current_frame)

    async def insert_pose_bone_keyframe(
        self,
        armature_name: str,
        bone_name: str,
        frame: int,
        data_path: str,
        index: int | None = None,
    ):
        return await self._executor.insert_pose_bone_keyframe(armature_name, bone_name, frame, data_path, index)

    async def list_keyframes(self, object_name: ObjectName, limit: int = 100):
        return await self._executor.list_keyframes(object_name, limit)

    async def list_actions(self, armature_name: str | None = None, limit: int = 100):
        return await self._executor.list_actions(armature_name, limit)

    async def import_animation_file(self, source_path: str, importer: str | None = None):
        return await self._executor.import_animation_file(source_path, importer)

    async def link_action_to_armature(self, armature_name: str, action_name: str):
        return await self._executor.link_action_to_armature(armature_name, action_name)

    async def list_pose_assets(self, limit: int = 100):
        return await self._executor.list_pose_assets(limit)

    async def create_pose_asset(self, armature_name: str, pose_name: str, catalog_path: str | None = None):
        return await self._executor.create_pose_asset(armature_name, pose_name, catalog_path)

    async def apply_pose_asset(
        self, armature_name: str, asset_name: str, blend_factor: float = 1.0, flipped: bool = False
    ):
        return await self._executor.apply_pose_asset(armature_name, asset_name, blend_factor, flipped)

    async def blend_pose_asset(self, armature_name: str, asset_name: str, blend_factor: float, flipped: bool = False):
        return await self._executor.blend_pose_asset(armature_name, asset_name, blend_factor, flipped)

    async def set_shape_key_keyframe(self, mesh_name: str, shape_key_name: str, value: float, frame: int):
        return await self._executor.set_shape_key_keyframe(mesh_name, shape_key_name, value, frame)

    async def create_nla_track(
        self, armature_name: str, track_name: str, is_solo: bool = False, is_muted: bool = False
    ):
        return await self._nla_executor.create_nla_track(armature_name, track_name, is_solo, is_muted)

    async def add_nla_strip(
        self,
        armature_name: str,
        track_name: str,
        action_name: str,
        strip_name: str,
        frame_start: float,
        scale: float = 1.0,
        repeat: float = 1.0,
        blend_in: float = 0.0,
        blend_out: float = 0.0,
        influence: float = 1.0,
        blend_type: str = "REPLACE",
        extrapolation: str = "HOLD",
        reversed: bool = False,
    ):
        return await self._nla_executor.add_nla_strip(
            armature_name,
            track_name,
            action_name,
            strip_name,
            frame_start,
            scale,
            repeat,
            blend_in,
            blend_out,
            influence,
            blend_type,
            extrapolation,
            reversed,
        )

    async def set_nla_strip(
        self,
        armature_name: str,
        track_name: str,
        strip_name: str,
        frame_start: float | None = None,
        scale: float | None = None,
        repeat: float | None = None,
        blend_in: float | None = None,
        blend_out: float | None = None,
        influence: float | None = None,
        blend_type: str | None = None,
        extrapolation: str | None = None,
        reversed: bool | None = None,
    ):
        return await self._nla_executor.set_nla_strip(
            armature_name,
            track_name,
            strip_name,
            frame_start,
            scale,
            repeat,
            blend_in,
            blend_out,
            influence,
            blend_type,
            extrapolation,
            reversed,
        )

    async def set_animation_layer(
        self,
        armature_name: str,
        track_name: str,
        blend_type: str | None = None,
        influence: float | None = None,
        is_solo: bool | None = None,
        is_muted: bool | None = None,
    ):
        return await self._nla_executor.set_animation_layer(
            armature_name, track_name, blend_type, influence, is_solo, is_muted
        )

    async def set_animation_mask(self, armature_name: str, track_name: str, strip_name: str, bone_names: list[str]):
        return await self._nla_executor.set_animation_mask(armature_name, track_name, strip_name, bone_names)

    async def remove_nla_strip(self, armature_name: str, track_name: str, strip_name: str):
        return await self._nla_executor.remove_nla_strip(armature_name, track_name, strip_name)

    async def bake_nla_assembly(
        self,
        armature_name: str,
        frame_start: int,
        frame_end: int,
        step: int = 1,
        output_action: str = "Wave5_Baked_Action",
        clear_constraints: bool = False,
        clear_nla: bool = False,
    ):
        return await self._nla_executor.bake_nla_assembly(
            armature_name, frame_start, frame_end, step, output_action, clear_constraints, clear_nla
        )

    async def validate_nla_assembly(self, armature_name: str, limit: int = 100):
        return await self._nla_executor.validate_nla_assembly(armature_name, limit)
