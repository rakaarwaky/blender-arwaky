"""Capability catalog helpers for registered external plugins."""

from __future__ import annotations

from .registry_plugin_catalog import PluginCatalog
from .schema_plugin_manifest import PluginCapability


class PluginCapabilityService:
    """Expose only capabilities declared by registered providers."""

    def __init__(self, catalog: PluginCatalog) -> None:
        self._catalog = catalog

    def list_capabilities(self) -> tuple[PluginCapability, ...]:
        """Return the current extension capability catalog."""
        return self._catalog.list_capabilities()

    def has_capability(self, capability_id: str) -> bool:
        """Check whether one extension capability is registered."""
        return any(capability.capability_id == capability_id for capability in self.list_capabilities())
