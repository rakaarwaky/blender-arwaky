"""Root: Launcher feature composition container.

Wires the five launcher capabilities to their protocol contracts and the
LauncherOrchestrator aggregate. This is the composition root — it instantiates
concrete capabilities and injects DI seams, but contains no business logic.

FRD: modules/launcher/FRD.md (FR-LAU-001..005)
"""

from __future__ import annotations

import logging

from modules.launcher.src.agent_launcher_orchestrator import LauncherOrchestrator
from modules.launcher.src.capabilities_launch_executor import LaunchExecutor
from modules.launcher.src.capabilities_locate_register_executor import LocateRegisterExecutor
from modules.launcher.src.capabilities_runtime_status import RuntimeStatusChecker
from modules.launcher.src.capabilities_shutdown_executor import ShutdownExecutor
from modules.launcher.src.capabilities_state_persistence import StatePersistence
from modules.shared.src.launcher.contract_launcher_operate_aggregate import LauncherOperateAggregate
from modules.shared.src.launcher.taxonomy_launcher_vo import LauncherConfigVO

logger = logging.getLogger("BlenderMCPServer")


class LauncherContainer:
    """Composition root for the launcher feature.

    Assembles capabilities + orchestrator. Production seams (process spawning,
    OS signalling) use real defaults; tests pass injected seams instead.
    """

    def __init__(self, config: LauncherConfigVO | None = None) -> None:
        self._config = config or LauncherConfigVO()
        self._build()

    def _build(self) -> None:
        self.locate_register = LocateRegisterExecutor()
        self.launch = LaunchExecutor(
            executable_resolver=lambda: self._config.executable_path or "blender",
        )
        self.shutdown = ShutdownExecutor(
            shutdown_timeout_seconds=self._config.shutdown_timeout_seconds,
            force_enabled=self._config.force_termination_enabled,
        )
        self.status = RuntimeStatusChecker()
        self.persist = StatePersistence(
            path_resolver=lambda: self._config.state_persistence_location,
        )
        self.orchestrator = LauncherOrchestrator(
            locate_register=self.locate_register,
            launch=self.launch,
            shutdown=self.shutdown,
            status=self.status,
            persist=self.persist,
            config=self._config,
        )

    def get_feature(self) -> LauncherOperateAggregate:
        """Return the aggregate facade for surface consumption."""
        return self.orchestrator


def create_launcher_feature(config: LauncherConfigVO | None = None) -> LauncherOperateAggregate:
    """Factory: build the launcher feature aggregate.

    This is the single public entry point consumed by CLI/MCP surfaces and the
    test suite.
    """
    return LauncherContainer(config).get_feature()
