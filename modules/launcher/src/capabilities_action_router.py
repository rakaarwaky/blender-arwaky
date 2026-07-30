"""Launcher action router — bridges dispatcher actions to launcher capabilities.

FR-LAU-002 / FR-LAU-003 / FR-LAU-004 / FR-LAU-001: Maps dispatcher action names
to the appropriate launcher capability methods.

P0: Constructs LaunchRequestVO from dispatcher params for launch_blender action.
P0: Routes shutdown, status, and register actions to their respective capabilities.
"""

from __future__ import annotations

import logging

from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchMode,
    LaunchRequestVO,
    RuntimeStatusVO,
)

logger = logging.getLogger("BlenderMCPServer")


class LauncherActionRouter:
    """Routes dispatcher actions to launcher capability methods.

    Implements execute_action(action_name, params) for use as the
    SyncDispatchExecutor._execute callable.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(self, launcher: ILauncherOperateAggregate) -> None:
        self._launcher = launcher

    # ─── Block 2: Public Contract ────────────────────────────
    def execute_action(self, action_name: str, params: dict) -> dict:
        """Route a dispatcher action to the appropriate launcher method.

        P0: Parses LaunchRequestVO from params for launch_blender action.
        Returns a dict result suitable for normalization by the dispatcher.
        """
        if action_name == "launch_blender":
            return self._handle_launch(params)
        elif action_name == "shutdown_blender":
            return self._handle_shutdown(params)
        elif action_name == "get_runtime_status":
            return self._handle_status(params)
        elif action_name == "register_executable":
            return self._handle_register(params)
        else:
            logger.warning("Unknown launcher action: %s", action_name)
            return {"success": False, "error": f"Unknown action: {action_name}", "category": "validation_error"}

    # ─── Block 3: Action Handlers ────────────────────────────
    def _handle_launch(self, params: dict) -> dict:
        """Handle launch_blender action — construct LaunchRequestVO and dispatch."""
        mode_str = params.get("mode", "headless")
        try:
            mode = LaunchMode(mode_str)
        except ValueError:
            mode = LaunchMode.INTERFACE if mode_str == "interface" else LaunchMode.HEADLESS

        timeout = params.get("readiness_timeout_seconds")
        if timeout is None:
            port = params.get("port")
            if port is not None:
                logger.warning("'port' parameter ignored — launcher uses readiness probe, not TCP port")

        request = LaunchRequestVO(mode=mode, readiness_timeout_seconds=timeout)
        result = self._launcher.launch(request)
        return {
            "success": result.success,
            "message": result.message or ("Launched successfully" if result.success else "Launch failed"),
            "data": {
                "process_id": result.process_id,
                "ready": result.ready,
                "launch_method": result.launch_method.value if result.launch_method else None,
                "duration_ms": result.duration_ms,
            },
            "error_category": result.error_category if not result.success else None,
        }

    def _handle_shutdown(self, params: dict) -> dict:
        """Handle shutdown_blender action."""
        force = params.get("force", False)
        allow_escalation = params.get("allow_escalation", True)
        result = self._launcher.shutdown(force=force, allow_escalation=allow_escalation)
        return {
            "success": result.success,
            "message": result.message or ("Shutdown successful" if result.success else "Shutdown failed"),
            "data": {
                "termination_method": result.termination_method.value if result.termination_method else None,
                "duration_ms": result.duration_ms,
                "final_state": result.final_state.value if result.final_state else None,
                "escalated": result.escalated,
            },
            "error_category": result.error_category if not result.success else None,
        }

    def _handle_status(self, params: dict) -> dict:
        """Handle get_runtime_status action."""
        depth_str = params.get("depth", "LIGHTWEIGHT")
        try:
            from modules.shared.src.launcher.taxonomy_launcher_vo import ProbeDepth

            depth = ProbeDepth[depth_str.upper()]
        except (KeyError, AttributeError):
            from modules.shared.src.launcher.taxonomy_launcher_vo import ProbeDepth

            depth = ProbeDepth.LIGHTWEIGHT

        result: RuntimeStatusVO = self._launcher.check_status(depth)
        return {
            "success": True,
            "data": {
                "state": result.state.value if result.state else None,
                "process_id": result.process_id,
                "bridge_endpoint": (
                    {
                        "host": ep.host,
                        "port": ep.port,
                    }
                    for ep in result.bridge_endpoints
                )
                if result.bridge_endpoints
                else None,
                "last_updated": result.last_updated,
            },
        }

    def _handle_register(self, params: dict) -> dict:
        """Handle register_executable action."""
        path = params.get("path")
        if path:
            from modules.shared.src.common.taxonomy_core_vo import FilePath

            config = LauncherConfigVO(executable_path=path)
            result = self._launcher.locate_and_register(config, override=FilePath(path))
        else:
            result = self._launcher.locate_and_register(LauncherConfigVO())
        return {
            "success": result.success,
            "message": result.message or ("Registration successful" if result.success else "Registration failed"),
            "data": {
                "executable_path": result.executable_path,
                "version": result.version,
            },
            "error_category": result.error_category if not result.success else None,
        }
