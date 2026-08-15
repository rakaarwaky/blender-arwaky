"""Provider-neutral adapter and lifecycle operations."""

from __future__ import annotations

from typing import Any

from .contract_plugin_protocol import PluginContract
from .schema_plugin_result import PluginHealth, PluginResult


class PluginAdapter:
    """Normalize provider lifecycle and execution behind one global boundary."""

    def __init__(self, provider: PluginContract) -> None:
        self._provider = provider

    @property
    def plugin_id(self) -> str:
        """Return the provider identifier."""
        return self._provider.get_manifest().plugin_id

    def health_check(self) -> PluginHealth:
        """Return provider health without invoking an arbitrary operation."""
        return self._provider.health_check()

    def execute(self, action: str, params: dict[str, Any]) -> PluginResult:
        """Execute only an explicitly declared provider capability."""
        capability_ids = {capability.capability_id for capability in self._provider.get_capabilities()}
        if action not in capability_ids:
            return PluginResult(
                success=False,
                plugin_id=self.plugin_id,
                action=action,
                category="capability_unsupported",
                message=f"plugin capability is unavailable: {action}",
            )
        return self._provider.execute(action, params)
