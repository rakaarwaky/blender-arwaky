"""Plugin agent orchestrator."""

from __future__ import annotations

from .contract_plugin_aggregate import PluginAggregate
from .contract_plugin_operation_protocol import PluginOperationProtocol
from .contract_plugin_registry_protocol import PluginRegistryProtocol
from .taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginCapabilityId,
    PluginCapabilityList,
    PluginExecutionVO,
    PluginHealthVO,
    PluginId,
    PluginIdList,
    PluginMessage,
    PluginParameterMap,
)


class PluginAgentOrchestrator(PluginAggregate):
    """Coordinate provider discovery, resolution, and operation execution."""

    def __init__(self, registry: PluginRegistryProtocol) -> None:
        self._registry = registry

    def discover(self, blender_version: BlenderVersion) -> PluginIdList:
        """Return providers that report compatible discovery state."""
        del blender_version
        healthy = tuple(
            item.plugin_id
            for item in self._registry.health_check()
            if item.installed and item.active and item.compatible
        )
        return PluginIdList(healthy)

    def capabilities(self) -> PluginCapabilityList:
        """Return capability identifiers through the registry contract."""
        return self._registry.list_capabilities()

    def health_check(self) -> tuple[PluginHealthVO, ...]:
        """Return provider health through the registry contract."""
        return self._registry.health_check()

    def execute(
        self,
        action: PluginActionName,
        params: PluginParameterMap,
    ) -> PluginExecutionVO:
        """Resolve and execute one declared capability."""
        operation: PluginOperationProtocol | None = self._registry.resolve(PluginCapabilityId(str(action)))
        if operation is None:
            return PluginExecutionVO(
                plugin_id=PluginId("plugin"),
                action=action,
                success=False,
                message=PluginMessage("plugin capability is not registered"),
            )
        return operation.execute(action, params)
