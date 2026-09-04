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

from .plugin_runtime_facts import RigifyRuntimeFacts, probe_blender_runtime

RIGIFY_CAPABILITIES = (
    PluginCapabilityId("rigging.inspect_armature"),
    PluginCapabilityId("rigging.set_pose_bone_transform"),
    PluginCapabilityId("rigging.configure_bone_constraint"),
    PluginCapabilityId("rigging.configure_shape_key"),
    PluginCapabilityId("rigging.get_deformation_state"),
    PluginCapabilityId("rigging.bind_character_to_rig"),
    PluginCapabilityId("rigging.create_rigify_metarig"),
)
RIGIFY_UNSUPPORTED_CAPABILITIES = ("character", "asset_generation")


class RigifyPluginOperation(PluginOperationProtocol):
    """Provider operation port for Blender's bundled Rigify add-on."""

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
        """Return provider metadata without importing Rigify internals."""
        return PluginManifestVO(
            plugin_id=PluginId("rigify"),
            name=PluginName("Rigify"),
            version=PluginVersion("bundled"),
            provider_type=PluginProviderType(PLUGIN_PROVIDER_TYPE_BLENDER_EXTENSION),
            blender_min_version=self._blender_min_version,
            entry_point=PluginMessage("plugin/rigify/plugin_entry.py; extension_id=rigify"),
            capabilities=PluginCapabilityList(RIGIFY_CAPABILITIES),
        )

    def discover(self, blender_version: BlenderVersion) -> PluginDiscoveryVO:
        """Return bundled provider availability and compatibility state."""
        compatible = self._is_compatible(blender_version, self._blender_min_version)
        message = PLUGIN_STATUS_SUCCESS
        if not self._installed or not self._active:
            message = PLUGIN_STATUS_UNAVAILABLE
        elif not compatible:
            message = PLUGIN_STATUS_INCOMPATIBLE
        return PluginDiscoveryVO(
            plugin_id=PluginId("rigify"),
            installed=self._installed,
            active=self._active,
            compatible=compatible,
            message=PluginMessage(message),
        )

    def health_check(self) -> PluginHealthVO:
        """Return current Rigify lifecycle state without executing operations."""
        compatible = self._is_compatible(self._blender_version, self._blender_min_version)
        available = self._installed and self._active and compatible
        return PluginHealthVO(
            plugin_id=PluginId("rigify"),
            installed=self._installed,
            active=self._active,
            compatible=compatible,
            message=PluginMessage(PLUGIN_STATUS_SUCCESS if available else PLUGIN_STATUS_UNAVAILABLE),
        )

    def capabilities(self) -> PluginCapabilityList:
        """Return canonical rigging capability identifiers owned by Rigify."""
        return PluginCapabilityList(RIGIFY_CAPABILITIES)

    def unsupported_capabilities(self) -> tuple[str, ...]:
        """Return explicit boundaries owned by other providers."""
        return RIGIFY_UNSUPPORTED_CAPABILITIES

    def execute(self, action: PluginActionName, params: PluginParameterMap) -> PluginExecutionVO:
        """Reject undeclared operations until the live operation adapter is wired."""
        del params
        if PluginCapabilityId(str(action)) not in self.capabilities():
            return PluginExecutionVO(
                plugin_id=PluginId("rigify"),
                action=action,
                success=False,
                message=PluginMessage(PLUGIN_STATUS_UNSUPPORTED),
            )
        return PluginExecutionVO(
            plugin_id=PluginId("rigify"),
            action=action,
            success=False,
            message=PluginMessage("Rigify operation mapping requires Blender integration"),
        )

    @staticmethod
    def _is_compatible(current: BlenderVersion, minimum: BlenderVersion) -> bool:
        """Compare numeric Blender versions conservatively."""
        current_parts = tuple(int(part) for part in str(current).split(".")[:3])
        minimum_parts = tuple(int(part) for part in str(minimum).split(".")[:3])
        width = max(len(current_parts), len(minimum_parts))
        return current_parts + (0,) * (width - len(current_parts)) >= (
            minimum_parts + (0,) * (width - len(minimum_parts))
        )


def create_provider(installed: bool = False, active: bool = False) -> RigifyPluginOperation:
    """Create the bundled Rigify provider boundary."""
    return RigifyPluginOperation(installed=installed, active=active)


def create_runtime_provider(runtime: object | None = None) -> RigifyPluginOperation:
    """Create a provider from a controlled Blender runtime probe."""
    facts: RigifyRuntimeFacts = probe_blender_runtime(runtime)
    return RigifyPluginOperation(
        installed=facts.installed,
        active=facts.active,
        blender_version=facts.blender_version,
    )
