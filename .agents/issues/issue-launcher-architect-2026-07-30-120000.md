File: `.agents/issues/issue-launcher-architect-2026-07-30-120000.md`

```markdown
# Issue: launcher — Architectural Review & Refactoring

## Summary
The `launcher` feature has a mostly correct AES layer split: shared taxonomy/contract files, five capability implementations, one agent orchestrator, and one root container. However, the current implementation contains several architectural defects that affect safety, contract correctness, and FRD compliance. The most urgent problems are typed-contract mismatches in runtime status resolution, primitive types leaking into contract signatures, root-layer technical parsing, and capability/root seams that do not implement the FRD’s readiness, registration, persistence, and stale-reconciliation requirements. This issue should be addressed before the launcher module is treated as production-ready or consumed by diagnostics/CLI/MCP surfaces.

## Findings by Category

### Layer Boundaries
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `RuntimeStatusChecker` expects a persisted-state resolver returning `RuntimeStatusVO or None`, but the root container supplies `_load_persisted_status`, which returns `dict or None`. The stale-detection path accesses `persisted.process_id`, which can raise `AttributeError` at runtime. | `modules/launcher/src/root_launcher_container.py:LauncherContainer._load_persisted_status`, `modules/launcher/src/capabilities_runtime_status.py:RuntimeStatusChecker.check_status` | Remove JSON parsing from root. Create `StatePersistence` first and inject `persist_cap.load` or a VO-returning resolver. Update `RuntimeStatusChecker` to depend on `RuntimeStateVO or None`. |
| 2 | 🔴 CRITICAL | `ProcessShutdown._wait_exit` calls `check_status(depth="lightweight")` using a primitive string instead of `ProbeDepth.LIGHTWEIGHT`. This violates the contract type and can fail when status event emission uses `depth.value`. | `modules/launcher/src/capabilities_process_shutdown.py:ProcessShutdown._wait_exit` | Use `ProbeDepth.LIGHTWEIGHT`. |
| 3 | 🟡 WARNING | Root calls `status_cap.mark_launched(...)`, but `mark_launched` is not declared on `RuntimeStatusProtocol`. The root layer is coupling to a concrete capability method outside the contract abstraction. | `modules/launcher/src/root_launcher_container.py:LauncherContainer.wire` | Either add an explicit contract method, or replace mutable `mark_launched` with an injected launch-time resolver sourced from persisted state. |
| 4 | 🟡 WARNING | Root contains technical parsing and file I/O in `_load_persisted_status`. Root should only compose dependencies, not parse JSON or read files. | `modules/launcher/src/root_launcher_container.py:LauncherContainer._load_persisted_status` | Delegate persistence reads to `StatePersistence` or a utility/repository seam. |
| 5 | 🟡 WARNING | `ExecutableLocator` performs low-level filesystem mechanics directly: `os.path.exists`, `os.path.isfile`, `os.access`, `shutil.which`. Technical mechanics should be isolated in Utility so capabilities remain expressive and testable. | `modules/launcher/src/capabilities_executable_locator.py:ExecutableLocator._build_candidate_order`, `ExecutableLocator._validate` | Extract filesystem discovery/validation mechanics to utility functions, then inject or call them from the capability. |
| 6 | 🟡 WARNING | `LauncherOrchestrator.status` exposes a capability protocol that is not part of `ILauncherOperateAggregate`. `LauncherContainer.agent` also returns concrete `LauncherOrchestrator`, encouraging consumers to bypass the aggregate contract. | `modules/launcher/src/agent_launcher_orchestrator.py:LauncherOrchestrator.status`, `modules/launcher/src/root_launcher_container.py:LauncherContainer.agent` | If health/status access is a public feature, add it to the aggregate contract. Otherwise hide it. Return `ILauncherOperateAggregate` from the container. |
| 7 | 🟢 INFO | Agent orchestrator uses logging. Agent should be orchestration-only; observability should preferably flow through domain events or diagnostics. | `modules/launcher/src/agent_launcher_orchestrator.py` | Keep agent logging minimal or move lifecycle observability to events/diagnostics. |

### Naming Convention
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟢 INFO | `capabilities_runtime_status.py` names a concept/status, not a capability role. The implementation class is `RuntimeStatusChecker`. | `modules/launcher/src/capabilities_runtime_status.py` | Rename to `capabilities_runtime_status_checker.py` to match role naming guidance. |
| 2 | 🟢 INFO | `capabilities_process_shutdown.py` uses a concept suffix. The role is closer to executor/terminator. | `modules/launcher/src/capabilities_process_shutdown.py` | Optionally rename to `capabilities_process_shutdown_executor.py` if suffix policy allows. |
| 3 | 🟢 INFO | `utility_process_ops.py` uses vague suffix `ops`. | `modules/shared/src/launcher/utility_process_ops.py` | Consider a more explicit role suffix such as `utility_process_executor.py` or `utility_process_adapter.py`. |

### Dead Code / Orphan
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | Several launcher constants are unused: `LAUNCHER_DISCOVERY_ORDER`, default timeout constants, mode string constants, and termination string constants. Meanwhile capabilities and VOs duplicate the same values as literals. | `modules/shared/src/launcher/taxonomy_launcher_constant.py` | Use the constants in capabilities/VOs/config defaults, or remove unused constants. |
| 2 | 🟡 WARNING | Unused VOs exist: `StatusCheckOutcomeVO`, `StatePersistenceOutcomeVO`. | `modules/shared/src/launcher/taxonomy_launcher_vo.py` | Remove unused VOs or adopt them in contracts/capabilities. |
| 3 | 🟡 WARNING | Most launcher error types are unused: `BlenderNotRunningError`, `StateError`, `LauncherConfigError`, `LaunchTimeoutError`, `ShutdownTimeoutError`, `LaunchError`, `TerminationError`. Only `ExecutableValidationError` is used. | `modules/shared/src/launcher/taxonomy_launcher_error.py` | Use typed domain errors for FRD error categories or remove unused errors. |
| 4 | 🟢 INFO | `PersistStateProtocol.load` is implemented but not consumed by root, agent, or status resolution. | `modules/shared/src/launcher/contract_persist_state_protocol.py`, `modules/launcher/src/capabilities_state_persistence.py` | Wire `load()` into PID resolution/stale reconciliation or remove it if not required. |
| 5 | 🟢 INFO | `LauncherLifecycleEvent.duration_ms` is rarely populated by emitters. | `modules/shared/src/launcher/taxonomy_launcher_event.py`, capability emitters | Populate duration metadata consistently or remove the field. |

### Scalability & Coupling
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | The orchestrator methods are thin one-to-one delegations. Launch does not persist runtime state, shutdown does not persist stopped state, and locate does not persist registration. This weakens the agent’s coordination role and FR-LAU integration. | `modules/launcher/src/agent_launcher_orchestrator.py` | Make the agent orchestrate multi-capability flows: locate → register → persist, launch → status → persist, shutdown → persist. |
| 2 | 🟡 WARNING | `ExecutableLocator._register` attempts to call `set_executable_path` on the config provider callable, not on the config object. Registration is therefore not applied or persisted in the current wiring. | `modules/launcher/src/capabilities_executable_locator.py:ExecutableLocator._register` | Inject a configuration/repository protocol capable of persisting the registered executable path. |
| 3 | 🟡 WARNING | Default readiness probe `process_probe_readiness` only checks OS process liveness. FR-LAU-002 requires readiness to mean process liveness plus bridge/integration readiness. | `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness`, `modules/launcher/src/root_launcher_container.py` | Implement a real bridge readiness probe or clearly rename the current function to liveness-only and inject a real readiness seam. |
| 4 | 🟡 WARNING | `process_spawn` does not activate the integration component or pass bridge endpoint settings. It only spawns Blender with optional headless flags. | `modules/shared/src/launcher/utility_process_ops.py:process_spawn` | Add launch arguments and bridge configuration required by FR-LAU-002 while keeping the utility stateless. |
| 5 | 🟡 WARNING | Version compatibility checking is placeholder logic: non-empty version becomes `SUPPORTED`, empty becomes `UNKNOWN`. The configured supported range is ignored. | `modules/launcher/src/capabilities_executable_locator.py:ExecutableLocator._check_compatibility` | Implement deterministic version parsing and comparison, preferably using utility functions and taxonomy constants/VOs. |
| 6 | 🟡 WARNING | `process_alive` docstring says EPERM should be treated as alive, but the code returns `False`. This can misclassify permission-denied processes as dead. | `modules/shared/src/launcher/utility_process_ops.py:process_alive` | Return `True` for EPERM or introduce a tri-state liveness result: alive, dead, unknown. |
| 7 | 🟢 INFO | `StatePersistence.load` silently returns `None` on corrupt/unreadable state. FR-LAU-005 expects corruption-safe recovery with warning. | `modules/launcher/src/capabilities_state_persistence.py:StatePersistence._load_impl` | Emit a warning/event or return a result VO containing reconciliation warnings. |

### Data Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Typed data flow is broken between root and runtime status: root supplies a dictionary where a VO is expected. This makes stale detection unsafe and bypasses the persistence contract. | `modules/launcher/src/root_launcher_container.py`, `modules/launcher/src/capabilities_runtime_status.py` | Standardize on `RuntimeStateVO` from `PersistStateProtocol.load`. |
| 2 | 🟡 WARNING | Executable registration emits a lifecycle event with `state_after=RUNNING_READY`, even though registration does not launch Blender. | `modules/launcher/src/capabilities_executable_locator.py:ExecutableLocator._emit_registered` | Use `RuntimeState.NOT_RUNNING` or a registration-specific event payload that does not imply a running process. |
| 3 | 🟡 WARNING | Uptime tracking starts when the container is wired because root calls `mark_launched(time.monotonic())`. This is not the actual Blender launch time. | `modules/launcher/src/root_launcher_container.py:LauncherContainer.wire` | Record launch time after successful launch, preferably from persisted runtime state or launch outcome. |
| 4 | 🟡 WARNING | Launch idempotency returns `success=True` for `RUNNING_UNRESPONSIVE` and `STARTING` states without expressing degraded policy. FR-LAU-002 requires distinguishing spawned from ready and handling alive-but-not-ready cases. | `modules/launcher/src/capabilities_process_launcher.py:ProcessLauncher.launch` | Return explicit degraded/failure semantics based on policy, or ensure callers can safely interpret `success` plus `ready`. |
| 5 | 🟢 INFO | Shutdown during launch does not explicitly resolve or coordinate launch state first. | `modules/launcher/src/capabilities_process_shutdown.py` | Introduce a small lifecycle state machine or coordinate with status/launch state before termination. |

## Violations
- AES402: primitive contract signatures. `readiness_timeout_seconds: float or None` appears in `LaunchProtocol` and `ILauncherOperateAggregate`. `override: str or None` appears in `LocateRegisterProtocol` and `ILauncherOperateAggregate`. Domain values should use taxonomy VOs.
- AES401: primitive field in taxonomy event. `LauncherLifecycleEvent.duration_ms: float` should use a VO such as `DurationMs`.
- AES405 / architecture role expectation: agent orchestration is currently single-capability passthrough for each operation; it does not coordinate persistence/status with launch/shutdown/locate flows.
- AES501-like orphan/dead taxonomy symbols: unused constants, unused VOs, and unused error types exist in the shared launcher taxonomy.
- Architecture root-layer rule violation: root performs technical parsing and file I/O in `_load_persisted_status`.
- Architecture contract abstraction issue: root calls `RuntimeStatusChecker.mark_launched`, which is not part of `RuntimeStatusProtocol`.

## Action Items (For Developer)
- [ ] P0 Fix `RuntimeStatusChecker` persisted-state resolver to return `RuntimeStateVO or None`, not `dict or None`.
- [ ] P0 Remove JSON/file parsing from `root_launcher_container.py`; delegate to `StatePersistence.load`.
- [ ] P0 Replace `depth="lightweight"` with `ProbeDepth.LIGHTWEIGHT` in `ProcessShutdown._wait_exit`.
- [ ] P0 Replace primitive contract types with taxonomy VOs: `TimeoutSeconds`, `FilePath` or `ExecutablePathOverride`.
- [ ] P0 Fix `LauncherLifecycleEvent.duration_ms` to use `DurationMs` VO.
- [ ] P1 Wire persistence into lifecycle flows: persist after registration, launch, shutdown, and stale reconciliation.
- [ ] P1 Replace placeholder readiness probing with real bridge readiness or clearly separate liveness from readiness.
- [ ] P1 Implement executable registration persistence and version compatibility checking.
- [ ] P1 Remove unused taxonomy VOs/errors/constants or adopt them in implementation.
- [ ] P1 Make `LauncherContainer.agent` return `ILauncherOperateAggregate`.
- [ ] P2 Extract filesystem discovery/validation mechanics from `ExecutableLocator` into Utility.
- [ ] P2 Rename `capabilities_runtime_status.py` to `capabilities_runtime_status_checker.py`.

## Proposed Fixes / Reference Code

### 1. Add launcher-specific primitive VOs

```python
# modules/shared/src/launcher/taxonomy_launcher_vo.py

from typing import NewType

TimeoutSeconds = NewType("TimeoutSeconds", float)
ProcessId = NewType("ProcessId", int)
ExecutablePathOverride = NewType("ExecutablePathOverride", str)
```

Alternatively, reuse `FilePath` from `modules/shared/src/common/taxonomy_core_vo.py` for executable path overrides.

---

### 2. Fix contract primitive leakage

```python
# modules/shared/src/launcher/contract_launch_protocol.py

from __future__ import annotations

from abc import ABC, abstractmethod

from .taxonomy_launcher_vo import (
    LaunchMode,
    LaunchOutcomeVO,
    TimeoutSeconds,
)


class LaunchProtocol(ABC):
    """Protocol interface for launching the Blender process with readiness wait."""

    @abstractmethod
    def launch(
        self,
        mode: LaunchMode = LaunchMode.INTERFACE,
        readiness_timeout_seconds: TimeoutSeconds | None = None,
    ) -> LaunchOutcomeVO:
        """Start Blender with the integration component active and confirm readiness."""
        ...
```

```python
# modules/shared/src/launcher/contract_locate_register_protocol.py

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import FilePath

from .taxonomy_launcher_vo import (
    LauncherConfigVO,
    RegistrationOutcomeVO,
)


class LocateRegisterProtocol(ABC):
    """Protocol interface for discovering and registering the Blender executable."""

    @abstractmethod
    def locate_and_register(
        self,
        config: LauncherConfigVO,
        override: FilePath | None = None,
    ) -> RegistrationOutcomeVO:
        """Discover, validate, and register a Blender executable per discovery order."""
        ...
```

```python
# modules/shared/src/launcher/contract_launcher_operate_aggregate.py

from __future__ import annotations

from abc import ABC, abstractmethod

from modules.shared.src.common.taxonomy_core_vo import FilePath

from .taxonomy_launcher_vo import (
    LauncherConfigVO,
    LaunchMode,
    LaunchOutcomeVO,
    PersistenceOutcomeVO,
    ProbeDepth,
    RegistrationOutcomeVO,
    RuntimeStateVO,
    RuntimeStatusVO,
    ShutdownOutcomeVO,
    TimeoutSeconds,
)


class ILauncherOperateAggregate(ABC):
    @abstractmethod
    def locate_and_register(
        self,
        config: LauncherConfigVO,
        override: FilePath | None = None,
    ) -> RegistrationOutcomeVO: ...

    @abstractmethod
    def launch(
        self,
        mode: LaunchMode = LaunchMode.INTERFACE,
        readiness_timeout_seconds: TimeoutSeconds | None = None,
    ) -> LaunchOutcomeVO: ...

    @abstractmethod
    def shutdown(
        self,
        force: bool = False,
        allow_escalation: bool = True,
    ) -> ShutdownOutcomeVO: ...

    @abstractmethod
    def check_status(
        self,
        depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT,
    ) -> RuntimeStatusVO: ...

    @abstractmethod
    def persist(
        self,
        state: RuntimeStateVO,
    ) -> PersistenceOutcomeVO: ...
```

---

### 3. Fix event primitive field

```python
# modules/shared/src/launcher/taxonomy_launcher_event.py

from __future__ import annotations

from dataclasses import dataclass

from modules.shared.src.common.taxonomy_core_vo import DurationMs

from .taxonomy_launcher_vo import RuntimeState


@dataclass(frozen=True)
class LauncherLifecycleEvent:
    event_category: str = ""
    state_before: RuntimeState = RuntimeState.NOT_RUNNING
    state_after: RuntimeState = RuntimeState.NOT_RUNNING
    process_reference: str = ""
    method: str = ""
    duration_ms: DurationMs = DurationMs(0.0)
    reason_summary: str = ""
```

---

### 4. Fix shutdown probe depth

```python
# modules/launcher/src/capabilities_process_shutdown.py

from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ProbeDepth,
    RuntimeState,
    ShutdownOutcomeVO,
    TerminationMethod,
)


class ProcessShutdown(ShutdownProtocol):
    def _wait_exit(self, _process_id: int) -> bool:
        deadline = time.monotonic() + self._timeout

        while time.monotonic() < deadline:
            st = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)

            if st.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
                return True

            time.sleep(0.05)

        return False
```

---

### 5. Fix runtime status persisted-state type

```python
# modules/launcher/src/capabilities_runtime_status.py

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Protocol

from modules.shared.src.launcher.contract_runtime_status_protocol import (
    RuntimeStatusProtocol,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ProbeDepth,
    RuntimeState,
    RuntimeStateVO,
    RuntimeStatusVO,
)


class RuntimeStatusChecker(RuntimeStatusProtocol):
    def __init__(
        self,
        liveness_checker: Callable[[int], bool],
        pid_resolver: Callable[[], int | None],
        bridge_probe: Callable[[float], bool] | None = None,
        persisted_state_resolver: Callable[[], RuntimeStateVO | None] = lambda: None,
        launch_time_resolver: Callable[[], float | None] = lambda: None,
        stale_reconciliation_enabled: bool = True,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None:
        self._is_alive = liveness_checker
        self._resolve_pid = pid_resolver
        self._bridge = bridge_probe
        self._resolve_persisted = persisted_state_resolver
        self._resolve_launch_time = launch_time_resolver
        self._stale_reconcile = stale_reconciliation_enabled
        self._events = event_sink

    def check_status(
        self,
        depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT,
    ) -> RuntimeStatusVO:
        pid = self._resolve_pid()

        if pid is None:
            return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, depth=depth)

        alive = self._is_alive(pid)

        if not alive:
            persisted = self._resolve_persisted()

            if persisted is not None and persisted.process_id == pid:
                if self._stale_reconcile:
                    self._emit_stale(pid)

                return RuntimeStatusVO(
                    state=RuntimeState.STALE,
                    process_id=pid,
                    stale=True,
                    depth=depth,
                )

            return RuntimeStatusVO(
                state=RuntimeState.NOT_RUNNING,
                process_id=pid,
                depth=depth,
            )

        ready = True

        if depth == ProbeDepth.FULL and self._bridge is not None:
            ready = self._bridge(1.0)

        state = RuntimeState.RUNNING_READY if ready else RuntimeState.RUNNING_UNRESPONSIVE

        launch_time = self._resolve_launch_time()
        uptime = (time.monotonic() - launch_time) if launch_time is not None else None

        return RuntimeStatusVO(
            state=state,
            process_id=pid,
            ready=ready,
            uptime_seconds=uptime,
            depth=depth,
        )
```

---

### 6. Remove technical parsing from root and wire persistence correctly

```python
# modules/launcher/src/root_launcher_container.py

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
from modules.shared.src.launcher.taxonomy_launcher_vo import LauncherConfigVO

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
    def __init__(
        self,
        config: LauncherConfigVO | None = None,
        state_path: str | None = None,
    ) -> None:
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

        def resolve_persisted_pid() -> int | None:
            state = persist_cap.load()
            return state.process_id if state is not None else None

        def resolve_launch_timestamp() -> float | None:
            state = persist_cap.load()
            return state.launch_timestamp if state is not None else None

        status_cap: RuntimeStatusProtocol = RuntimeStatusChecker(
            liveness_checker=process_alive,
            pid_resolver=resolve_persisted_pid,
            bridge_probe=None,
            persisted_state_resolver=persist_cap.load,
            launch_time_resolver=resolve_launch_timestamp,
        )

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

        self._orchestrator = LauncherOrchestrator(
            locate_register_cap=locate_cap,
            launch_cap=launch_cap,
            shutdown_cap=shutdown_cap,
            status_cap=status_cap,
            persist_cap=persist_cap,
        )

        self._wired = True
        logger.info("Launcher feature module wired successfully")

    @property
    def agent(self) -> ILauncherOperateAggregate:
        if not self._wired or self._orchestrator is None:
            raise RuntimeError("LauncherContainer not wired — call wire() first")

        return self._orchestrator
```

---

### 7. Make agent coordinate persistence after lifecycle operations

```python
# modules/launcher/src/agent_launcher_orchestrator.py

from modules.shared.src.launcher.taxonomy_launcher_vo import (
    RuntimeState,
    RuntimeStateVO,
)


class LauncherOrchestrator(ILauncherOperateAggregate):
    def launch(
        self,
        mode: LaunchMode = LaunchMode.INTERFACE,
        readiness_timeout_seconds: float | None = None,
    ) -> LaunchOutcomeVO:
        outcome = self._launch.launch(mode, readiness_timeout_seconds)

        if outcome.success and outcome.process_id is not None:
            state = RuntimeStateVO(
                executable_path="",
                process_id=outcome.process_id,
                launch_timestamp=0.0,
                bridge_endpoint=outcome.bridge_endpoint,
                last_status=(RuntimeState.RUNNING_READY if outcome.ready else RuntimeState.STARTING),
            )
            self._persist.persist(state)

        return outcome

    def shutdown(
        self,
        force: bool = False,
        allow_escalation: bool = True,
    ) -> ShutdownOutcomeVO:
        outcome = self._shutdown.shutdown(force, allow_escalation)

        if outcome.success:
            state = RuntimeStateVO(
                executable_path="",
                process_id=None,
                launch_timestamp=0.0,
                bridge_endpoint=None,
                last_status=outcome.final_state,
            )
            self._persist.persist(state)

        return outcome
```

The final implementation should source `executable_path`, `launch_timestamp`, and `bridge_endpoint` from capabilities or persisted state rather than using placeholders.

---

### 8. Use taxonomy constants instead of literals

```python
# modules/launcher/src/capabilities_process_launcher.py

from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_DEFAULT_LAUNCH_TIMEOUT_SECONDS,
)


class ProcessLauncher(LaunchProtocol):
    def launch(
        self,
        mode: LaunchMode = LaunchMode.INTERFACE,
        readiness_timeout_seconds: float | None = None,
    ) -> LaunchOutcomeVO:
        timeout = (
            readiness_timeout_seconds
            if readiness_timeout_seconds is not None
            else LAUNCHER_DEFAULT_LAUNCH_TIMEOUT_SECONDS
        )
        ...
```

```python
# modules/launcher/src/capabilities_process_shutdown.py

from modules.shared.src.launcher.taxonomy_launcher_constant import (
    LAUNCHER_DEFAULT_SHUTDOWN_TIMEOUT_SECONDS,
)


class ProcessShutdown(ShutdownProtocol):
    def __init__(
        self,
        status_protocol: RuntimeStatusProtocol,
        signal_sender: _SignalSender | None = None,
        killer: _ProcessKiller | None = None,
        timeout_seconds: float = LAUNCHER_DEFAULT_SHUTDOWN_TIMEOUT_SECONDS,
        force_enabled: bool = True,
        event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    ) -> None: ...
```

```
```
