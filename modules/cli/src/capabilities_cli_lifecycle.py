"""Capability: CLI lifecycle manager.

Implements CliLifecycleProtocol — handles Blender application lifecycle
(init, launch, close, status) through the surface layer's BlenderManager.
"""

from __future__ import annotations

import logging

from modules.shared.src.common.taxonomy_core_vo import ErrorMessage
from modules.shared.src.cli.contract_cli_lifecycle_protocol import CliLifecycleProtocol

logger = logging.getLogger("BlenderMCPServer")


class CliLifecycleManager(CliLifecycleProtocol):
    """Business logic for CLI lifecycle management."""

    def __init__(self, blender_manager: object) -> None:
        """Initialize with a Blender manager from the surface layer.

        Args:
            blender_manager: A callable or surface capability that manages
                Blender process lifecycle (init, run, close, status).
        """
        self._blender_manager = blender_manager

    async def locate_and_register(self, path: str | None = None) -> dict:
        """Locate Blender executable and register it persistently.

        FR-CLI-001: Auto-detects from standard paths if no path provided.
        Validates the executable is correct software.
        Returns success status and resolved path.

        Args:
            path: Optional custom path to Blender executable.

        Returns:
            Dictionary with success status, resolved path, and message.
        """
        logger.info("Locating and registering Blender (path=%s)...", path)

        try:
            result = self._blender_manager.locate_blender(path)
            if isinstance(result, dict):
                logger.info("Blender registered: %s", result.get("path"))
                return result
            return {
                "success": True,
                "path": result if result else path,
                "message": "Blender path registered successfully",
            }
        except Exception as e:
            logger.error("Locate and register failed: %s", e)
            return {
                "success": False,
                "path": None,
                "message": f"Failed to locate Blender: {e}",
            }

    async def launch(self, extra_args: list[str] | None = None) -> dict:
        """Launch Blender with integration components enabled.

        FR-CLI-002: Injects necessary startup arguments.
        Waits for application to signal readiness.
        Refuses duplicate instance if one is already running.
        Returns process PID and readiness confirmation.

        Args:
            extra_args: Optional additional startup arguments.

        Returns:
            Dictionary with success status, process PID, and message.
        """
        logger.info("Launching Blender (extra_args=%s)...", extra_args)

        try:
            result = self._blender_manager.launch_blender(extra_args)
            if isinstance(result, dict):
                logger.info("Blender launched with PID: %s", result.get("pid"))
                return result
            return {
                "success": True,
                "pid": result,
                "message": "Blender launched successfully",
            }
        except Exception as e:
            logger.error("Launch failed: %s", e)
            return {
                "success": False,
                "pid": None,
                "message": f"Failed to launch Blender: {e}",
            }

    async def shutdown(self) -> dict:
        """Gracefully terminate the Blender process.

        FR-CLI-003: Attempts graceful shutdown first, force-kills as fallback.
        Updates system state to reflect stopped status.
        Succeeds silently if already closed.
        Returns success status and termination method used.

        Returns:
            Dictionary with success status, method used, and message.
        """
        logger.info("Shutting down Blender...")

        try:
            result = self._blender_manager.close_blender()
            if isinstance(result, dict):
                logger.info("Blender shutdown: %s", result.get("method"))
                return result
            return {
                "success": True,
                "method": "graceful" if result else "already_closed",
                "message": "Blender shut down successfully",
            }
        except Exception as e:
            logger.error("Shutdown failed: %s", e)
            return {
                "success": False,
                "method": "force",
                "message": f"Failed to shutdown Blender: {e}",
            }

    async def check_status(self) -> dict:
        """Verify Blender is running, healthy, and ready.

        FR-CLI-004: Confirms actual process state (not stale record).
        Verifies communication channel is active.
        Returns detailed status including process ID, channel, uptime.

        Returns:
            Dictionary with success status, process details, and message.
        """
        logger.info("Checking Blender status...")

        try:
            result = self._blender_manager.get_status()
            if isinstance(result, dict):
                logger.info("Blender status: %s", result.get("state"))
                return result
            return {
                "success": True,
                "state": result,
                "message": "Blender is running",
            }
        except Exception as e:
            logger.error("Status check failed: %s", e)
            return {
                "success": False,
                "state": "not_running",
                "message": f"Failed to check status: {e}",
            }
