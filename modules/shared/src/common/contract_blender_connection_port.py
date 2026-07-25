"""Common contract: Blender socket connection port interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_core_vo import ActionName, Details, SuccessFlag


class ContractBlenderConnectionPort(ABC):
    """Port interface for managing Blender socket connections."""

    @abstractmethod
    def connect(self) -> SuccessFlag:
        """Establish connection to Blender. Returns True if successful."""
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the connection to Blender."""
        pass

    @abstractmethod
    def is_connected(self) -> SuccessFlag:
        """Check if the socket is currently connected and alive."""
        pass

    @abstractmethod
    def send_command(
        self, command_type: ActionName, params: Details | None = None
    ) -> Details:
        """Send a command to Blender and return the response."""
        pass
