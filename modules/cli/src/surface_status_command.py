from typing import Any

from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate


def handle(_args: Any, launcher: ILauncherOperateAggregate | None = None) -> CliResultVo:
    if launcher is None:
        return CliResultVo(success=False, error="Launcher aggregate not available", category="configuration_error", ref="cli-500")
    try:
        status = launcher.check_status()
        return CliResultVo(success=True, data={"state": status.state.value, "pid": status.process_id, "ready": status.ready, "stale": status.stale})
    except Exception as exc:
        return CliResultVo(success=False, error=str(exc), category="unexpected", ref="cli-status")
