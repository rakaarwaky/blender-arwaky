from typing import Any

from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate
from modules.shared.src.launcher.taxonomy_launcher_vo import LaunchMode, TimeoutSeconds


def handle(args: Any, launcher: ILauncherOperateAggregate | None = None) -> CliResultVo:
    if launcher is None:
        return CliResultVo(success=False, error="Launcher aggregate not available", category="configuration_error", ref="cli-500")
    try:
        mode = LaunchMode.HEADLESS if args.mode == "headless" else LaunchMode.INTERFACE
        timeout = TimeoutSeconds(float(getattr(args, "timeout", 30)))
        outcome = launcher.launch(mode=mode, readiness_timeout_seconds=timeout)
        if outcome.success:
            return CliResultVo(success=True, message="Blender session started", data={"pid": outcome.process_id, "bridge_endpoint": outcome.bridge_endpoint})
        return CliResultVo(success=False, error=outcome.error or "Launch failed", category="timeout" if outcome.error and "timeout" in outcome.error.lower() else "upstream_error", ref="cli-init")
    except Exception as exc:
        return CliResultVo(success=False, error=str(exc), category="unexpected", ref="cli-init")
