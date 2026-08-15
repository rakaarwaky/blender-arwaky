"""Discovery and compatibility checks for external plugin providers."""

from __future__ import annotations

from .contract_plugin_protocol import PluginContract
from .schema_plugin_result import PluginDiscovery


class PluginDiscoveryService:
    """Discover providers using provider-neutral contract metadata."""

    def discover(
        self,
        provider: PluginContract,
        blender_version: str,
    ) -> PluginDiscovery:
        """Return availability and compatibility without executing an action."""
        manifest = provider.get_manifest()
        available = provider.discover({"blender_version": blender_version})
        compatible = self._is_compatible(blender_version, manifest.blender_min_version)
        if not available:
            return PluginDiscovery(
                plugin_id=manifest.plugin_id,
                manifest=manifest,
                available=False,
                compatible=compatible,
                category="plugin_unavailable",
                message="provider is not installed or not active",
            )
        if not compatible:
            return PluginDiscovery(
                plugin_id=manifest.plugin_id,
                manifest=manifest,
                available=True,
                compatible=False,
                category="plugin_incompatible",
                message=(
                    f"Blender {blender_version} is below the minimum supported version {manifest.blender_min_version}"
                ),
            )
        return PluginDiscovery(
            plugin_id=manifest.plugin_id,
            manifest=manifest,
            available=True,
            compatible=True,
            category="available",
            message="provider is available and compatible",
        )

    @staticmethod
    def _is_compatible(current: str, minimum: str) -> bool:
        """Compare dotted numeric Blender versions conservatively."""
        current_parts = tuple(int(part) for part in current.split(".")[:3])
        minimum_parts = tuple(int(part) for part in minimum.split(".")[:3])
        width = max(len(current_parts), len(minimum_parts))
        return current_parts + (0,) * (width - len(current_parts)) >= (
            minimum_parts + (0,) * (width - len(minimum_parts))
        )
