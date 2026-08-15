"""Provider-neutral plugin contract."""

from __future__ import annotations

from typing import Any, Protocol

from modules.shared.src.common.taxonomy_core_vo import ActionName

from .schema_plugin_manifest import PluginCapability, PluginManifest
from .schema_plugin_result import PluginHealth, PluginResult


class PluginContract(Protocol):
    """Contract implemented by every external Blender plugin provider."""

    def get_manifest(self) -> PluginManifest:
        """Return static provider metadata."""
        ...

    def discover(self, context: dict[str, Any] | None = None) -> bool:
        """Return whether the provider is installed and usable."""
        ...

    def get_capabilities(self) -> tuple[PluginCapability, ...]:
        """Return capabilities available in the current runtime."""
        ...

    def execute(self, action: ActionName, params: dict[str, Any]) -> PluginResult:
        """Execute one declared action; arbitrary code is not accepted."""
        ...

    def health_check(self) -> PluginHealth:
        """Return current provider health."""
        ...
