"""Root: Launcher feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
launcher module: Capabilities → Agent Orchestrator → (exposed as LauncherOrchestrator).
"""

from __future__ import annotations

import logging

from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.contract_launcher_operate_aggregate import (
    ILauncherOperateAggregate,
)
from modules.shared.src.launcher.contract_locate_register_protocol import (
    LocateRegisterProtocol,
)
from modules.shared.src.launcher.contract_persist_state_protocol import (
    PersistStateProtocol,
)
from modules.shared.src.launcher.contract_runtime_status_protocol import (
    RuntimeStatusProtocol,
)
from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
)
from modules.shared.src.launcher.utility_process_ops import (
    process_alive,
    process_kill,
    process_probe_readiness,
    process_signal_term,
    process_spawn,
    process_version_check,
)

from .agent_launcher_orchestrator import LauncherOrchestrator
from .capabilities_executable_locator import ExecutableLocator
from .capabilities_process_launcher import ProcessLauncher
from .capabilities_process_shutdown import ProcessShutdown
from .capabilities_runtime_status import RuntimeStatusChecker
from .capabilities_state_persistence import StatePersistence

logger = logging.getLogger("BlenderMCPServer")


class LauncherContainer:
    def __init__(self, config: LauncherConfigVO | None = None, state_path: str | None = None) -> None:
        self._config = config or LauncherConfigVO()
        self._state_path = state_path
        self._orchestrator: LauncherOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        if self._wired:
            return

        logger.info("Wiring launcher feature module")

        persist_cap: PersistStateProtocol = StatePersistence(
            path_resolver=lambda: self._state_path,
        )

        status_cap: RuntimeStatusProtocol = RuntimeStatusChecker(
            liveness_checker=process_alive,
            pid_resolver=lambda: self._resolve_persisted_pid(persist_cap),
            bridge_probe=None,
            persisted_state_resolver=persist_cap.load,
            stale_reconciliation_enabled=self._config.stale_reconciliation_enabled,
        )

        locate_cap: LocateRegisterProtocol = ExecutableLocator(
            config_provider=lambda: self._config,
            command_runner=lambda args, timeout=5.0: process_version_check(args, timeout),
        )
        launch_cap: LaunchProtocol = ProcessLauncher(
            executable_resolver=lambda: self._config.executable_path,
            status_protocol=status_cap,
            config_provider=lambda: self._config,
            spawner=lambda executable, mode, bridge_host, bridge_port, protocol_version: process_spawn(
                executable, mode, bridge_host, bridge_port, protocol_version
            ),
            readiness_probe=lambda pid, bridge_host, bridge_port, timeout: process_probe_readiness(
                pid, bridge_host, bridge_port, timeout
            ),
        )
        shutdown_cap: ShutdownProtocol = ProcessShutdown(
            status_protocol=status_cap,
            signal_sender=process_signal_term,
            killer=process_kill,
            timeout_seconds=self._config.shutdown_timeout_seconds,
            force_enabled=self._config.force_termination_enabled,
        )

        self._orchestrator = LauncherOrchestrator(
            locate_register_cap=locate_cap,
            launch_cap=launch_cap,
            shutdown_cap=shutdown_cap,
            status_cap=status_cap,
            persist_cap=persist_cap,
        )

        self._wired = True
        logger.info("Launcher feature module wired successfully")

    def _resolve_persisted_pid(self, persist_cap: PersistStateProtocol) -> int | None:
        state = persist_cap.load()
        return state.process_id if state is not None else None

    @property
    def agent(self) -> ILauncherOperateAggregate:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("LauncherContainer not wired — call wire() first")
        return self._orchestrator


def create_launcher_feature(
    config: LauncherConfigVO | None = None,
    state_path: str | None = None,
) -> ILauncherOperateAggregate:
    container = LauncherContainer(config=config, state_path=state_path)
    container.wire()
    return container.agent
