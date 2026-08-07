"""CLI domain contract: registry state protocol.

Defines the thread-safe registry API for tracking the active Blender
instance. Capabilities implement this protocol; surfaces depend on it.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from ..common.taxonomy_core_vo import FilePath, PortNumber
from .taxonomy_cli_constant import REGISTRY_DEFAULT_PORT
from .taxonomy_cli_vo import BlenderPid, CliResultVo, RegistryStateVo


class IRegistryProtocol(ABC):
    """Protocol for the Blender registry state store."""

    @abstractmethod
    def get_state(self) -> RegistryStateVo:
        """Return current registry state VO."""
        ...

    @abstractmethod
    def get_active(self) -> FilePath | None:
        """Return active entity filepath or None."""
        ...

    @abstractmethod
    def get_port(self) -> PortNumber:
        """Return configured Blender port."""
        ...

    @abstractmethod
    def get_pid(self) -> BlenderPid | None:
        """Return active Blender PID or None."""
        ...

    @abstractmethod
    def is_active(self) -> bool:
        """Check whether an instance is registered."""
        ...

    @abstractmethod
    def set_active(self, filepath: FilePath, pid: BlenderPid, port: PortNumber = REGISTRY_DEFAULT_PORT) -> None:
        """Register the active Blender instance."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear the registered state."""
        ...

    @abstractmethod
    def assert_no_active(self) -> CliResultVo | None:
        """Return an error VO if an instance is active, else None."""
        ...

    @abstractmethod
    def assert_active(self, filepath: FilePath) -> CliResultVo | None:
        """Return an error VO if active state does not match filepath, else None."""
        ...
