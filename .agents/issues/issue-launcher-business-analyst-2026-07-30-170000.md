.agents/issues/issue-launcher-business-analyst-2026-07-30-120000.md`

```markdown
# Issue: launcher — Business Logic & Requirements Review

## Summary
The Launcher module has a well-structured AES layering (taxonomy, contract, capabilities, agent, root), but its implementation does not yet satisfy several core FRD obligations. Executable registration is not actually persisted, launch does not activate the Blender integration component or verify bridge readiness, shutdown does not verify force termination or update persisted state, runtime status lacks bridge responsiveness and PID-reuse protection, lifecycle events are not wired, and state persistence location is not derived from configuration. These gaps make Launcher unsafe as the single authority for Blender process lifecycle and block CLI/MCP from delegating process operations correctly.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-LAU-001 discovery order includes “registered path from config/state store”, but implementation only uses `LauncherConfigVO.executable_path`. It does not read persisted state from `StatePersistence`. | `modules/launcher/src/capabilities_executable_locator.py:_build_candidate_order()` | Clarify whether registration is stored in config, state store, or both. Wire locator to persisted state if required. |
| 2 | 🔴 CRITICAL | FR-LAU-002 mentions bridge endpoint settings and integration component activation, but the aggregate/protocol signature has no bridge endpoint or filepath input. CLI `init --filepath` cannot be delegated cleanly to current Launcher contract. | `modules/shared/src/launcher/contract_launch_protocol.py:LaunchProtocol.launch()`, `modules/shared/src/launcher/contract_launcher_operate_aggregate.py:ILauncherOperateAggregate.launch()` | Introduce `LaunchRequestVO` (mode, bridge endpoint, optional filepath, timeout) or explicitly document that filepath is out of Launcher scope and how CLI obtains it. |
| 3 | 🟡 WARNING | FR-LAU-004 requires `starting` and `stopping` classifications, but no transition state is tracked in capabilities or agent. | `modules/launcher/src/capabilities_runtime_status.py:check_status()` | Add transition tracking or clarify that STARTING/STOPPING are derived from active launch/shutdown operations. |
| 4 | 🟡 WARNING | FR-LAU-005 says persistence location is derived from config/workspace. `LauncherConfigVO.state_persistence_location` exists but container ignores it unless caller passes `state_path`. | `modules/launcher/src/root_launcher_container.py:__init__()` | Use `config.state_persistence_location` as default when `state_path` is not supplied. |
| 5 | 🟢 INFO | Contracts use `TimeoutSeconds`, a `NewType` over `float`. If AES402 is interpreted strictly, primitive-backed aliases may need to become frozen VOs. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:TimeoutSeconds` | Confirm lint policy. If strict, wrap timeout in a validated VO. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Launch does not activate the Blender integration component/addon and does not pass bridge endpoint settings. `process_spawn()` only starts Blender with optional `--background`. | `modules/shared/src/launcher/utility_process_ops.py:process_spawn()` | Implement Blender spawn with addon activation and bridge endpoint arguments. Move CLI’s addon activation logic into Launcher/Gateway-owned utility if appropriate. |
| 2 | 🔴 CRITICAL | Readiness probe checks only OS process liveness. FR-LAU-002 requires readiness = process liveness + bridge readiness signal. A live process with dead/unstarted bridge is incorrectly reported ready. | `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness()` | Probe the bridge endpoint (TCP connect or protocol handshake) before returning ready. |
| 3 | 🔴 CRITICAL | Shutdown does not update persisted runtime state to stopped. FR-LAU-003 requires persisted state updated to stopped. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown()` | After confirmed stop, persist `RuntimeStateVO(last_status=NOT_RUNNING, process_id=None)` or delegate to persistence capability. |
| 4 | 🔴 CRITICAL | Lifecycle events are defined but never emitted in wired composition because `event_sink` is not provided to capabilities. | `modules/launcher/src/root_launcher_container.py:wire()` | Inject an event sink into all capabilities. Ensure events are emitted for started, failed, stopped, escalation, status checked, stale detected, executable registered. |
| 5 | 🟡 WARNING | Launch and shutdown do not automatically persist runtime state. The aggregate exposes `persist()`, but no flow calls it after launch/shutdown. | `modules/launcher/src/agent_launcher_orchestrator.py:launch()`, `shutdown()` | Orchestrate persistence after successful launch/shutdown, or document that caller must call `persist()` immediately. Prefer automatic persistence in Launcher agent. |
| 6 | 🟡 WARNING | Launch idempotency returns success for `STARTING` state without waiting for readiness. This can mislead callers into thinking launch completed. | `modules/launcher/src/capabilities_process_launcher.py:launch()` | If state is STARTING, either wait until readiness timeout or return a distinct “already starting” outcome with `ready=False`. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `ExecutableLocator._register()` is effectively a no-op. It looks for `set_executable_path` on a callable config provider, but the container supplies a lambda returning immutable `LauncherConfigVO`. Registered path is never stored. | `modules/launcher/src/capabilities_executable_locator.py:_register()` | Inject a registration callback or `PersistStateProtocol`/config mutator. Persist the validated executable path. |
| 2 | 🔴 CRITICAL | Version compatibility is not checked against `supported_version_range`. Any nonempty version string is marked `SUPPORTED`; empty is `UNKNOWN` but still registered. | `modules/launcher/src/capabilities_executable_locator.py:_check_compatibility()` | Parse semantic version and compare to supported range. Return `WARNING`/`UNSUPPORTED` according to policy; reject or warn as configured. |
| 3 | 🔴 CRITICAL | Runtime status has no PID-reuse guard. If persisted PID is reused by another process, `process_alive(pid)` returns true and status becomes `RUNNING_READY`. | `modules/launcher/src/capabilities_runtime_status.py:check_status()` | Store process start time/token at launch and compare against live process start time. Treat mismatch as STALE/NOT_RUNNING. |
| 4 | 🔴 CRITICAL | Container wires `bridge_probe=None`, so full-depth status never checks bridge responsiveness. `RUNNING_UNRESPONSIVE` is unreachable. | `modules/launcher/src/root_launcher_container.py:wire()` | Provide a bridge probe implementation using configured host/port and bounded timeout. |
| 5 | 🟡 WARNING | Force termination is not verified by subsequent liveness check. `process_kill()` return value is ignored and success is assumed. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown()` | After kill, poll liveness until process is absent. Return termination error if still alive. |
| 6 | 🟡 WARNING | `process_alive()` comment says EPERM should be treated as alive, but code returns `False`. This can cause false NOT_RUNNING when permission is restricted. | `modules/shared/src/launcher/utility_process_ops.py:process_alive()` | Decide correct semantics. If EPERM means process exists but not signalable, return `True` or expose an “unknown/permission denied” state. |
| 7 | 🟡 WARNING | Corrupt state load returns `None` without warning. FR-LAU-005 requires corrupt/unreadable state to fall back to empty state with warning. | `modules/launcher/src/capabilities_state_persistence.py:load()` | Return a load outcome with warnings or emit a reconciliation warning event. |
| 8 | 🟡 WARNING | `RuntimeStatusChecker.mark_launched()` exists but is never called by container or agent, so uptime is always `None`. | `modules/launcher/src/capabilities_runtime_status.py:mark_launched()` | Call after successful launch or derive uptime from persisted `launch_timestamp`. |
| 9 | 🟢 INFO | Executable-registered event uses `state_after=RUNNING_READY`, which is semantically incorrect because registration does not start Blender. | `modules/launcher/src/capabilities_executable_locator.py:_emit_registered()` | Use `NOT_RUNNING` or add a non-runtime event field. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | No acceptance tests traceable to FR-LAU-001 discovery order, executable validation, version rejection, symlink normalization, or stale path revalidation. | `tests/` (missing) | Add unit/integration tests with fake command runner and temporary executable stubs. |
| 2 | 🟡 WARNING | No tests for FR-LAU-002 readiness timeout, bridge readiness, duplicate-launch idempotency, or early process exit reason. | `tests/` (missing) | Add tests with injected spawner/probe mocks. |
| 3 | 🟡 WARNING | No tests for FR-LAU-003 graceful timeout, force escalation, force verification, or persisted stopped state. | `tests/` (missing) | Add shutdown scenario tests. |
| 4 | 🟡 WARNING | No tests for FR-LAU-004 PID reuse, zombie process, bridge dead, stale reconciliation. | `tests/` (missing) | Add status classification tests with mocked liveness/bridge/process start time. |
| 5 | 🟡 WARNING | No tests for FR-LAU-005 atomic write, corrupt file fallback, missing path fallback, secret exclusion. | `tests/` (missing) | Add persistence corruption and concurrency tests. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-LAU-001 “Successful validation registers path” is not traceable to persisted config/state. | `modules/launcher/src/capabilities_executable_locator.py:_register()` | Add registration persistence and test. |
| 2 | 🔴 CRITICAL | FR-LAU-002 “Activates integration component during startup” is not traceable in spawn logic. | `modules/shared/src/launcher/utility_process_ops.py:process_spawn()` | Add addon activation arguments and trace to FR-LAU-002 in docstrings/tests. |
| 3 | 🔴 CRITICAL | FR-LAU-004 “Process alive but bridge unresponsive → unresponsive/stale” is not traceable because bridge probe is absent in wiring. | `modules/launcher/src/root_launcher_container.py:wire()` | Wire bridge probe and add classification tests. |
| 4 | 🟡 WARNING | FR-LAU-005 “Location from config/workspace, never invented” is only partially traceable; container ignores config location unless manually passed. | `modules/launcher/src/root_launcher_container.py:__init__()` | Default to `config.state_persistence_location`. |
| 5 | 🟡 WARNING | FRD events are defined in taxonomy but not observable at runtime because event sink is not wired. | `modules/launcher/src/root_launcher_container.py:wire()` | Wire event sink and add event-emission tests. |

## Violations
- No direct AES layer-import violation identified in the provided Launcher files.
- **Potential AES402 — Contract Role:** `TimeoutSeconds` is a `NewType` over `float`. If the AES linter treats primitive-backed aliases as primitives, contract signatures should use a validated VO instead.
- Business/FRD gaps are the primary issue; they may become AES role/orphan issues if CLI continues to duplicate Launcher responsibilities.

## Action Items (For Developer)
- [ ] P0 Add and wire a real bridge readiness probe; launch must not report ready based only on OS liveness.
- [ ] P0 Implement integration component/addon activation in Launcher spawn logic.
- [ ] P0 Persist executable registration and runtime state after launch/shutdown.
- [ ] P0 Verify force termination with post-kill liveness polling.
- [ ] P0 Add PID-reuse protection using process start time/token.
- [ ] P0 Wire lifecycle event sink into all capabilities.
- [ ] P1 Implement version compatibility checking against `supported_version_range`.
- [ ] P1 Use `LauncherConfigVO.state_persistence_location` as default persistence path.
- [ ] P1 Emit warnings for corrupt state fallback and persistence failures.
- [ ] P1 Add `LaunchRequestVO` or clarify filepath/bridge endpoint ownership between CLI and Launcher.
- [ ] P2 Add FR-LAU acceptance tests for all five requirements.

## Proposed Fixes / Reference Code

### `modules/shared/src/launcher/taxonomy_launcher_vo.py`
```python
from modules.shared.src.common.taxonomy_core_vo import FilePath, Host, PortNumber

@dataclass(frozen=True)
class BridgeEndpointVO:
    host: Host = Host("localhost")
    port: PortNumber = PortNumber(9876)

@dataclass(frozen=True)
class LaunchRequestVO:
    mode: LaunchMode = LaunchMode.INTERFACE
    bridge_endpoint: BridgeEndpointVO | None = None
    readiness_timeout_seconds: TimeoutSeconds | None = None
    filepath: FilePath | None = None
```

### `modules/shared/src/launcher/contract_launch_protocol.py`

```python
class LaunchProtocol(ABC):
    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """Start Blender with integration component active and confirm bridge readiness."""
        ...
```

### `modules/shared/src/launcher/utility_process_ops.py`

```python
import socket


def bridge_ready(endpoint: "BridgeEndpointVO", timeout_seconds: float) -> bool:
    try:
        with socket.create_connection((endpoint.host, endpoint.port), timeout=timeout_seconds):
            return True
    except OSError:
        return False


def process_spawn_blender(
    executable: str,
    request: "LaunchRequestVO",
    addon_path: str | None = None,
) -> int:
    args = [executable]
    if request.mode == LaunchMode.HEADLESS:
        args.append("--background")
    if request.filepath:
        args.append(str(request.filepath))
    if addon_path:
        args.extend(
            [
                "--python-expr",
                f"import sys; sys.path.insert(0, r'{addon_path}'); "
                "import bpy; bpy.ops.preferences.addon_enable(module='blender_mcp_addon')",
            ]
        )
    proc = subprocess.Popen(args)
    return proc.pid
```

### `modules/launcher/src/root_launcher_container.py`

```python
def wire(self) -> None:
    if self._wired:
        return

    state_path = self._state_path or self._config.state_persistence_location

    def event_sink(event: LauncherLifecycleEvent) -> None:
        logger.info(
            "launcher_event category=%s before=%s after=%s",
            event.event_category,
            event.state_before.value,
            event.state_after.value,
        )

    persist_cap = StatePersistence(path_resolver=lambda: state_path)

    bridge_probe = lambda timeout_seconds: bridge_ready(
        BridgeEndpointVO(),  # replace with configured endpoint VO
        timeout_seconds,
    )

    status_cap = RuntimeStatusChecker(
        liveness_checker=process_alive,
        pid_resolver=lambda: self._resolve_persisted_pid(persist_cap),
        bridge_probe=bridge_probe,
        persisted_state_resolver=persist_cap.load,
        stale_reconciliation_enabled=self._config.stale_reconciliation_enabled,
        event_sink=event_sink,
    )

    launch_cap = ProcessLauncher(
        executable_resolver=lambda: self._config.executable_path,
        status_protocol=status_cap,
        spawner=lambda executable, mode, timeout: process_spawn_blender(
            executable,
            LaunchRequestVO(mode=LaunchMode(mode)),
        ),
        readiness_probe=lambda pid, timeout: bridge_probe(timeout),
        event_sink=event_sink,
    )
    ...
```

### `modules/launcher/src/capabilities_executable_locator.py`

```python
def __init__(
    self,
    config_provider: Callable[[], LauncherConfigVO] | None = None,
    command_runner: _CommandRunner | None = None,
    event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
    register_callback: Callable[[str], None] | None = None,
) -> None:
    ...
    self._register_callback = register_callback


def _register(self, _config: LauncherConfigVO, path: str) -> None:
    if self._register_callback is not None:
        self._register_callback(path)
```

### `modules/launcher/src/capabilities_process_shutdown.py`

```python
if self._kill is not None and self._kill(current.process_id):
    deadline = time.monotonic() + 1.0
    while time.monotonic() < deadline:
        if not process_alive(current.process_id):
            break
        time.sleep(0.05)
    else:
        return ShutdownOutcomeVO(
            success=False,
            termination_method=TerminationMethod.FORCE,
            error="Force termination attempted but process is still alive",
        )
```

### `modules/launcher/src/agent_launcher_orchestrator.py`

```python
def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
    outcome = self._launch.launch(request)
    if outcome.success and outcome.process_id is not None:
        self._persist.persist(
            RuntimeStateVO(
                executable_path=self._locate_current_path(),
                process_id=outcome.process_id,
                launch_timestamp=time.time(),
                bridge_endpoint=outcome.bridge_endpoint,
                last_status=RuntimeState.RUNNING_READY if outcome.ready else RuntimeState.STARTING,
            )
        )
    return outcome
```

```

```
