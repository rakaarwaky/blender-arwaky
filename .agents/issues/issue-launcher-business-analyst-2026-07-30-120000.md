Issue document created at: `.agents/issues/issue-launcher-business-analyst-2026-07-30-120000.md`

```markdown
# Issue: launcher — Business Logic & Requirements Review

## Summary
The `launcher` feature has a clear FRD and a structurally AES-aligned layer split: five capability files map to FR-LAU-001..005, one aggregate orchestrator implements the facade, and a root container wires dependencies. However, the business logic implementation is incomplete in several core areas. Executable registration is effectively a no-op in the default composition, launch does not activate or verify the Blender integration bridge, readiness is reduced to OS process liveness, shutdown does not verify force termination or persist stopped state, and runtime status cannot detect bridge unresponsiveness, PID reuse, or transition states. In addition, lifecycle events are not wired in the default container, several configuration keys are unused, and typed launcher errors are defined but largely unused. These gaps create a risk of false-positive readiness, stale runtime state, orphaned processes, misleading health status, and weak traceability from FRD acceptance criteria to tests. This issue must be addressed before the launcher can be considered functionally complete and safe for downstream consumers such as CLI, MCP, diagnostics, and gateway.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-LAU-002 specifies input “bridge endpoint settings”, but `LaunchProtocol.launch()` only accepts `mode` and `readiness_timeout_seconds`. There is no VO for bridge endpoint settings in the launch contract. | `modules/shared/src/launcher/contract_launch_protocol.py:LaunchProtocol.launch` | Define `BridgeEndpointSettingsVO` and either add it as a parameter or introduce `LaunchRequestVO`. Update aggregate, capability, and container wiring. |
| 2 | 🟡 WARNING | FR-LAU-001 discovery order includes “registered path from config/state store”, but implementation only uses `config.executable_path`. The state store is not consulted for a previously registered executable. | `modules/launcher/src/capabilities_executable_locator.py:_build_candidate_order` | Clarify whether “registered path” means config, persisted state, or both. If persisted state is included, inject `PersistStateProtocol.load` into locator and add persisted executable path as a discovery source. |
| 3 | 🟡 WARNING | “Must validate as genuine Blender runtime” is not defined with acceptance criteria. Current code only checks file existence/executability and optionally runs `--version`. | `modules/launcher/FRD.md:FR-LAU-001`, `modules/launcher/src/capabilities_executable_locator.py:_validate` | Define what proves authenticity, e.g. `--version` exit code 0, stdout contains `Blender`, parseable version, and version within supported range. |
| 4 | 🟡 WARNING | FR-LAU-001 says unsupported version results in “warning or rejection per policy”, but no policy configuration exists. `LauncherConfigVO.supported_version_range` is present but unused. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO.supported_version_range` | Add explicit policy, e.g. `version_policy: reject|warn`, and implement version comparison against `supported_version_range`. |
| 5 | 🟡 WARNING | FR-LAU-002 says process alive without bridge readiness may be “launch failure or degraded per policy”, but no degraded-mode policy is defined. | `modules/launcher/FRD.md:FR-LAU-002` | Define config key such as `launch_degraded_mode_enabled` and specify resulting `LaunchOutcomeVO` semantics. |
| 6 | 🟡 WARNING | FR-LAU-003 input includes “confirmation flag for escalation”. Implementation has `force` and `allow_escalation`, but their semantic relationship is ambiguous. | `modules/shared/src/launcher/contract_shutdown_protocol.py:ShutdownProtocol.shutdown` | Specify exact semantics: `force` = skip graceful and kill immediately; `allow_escalation` = permit graceful-to-force timeout escalation. Document in FRD and contract docstring. |
| 7 | 🟡 WARNING | FR-LAU-004 mentions “stale per configured threshold”, but no threshold configuration exists in `LauncherConfigVO`. | `modules/launcher/FRD.md:FR-LAU-004`, `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO` | Add `stale_threshold_seconds` or equivalent and use it in status classification. |
| 8 | 🟢 INFO | FR-LAU-005 says corruption/reconciliation/persistence warnings are “emitted”, but the emission channel is not defined: event sink, structured log, or outcome warnings. | `modules/launcher/FRD.md:FR-LAU-005` | Define warning emission contract. Prefer lifecycle event plus `PersistenceOutcomeVO.warnings` for caller-visible warnings. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Launch does not activate the Blender integration component. `process_spawn()` only starts Blender and adds `--background` for headless mode. It does not enable the bridge/addon or pass bridge endpoint/protocol settings. | `modules/shared/src/launcher/utility_process_ops.py:process_spawn`, `modules/launcher/src/capabilities_process_launcher.py:launch` | Implement launch arguments or startup mechanism that activates the integration component and passes bridge endpoint settings. Ensure auth material is redacted and handled via security policy. |
| 2 | 🔴 CRITICAL | Readiness check is process liveness only. `process_probe_readiness()` returns true while the OS process is alive, not when the integration bridge is ready. This violates FR-LAU-002 readiness = process liveness + bridge readiness. | `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness`, `modules/launcher/src/root_launcher_container.py:wire` | Replace default readiness probe with a bridge-aware probe. The launcher should depend on an injected bridge readiness contract/utility, not only `process_alive`. |
| 3 | 🔴 CRITICAL | Launched process state is not persisted. `ProcessLauncher.launch()` returns a PID but never calls `PersistStateProtocol.persist()`. Since `RuntimeStatusChecker` resolves PID from persisted state, status after launch may incorrectly report `NOT_RUNNING`. | `modules/launcher/src/capabilities_process_launcher.py:launch`, `modules/launcher/src/root_launcher_container.py:_resolve_persisted_pid` | Persist `RuntimeStateVO` immediately after successful spawn/readiness, including executable path, PID, launch timestamp, bridge endpoint summary, and last status. |
| 4 | 🔴 CRITICAL | Shutdown does not update persisted state to stopped. FR-LAU-003 explicitly requires persisted state updated to stopped. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown` | Inject `PersistStateProtocol` and persist stopped state after verified termination. |
| 5 | 🔴 CRITICAL | Force termination is not verified. `ProcessShutdown.shutdown()` ignores the boolean result of `self._kill()` and returns success/final `NOT_RUNNING` without a subsequent liveness check. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown` | Check kill result and perform a post-termination liveness check. Return `TerminationError`/failed `ShutdownOutcomeVO` if process remains alive. |
| 6 | 🔴 CRITICAL | Executable registration is a no-op in default wiring. `_register()` looks for `set_executable_path` on the config provider, but the container supplies a lambda returning a frozen `LauncherConfigVO`, which has no setter. The validated path is not persisted or registered. | `modules/launcher/src/capabilities_executable_locator.py:_register`, `modules/launcher/src/root_launcher_container.py:wire` | Make registration explicit: persist registered executable path via `PersistStateProtocol` and/or update a mutable config registry. Do not rely on optional duck-typed setter. |
| 7 | 🟡 WARNING | Lifecycle events are specified but not emitted in default composition. All capabilities accept optional `event_sink`, but `LauncherContainer.wire()` passes none. | `modules/launcher/src/root_launcher_container.py:wire` | Wire a default event sink, e.g. structured logger or diagnostics event dispatcher, to all launcher capabilities. |
| 8 | 🟡 WARNING | Platform-standard search locations are not defaulted. `LauncherConfigVO.search_locations` defaults to empty tuple, so discovery may skip platform locations unless caller supplies them. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO.search_locations`, `modules/launcher/src/capabilities_executable_locator.py:_build_candidate_order` | Provide platform-appropriate defaults in container or config resolution. |
| 9 | 🟡 WARNING | Runtime status cannot classify `RUNNING_UNRESPONSIVE` in default wiring because `bridge_probe=None`. Full depth behaves like lightweight. | `modules/launcher/src/capabilities_runtime_status.py:check_status`, `modules/launcher/src/root_launcher_container.py:wire` | Wire a real bridge probe for full-depth checks. Use lightweight only when caller explicitly requests it. |
| 10 | 🟡 WARNING | Shutdown during launch is not explicitly resolved. FR-LAU-003 requires deterministic resolution when shutdown occurs during launch. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown` | Introduce launch-state awareness or coordinate through status classification `STARTING`. Define behavior: cancel readiness wait, then terminate. |
| 11 | 🟢 INFO | Orphaned child process cleanup is not implemented. FRD allows “where detectable + safe”, but no detection exists. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown` | Add optional child-process discovery/cleanup via utility layer, guarded by platform support and safety checks. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Non-Blender executables can pass validation. If a command runner is absent, version is empty and compatibility becomes `UNKNOWN`, but the executable is still registered. If present, any executable returning exit code 0 and a numeric token can pass. | `modules/launcher/src/capabilities_executable_locator.py:_validate`, `_detect_version`, `_check_compatibility` | Require positive Blender authenticity evidence: `--version` succeeds and output contains `Blender` or another deterministic marker. Reject when authenticity cannot be confirmed. |
| 2 | 🔴 CRITICAL | Version compatibility is not compared against supported range. `_check_compatibility()` returns `SUPPORTED` for any non-empty version. | `modules/launcher/src/capabilities_executable_locator.py:_check_compatibility` | Parse semantic version and compare with `LauncherConfigVO.supported_version_range`. Return `WARNING` or `UNSUPPORTED` according to policy. |
| 3 | 🟡 WARNING | Idempotent launch returns `success=True` for `RUNNING_UNRESPONSIVE` and `STARTING`. This may hide an unhealthy or incomplete launch. | `modules/launcher/src/capabilities_process_launcher.py:launch` | Return success only for verified `RUNNING_READY`. For `RUNNING_UNRESPONSIVE`, return failure or degraded result per policy. For `STARTING`, either wait for readiness or return a distinct “already starting” outcome. |
| 4 | 🟡 WARNING | `process_alive()` comment says EPERM should be treated as alive, but implementation returns `False`. This can misclassify a permission-restricted live process as dead/stale. | `modules/shared/src/launcher/utility_process_ops.py:process_alive` | Return `True` on `EPERM` or introduce an `UNKNOWN` liveness classification. Update status logic accordingly. |
| 5 | 🟡 WARNING | Secret detection in persistence is shallow. `_contains_secret()` only checks fixed top-level keys from serialized state. It will not detect secret-like content inside `bridge_endpoint` or future fields. | `modules/launcher/src/capabilities_state_persistence.py:_contains_secret` | Recursively scan serialized payload for secret-like keys/values and redact before persistence. Ensure bridge endpoint summary never includes auth material. |
| 6 | 🟡 WARNING | Corrupt state load silently returns `None` without warning or event. FR-LAU-005 requires corrupt/unreadable state to fall back to empty state with warning. | `modules/launcher/src/capabilities_state_persistence.py:_load_impl` | Emit a warning event/log and/or return a richer load result with warnings. If contract must remain `RuntimeStateVO | None`, emit through injected event sink. |
| 7 | 🟡 WARNING | Uptime is always `None` in practice. `RuntimeStatusChecker.mark_launched()` exists but is not called by launcher or container, and the method is not part of the contract. | `modules/launcher/src/capabilities_runtime_status.py:mark_launched`, `modules/launcher/src/root_launcher_container.py:wire` | Derive uptime from persisted `launch_timestamp` or wire launch notification through a contract-safe mechanism. |
| 8 | 🟡 WARNING | Executable registration event uses `state_after=RuntimeState.RUNNING_READY`, which is semantically wrong. Registration does not mean Blender is running. | `modules/launcher/src/capabilities_executable_locator.py:_emit_registered` | Use `state_after=RuntimeState.NOT_RUNNING` or current observed state. Add a separate event field for registration success. |
| 9 | 🟡 WARNING | Persistence path resolution ignores `LauncherConfigVO.state_persistence_location` unless caller manually passes `state_path`. | `modules/launcher/src/root_launcher_container.py:__init__`, `wire` | Resolve state path as `state_path or config.state_persistence_location`. If neither exists, degrade with explicit warning. |
| 10 | 🟢 INFO | Typed launcher errors are defined but mostly unused. Capabilities return outcome VOs with string errors, reducing traceability to FRD error categories. | `modules/shared/src/launcher/taxonomy_launcher_error.py`, capability files | Use typed errors internally or include error category enums in outcome VOs. Keep outcome VOs for caller-facing results, but preserve categorized error codes. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | The FRD includes a QA checklist, but no test files are traceable in the provided launcher module. | `modules/launcher/FRD.md:QA Checklist`, `modules/launcher/tests/` | Add `tests/contract_launcher.py`, `tests/unit_launcher_*.py`, and `tests/integration_launcher.py` per project test conventions. |
| 2 | 🟡 WARNING | “Genuine Blender runtime” validation has no testable acceptance criteria. | `modules/launcher/FRD.md:FR-LAU-001` | Define expected `--version` output pattern and version parse behavior. Add unit tests with fake command runner outputs. |
| 3 | 🟡 WARNING | Bridge readiness acceptance criteria are not represented in code or tests. Current probe tests would only verify process liveness. | `modules/launcher/FRD.md:FR-LAU-002`, `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness` | Define bridge readiness signal contract. Add tests for: process alive + bridge not ready, process dead + bridge ready/unknown, timeout, early exit. |
| 4 | 🟡 WARNING | Force termination verification has no acceptance criteria in implementation. | `modules/launcher/FRD.md:FR-LAU-003` | Add tests where kill returns false or liveness remains true, asserting failed shutdown outcome. |
| 5 | 🟡 WARNING | PID reuse guard is required but no metadata exists to test or implement it. | `modules/launcher/FRD.md:FR-LAU-004` | Store launch timestamp/process start identifier and test PID reuse scenario where PID is alive but process identity differs. |
| 6 | 🟢 INFO | Corruption fallback is not observable. Tests can assert `None`, but cannot assert that a warning was emitted. | `modules/launcher/src/capabilities_state_persistence.py:_load_impl` | Emit event/log or return load warnings so tests can verify FR-LAU-005 warning behavior. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-LAU-001 is only partially implemented. Code traces to `ExecutableLocator`, but registration, version policy, and genuine validation are missing. | `modules/launcher/src/capabilities_executable_locator.py` | Update locator and container. Add tests named with `acceptance_FR_LAU_001_*`. |
| 2 | 🔴 CRITICAL | FR-LAU-002 is only partially implemented. Code traces to `ProcessLauncher`, but integration activation, bridge endpoint passing, and bridge readiness are missing. | `modules/launcher/src/capabilities_process_launcher.py`, `modules/shared/src/launcher/utility_process_ops.py:process_spawn` | Extend launch contract and capability. Add acceptance tests for readiness and idempotency. |
| 3 | 🔴 CRITICAL | FR-LAU-003 is only partially implemented. Code traces to `ProcessShutdown`, but force verification, persisted stopped state, and launch-transition handling are missing. | `modules/launcher/src/capabilities_process_shutdown.py` | Implement verification and persistence. Add acceptance tests for graceful, force, escalation, and already-stopped cases. |
| 4 | 🟡 WARNING | FR-LAU-004 is partially implemented. Status checks OS liveness but lacks bridge unresponsiveness, PID reuse guard, transition states, and uptime wiring. | `modules/launcher/src/capabilities_runtime_status.py` | Wire bridge probe, add process identity guard, classify `STARTING`/`STOPPING`, derive uptime. |
| 5 | 🟡 WARNING | FR-LAU-005 is partially implemented. Atomic write and corrupt-read fallback exist, but config location, warnings, reconciliation, and event emission are incomplete. | `modules/launcher/src/capabilities_state_persistence.py` | Use config location, emit warnings, reconcile stale state with status, and persist after launch/shutdown. |
| 6 | 🟡 WARNING | Several configuration keys are defined but unused: `supported_version_range`, `launch_timeout_seconds`, `readiness_probe_interval_seconds`, `state_persistence_location`, `default_launch_mode`. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO`, `modules/launcher/src/root_launcher_container.py:wire` | Wire each config key to the relevant capability or remove from FRD/config if not required. |
| 7 | 🟡 WARNING | Lifecycle events are defined in taxonomy and emitted conditionally, but no event sink is composed in root. This breaks traceability from FRD events to runtime observability. | `modules/launcher/src/root_launcher_container.py:wire` | Add event sink wiring and integration test asserting events for started, failed, stopped, escalation, stale, registered. |

## Violations
Potential AES-related observations from the provided launcher source:

- **Potential AES501 — Taxonomy Orphan / unused taxonomy definitions**: Several error classes in `modules/shared/src/launcher/taxonomy_launcher_error.py` are defined but not used by capabilities or contracts, e.g. `BlenderNotRunningError`, `StateError`, `LauncherConfigError`, `LaunchTimeoutError`, `ShutdownTimeoutError`, `LaunchError`, `TerminationError`. Only `ExecutableValidationError` is imported by `capabilities_executable_locator.py`. Either use these typed errors or remove them to avoid dead taxonomy.
- **No confirmed AES201 import-boundary violations detected** in the provided launcher files: capabilities import taxonomy, protocol contracts, and utility; agent imports aggregate/protocol contracts; root wires capabilities and agent.
- **No confirmed AES403 capability role violations detected**: each capability implements its corresponding protocol and appears to keep type count within limits.
- **No confirmed AES304 bypass-comment violations detected** in launcher source files.

## Action Items (For Developer)
- [ ] P0 Define bridge endpoint settings VO and launch request contract for FR-LAU-002.
- [ ] P0 Implement Blender integration activation during spawn, including bridge endpoint and protocol info passing.
- [ ] P0 Replace process-only readiness probe with bridge-aware readiness probe: readiness = process alive + bridge ready.
- [ ] P0 Persist runtime state after successful launch: executable path, PID, launch timestamp, bridge endpoint summary, last status.
- [ ] P0 Persist stopped state after verified shutdown.
- [ ] P0 Implement real executable registration: persist registered path and/or update authoritative config registry.
- [ ] P0 Implement genuine Blender validation and supported-version comparison in `ExecutableLocator`.
- [ ] P0 Verify force termination with post-kill liveness check and fail shutdown if process remains alive.
- [ ] P1 Wire lifecycle event sink in `LauncherContainer` for all capabilities.
- [ ] P1 Wire `bridge_probe` into `RuntimeStatusChecker` for full-depth status.
- [ ] P1 Add PID reuse guard using process start time or equivalent process identity metadata.
- [ ] P1 Implement transition classifications `STARTING` and `STOPPING` in runtime status.
- [ ] P1 Use all relevant `LauncherConfigVO` keys: `launch_timeout_seconds`, `shutdown_timeout_seconds`, `readiness_probe_interval_seconds`, `state_persistence_location`, `default_launch_mode`, `supported_version_range`, `stale_reconciliation_enabled`.
- [ ] P1 Add default platform-standard Blender search locations when config does not provide them.
- [ ] P1 Emit warnings/events for corrupt state load, persistence failure, stale reconciliation, and version compatibility warnings.
- [ ] P2 Add contract/unit/integration/acceptance tests mapped to FR-LAU-001..005 and the FRD QA checklist.
- [ ] P2 Use typed launcher errors or categorized error enums in outcome VOs to improve traceability.

## Proposed Fixes / Reference Code

### `modules/shared/src/launcher/taxonomy_launcher_vo.py`

Add bridge endpoint and launch request VOs. Use existing branded primitives where possible.

```python
from modules.shared.src.common.taxonomy_core_vo import Host, PortNumber, ProtocolVersion

@dataclass(frozen=True)
class BridgeEndpointSettingsVO:
    """Bridge endpoint settings passed to Blender during launch."""

    host: Host
    port: PortNumber
    protocol_version: ProtocolVersion | None = None


@dataclass(frozen=True)
class LaunchRequestVO:
    """Unified launch request input."""

    mode: LaunchMode = LaunchMode.INTERFACE
    readiness_timeout: TimeoutSeconds | None = None
    bridge_endpoint: BridgeEndpointSettingsVO | None = None
```

Extend `LaunchOutcomeVO` only if endpoint summary is needed:

```python
@dataclass(frozen=True)
class LaunchOutcomeVO:
    success: bool = False
    process_id: int | None = None
    ready: bool = False
    bridge_endpoint: str | None = None
    duration_ms: float = 0.0
    launch_method: LaunchMethod = LaunchMethod.SPAWN
    error: str | None = None
```

Add stale threshold config:

```python
@dataclass(frozen=True)
class LauncherConfigVO:
    executable_path: str | None = None
    search_locations: tuple[str, ...] = dc_field(default_factory=tuple)
    supported_version_range: str = ""
    launch_timeout_seconds: float = 30.0
    shutdown_timeout_seconds: float = 10.0
    force_termination_enabled: bool = True
    readiness_probe_interval_seconds: float = 0.5
    state_persistence_location: str | None = None
    default_launch_mode: LaunchMode = LaunchMode.INTERFACE
    stale_reconciliation_enabled: bool = True
    stale_threshold_seconds: float = 60.0
```

---

### `modules/shared/src/launcher/contract_launch_protocol.py`

Replace primitive-ish launch parameters with a VO-based request.

```python
from .taxonomy_launcher_vo import LaunchOutcomeVO, LaunchRequestVO


class LaunchProtocol(ABC):
    """Protocol interface for launching Blender with integration bridge readiness."""

    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """Start Blender with the integration component active and confirm bridge readiness."""
        ...
```

Update aggregate accordingly:

```python
@abstractmethod
def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
    """FR-LAU-002: Launch Blender and confirm readiness."""
    ...
```

---

### `modules/launcher/src/capabilities_executable_locator.py`

Reference logic for genuine validation, version policy, and registration.

```python
def _validate(self, path: str, config: LauncherConfigVO) -> ExecutableReferenceVO:
    canonical = os.path.realpath(path)

    if not os.path.isfile(canonical) or not os.access(canonical, os.X_OK):
        raise ExecutableValidationError(f"Not an executable file: {canonical}")

    if self._runner is None:
        raise ExecutableValidationError("Cannot confirm Blender authenticity without command runner")

    try:
        rc, out = self._runner([canonical, "--version"], timeout=5.0)
    except Exception as exc:
        raise ExecutableValidationError(f"Version check failed: {exc}") from exc

    if rc != 0:
        raise ExecutableValidationError("Executable version check returned non-zero exit code")

    if "Blender" not in out:
        raise ExecutableValidationError("Executable does not identify as Blender")

    version = self._parse_version(out)
    compat = self._check_compatibility(version, config.supported_version_range)

    if compat is VersionCompatibility.UNSUPPORTED:
        raise ExecutableValidationError(f"Unsupported Blender version: {version}")

    return ExecutableReferenceVO(
        path=canonical,
        version_summary=version,
        compatibility=compat,
    )
```

Registration should persist authoritative path:

```python
def __init__(
    self,
    config_provider: Callable[[], LauncherConfigVO] | None = None,
    command_runner: _CommandRunner | None = None,
    persist_cap: PersistStateProtocol | None = None,
    event_sink: Callable[[LauncherLifecycleEvent], None] | None = None,
) -> None:
    self._config_provider = config_provider or (lambda: LauncherConfigVO())
    self._runner = command_runner
    self._persist = persist_cap
    self._events = event_sink


def _register(self, config: LauncherConfigVO, ref: ExecutableReferenceVO) -> None:
    if self._persist is None:
        return

    current = self._persist.load()
    updated = RuntimeStateVO(
        executable_path=ref.path,
        process_id=current.process_id if current else None,
        launch_timestamp=current.launch_timestamp if current else 0.0,
        bridge_endpoint=current.bridge_endpoint if current else None,
        last_status=current.last_status if current else RuntimeState.NOT_RUNNING,
    )
    self._persist.persist(updated)
```

Fix registration event state:

```python
def _emit_registered(self, source: RegistrationSource, path: str) -> None:
    if self._events is not None:
        self._events(
            LauncherLifecycleEvent(
                event_category=LAUNCHER_EVENT_EXECUTABLE_REGISTERED,
                state_before=RuntimeState.NOT_RUNNING,
                state_after=RuntimeState.NOT_RUNNING,
                process_reference=path,
                reason_summary=f"registered_from_{source.value}",
            )
        )
```

---

### `modules/launcher/src/capabilities_process_launcher.py`

Reference launch flow with bridge readiness and persistence.

```python
def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
    timeout = request.readiness_timeout or self._config.launch_timeout_seconds

    current = self._status.check_status(depth=ProbeDepth.FULL)
    if current.state == RuntimeState.RUNNING_READY:
        return LaunchOutcomeVO(
            success=True,
            process_id=current.process_id,
            ready=True,
            launch_method=LaunchMethod.IDEMPOTENT,
        )

    if current.state == RuntimeState.RUNNING_UNRESPONSIVE:
        return LaunchOutcomeVO(
            success=False,
            process_id=current.process_id,
            ready=False,
            error="Existing Blender process is running but bridge is unresponsive",
        )

    executable = self._resolve_executable()
    if not executable:
        return LaunchOutcomeVO(success=False, error="No registered executable path")

    if self._spawner is None:
        return LaunchOutcomeVO(success=False, error="Process spawner not configured")

    start = time.monotonic()

    try:
        pid = self._spawner(executable, request.mode.value, request.bridge_endpoint)
    except Exception as exc:
        self._emit(
            LAUNCHER_EVENT_LAUNCH_FAILED,
            RuntimeState.NOT_RUNNING,
            RuntimeState.NOT_RUNNING,
            reason=str(exc),
        )
        return LaunchOutcomeVO(success=False, error=f"Spawn failed: {exc}")

    ready = False
    if self._probe is not None:
        ready = self._probe(pid, timeout)

    duration_ms = (time.monotonic() - start) * 1000.0

    if not ready:
        self._emit(
            LAUNCHER_EVENT_LAUNCH_FAILED,
            RuntimeState.STARTING,
            RuntimeState.STARTING,
            process_reference=str(pid),
            reason="bridge readiness not confirmed",
        )
        return LaunchOutcomeVO(
            success=False,
            process_id=pid,
            ready=False,
            duration_ms=duration_ms,
            error="Readiness not confirmed within timeout",
        )

    self._persist_launched_state(executable, pid, request)

    self._emit(
        LAUNCHER_EVENT_APPLICATION_STARTED,
        RuntimeState.STARTING,
        RuntimeState.RUNNING_READY,
        process_reference=str(pid),
    )

    return LaunchOutcomeVO(
        success=True,
        process_id=pid,
        ready=True,
        bridge_endpoint=self._endpoint_summary(request.bridge_endpoint),
        launch_method=LaunchMethod.SPAWN,
        duration_ms=duration_ms,
    )
```

Persist launched state:

```python
def _persist_launched_state(self, executable: str, pid: int, request: LaunchRequestVO) -> None:
    if self._persist is None:
        return

    state = RuntimeStateVO(
        executable_path=executable,
        process_id=pid,
        launch_timestamp=time.time(),
        bridge_endpoint=self._endpoint_summary(request.bridge_endpoint),
        last_status=RuntimeState.RUNNING_READY,
    )
    self._persist.persist(state)
```

---

### `modules/launcher/src/capabilities_process_shutdown.py`

Reference shutdown with verification and persistence.

```python
def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownOutcomeVO:
    current = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)

    if current.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
        self._persist_stopped_state()
        return ShutdownOutcomeVO(
            success=True,
            termination_method=TerminationMethod.NONE,
            final_state=RuntimeState.NOT_RUNNING,
        )

    if current.process_id is None:
        return ShutdownOutcomeVO(success=False, error="Process id unknown for running instance")

    start = time.monotonic()
    method = TerminationMethod.GRACEFUL
    escalated = False

    if force:
        if not self._force_enabled or self._kill is None:
            return ShutdownOutcomeVO(success=False, error="Force termination disabled")
        self._kill(current.process_id)
        method = TerminationMethod.FORCE
        escalated = True
    else:
        if self._signal is not None:
            self._signal(current.process_id)

        if not self._wait_exit(current.process_id):
            if allow_escalation and self._force_enabled and self._kill is not None:
                self._kill(current.process_id)
                method = TerminationMethod.FORCE
                escalated = True
            else:
                return ShutdownOutcomeVO(
                    success=False,
                    termination_method=TerminationMethod.GRACEFUL,
                    duration_ms=(time.monotonic() - start) * 1000.0,
                    error="Graceful shutdown exceeded timeout; escalation disallowed",
                )

    if self._still_alive(current.process_id):
        return ShutdownOutcomeVO(
            success=False,
            termination_method=method,
            duration_ms=(time.monotonic() - start) * 1000.0,
            error="Termination attempted but process remains alive",
        )

    self._persist_stopped_state()

    return ShutdownOutcomeVO(
        success=True,
        termination_method=method,
        duration_ms=(time.monotonic() - start) * 1000.0,
        final_state=RuntimeState.NOT_RUNNING,
        escalated=escalated,
    )
```

Helper:

```python
def _still_alive(self, process_id: int) -> bool:
    status = self._status.check_status(depth=ProbeDepth.LIGHTWEIGHT)
    return status.process_id == process_id and status.state not in (
        RuntimeState.NOT_RUNNING,
        RuntimeState.STALE,
    )
```

---

### `modules/launcher/src/capabilities_runtime_status.py`

Reference status improvements.

```python
def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
    persisted = self._resolve_persisted()
    pid = persisted.process_id if persisted else None

    if pid is None:
        return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, depth=depth)

    alive = self._is_alive(pid)

    if not alive:
        if persisted is not None and persisted.process_id == pid:
            if self._stale_reconcile:
                self._emit_stale(pid)
            return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)
        return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, process_id=pid, depth=depth)

    if persisted is not None and not self._same_process_instance(pid, persisted.launch_timestamp):
        if self._stale_reconcile:
            self._emit_stale(pid)
        return RuntimeStatusVO(state=RuntimeState.STALE, process_id=pid, stale=True, depth=depth)

    ready = True
    if depth == ProbeDepth.FULL and self._bridge is not None:
        ready = self._bridge(timeout_seconds=1.0)

    state = RuntimeState.RUNNING_READY if ready else RuntimeState.RUNNING_UNRESPONSIVE
    uptime = self._uptime_seconds(persisted)

    return RuntimeStatusVO(
        state=state,
        process_id=pid,
        ready=ready,
        uptime_seconds=uptime,
        depth=depth,
    )
```

---

### `modules/shared/src/launcher/utility_process_ops.py`

Correct EPERM behavior:

```python
def process_alive(process_id: int) -> bool:
    if process_id is None or process_id <= 0:
        return False

    try:
        os.kill(process_id, 0)
        return True
    except OSError as e:
        if e.errno == os.errno.ESRCH:
            return False
        if e.errno == os.errno.EPERM:
            logger.warning("os.kill(pid=%d) returned EPERM; treating process as alive", process_id)
            return True
        logger.warning("os.kill(pid=%d) failed: %s", process_id, e)
        return False
```

Bridge readiness should not be process-only. Introduce an injected bridge probe or a separate utility that checks the bridge endpoint. Example contract boundary:

```python
class _BridgeProbe(Protocol):
    def __call__(self, timeout_seconds: float) -> bool: ...
```

---

### `modules/launcher/src/root_launcher_container.py`

Wire config state path, event sink, bridge probe, and persistence into capabilities.

```python
def wire(self) -> None:
    if self._wired:
        return

    state_path = self._state_path or self._config.state_persistence_location

    persist_cap: PersistStateProtocol = StatePersistence(
        path_resolver=lambda: state_path,
    )

    status_cap: RuntimeStatusProtocol = RuntimeStatusChecker(
        liveness_checker=process_alive,
        pid_resolver=lambda: self._resolve_persisted_pid(persist_cap),
        bridge_probe=self._bridge_probe,
        persisted_state_resolver=persist_cap.load,
        stale_reconciliation_enabled=self._config.stale_reconciliation_enabled,
        event_sink=self._event_sink,
    )

    locate_cap: LocateRegisterProtocol = ExecutableLocator(
        config_provider=lambda: self._config,
        command_runner=lambda args, timeout=5.0: process_version_check(args, timeout),
        persist_cap=persist_cap,
        event_sink=self._event_sink,
    )

    launch_cap: LaunchProtocol = ProcessLauncher(
        executable_resolver=lambda: self._config.executable_path,
        status_protocol=status_cap,
        spawner=self._process_spawner,
        readiness_probe=self._readiness_probe,
        persist_cap=persist_cap,
        config=self._config,
        event_sink=self._event_sink,
    )

    shutdown_cap: ShutdownProtocol = ProcessShutdown(
        status_protocol=status_cap,
        signal_sender=process_signal_term,
        killer=process_kill,
        timeout_seconds=self._config.shutdown_timeout_seconds,
        force_enabled=self._config.force_termination_enabled,
        persist_cap=persist_cap,
        event_sink=self._event_sink,
    )

    self._orchestrator = LauncherOrchestrator(
        locate_register_cap=locate_cap,
        launch_cap=launch_cap,
        shutdown_cap=shutdown_cap,
        status_cap=status_cap,
        persist_cap=persist_cap,
    )

    self._wired = True
```
```