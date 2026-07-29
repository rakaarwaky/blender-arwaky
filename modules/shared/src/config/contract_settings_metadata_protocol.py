"""Contract: Settings metadata protocol (FR-CFG-004).

Defines the inbound behavior interface for exposing diagnostic metadata
about how settings were loaded, merged, and validated.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol

from ..common.taxonomy_core_vo import ConfigMetadata


class _IMetadataSource(Protocol):
    """Protocol for providing ConfigMetadata (FR-CFG-004).

    Replaces primitive Callable type with a proper protocol for DI inversion.
    Implemented by SettingsLoaderCapability.get_last_metadata bound method.
    """

    def __call__(self) -> ConfigMetadata: ...


class ISettingsMetadataProtocol(ABC):
    """Protocol for providing settings metadata (FR-CFG-004)."""

    @abstractmethod
    def get_metadata(self) -> ConfigMetadata:
        """Return current settings metadata. Must not leak secret values."""
        ...

    @abstractmethod
    def to_safe_dict(self, metadata: ConfigMetadata) -> dict[str, Any]:
        """Serialize metadata for diagnostics. Secrets excluded, safe for MCP/CLI output."""
        ...
