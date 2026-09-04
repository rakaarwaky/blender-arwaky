"""Mesh agent orchestrator implementing the Wave 2 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class MeshOrchestrator(IWaveFeatureAggregate):
    """Coordinate mesh operations without owning gateway transport."""

    def __init__(self, executor: IWaveFeatureProtocol) -> None:
        self._executor = executor

    async def get_statistics(self, object_name: ObjectName):
        return await self._executor.get_statistics(object_name)

    async def validate(self, object_name: ObjectName, limit: int = 100):
        return await self._executor.validate(object_name, limit)

    async def edit(self, object_name: ObjectName, operation: str):
        return await self._executor.edit(object_name, operation)

    async def ensure_uv_layer(self, object_name: ObjectName, uv_layer_name: ObjectName = "UVMap"):
        return await self._executor.ensure_uv_layer(object_name, uv_layer_name)
