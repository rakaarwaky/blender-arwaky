"""CLI domain contract: command protocol (ABC).

Capability implements this protocol. The Agent layer depends on it.
FR-CLI-001: Parse and Route Commands — surface routes CLI intents
through this aggregate; capabilities implement the actual operations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from .taxonomy_cli_vo import CliResultVo as _CliResultVo  # AES202: mandatory taxonomy import


class ICliCommandProtocol(ABC):
    """Aggregate protocol for all CLI command operations.

    Surface depends on this contract. Capabilities implement it.
    """

    @abstractmethod
    def init(
        self,
        filepath: str,
        mode: str = "headless",
        port: int = 9876,
    ) -> dict[str, Any]:
        """Initialize a Blender session with the given file.

        Args:
            filepath: Path to .blend file
            mode: "gui" or "headless"
            port: TCP port for addon

        Returns:
            CliResultVo serialized as dict with success/error envelope
        """
        ...

    @abstractmethod
    def run(
        self,
        filepath: str,
        action: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Execute an action on the active Blender instance.

        Args:
            filepath: Path to .blend file (must match active entity)
            action: Action name (e.g., "execute_code", "get_scene_info")
            params: Action parameters

        Returns:
            CliResultVo serialized as dict
        """
        ...

    @abstractmethod
    def screenshot(
        self,
        filepath: str,
        output: str,
        max_size: int = 800,
        view_angle: str = "PERSPECTIVE",
        shading: str = "MATERIAL",
        show_overlays: bool = True,
        focus_object: str | None = None,
    ) -> dict[str, Any]:
        """Capture a viewport screenshot.

        Returns:
            CliResultVo serialized as dict
        """
        ...

    @abstractmethod
    def render(
        self,
        filepath: str,
        output: str,
        resolution_x: int = 1920,
        resolution_y: int = 1080,
    ) -> dict[str, Any]:
        """Execute a full frame render.

        Returns:
            CliResultVo serialized as dict
        """
        ...

    @abstractmethod
    def close(self, filepath: str) -> dict[str, Any]:
        """Close the active Blender instance.

        Returns:
            CliResultVo serialized as dict
        """
        ...

    @abstractmethod
    def status(self) -> dict[str, Any]:
        """Get status of the active Blender instance.

        Returns:
            CliResultVo serialized as dict
        """
        ...
