"""Standard plugin discovery, health, and execution results."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PluginResult:
    """Normalized result returned by a plugin operation."""

    success: bool
    plugin_id: str
    action: str
    data: dict[str, Any] = field(default_factory=dict)
    category: str = ""
    message: str = ""
    detail: str | None = None


@dataclass(frozen=True)
class PluginHealth:
    """Runtime status for one plugin."""

    plugin_id: str
    installed: bool
    active: bool
    compatible: bool
    available_capabilities: frozenset[str] = frozenset()
    category: str = ""
    message: str = ""


@dataclass(frozen=True)
class PluginDiscovery:
    """Discovery result produced before plugin activation."""

    plugin_id: str
    manifest: object | None
    available: bool
    compatible: bool
    category: str = ""
    message: str = ""
