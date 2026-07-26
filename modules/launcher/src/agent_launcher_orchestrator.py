"""Agent: Launcher feature orchestrator.

Coordinates the 5 launcher operations through the individual capability
protocols. Implements LauncherOperateAggregate.

Orchestration only — no business logic; depends on individual capability
protocols. Wires the shared RuntimeStatusProtocol into the launcher and
shutdown capabilities so status is consistent across operations.
"""

from __future__ import annotations

import logging

from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.contract_launcher_operate_aggregate import LauncherOperateAggregate
from modules.shared.src.launcher.contract_locate_register_protocol import LocateRegisterProtocol
from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchResultVO,
    PersistenceResultVO,
    RegistrationResultVO,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class LauncherOrchestrator(LauncherOperateAggregate):
    """Orchestrates launcher operations through 5 individual capability protocols."""

    # ─── Block 1: Class Definition & Constructor ──────────────
    def __init__(
        self,
        locate_register_cap: LocateRegisterProtocol,
        launch_cap: LaunchProtocol,
        shutdown_cap: ShutdownProtocol,
        status_cap: RuntimeStatusProtocol,
        persist_cap: PersistStateProtocol,
    ) -> None:
        self._locate = locate_register_cap
        self._launch = launch_cap
        self._shutdown = shutdown_cap
        self._status = status_cap
        self._persist = persist_cap

    # ─── Block 2: Aggregate Implementation ───────────────────
    def locate_and_register(self, config: LauncherConfigVO, override: str | None = None) -> RegistrationResultVO:
        """Delegate executable location/registration to the capabilities layer."""
        logger.info("Orchestrating locate_and_register")
        return self._locate.locate_and_register(config, override)

    def launch(self, mode: str = "interface", readiness_timeout_seconds: float | None = None) -> LaunchResultVO:
        """Delegate launch to the capabilities layer."""
        logger.info("Orchestrating launch (mode=%s)", mode)
        return self._launch.launch(mode, readiness_timeout_seconds)

    def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownResultVO:
        """Delegate shutdown to the capabilities layer."""
        logger.info("Orchestrating shutdown (force=%s)", force)
        return self._shutdown.shutdown(force, allow_escalation)

    def check_status(self, depth: str = "lightweight") -> RuntimeStatusVO:
        """Delegate status check to the capabilities layer."""
        return self._status.check_status(depth)

    def persist(self, state: RuntimeStateVO) -> PersistenceResultVO:
        """Delegate state persistence to the capabilities layer."""
        return self._persist.persist(state)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    @property
    def status(self) -> RuntimeStatusProtocol:
        """Expose the status capability for health composition consumers."""
        return self._status
