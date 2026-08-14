"""Execution adapter used by the CLI-backed dispatcher composition root."""

from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass

from modules.config.src.root_config_container import ConfigContainer
from modules.job.src.root_job_container import create_job_feature
from modules.shared.src.cli.capabilities_cli_registry import Registry
from modules.shared.src.common.taxonomy_core_vo import JobId
from modules.shared.src.gateway.capabilities_socket_client import BlenderSocketClient
from modules.shared.src.job.taxonomy_job_vo import CancellationReason, CancelTaskCommand
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
        self._job = create_job_feature()
        self._config = ConfigContainer().build()

    def execute_action(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name in self._LAUNCHER_ACTIONS:
            return self._execute_launcher(action_name, params)
        if action_name in {"get_task_status", "cancel_task"}:
            return self._execute_job(action_name, params)
        if action_name in {"get_config", "set_config"}:
            return self._execute_config(action_name, params)

        wire_action = "execute_code" if action_name == "execute_blender_code" else action_name
        with BlenderSocketClient(port=Registry().get_port()) as client:
            response = client.send_command(wire_action, params)
        if response.get("status") != "success":
            raise RuntimeError(str(response.get("message", f"Action failed: {action_name}")))
        result = response.get("result", {})
        return result if isinstance(result, dict) else {"result": result}

    def _execute_job(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        task_id = JobId(str(params.get("task_id", "")))
        if not str(task_id).strip():
            raise ValueError("task_id is required")
        if action_name == "get_task_status":
            return asdict(self._job.get_task_status(task_id))
        command = CancelTaskCommand(
            job_id=task_id,
            reason=CancellationReason(str(params.get("reason", "CLI cancellation"))),
        )
        result = self._job.cancel_task(command)
        if not result.accepted and result.outcome == "NOT_FOUND":
            raise LookupError(f"Task not found: {task_id}")
        return asdict(result)

    def _execute_config(self, action_name: str, params: dict[str, object]) -> dict[str, object]:
        if action_name == "get_config":
            key = str(params.get("key", ""))
            if key:
                value = self._config.get(key)
                return {"key": key, "value": self._config.redact_dict({key: value}).get(key)}
            return {"settings": self._config.redact_dict(self._config.get_snapshot().to_dict())}

        key = str(params.get("key", ""))
        if not key:
            raise ValueError("key is required")
        raw_value = params.get("value")
        if isinstance(raw_value, str):
            try:
                value = json.loads(raw_value)
            except json.JSONDecodeError:
                value = raw_value
        else:
            value = raw_value
        snapshot = self._config.set_config(key, value)
        return {"key": key, "value": self._config.redact_dict({key: snapshot.get(key)}).get(key)}

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
