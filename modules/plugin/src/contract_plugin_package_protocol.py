"""Contract for safe plugin package lifecycle operations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_plugin_vo import PluginActionName, PluginPackageRequestVO, PluginPackageResultVO


class PluginPackageProtocol(ABC):
    """Port for controlled package acquisition and lifecycle operations."""

    @abstractmethod
    def execute(
        self,
        action: PluginActionName,
        request: PluginPackageRequestVO,
    ) -> PluginPackageResultVO:
        """Execute one explicitly declared package lifecycle action."""
        ...
