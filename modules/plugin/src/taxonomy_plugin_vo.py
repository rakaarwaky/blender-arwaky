"""Stable value objects for the plugin feature boundary."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import NewType

PluginId = NewType("PluginId", str)
PluginName = NewType("PluginName", str)
PluginVersion = NewType("PluginVersion", str)
PluginProviderType = NewType("PluginProviderType", str)
BlenderVersion = NewType("BlenderVersion", str)
PluginCapabilityId = NewType("PluginCapabilityId", str)
PluginActionName = NewType("PluginActionName", str)
PluginParameterName = NewType("PluginParameterName", str)
PluginParameterMap = NewType("PluginParameterMap", dict[str, object])
PluginIdList = NewType("PluginIdList", tuple[PluginId, ...])
PluginCapabilityList = NewType("PluginCapabilityList", tuple[PluginCapabilityId, ...])
PluginMessage = NewType("PluginMessage", str)
PluginSourceUrl = NewType("PluginSourceUrl", str)
PluginSha256 = NewType("PluginSha256", str)
PluginCachePath = NewType("PluginCachePath", str)
PluginInstallPath = NewType("PluginInstallPath", str)


class PluginLifecycleState(StrEnum):
    """Normalized provider lifecycle states shared by every plugin."""

    UNKNOWN = "unknown"
    UNAVAILABLE = "unavailable"
    INSTALLED = "installed"
    ENABLED = "enabled"
    INCOMPATIBLE = "incompatible"


def derive_plugin_lifecycle_state(installed: bool, active: bool, compatible: bool) -> PluginLifecycleState:
    """Derive one deterministic lifecycle state from provider health flags."""
    if not installed:
        return PluginLifecycleState.UNAVAILABLE
    if not compatible:
        return PluginLifecycleState.INCOMPATIBLE
    if active:
        return PluginLifecycleState.ENABLED
    return PluginLifecycleState.INSTALLED


@dataclass(frozen=True)
class PluginManifestVO:
    """Provider metadata declared at the plugin boundary."""

    plugin_id: PluginId
    name: PluginName
    version: PluginVersion
    provider_type: PluginProviderType
    blender_min_version: BlenderVersion
    entry_point: PluginMessage
    capabilities: PluginCapabilityList


@dataclass(frozen=True)
class PluginDiscoveryVO:
    """Provider availability and compatibility result."""

    plugin_id: PluginId
    installed: bool
    active: bool
    compatible: bool
    message: PluginMessage
    state: PluginLifecycleState = PluginLifecycleState.UNKNOWN


@dataclass(frozen=True)
class PluginHealthVO:
    """Provider health result."""

    plugin_id: PluginId
    installed: bool
    active: bool
    compatible: bool
    message: PluginMessage
    state: PluginLifecycleState = PluginLifecycleState.UNKNOWN


@dataclass(frozen=True)
class PluginExecutionVO:
    """Normalized provider operation result."""

    plugin_id: PluginId
    action: PluginActionName
    success: bool
    message: PluginMessage


@dataclass(frozen=True)
class PluginRegistrationVO:
    """Provider registration result."""

    plugin_id: PluginId
    registered: bool
    message: PluginMessage


@dataclass(frozen=True)
class PluginPackageRequestVO:
    """Validated package lifecycle request."""

    plugin_id: PluginId
    source_url: PluginSourceUrl
    sha256: PluginSha256
    cache_path: PluginCachePath
    install_path: PluginInstallPath
    blender_path: PluginInstallPath | None = None
    repository_id: PluginMessage = PluginMessage("user_default")
    extension_id: PluginId | None = None
    enable: bool = True


@dataclass(frozen=True)
class PluginPackageResultVO:
    """Normalized package lifecycle result."""

    plugin_id: PluginId
    operation: PluginActionName
    success: bool
    package_path: PluginCachePath
    install_path: PluginInstallPath
    message: PluginMessage
