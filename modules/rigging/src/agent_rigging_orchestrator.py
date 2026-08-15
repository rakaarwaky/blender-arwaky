"""Rigging and deformation agent orchestrator for Wave 5."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class RiggingOrchestrator(IWaveFeatureAggregate):
    """Coordinate rigging operations without owning Blender transport."""

    def __init__(self, executor: IWaveFeatureProtocol) -> None:
        self._executor = executor

    async def inspect_armature(self, object_name: ObjectName, limit: int = 100):
        return await self._executor.inspect_armature(object_name, limit)

    async def set_pose_bone_transform(
        self,
        armature_name: ObjectName,
        bone_name: ObjectName,
        location: list[float] | None = None,
        rotation_euler: list[float] | None = None,
        scale: list[float] | None = None,
    ):
        return await self._executor.set_pose_bone_transform(armature_name, bone_name, location, rotation_euler, scale)

    async def configure_bone_constraint(
        self,
        armature_name: ObjectName,
        bone_name: ObjectName,
        constraint_type: str,
        enabled: bool,
        constraint_name: ObjectName | None = None,
        target_object: str | None = None,
        subtarget: str | None = None,
    ):
        return await self._executor.configure_bone_constraint(
            armature_name, bone_name, constraint_type, enabled, constraint_name, target_object, subtarget
        )

    async def configure_shape_key(
        self,
        object_name: ObjectName,
        shape_key_name: ObjectName,
        enabled: bool,
        value: float = 0.0,
        slider_min: float = 0.0,
        slider_max: float = 1.0,
    ):
        return await self._executor.configure_shape_key(
            object_name, shape_key_name, enabled, value, slider_min, slider_max
        )

    async def get_deformation_state(self, object_name: ObjectName):
        return await self._executor.get_deformation_state(object_name)
