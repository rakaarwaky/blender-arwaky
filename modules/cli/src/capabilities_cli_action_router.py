"""Execution adapter used by the CLI-backed dispatcher composition root."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass

from modules.shared.src.cli.capabilities_cli_registry import Registry
from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    BridgeEndpointVO,
    LauncherConfigVO,
    LaunchMode,
    LaunchRequestVO,
    ProbeDepth,
)


class CliActionRouter:
    """Route launcher actions locally and Blender actions over the active TCP bridge."""

    _LAUNCHER_ACTIONS = {
        "launch_blender",
        "shutdown_blender",
        "get_runtime_status",
        "register_executable",
    }

    def __init__(self, launcher: object) -> None:
        self._launcher = launcher

    def execute_action(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name in self._LAUNCHER_ACTIONS:
            return self._execute_launcher(action_name, params)

        wire_action = "execute_code" if action_name == "execute_blender_code" else action_name
        with BlenderSocketClient(port=Registry().get_port()) as client:
            response = client.send_command(wire_action, params)
        if response.get("status") != "success":
            raise RuntimeError(str(response.get("message", f"Action failed: {action_name}")))
        result = response.get("result", {})
        return result if isinstance(result, dict) else {"result": result}

    def _execute_launcher(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name == "launch_blender":
            mode = LaunchMode(str(params.get("mode", LaunchMode.HEADLESS.value)))
            port = int(params.get("port", 9876))
            filepath = params.get("filepath")
            request = LaunchRequestVO(
                filepath=str(filepath) if filepath else None,
                mode=mode,
                bridge_endpoint=BridgeEndpointVO(port=port),
            )
            result = self._launcher.launch(request)
        elif action_name == "shutdown_blender":
            result = self._launcher.shutdown(force=bool(params.get("force", False)))
        elif action_name == "get_runtime_status":
            result = self._launcher.check_status(depth=ProbeDepth.FULL)
        else:
            path = params.get("path")
            result = self._launcher.locate_and_register(
                LauncherConfigVO(),
                str(path) if path else None,
            )
        if is_dataclass(result):
            return asdict(result)
        return result if isinstance(result, dict) else {"result": result}
