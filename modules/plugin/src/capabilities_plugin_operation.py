"""Plugin operation capability."""

from __future__ import annotations

from .contract_plugin_operation_protocol import PluginOperationProtocol
from .taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginCapabilityList,
    PluginDiscoveryVO,
    PluginExecutionVO,
    PluginHealthVO,
    PluginId,
    PluginMessage,
    PluginParameterMap,
)


class PluginOperationCapability(PluginOperationProtocol):
    """Guard and normalize one provider operation port."""

    def __init__(self, plugin_id: PluginId, provider: PluginOperationProtocol) -> None:
        self._plugin_id = plugin_id
        self._provider = provider

    def discover(self, blender_version: BlenderVersion) -> PluginDiscoveryVO:
        """Return provider discovery state."""
        return self._provider.discover(blender_version)

    def health_check(self) -> PluginHealthVO:
        """Return provider health state."""
        return self._provider.health_check()

    def capabilities(self) -> PluginCapabilityList:
        """Return the provider allow-list."""
        return self._provider.capabilities()

    def execute(
        self,
        action: PluginActionName,
        params: PluginParameterMap,
    ) -> PluginExecutionVO:
        """Execute only an action explicitly declared by the provider."""
        if action not in self.capabilities():
            return PluginExecutionVO(
                plugin_id=self._plugin_id,
                action=action,
                success=False,
                message=PluginMessage("plugin capability is not declared"),
            )
        return self._provider.execute(action, params)
