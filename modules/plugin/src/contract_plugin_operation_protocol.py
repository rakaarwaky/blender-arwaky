"""Contract for one provider's declared plugin operations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginCapabilityList,
    PluginDiscoveryVO,
    PluginExecutionVO,
    PluginHealthVO,
    PluginParameterMap,
)


class PluginOperationProtocol(ABC):
    """Provider operation port implemented by a capability."""

    @abstractmethod
    def discover(self, blender_version: BlenderVersion) -> PluginDiscoveryVO:
        """Discover provider availability and compatibility."""
        ...

    @abstractmethod
    def health_check(self) -> PluginHealthVO:
        """Return the provider health state."""
        ...

    @abstractmethod
    def capabilities(self) -> PluginCapabilityList:
        """Return explicitly declared provider capability identifiers."""
        ...

    @abstractmethod
    def execute(
        self,
        action: PluginActionName,
        params: PluginParameterMap,
    ) -> PluginExecutionVO:
        """Execute one declared operation."""
        ...
