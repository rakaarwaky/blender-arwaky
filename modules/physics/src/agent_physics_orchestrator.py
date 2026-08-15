"""Physics agent orchestrator for the Wave 3 aggregate."""

from __future__ import annotations

from modules.physics.src.capabilities_physics_executor import PhysicsExecutor


class PhysicsOrchestrator:
    """Coordinate physics operations without owning transport or job storage."""

    def __init__(self, executor: PhysicsExecutor) -> None:
        self._executor = executor

    async def get_state(self, object_name: str):
        return await self._executor.get_state(object_name)

    async def configure_rigid_body(
        self,
        object_name: str,
        enabled: bool,
        body_type: str = "ACTIVE",
        mass: float = 1.0,
        kinematic: bool = False,
    ):
        return await self._executor.configure_rigid_body(object_name, enabled, body_type, mass, kinematic)

    async def configure_cloth(
        self,
        object_name: str,
        enabled: bool,
        quality: int = 5,
        pin_group: str | None = None,
    ):
        return await self._executor.configure_cloth(object_name, enabled, quality, pin_group)

    async def bake(self, frame_start: int | None = None, frame_end: int | None = None):
        return await self._executor.bake(frame_start, frame_end)

    async def clear_bake(self):
        return await self._executor.clear_bake()
