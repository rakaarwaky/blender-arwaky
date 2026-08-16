"""MPFB 2 provider boundary for Blender Arwaky."""

from __future__ import annotations

from modules.plugin.src.contract_plugin_operation_protocol import PluginOperationProtocol
from modules.plugin.src.taxonomy_plugin_constant import (
    PLUGIN_PROVIDER_TYPE_BLENDER_EXTENSION,
    PLUGIN_STATUS_INCOMPATIBLE,
    PLUGIN_STATUS_SUCCESS,
    PLUGIN_STATUS_UNAVAILABLE,
    PLUGIN_STATUS_UNSUPPORTED,
)
from modules.plugin.src.taxonomy_plugin_vo import (
    BlenderVersion,
    PluginActionName,
    PluginCapabilityId,
    PluginCapabilityList,
    PluginDiscoveryVO,
    PluginExecutionVO,
    PluginHealthVO,
    PluginId,
    PluginManifestVO,
    PluginMessage,
    PluginName,
    PluginParameterMap,
    PluginProviderType,
    PluginVersion,
)

from .plugin_runtime_facts import Mpfb2RuntimeFacts, probe_blender_runtime


class Mpfb2PluginOperation(PluginOperationProtocol):
    """Provider operation port for an externally installed MPFB 2 add-on."""

    def __init__(
        self,
        installed: bool = False,
        active: bool = False,
        blender_min_version: BlenderVersion | None = None,
        blender_version: BlenderVersion | None = None,
    ) -> None:
        self._installed = installed
        self._active = active
        self._blender_min_version = blender_min_version or BlenderVersion("5.2")
        self._blender_version = blender_version or self._blender_min_version

    def manifest(self) -> PluginManifestVO:
        """Return provider metadata without importing MPFB2."""
        return PluginManifestVO(
            plugin_id=PluginId("mpfb2"),
            name=PluginName("MPFB 2"),
            version=PluginVersion("2.0.17"),
            provider_type=PluginProviderType(PLUGIN_PROVIDER_TYPE_BLENDER_EXTENSION),
            blender_min_version=self._blender_min_version,
            entry_point=PluginMessage("plugin/mpfb2/plugin_entry.py; extension_id=mpfb"),
            capabilities=PluginCapabilityList((PluginCapabilityId("character.create"),)),
        )

    def discover(self, blender_version: BlenderVersion) -> PluginDiscoveryVO:
        """Return installation, activation, and compatibility state."""
        compatible = self._is_compatible(blender_version, self._blender_min_version)
        message = PLUGIN_STATUS_SUCCESS
        if not self._installed or not self._active:
            message = PLUGIN_STATUS_UNAVAILABLE
        elif not compatible:
            message = PLUGIN_STATUS_INCOMPATIBLE
        return PluginDiscoveryVO(
            plugin_id=PluginId("mpfb2"),
            installed=self._installed,
            active=self._active,
            compatible=compatible,
            message=PluginMessage(message),
        )

    def health_check(self) -> PluginHealthVO:
        """Return current provider state without executing an operation."""
        compatible = self._is_compatible(
            self._blender_version,
            self._blender_min_version,
        )
        return PluginHealthVO(
            plugin_id=PluginId("mpfb2"),
            installed=self._installed,
            active=self._active,
            compatible=compatible,
            message=PluginMessage(
                PLUGIN_STATUS_SUCCESS if self._installed and self._active and compatible else PLUGIN_STATUS_UNAVAILABLE
            ),
        )

    def capabilities(self) -> PluginCapabilityList:
        """Return capabilities only when the provider is available."""
        if not self._installed or not self._active:
            return PluginCapabilityList(())
        return PluginCapabilityList((PluginCapabilityId("character.create"),))

    def execute(
        self,
        action: PluginActionName,
        params: PluginParameterMap,
    ) -> PluginExecutionVO:
        """Return bounded provider state until live MPFB2 mapping is implemented."""
        del params
        if action not in self.capabilities():
            return PluginExecutionVO(
                plugin_id=PluginId("mpfb2"),
                action=action,
                success=False,
                message=PluginMessage(PLUGIN_STATUS_UNSUPPORTED),
            )
        return PluginExecutionVO(
            plugin_id=PluginId("mpfb2"),
            action=action,
            success=False,
            message=PluginMessage("MPFB2 operation mapping requires Blender integration"),
        )

    @staticmethod
    def _is_compatible(
        current: BlenderVersion,
        minimum: BlenderVersion,
    ) -> bool:
        """Compare numeric Blender versions conservatively."""
        current_parts = tuple(int(part) for part in str(current).split(".")[:3])
        minimum_parts = tuple(int(part) for part in str(minimum).split(".")[:3])
        width = max(len(current_parts), len(minimum_parts))
        return current_parts + (0,) * (width - len(current_parts)) >= (
            minimum_parts + (0,) * (width - len(minimum_parts))
        )


def create_provider(
    installed: bool = False,
    active: bool = False,
) -> Mpfb2PluginOperation:
    """Create the optional MPFB2 provider boundary."""
    return Mpfb2PluginOperation(installed=installed, active=active)


def create_runtime_provider(runtime: object | None = None) -> Mpfb2PluginOperation:
    """Create a provider from a controlled Blender runtime probe."""
    facts: Mpfb2RuntimeFacts = probe_blender_runtime(runtime)
    return Mpfb2PluginOperation(
        installed=facts.installed,
        active=facts.active,
        blender_version=facts.blender_version,
    )
