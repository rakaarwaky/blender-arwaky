from typing import Any

from modules.shared.src.cli.taxonomy_cli_vo import CliResultVo
from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate


def handle(_args: Any, launcher: ILauncherOperateAggregate | None = None) -> CliResultVo:
    if launcher is None:
        return CliResultVo(success=False, error="Launcher aggregate not available", category="configuration_error", ref="cli-500")
    try:
        outcome = launcher.shutdown(force=False, allow_escalation=True)
        if outcome.success:
            return CliResultVo(success=True, message="Blender closed")
        return CliResultVo(success=False, error=outcome.error or "Shutdown failed", category="state", ref="cli-close")
    except Exception as exc:
        return CliResultVo(success=False, error=str(exc), category="unexpected", ref="cli-close")
