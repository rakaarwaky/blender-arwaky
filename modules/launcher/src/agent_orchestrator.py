"""Launcher orchestrator — Aggregate facade coordinating all 5 capabilities.

FR-LAU-001 through FR-LAU-005: Coordinates locate, launch, shutdown,
status check, and state persistence via individual protocol delegation.
"""

import logging

from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.contract_locate_register_protocol import (
    LocateRegisterProtocol,
)
from modules.shared.src.launcher.contract_runtime_status_protocol import (
    RuntimeStatusProtocol,
)
from modules.shared.src.launcher.contract_persist_state_protocol import (
    PersistStateProtocol,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    RegistrationResultVO,
    LaunchResultVO,
    ShutdownResultVO,
    StatusCheckResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class LauncherOrchestrator:
    """Aggregate facade for the Launcher feature.

    Coordinates all 5 launcher capabilities via protocol delegation.
    Implements the LauncherOperateAggregate interface pattern.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        locate_register: LocateRegisterProtocol,
        launch: LaunchProtocol,
        shutdown: ShutdownProtocol,
        status_check: RuntimeStatusProtocol,
        persist_state: PersistStateProtocol,
    ) -> None:
        self._locate_register = locate_register
        self._launch = launch
        self._shutdown = shutdown
        self._status_check = status_check
        self._persist_state = persist_state

    # ─── Block 2: Protocol Method Implementation ─────────────

    def locate_and_register(
        self,
        config: LauncherConfigVO,
        override: str | None = None,
    ) -> RegistrationResultVO:
        """FR-LAU-001: Locate, validate, and register Blender executable."""
        logger.info("Locating and registering Blender executable")
        result = self._locate_register.locate_and_register(config, override)
        logger.info("Registration complete: %s", result.source.value)

        # Persist the registered path for later use
        if result.registered and result.executable:
            self._persist_state.persist_state(
                process_id=None, ready=False, bridge_endpoint=None
            )

        return result

    def launch_blender(
        self,
        mode: str = "interface",
        readiness_timeout_seconds: float | None = None,
    ) -> LaunchResultVO:
        """FR-LAU-002: Launch Blender and wait for readiness.

        Loads persisted state first (idempotency check), then spawns.
        Updates runtime state after successful launch.
        """
        # Check persisted state for idempotency
        pid, ready, endpoint = self._persist_state.load_state()
        if ready and pid is not None:
            logger.info("Blender already running (restored pid=%d)", pid)
            self._status_check.update_runtime_state(pid, ready, endpoint)
            return LaunchResultVO(
                success=True, process_id=pid, ready=True,
                bridge_endpoint=endpoint, duration_ms=0.0, launch_method="existing",
            )

        logger.info("Launching Blender (mode=%s)", mode)
        result = self._launch.launch(mode, readiness_timeout_seconds)

        # Update runtime state after launch
        if result.success:
            self._status_check.update_runtime_state(
                result.process_id, result.ready, result.bridge_endpoint
            )
            self._persist_state.persist_state(
                result.process_id, result.ready, result.bridge_endpoint
            )

        return result

    def shutdown_blender(
        self,
        force: bool = False,
        allow_escalation: bool = True,
    ) -> ShutdownResultVO:
        """FR-LAU-003: Graceful shutdown with force escalation.

        Coordinates shutdown and clears persisted state on success.
        """
        logger.info("Shutting down Blender (force=%s)", force)
        result = self._shutdown.shutdown(force, allow_escalation)

        # Clear state on successful shutdown
        if result.success:
            self._shutdown.mark_stopped()
            self._status_check.update_runtime_state(None, False, None)
            self._persist_state.persist_state(None, False, None)

        return result

    def check_status(self) -> StatusCheckResultVO:
        """FR-LAU-004: Verify actual process liveness and classify state."""
        logger.debug("Checking runtime status")
        return self._status_check.check_status()

    def update_runtime_state(
        self,
        process_id: int | None,
        ready: bool,
        bridge_endpoint: str | None,
    ) -> None:
        """Coordinate state updates across all capabilities."""
        self._status_check.update_runtime_state(process_id, ready, bridge_endpoint)
        self._persist_state.persist_state(process_id, ready, bridge_endpoint)
