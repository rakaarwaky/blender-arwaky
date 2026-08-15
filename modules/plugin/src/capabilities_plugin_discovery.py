"""Plugin discovery capability."""

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


class PluginDiscoveryCapability(PluginOperationProtocol):
    """Discover one provider through an injected provider probe."""

    def __init__(self, plugin_id: PluginId, probe: PluginOperationProtocol) -> None:
        self._plugin_id = plugin_id
        self._probe = probe

    def discover(self, blender_version: BlenderVersion) -> PluginDiscoveryVO:
        """Delegate discovery to the provider boundary."""
        return self._probe.discover(blender_version)

    def health_check(self) -> PluginHealthVO:
        """Delegate provider health checking."""
        return self._probe.health_check()

    def capabilities(self) -> PluginCapabilityList:
        """Return provider-declared capabilities."""
        return self._probe.capabilities()

    def execute(
        self,
        action: PluginActionName,
        params: PluginParameterMap,
    ) -> PluginExecutionVO:
        """Expose discovery as a bounded operation."""
        del params
        if action != PluginActionName("plugin.discover"):
            return PluginExecutionVO(
                plugin_id=self._plugin_id,
                action=action,
                success=False,
                message=PluginMessage("discovery capability does not execute this action"),
            )
        return PluginExecutionVO(
            plugin_id=self._plugin_id,
            action=action,
            success=True,
            message=PluginMessage("provider discovery is available through discover"),
        )
