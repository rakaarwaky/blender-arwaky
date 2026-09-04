"""Geometry Nodes agent orchestrator implementing the Wave 2 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class GeometryNodesOrchestrator(IWaveFeatureAggregate):
    """Coordinate Geometry Nodes operations without owning transport concerns."""

    def __init__(self, executor: IWaveFeatureProtocol) -> None:
        self._executor = executor

    async def inspect_group(self, group_name: ObjectName):
        return await self._executor.inspect_group(group_name)

    async def create_group(self, group_name: ObjectName, object_name: ObjectName | None = None):
        return await self._executor.create_group(group_name, object_name)

    async def set_link(self, group_name: ObjectName, from_node: str, from_socket: str, to_node: str, to_socket: str):
        return await self._executor.set_link(group_name, from_node, from_socket, to_node, to_socket)

    async def bind_modifier(self, object_name: ObjectName, group_name: ObjectName):
        return await self._executor.bind_modifier(object_name, group_name)
