"""Composition root for the plugin feature."""

from __future__ import annotations

from .agent_plugin_orchestrator import PluginAgentOrchestrator
from .capabilities_plugin_package import PluginPackageCapability
from .capabilities_plugin_registry import PluginRegistryCapability
from .contract_plugin_aggregate import PluginAggregate
from .contract_plugin_operation_protocol import PluginOperationProtocol
from .taxonomy_plugin_vo import PluginId


class PluginContainer:
    """Wire plugin capabilities and expose the aggregate boundary."""

    def __init__(self) -> None:
        self._registry = PluginRegistryCapability()
        self._package = PluginPackageCapability()
        self._aggregate: PluginAggregate = PluginAgentOrchestrator(self._registry)

    def register_provider(
        self,
        plugin_id: PluginId,
        operation: PluginOperationProtocol,
    ) -> None:
        """Register a provider through the composed registry."""
        self._registry.register(plugin_id, operation)

    def aggregate(self) -> PluginAggregate:
        """Return the stable plugin aggregate."""
        return self._aggregate

    def package(self) -> PluginPackageCapability:
        """Return the controlled package lifecycle capability."""
        return self._package
