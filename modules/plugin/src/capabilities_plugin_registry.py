"""Plugin registry capability."""

from __future__ import annotations

from dataclasses import replace

from .contract_plugin_operation_protocol import PluginOperationProtocol
from .contract_plugin_registry_protocol import PluginRegistryProtocol
from .taxonomy_plugin_vo import (
    BlenderVersion,
    PluginCapabilityId,
    PluginCapabilityList,
    PluginDiscoveryVO,
    PluginHealthVO,
    PluginId,
    PluginIdList,
    PluginMessage,
    PluginRegistrationVO,
    derive_plugin_lifecycle_state,
)


class PluginRegistryCapability(PluginRegistryProtocol):
    """Maintain explicit provider and capability indexes."""

    def __init__(self) -> None:
        self._providers: dict[PluginId, PluginOperationProtocol] = {}
        self._capabilities: dict[PluginCapabilityId, PluginOperationProtocol] = {}

    def register(
        self,
        plugin_id: PluginId,
        operation: PluginOperationProtocol,
    ) -> PluginRegistrationVO:
        """Register a provider and its declared capabilities."""
        if plugin_id in self._providers:
            return PluginRegistrationVO(
                plugin_id=plugin_id,
                registered=False,
                message=PluginMessage("plugin is already registered"),
            )
        capabilities = tuple(operation.capabilities())
        if len(set(capabilities)) != len(capabilities):
            return PluginRegistrationVO(
                plugin_id=plugin_id,
                registered=False,
                message=PluginMessage("plugin declares a duplicate capability"),
            )
        collisions = tuple(capability for capability in capabilities if capability in self._capabilities)
        if collisions:
            return PluginRegistrationVO(
                plugin_id=plugin_id,
                registered=False,
                message=PluginMessage(f"plugin capability collision: {collisions[0]}"),
            )
        self._providers[plugin_id] = operation
        for capability_id in capabilities:
            self._capabilities[capability_id] = operation
        return PluginRegistrationVO(
            plugin_id=plugin_id,
            registered=True,
            message=PluginMessage("plugin registered"),
        )

    def unregister(self, plugin_id: PluginId) -> PluginRegistrationVO:
        """Remove a provider and all of its capability indexes."""
        operation = self._providers.pop(plugin_id, None)
        if operation is None:
            return PluginRegistrationVO(
                plugin_id=plugin_id,
                registered=False,
                message=PluginMessage("plugin is not registered"),
            )
        for capability_id, candidate in tuple(self._capabilities.items()):
            if candidate is operation:
                del self._capabilities[capability_id]
        return PluginRegistrationVO(
            plugin_id=plugin_id,
            registered=False,
            message=PluginMessage("plugin unregistered"),
        )

    def discover(self, blender_version: BlenderVersion) -> tuple[PluginDiscoveryVO, ...]:
        """Discover providers in deterministic registration order."""
        return tuple(self._providers[plugin_id].discover(blender_version) for plugin_id in self.list_plugin_ids())

    def list_plugin_ids(self) -> PluginIdList:
        """Return provider identifiers in deterministic order."""
        return PluginIdList(tuple(sorted(self._providers, key=str)))

    def resolve_provider_id(self, operation: PluginOperationProtocol) -> PluginId | None:
        """Return the identifier for a registered operation instance."""
        return next(
            (plugin_id for plugin_id, candidate in self._providers.items() if candidate is operation),
            None,
        )

    def resolve(
        self,
        capability_id: PluginCapabilityId,
    ) -> PluginOperationProtocol | None:
        """Resolve only a declared capability."""
        return self._capabilities.get(capability_id)

    def list_capabilities(self) -> PluginCapabilityList:
        """Return all declared capability identifiers."""
        return PluginCapabilityList(tuple(sorted(self._capabilities, key=str)))

    def health_check(self) -> tuple[PluginHealthVO, ...]:
        """Return health results with a normalized lifecycle state."""
        results: list[PluginHealthVO] = []
        for plugin_id in self.list_plugin_ids():
            health = self._providers[plugin_id].health_check()
            results.append(
                replace(
                    health,
                    state=derive_plugin_lifecycle_state(
                        health.installed,
                        health.active,
                        health.compatible,
                    ),
                )
            )
        return tuple(results)
