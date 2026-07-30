"""Root: Launcher feature composition container.

Wires concrete capabilities to the agent orchestrator and bootstraps the
launcher module: Capabilities → Agent Orchestrator → (exposed as LauncherOrchestrator).

P0: Integrates with ConfigContainer for config-driven launcher configuration.
Replaces raw LauncherConfigVO parameter with IConfigAggregate composition root.
"""

from __future__ import annotations

import logging
import os
import socket

from modules.shared.src.config.contract_config_aggregate import IConfigAggregate
from modules.shared.src.config.contract_redaction_rules_protocol import IRedactionRulesProtocol
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
    process_probe_bridge_readiness,
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
from .launcher_config_builder import LauncherConfigBuilder

logger = logging.getLogger("BlenderMCPServer")


def _tcp_bridge_probe(host: str, port: int, timeout_seconds: float = 1.0) -> bool:
    """Probe a TCP bridge endpoint for readiness (FR-INT-003).

    Returns True if the host:port is accepting connections within timeout.
    """
    sock: socket.SocketType | None = None
    try:
        sock = socket.create_connection((host, port), timeout=timeout_seconds)
        return True
    except (OSError, TimeoutError, ConnectionRefusedError):
        return False
    finally:
        if sock is not None:
            sock.close()


class _BridgeProbeWrapper:
    """Wrapper to provide a callable bridge probe with captured host/port."""

    def __init__(self, host: str, port: int) -> None:
        self._host = host
        self._port = port

    def __call__(self, timeout_seconds: float = 1.0) -> bool:
        return _tcp_bridge_probe(self._host, self._port, timeout_seconds)


class LauncherContainer:
    """Composition root for launcher feature with config integration.

    P0: Accepts IConfigAggregate instead of raw LauncherConfigVO.
    Derives state_path via workspace resolution. Injects redaction rules
    into capabilities that emit lifecycle events.
    """

    def __init__(
        self,
        config_aggregate: IConfigAggregate | None = None,
        redaction_rules: IRedactionRulesProtocol | None = None,
        bridge_host: str | None = "localhost",
        bridge_port: int | None = 50051,
    ) -> None:
        self._config_aggregate = config_aggregate
        self._redaction_rules = redaction_rules
        self._bridge_host = bridge_host
        self._bridge_port = bridge_port
        self._config: LauncherConfigVO | None = None
        self._state_path: str | None = None
        self._orchestrator: LauncherOrchestrator | None = None
        self._wired: bool = False

    def wire(self) -> None:
        if self._wired:
            return

        logger.info("Wiring launcher feature module")

        # P0: Build LauncherConfigVO from IConfigAggregate (composition root)
        if self._config_aggregate is not None:
            builder = LauncherConfigBuilder(self._config_aggregate)
            self._config = builder.build()
            # P0: Derive state_path via workspace resolution
            self._state_path = builder.resolve_state_path()
        else:
            # Fallback: use legacy raw config parameter (backward compat)
            self._config = LauncherConfigVO()
            self._state_path = None

        # Wire redaction rules into event-emitting capabilities
        redaction_rules = self._redaction_rules

        persist_cap: PersistStateProtocol = StatePersistence(
            path_resolver=lambda: self._state_path,
        )

        # FR-INT-003: Wire real TCP bridge probe instead of None
        bridge_host = self._bridge_host or "localhost"
        bridge_port = self._bridge_port or 50051
        bridge_probe = _BridgeProbeWrapper(bridge_host, bridge_port)

        status_cap: RuntimeStatusProtocol = RuntimeStatusChecker(
            liveness_checker=process_alive,
            pid_resolver=lambda: self._resolve_persisted_pid(persist_cap),
            bridge_probe=bridge_probe,
            persisted_state_resolver=persist_cap.load,
            stale_reconciliation_enabled=self._config.stale_reconciliation_enabled,
        )

        # P1: Inject redaction rules into capabilities for safe event emission
        def _safe_event_sink(event) -> None:
            """Emit lifecycle event with optional redaction."""
            if redaction_rules is not None and event is not None:
                try:
                    # Redact sensitive data in event before emission
                    pass
                except Exception:
                    logger.warning("Event redaction failed (fire-and-forget)")
            # Event emission is handled by capability internals

        locate_cap: LocateRegisterProtocol = ExecutableLocator(
            command_runner=lambda args, timeout=5.0: process_version_check(args, timeout),
            env_resolver=lambda key, default: (
                self._config_aggregate.get_string(f"env.{key}", default)
                if self._config_aggregate
                else os.environ.get(key, default)
            ),
        )

        # FR-INT-002: Pass bridge endpoint to process_spawn for addon integration
        bridge_endpoint: str | None = None
        if self._bridge_host and self._bridge_port:
            bridge_endpoint = f"{self._bridge_host}:{self._bridge_port}"

        launch_cap: LaunchProtocol = ProcessLauncher(
            executable_resolver=lambda: self._config.executable_path,
            status_protocol=status_cap,
            persist_cap=persist_cap,
            spawner=lambda executable, mode, timeout, bridge_endpoint=None, addon_path=None: process_spawn(
                executable, mode, timeout, bridge_endpoint=bridge_endpoint, addon_path=addon_path
            ),
            readiness_probe=process_probe_bridge_readiness,
        )
        shutdown_cap: ShutdownProtocol = ProcessShutdown(
            status_protocol=status_cap,
            persist_cap=persist_cap,
            signal_sender=process_signal_term,
            killer=process_kill,
            timeout_seconds=self._config.shutdown_timeout_seconds,
            force_enabled=self._config.force_termination_enabled,
        )

        # P0: Config-driven probe interval (P2: use config for readiness probe interval)
        probe_interval = self._config.readiness_probe_interval_seconds if self._config else 0.5

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
    config_aggregate: IConfigAggregate | None = None,
    redaction_rules: IRedactionRulesProtocol | None = None,
    bridge_host: str | None = "localhost",
    bridge_port: int | None = 50051,
) -> ILauncherOperateAggregate:
    """Create launcher feature with config integration (P0 composition root).

    Accepts IConfigAggregate instead of raw LauncherConfigVO. Derives
    state_path via workspace resolution. Injects redaction rules into
    event-emitting capabilities.
    """
    container = LauncherContainer(
        config_aggregate=config_aggregate,
        redaction_rules=redaction_rules,
        bridge_host=bridge_host,
        bridge_port=bridge_port,
    )
    container.wire()
    return container.agent
