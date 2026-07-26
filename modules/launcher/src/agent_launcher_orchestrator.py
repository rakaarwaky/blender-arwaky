"""Agent: Launcher feature orchestrator.

Coordinates the five launcher capabilities (locate/register, launch, shutdown,
status, persist) into the LauncherOperateAggregate facade consumed by CLI/MCP
surfaces.

Structure (AES Agent layer):
  1. Constructor wiring (depends on contracts only)
  2. Aggregate facade methods — delegate to capabilities, coordinate shared state
  3. Dunder methods, factories, and helpers
"""

from __future__ import annotations

import logging

from modules.shared.src.launcher.contract_launcher_operate_aggregate import LauncherOperateAggregate
from modules.shared.src.launcher.contract_launch_protocol import LaunchProtocol
from modules.shared.src.launcher.contract_locate_register_protocol import LocateRegisterProtocol
from modules.shared.src.launcher.contract_persist_state_protocol import PersistStateProtocol
from modules.shared.src.launcher.contract_runtime_status_protocol import RuntimeStatusProtocol
from modules.shared.src.launcher.contract_shutdown_protocol import ShutdownProtocol
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchResultVO,
    PersistenceResultVO,
    RegistrationResultVO,
    RuntimeState,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownResultVO,
)

logger = logging.getLogger("BlenderMCPServer")


class LauncherOrchestrator(LauncherOperateAggregate):
    """Aggregate facade coordinating all launcher capabilities.

    Implements LauncherOperateAggregate (FR-LAU-001..005). Owns shared runtime
    state (active pid) and propagates it across capabilities; never contains
    business logic itself — it delegates to capabilities and coordinates.
    """

    # ─── Block 1: Class Definition & Constructor ──────────────

    def __init__(
        self,
        locate_register: LocateRegisterProtocol,
        launch: LaunchProtocol,
        shutdown: ShutdownProtocol,
        status: RuntimeStatusProtocol,
        persist: PersistStateProtocol,
        config: LauncherConfigVO | None = None,
    ) -> None:
        self._locate = locate_register
        self._launch = launch
        self._shutdown = shutdown
        self._status = status
        self._persist = persist
        self._config = config or LauncherConfigVO()

        # Shared runtime state — coordinated, not owned by a single capability.
        self._active_pid: int | None = None

    # ─── Block 2: Aggregate Facade Methods (delegate + coordinate) ──

    def locate_and_register(self, config: LauncherConfigVO, override: str | None = None) -> RegistrationResultVO:
        """FR-LAU-001: Delegate to LocateRegister capability."""
        return self._locate.locate_and_register(config, override)

    def launch(self, mode: str = "interface", readiness_timeout_seconds: float | None = None) -> LaunchResultVO:
        """FR-LAU-002: Launch and capture the active pid into shared state."""
        result = self._launch.launch(mode, readiness_timeout_seconds)
        if result.success and result.process_id is not None:
            self._active_pid = result.process_id
            if self._config.state_persistence_location:
                self._persist.persist(
                    RuntimeStateVO(
                        process_id=self._active_pid,
                        last_status=RuntimeState.RUNNING_READY,
                    )
                )
        return result

    def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownResultVO:
        """FR-LAU-003: Delegate to Shutdown capability; reconcile persisted state."""
        result = self._shutdown.shutdown(force, allow_escalation)
        if result.success:
            self._active_pid = None
        return result

    def check_status(self, depth: str = "lightweight") -> RuntimeStatusVO:
        """FR-LAU-004: Delegate to Status capability (reads true liveness)."""
        return self._status.check_status(depth)

    def persist(self, state: RuntimeStateVO) -> PersistenceResultVO:
        """FR-LAU-005: Delegate to Persist capability."""
        return self._persist.persist(state)

    # ─── Block 3: Dunder Methods, Factories & Helpers ──────────

    def load_persisted_state(self) -> RuntimeStateVO | None:
        """Load persisted runtime state (reconciliation entry point)."""
        return self._persist.load()

    def get_active_pid(self) -> int | None:
        return self._active_pid

    def __repr__(self) -> str:
        return (
            f"LauncherOrchestrator(active_pid={self._active_pid}, "
            f"locate={self._locate is not None}, launch={self._launch is not None}, "
            f"shutdown={self._shutdown is not None}, status={self._status is not None}, "
            f"persist={self._persist is not None})"
        )
