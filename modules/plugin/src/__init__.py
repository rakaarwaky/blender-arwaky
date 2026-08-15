"""Global plugin framework for optional Blender providers."""

from .contract_plugin_protocol import PluginContract
from .registry_plugin_catalog import PluginCatalog
from .schema_plugin_manifest import PluginManifest
from .schema_plugin_result import PluginResult

__all__ = ["PluginCatalog", "PluginContract", "PluginManifest", "PluginResult"]
