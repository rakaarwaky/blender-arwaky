"""Animation agent orchestrator implementing the Wave 2 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class AnimationOrchestrator(IWaveFeatureAggregate):
    """Coordinate animation operations without owning gateway transport."""

    def __init__(
        self, executor: IWaveFeatureProtocol, retarget_executor: IWaveFeatureProtocol | None = None
    ) -> None:
        self._executor = executor
        self._retarget_executor = retarget_executor or executor

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

    async def list_pose_assets(self, limit: int = 100):
        return await self._executor.list_pose_assets(limit)

    async def create_pose_asset(self, armature_name: str, pose_name: str, catalog_path: str | None = None):
        return await self._executor.create_pose_asset(armature_name, pose_name, catalog_path)

    async def apply_pose_asset(
        self, armature_name: str, asset_name: str, blend_factor: float = 1.0, flipped: bool = False
    ):
        return await self._executor.apply_pose_asset(armature_name, asset_name, blend_factor, flipped)

    async def blend_pose_asset(
        self, armature_name: str, asset_name: str, blend_factor: float, flipped: bool = False
    ):
        return await self._executor.blend_pose_asset(armature_name, asset_name, blend_factor, flipped)

    async def copy_rigify_pose(self, armature_name: str):
        return await self._executor.copy_rigify_pose(armature_name)

    async def paste_rigify_pose(
        self, armature_name: str, flipped: bool = False, selected_mask: bool = False
    ):
        return await self._executor.paste_rigify_pose(armature_name, flipped, selected_mask)

    async def keyframe_rigify_pose(self, armature_name: str, frame: int, bone_names: list[str] | None = None):
        return await self._executor.keyframe_rigify_pose(armature_name, frame, bone_names)

    async def inspect_face_animation_channels(
        self, armature_name: str, mesh_name: str | None = None, limit: int = 200
    ):
        return await self._executor.inspect_face_animation_channels(armature_name, mesh_name, limit)

    async def inspect_hand_animation_controls(self, armature_name: str, side: str = "both", limit: int = 200):
        return await self._executor.inspect_hand_animation_controls(armature_name, side, limit)

    async def set_rigify_fk_ik_mode(
        self, armature_name: str, limb: str, side: str, mode: str, frame: int | None = None
    ):
        return await self._executor.set_rigify_fk_ik_mode(armature_name, limb, side, mode, frame)

    async def set_shape_key_keyframe(self, mesh_name: str, shape_key_name: str, value: float, frame: int):
        return await self._executor.set_shape_key_keyframe(mesh_name, shape_key_name, value, frame)

    async def edit_face_control_animation(
        self,
        armature_name: str,
        bone_name: str,
        frame: int,
        rotation_euler: list[float] | None = None,
        location: list[float] | None = None,
    ):
        return await self._executor.edit_face_control_animation(
            armature_name, bone_name, frame, rotation_euler, location
        )

    async def import_motion_capture(self, source_path: str, importer: str | None = None):
        return await self._retarget_executor.import_motion_capture(source_path, importer)

    async def build_bone_mapping(
        self,
        source_armature: str,
        target_armature: str,
        preset: str = "exact",
        overrides: dict[str, str] | None = None,
        unmapped_policy: str = "report",
    ):
        return await self._retarget_executor.build_bone_mapping(
            source_armature, target_armature, preset, overrides, unmapped_policy
        )

    async def validate_rest_pose(
        self, source_armature: str, target_armature: str, mapping: dict[str, object], tolerance: float = 0.25
    ):
        return await self._retarget_executor.validate_rest_pose(source_armature, target_armature, mapping, tolerance)

    async def retarget_animation(
        self,
        source_armature: str,
        target_armature: str,
        source_action: str,
        mapping: dict[str, object],
        output_action: str,
        frame_start: int | None = None,
        frame_end: int | None = None,
        scale_policy: str = "preserve",
        root_motion: str = "preserve",
    ):
        return await self._retarget_executor.retarget_animation(
            source_armature,
            target_armature,
            source_action,
            mapping,
            output_action,
            frame_start,
            frame_end,
            scale_policy,
            root_motion,
        )

    async def set_root_motion(self, armature_name: str, policy: str):
        return await self._retarget_executor.set_root_motion(armature_name, policy)

    async def bake_retarget_action(
        self,
        armature_name: str,
        action_name: str,
        frame_start: int,
        frame_end: int,
        step: int = 1,
        clear_constraints: bool = False,
    ):
        return await self._retarget_executor.bake_retarget_action(
            armature_name, action_name, frame_start, frame_end, step, clear_constraints
        )

    async def validate_animation_result(self, armature_name: str, action_name: str, limit: int = 1000):
        return await self._retarget_executor.validate_animation_result(armature_name, action_name, limit)
