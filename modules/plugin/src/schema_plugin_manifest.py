"""Manifest and capability schemas for optional Blender plugins."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class PluginCapability:
    """A validated operation exposed by one plugin."""

    capability_id: str
    version: int = 1
    parameters: tuple[str, ...] = ()


@dataclass(frozen=True)
class PluginManifest:
    """Static metadata used before activating a plugin."""

    plugin_id: str
    name: str
    version: str
    provider_type: str
    blender_min_version: str
    entry_point: str
    capabilities: tuple[PluginCapability, ...] = field(default_factory=tuple)

    def capability_ids(self) -> frozenset[str]:
        """Return the declared capability identifiers."""
        return frozenset(capability.capability_id for capability in self.capabilities)
