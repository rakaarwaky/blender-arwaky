"""Root: Launcher feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
launcher module: Capabilities → Agent Orchestrator → (exposed as LauncherOrchestrator).

This file is the composition root for the launcher feature. It instantiates
the five launcher capabilities (with real OS seams by default, injectable for
tests), connects them to the aggregate facade, and provides the assembled
orchestrator for dependency injection by callers.
"""

from __future__ import annotations

import logging
import time

from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.contract_locate_register_protocol import LocateRegisterProtocol
from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
)

from .agent_launcher_orchestrator import LauncherOrchestrator
from .capabilities_executable_locator import ExecutableLocator
from .capabilities_process_launcher import ProcessLauncher
from .capabilities_process_shutdown import ProcessShutdown
from .capabilities_runtime_status import RuntimeStatusChecker
from .capabilities_state_persistence import StatePersistence
from modules.shared.src.launcher.utility_process_ops import (
    process_alive,
    process_kill,
    process_probe_readiness,
    process_signal_term,
    process_spawn,
    process_version_check,
)

logger = logging.getLogger("BlenderMCPServer")


class LauncherContainer:
    """Dependency injection container for the launcher feature module.

    Wires the five launcher capabilities to the aggregate orchestrator.
    """

    def __init__(self, config: LauncherConfigVO | None = None, state_path: str | None = None) -> None:
        self._config = config or LauncherConfigVO()
        self._state_path = state_path
        self._orchestrator: LauncherOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        """Wire the five launcher capabilities to the orchestrator."""
        if self._wired:
            return

        logger.info("Wiring launcher feature module")

        status_cap: RuntimeStatusProtocol = RuntimeStatusChecker(
            liveness_checker=process_alive,
            pid_resolver=self._resolve_active_pid,
            bridge_probe=None,
            persisted_state_resolver=self._load_persisted_status,
        )

        # Track launch time for uptime calculation (FR-LAU-004)
        status_cap.mark_launched(time.monotonic())

        locate_cap: LocateRegisterProtocol = ExecutableLocator(
            config_provider=lambda: self._config,
            command_runner=lambda args, timeout=5.0: process_version_check(args, timeout),
        )
        launch_cap: LaunchProtocol = ProcessLauncher(
            executable_resolver=lambda: self._config.executable_path,
            status_protocol=status_cap,
            spawner=lambda executable, mode, _timeout: process_spawn(executable, mode),
            readiness_probe=lambda pid, timeout: process_probe_readiness(pid, timeout),
        )
        shutdown_cap: ShutdownProtocol = ProcessShutdown(
            status_protocol=status_cap,
            signal_sender=process_signal_term,
            killer=process_kill,
            timeout_seconds=self._config.shutdown_timeout_seconds,
            force_enabled=self._config.force_termination_enabled,
        )
        persist_cap: PersistStateProtocol = StatePersistence(
            path_resolver=lambda: self._state_path,
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

    def _load_persisted_status(self) -> dict | None:
        """Load persisted runtime state for status resolution.

        Returns dict with process_id or None if no state/missing/corrupt.
        """
        if not self._state_path:
            return None
        try:
            import json
            import os as _os

            with open(self._state_path, encoding="utf-8") as fh:
                data = json.load(fh)
            if not isinstance(data, dict):
                return None
            pid = data.get("process_id")
            return {"process_id": pid} if pid else None
        except (OSError, json.JSONDecodeError, ValueError):
            return None

    def _resolve_active_pid(self) -> int | None:
        """Resolve active process PID from persisted state."""
        status = self._load_persisted_status()
        if status and isinstance(status.get("process_id"), int):
            return status["process_id"]
        return None

    @property
    def agent(self) -> LauncherOrchestrator:
        """Return the assembled launcher orchestrator facade.

        Must call wire() first, or this property will raise RuntimeError.
        """
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("LauncherContainer not wired — call wire() first")
        return self._orchestrator


def create_launcher_feature(
    config: LauncherConfigVO | None = None,
    state_path: str | None = None,
) -> LauncherOrchestrator:
    """Factory function to create and wire the launcher feature module."""
    container = LauncherContainer(config=config, state_path=state_path)
    container.wire()
    return container.agent
