"""Launcher feature orchestrator implementing LauncherOperateAggregate.

FR-LAU-001: Locate and Register Application — locate() finds Blender executable path
FR-LAU-002: Launch Application — launch() spawns Blender process with mode configuration
FR-LAU-003: Shut Down Application — shutdown() terminates Blender gracefully
FR-LAU-004: Check Runtime Status — status() returns current runtime state
FR-LAU-005: Persist Runtime State — persist() saves runtime state to registry

Coordinates the 5 launcher operations through the individual capability
protocols. Implements LauncherOperateAggregate.

Orchestration only — no business logic; depends on individual capability
protocols. Wires the shared RuntimeStatusProtocol into the launcher and
shutdown capabilities so status is consistent across operations.
"""

from __future__ import annotations

import logging
import time

from modules.shared.src.common.taxonomy_core_vo import FilePath
from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate
from modules.shared.src.launcher.contract_locate_register_protocol import LocateRegisterProtocol
from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchOutcomeVO,
    LaunchRequestVO,
    PersistenceOutcomeVO,
    ProbeDepth,
    RegistrationOutcomeVO,
    RuntimeState,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownOutcomeVO,
)

logger = logging.getLogger("BlenderMCPServer")


class LauncherOrchestrator(ILauncherOperateAggregate):
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
    def locate_and_register(self, config: LauncherConfigVO, override: FilePath | None = None) -> RegistrationOutcomeVO:
        """Delegate executable location/registration to the capabilities layer."""
        logger.info("Orchestrating locate_and_register")
        return self._locate.locate_and_register(config, override)

    def launch(self, request: LaunchRequestVO | None = None) -> LaunchOutcomeVO:
        """Delegate launch and persist process state for later status/shutdown calls."""
        req = request or LaunchRequestVO()
        logger.info("Orchestrating launch (mode=%s)", req.mode.value)
        outcome = self._launch.launch(req)
        if outcome.success and outcome.process_id is not None:
            previous = self._persist.load()
            self._persist.persist(
                RuntimeStateVO(
                    executable_path=previous.executable_path if previous is not None else "",
                    process_id=outcome.process_id,
                    launch_timestamp=time.time(),
                    bridge_endpoint=outcome.bridge_endpoint,
                    last_status=RuntimeState.RUNNING_READY if outcome.ready else RuntimeState.STARTING,
                )
            )
        return outcome

    def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownOutcomeVO:
        """Delegate shutdown and persist the terminal runtime state."""
        logger.info("Orchestrating shutdown (force=%s)", force)
        outcome = self._shutdown.shutdown(force, allow_escalation)
        if outcome.success:
            previous = self._persist.load()
            self._persist.persist(
                RuntimeStateVO(
                    executable_path=previous.executable_path if previous is not None else "",
                    process_id=None,
                    launch_timestamp=previous.launch_timestamp if previous is not None else 0.0,
                    bridge_endpoint=previous.bridge_endpoint if previous is not None else None,
                    last_status=outcome.final_state,
                )
            )
        return outcome

    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """Delegate status check to the capabilities layer."""
        return self._status.check_status(depth)

    def persist(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """Delegate state persistence to the capabilities layer."""
        return self._persist.persist(state)

    # ─── Block 3: Dunder Methods, Factories & Helpers ─────
    @property
    def status(self) -> RuntimeStatusProtocol:
        """Expose the status capability for health composition consumers."""
        return self._status
