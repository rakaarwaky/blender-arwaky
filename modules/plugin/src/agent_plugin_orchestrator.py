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
        """Return providers that report an enabled and compatible discovery state."""
        discovered = self._registry.discover(blender_version)
        return PluginIdList(
            tuple(item.plugin_id for item in discovered if item.installed and item.active and item.compatible)
        )

    def capabilities(self) -> PluginCapabilityList:
        """Return all registered capability identifiers for internal diagnostics."""
        return self._registry.list_capabilities()

    def enabled_plugin_ids(self) -> PluginIdList:
        """Return only providers that are installed, active, and compatible."""
        return PluginIdList(
            tuple(
                health.plugin_id
                for health in self.health_check()
                if health.installed and health.active and health.compatible
            )
        )

    def enabled_capabilities(self) -> PluginCapabilityList:
        """Return only capabilities owned by enabled providers."""
        enabled = set(self.enabled_plugin_ids())
        capability_ids: list[PluginCapabilityId] = []
        for capability_id in self._registry.list_capabilities():
            operation = self._registry.resolve(capability_id)
            provider_id = self._registry.resolve_provider_id(operation) if operation is not None else None
            if provider_id in enabled:
                capability_ids.append(capability_id)
        return PluginCapabilityList(tuple(sorted(capability_ids, key=str)))

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
        provider_id = self._registry.resolve_provider_id(operation)
        health = next(
            (item for item in self._registry.health_check() if item.plugin_id == provider_id),
            None,
        )
        if health is not None and (not health.installed or not health.active or not health.compatible):
            return PluginExecutionVO(
                plugin_id=health.plugin_id,
                action=action,
                success=False,
                message=PluginMessage(f"plugin is not executable in lifecycle state {health.state.value}"),
            )
        return operation.execute(action, params)
