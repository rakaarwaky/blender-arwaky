"""Aggregate contract for the plugin feature."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginCapabilityList,
    PluginExecutionVO,
    PluginHealthVO,
    PluginIdList,
    PluginParameterMap,
)


class PluginAggregate(ABC):
    """Stable facade for plugin discovery and declared operations."""

    @abstractmethod
    def discover(self, blender_version: BlenderVersion) -> PluginIdList:
        """Discover registered providers and return available identifiers."""
        ...

    @abstractmethod
    def capabilities(self) -> PluginCapabilityList:
        """Return the extension capability catalog."""
        ...

    @abstractmethod
    def health_check(self) -> tuple[PluginHealthVO, ...]:
        """Return health for registered providers."""
        ...

    @abstractmethod
    def execute(
        self,
        action: PluginActionName,
        params: PluginParameterMap,
    ) -> PluginExecutionVO:
        """Execute one explicitly declared plugin operation."""
        ...
