"""In-memory registry for validated plugin providers."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from .contract_plugin_protocol import PluginContract
from .schema_plugin_manifest import PluginCapability
from .schema_plugin_result import PluginHealth, PluginResult


class PluginCatalog:
    """Registry that exposes only explicitly declared plugin capabilities."""

    def __init__(self) -> None:
        self._providers: dict[str, PluginContract] = {}

    def register(self, provider: PluginContract) -> None:
        """Register a provider after validating its manifest identity."""
        manifest = provider.get_manifest()
        if not manifest.plugin_id:
            raise ValueError("plugin manifest requires plugin_id")
        if manifest.plugin_id in self._providers:
            raise ValueError(f"plugin already registered: {manifest.plugin_id}")
        self._providers[manifest.plugin_id] = provider

    def unregister(self, plugin_id: str) -> None:
        """Remove a provider if it is registered."""
        self._providers.pop(plugin_id, None)

    def list_plugin_ids(self) -> tuple[str, ...]:
        """Return registered plugin identifiers in stable order."""
        return tuple(sorted(self._providers))

    def get_provider(self, plugin_id: str) -> PluginContract | None:
        """Return one provider by identifier."""
        return self._providers.get(plugin_id)

    def list_capabilities(self) -> tuple[PluginCapability, ...]:
        """Return declared capabilities from all registered providers."""
        capabilities: list[PluginCapability] = []
        for plugin_id in self.list_plugin_ids():
            provider = self._providers[plugin_id]
            capabilities.extend(provider.get_capabilities())
        return tuple(capabilities)

    def health_check(self) -> tuple[PluginHealth, ...]:
        """Return health results for all registered providers."""
        return tuple(self._providers[plugin_id].health_check() for plugin_id in self.list_plugin_ids())

    def execute(
        self,
        plugin_id: str,
        action: str,
        params: dict[str, Any],
    ) -> PluginResult:
        """Execute a declared action through a registered provider."""
        provider = self._providers.get(plugin_id)
        if provider is None:
            return PluginResult(
                success=False,
                plugin_id=plugin_id,
                action=action,
                category="plugin_not_found",
                message=f"plugin is not registered: {plugin_id}",
            )
        allowed = {capability.capability_id for capability in provider.get_capabilities()}
        if action not in allowed:
            return PluginResult(
                success=False,
                plugin_id=plugin_id,
                action=action,
                category="capability_unsupported",
                message=f"plugin capability is unavailable: {action}",
            )
        return provider.execute(action, params)

    def extend(self, providers: Iterable[PluginContract]) -> None:
        """Register multiple providers using the same validation path."""
        for provider in providers:
            self.register(provider)
