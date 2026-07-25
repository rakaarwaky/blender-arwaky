"""CLI domain contract: lifecycle management protocol (ABC based).

Defines the protocol for managing Blender application lifecycle — init, launch,
close, and status checks.

FR-CLI-001: Locate and Register Application
FR-CLI-002: Launch Application
FR-CLI-003: Shut Down Application
FR-CLI-004: Check Application Status
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class CliLifecycleProtocol(ABC):
    """Protocol for managing Blender application lifecycle."""

    @abstractmethod
    async def locate_and_register(self, path: str | None = None) -> dict:
        """Locate Blender executable and register it persistently.

        FR-CLI-001: Auto-detects from standard paths if no path provided.
        Validates the executable is correct software.
        Returns success status and resolved path.
        """
        pass

    @abstractmethod
    async def launch(self, extra_args: list[str] | None = None) -> dict:
        """Launch Blender with integration components enabled.

        FR-CLI-002: Injects necessary startup arguments.
        Waits for application to signal readiness.
        Refuses duplicate instance if one is already running.
        Returns process PID and readiness confirmation.
        """
        pass

    @abstractmethod
    async def shutdown(self) -> dict:
        """Gracefully terminate the Blender process.

        FR-CLI-003: Attempts graceful shutdown first, force-kills as fallback.
        Updates system state to reflect stopped status.
        Succeeds silently if already closed.
        Returns success status and termination method used.
        """
        pass

    @abstractmethod
    async def check_status(self) -> dict:
        """Verify Blender is running, healthy, and ready.

        FR-CLI-004: Confirms actual process state (not stale record).
        Verifies communication channel is active.
        Returns detailed status including process ID, channel, uptime.
        """
        pass
