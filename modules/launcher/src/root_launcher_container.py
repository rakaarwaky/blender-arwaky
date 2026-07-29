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
import os
import signal
import subprocess

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

    # ─── Real OS seams (default; overridable in tests) ──────
    @staticmethod
    def _real_runner(args: list[str], timeout: float = 5.0) -> tuple[int, str]:
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        return proc.returncode, proc.stdout

    @staticmethod
    def _real_spawn(executable: str, mode: str, readiness_timeout_seconds: float) -> int:  # noqa: ARG004 (interface signature match; timeout handled by readiness probe)
        args = [executable]
        if mode == "headless":
            args += ["--background", "--python-exit-code", "1"]
        proc = subprocess.Popen(args)
        return proc.pid

    @staticmethod
    def _real_probe(process_id: int, timeout_seconds: float) -> bool:
        import time

        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            if not LauncherContainer._real_alive(process_id):
                return False
            time.sleep(0.2)
        return True

    @staticmethod
    def _real_alive(process_id: int) -> bool:
        if process_id is None:
            return False
        try:
            os.kill(process_id, 0)
            return True
        except OSError:
            return False

    @staticmethod
    def _real_signal(process_id: int) -> bool:
        try:
            os.kill(process_id, signal.SIGTERM)
            return True
        except OSError:
            return False

    @staticmethod
    def _real_kill(process_id: int) -> bool:
        try:
            os.kill(process_id, signal.SIGKILL)
            return True
        except OSError:
            return False

    def wire(self) -> None:
        """Wire the five launcher capabilities to the orchestrator."""
        if self._wired:
            return

        logger.info("Wiring launcher feature module")

        status_cap: RuntimeStatusProtocol = RuntimeStatusChecker(
            liveness_checker=self._real_alive,
            pid_resolver=self._resolve_active_pid,
            bridge_probe=self._real_probe,
            persisted_state_resolver=lambda: None,
        )

        locate_cap: LocateRegisterProtocol = ExecutableLocator(
            config_provider=lambda: self._config,
            command_runner=self._real_runner,
        )
        launch_cap: LaunchProtocol = ProcessLauncher(
            executable_resolver=lambda: self._config.executable_path,
            status_protocol=status_cap,
            spawner=self._real_spawn,
            readiness_probe=self._real_probe,
        )
        shutdown_cap: ShutdownProtocol = ProcessShutdown(
            status_protocol=status_cap,
            signal_sender=self._real_signal,
            killer=self._real_kill,
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

    def _resolve_active_pid(self) -> int | None:
        """Resolve active process PID from config or persisted state."""
        if self._state_path:
            persist_cap = StatePersistence(path_resolver=lambda: self._state_path)
            state = persist_cap.load()
            if state and state.process_id is not None:
                return state.process_id
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
