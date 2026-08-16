"""Contract for resolving registered plugin operation providers."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .contract_plugin_operation_protocol import PluginOperationProtocol
from .taxonomy_plugin_vo import (
    PluginCapabilityId,
    PluginCapabilityList,
    PluginHealthVO,
    PluginId,
    PluginIdList,
    PluginRegistrationVO,
)


class PluginRegistryProtocol(ABC):
    """Registry port consumed by the plugin aggregate and orchestrator."""

    @abstractmethod
    def register(
        self,
        plugin_id: PluginId,
        operation: PluginOperationProtocol,
    ) -> PluginRegistrationVO:
        """Register one operation provider."""
        ...

    @abstractmethod
    def unregister(self, plugin_id: PluginId) -> PluginRegistrationVO:
        """Remove one provider from the registry."""
        ...

    @abstractmethod
    def list_plugin_ids(self) -> PluginIdList:
        """Return registered provider identifiers."""
        ...

    @abstractmethod
    def resolve(
        self,
        capability_id: PluginCapabilityId,
    ) -> PluginOperationProtocol | None:
        """Resolve a provider for one declared capability."""
        ...

    @abstractmethod
    def list_capabilities(self) -> PluginCapabilityList:
        """Return all declared capability identifiers."""
        ...

    @abstractmethod
    def health_check(self) -> tuple[PluginHealthVO, ...]:
        """Return health for all registered providers."""
        ...
