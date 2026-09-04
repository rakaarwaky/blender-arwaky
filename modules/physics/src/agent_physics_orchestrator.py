"""Physics agent orchestrator for the Wave 3 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class PhysicsOrchestrator(IWaveFeatureAggregate):
    """Coordinate physics operations without owning transport or job storage."""

    def __init__(self, executor: IWaveFeatureProtocol) -> None:
        self._executor = executor

    async def get_state(self, object_name: ObjectName):
        return await self._executor.get_state(object_name)

    async def configure_rigid_body(
        self,
        object_name: ObjectName,
        enabled: bool,
        body_type: str = "ACTIVE",
        mass: float = 1.0,
        kinematic: bool = False,
    ):
        return await self._executor.configure_rigid_body(object_name, enabled, body_type, mass, kinematic)

    async def configure_cloth(
        self,
        object_name: ObjectName,
        enabled: bool,
        quality: int = 5,
        pin_group: str | None = None,
    ):
        return await self._executor.configure_cloth(object_name, enabled, quality, pin_group)

    async def bake(self, frame_start: int | None = None, frame_end: int | None = None):
        return await self._executor.bake(frame_start, frame_end)

    async def clear_bake(self):
        return await self._executor.clear_bake()

    async def get_simulation_state(self, object_name: ObjectName):
        return await self._executor.get_simulation_state(object_name)

    async def get_simulation_cache_status(self):
        return await self._executor.get_simulation_cache_status()

    async def configure_particle_system(
        self,
        object_name: ObjectName,
        enabled: bool,
        count: int = 1000,
        frame_start: int = 1,
        frame_end: int = 200,
        lifetime: float = 50.0,
        physics_type: str = "NEWTON",
    ):
        return await self._executor.configure_particle_system(
            object_name, enabled, count, frame_start, frame_end, lifetime, physics_type
        )

    async def configure_force_field(
        self,
        object_name: ObjectName,
        enabled: bool,
        field_type: str = "FORCE",
        strength: float = 1.0,
        noise: float = 0.0,
    ):
        return await self._executor.configure_force_field(object_name, enabled, field_type, strength, noise)

    async def configure_fluid_domain(
        self,
        object_name: ObjectName,
        enabled: bool,
        domain_type: str = "LIQUID",
        resolution: int = 64,
        cache_type: str = "REPLAY",
    ):
        return await self._executor.configure_fluid_domain(object_name, enabled, domain_type, resolution, cache_type)
