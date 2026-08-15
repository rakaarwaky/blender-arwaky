"""Compositor agent orchestrator for the Wave 3 aggregate."""

from __future__ import annotations

from modules.shared.src.common.contract_wave_feature_aggregate import IWaveFeatureAggregate
from modules.shared.src.common.contract_wave_feature_protocol import IWaveFeatureProtocol
from modules.shared.src.common.taxonomy_core_vo import ObjectName


class CompositorOrchestrator(IWaveFeatureAggregate):
    """Coordinate compositor operations without owning transport."""

    def __init__(self, executor: IWaveFeatureProtocol) -> None:
        self._executor = executor

    async def inspect_nodes(self, limit: int = 100):
        return await self._executor.inspect_nodes(limit)

    async def configure(self, use_nodes: bool):
        return await self._executor.configure(use_nodes)

    async def create_node(self, node_type: str, node_name: ObjectName | None = None):
        return await self._executor.create_node(node_type, node_name)

    async def set_link(self, from_node: str, from_socket: str, to_node: str, to_socket: str):
        return await self._executor.set_link(from_node, from_socket, to_node, to_socket)
