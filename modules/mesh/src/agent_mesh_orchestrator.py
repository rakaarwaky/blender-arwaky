"""Mesh agent orchestrator implementing the Wave 2 aggregate."""

from __future__ import annotations

from modules.mesh.src.capabilities_mesh_executor import MeshExecutor


class MeshOrchestrator:
    """Coordinate mesh operations without owning gateway transport."""

    def __init__(self, executor: MeshExecutor) -> None:
        self._executor = executor

    async def get_statistics(self, object_name: str):
        return await self._executor.get_statistics(object_name)

    async def validate(self, object_name: str, limit: int = 100):
        return await self._executor.validate(object_name, limit)

    async def edit(self, object_name: str, operation: str):
        return await self._executor.edit(object_name, operation)

    async def ensure_uv_layer(self, object_name: str, uv_layer_name: str = "UVMap"):
        return await self._executor.ensure_uv_layer(object_name, uv_layer_name)
