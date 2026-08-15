"""MPFB 2 provider entry point.

The provider intentionally contains no copied MPFB 2 source. Runtime probing and
operation mapping will be implemented in later integration waves.
"""

from __future__ import annotations

from typing import Any

from modules.plugin.src.contract_plugin_protocol import PluginContract
from modules.plugin.src.schema_plugin_manifest import PluginCapability, PluginManifest
from modules.plugin.src.schema_plugin_result import PluginHealth, PluginResult


class Mpfb2Provider:
    """Provider-neutral boundary for an externally installed MPFB 2 add-on."""

    _manifest = PluginManifest(
        plugin_id="mpfb2",
        name="MPFB 2",
        version="2.0.17",
        provider_type="blender_addon",
        blender_min_version="4.2",
        entry_point="plugin_entry:create_provider",
        capabilities=(
            PluginCapability(
                capability_id="character.create",
                version=1,
                parameters=("base",),
            ),
        ),
    )

    def get_manifest(self) -> PluginManifest:
        """Return static MPFB 2 metadata."""
        return self._manifest

    def discover(self, context: dict[str, Any] | None = None) -> bool:
        """Use an explicit runtime probe result until Blender integration lands."""
        return bool((context or {}).get("mpfb2_available", False))

    def get_capabilities(self) -> tuple[PluginCapability, ...]:
        """Return capability declarations for the current provider version."""
        return self._manifest.capabilities

    def execute(self, action: str, params: dict[str, Any]) -> PluginResult:
        """Return a bounded not-implemented result for the initial skeleton."""
        del params
        return PluginResult(
            success=False,
            plugin_id=self._manifest.plugin_id,
            action=action,
            category="capability_not_implemented",
            message="MPFB 2 operation mapping is planned for the next integration wave",
        )

    def health_check(self) -> PluginHealth:
        """Report an inactive provider until Blender probing is wired."""
        return PluginHealth(
            plugin_id=self._manifest.plugin_id,
            installed=False,
            active=False,
            compatible=False,
            available_capabilities=frozenset(),
            category="provider_probe_pending",
            message="MPFB 2 runtime discovery is not wired yet",
        )


def create_provider() -> PluginContract:
    """Create the MPFB 2 provider without importing the external add-on."""
    return Mpfb2Provider()
