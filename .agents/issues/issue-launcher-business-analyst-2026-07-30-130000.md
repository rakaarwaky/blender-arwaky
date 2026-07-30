
Issue document created at: `.agents/issues/issue-launcher-business-analyst-2026-07-30-130000.md`

```markdown
# Issue: launcher — Business Logic & Requirements Review

## Summary
This is a second launcher issue focused on FRD-to-contract misalignment, authority boundaries, error-category traceability, and observability completeness. The launcher aggregate and protocol contracts do not fully represent the FRD inputs/outputs: `locate_and_register()` forces callers to supply configuration even though FR-LAU-001 input is only an optional override; `launch()` has no bridge endpoint settings; shutdown escalation semantics are ambiguous; runtime status output lacks process/reference metadata needed by diagnostics; persistence load failures do not expose warnings; and FRD error categories are reduced to free-text strings. In addition, the implementation contains inconsistent configuration authority: `locate_and_register(config, ...)` accepts a config argument but registration uses an injected config provider, so caller-supplied configuration may be ignored. These gaps make acceptance testing, diagnostics integration, security redaction, and surface-layer usage ambiguous and error-prone.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-LAU-001 input is “optional explicit location override”, but the aggregate requires a full `LauncherConfigVO` argument: `locate_and_register(config, override=None)`. This leaks config ownership to callers and contradicts launcher being the single authority for executable resolution. | `modules/shared/src/launcher/contract_launcher_operate_aggregate.py:ILauncherOperateAggregate.locate_and_register` | Change aggregate signature to `locate_and_register(override: FilePath | None = None)`. Inject configuration into the capability/container. |
| 2 | 🔴 CRITICAL | FR-LAU-002 input includes “bridge endpoint settings”, but `LaunchProtocol.launch()` and aggregate `launch()` only accept `mode` and `readiness_timeout_seconds`. There is no contract-level way to pass endpoint host/port/protocol information. | `modules/shared/src/launcher/contract_launch_protocol.py:LaunchProtocol.launch`, `modules/shared/src/launcher/contract_launcher_operate_aggregate.py:ILauncherOperateAggregate.launch` | Introduce `LaunchRequestVO` containing mode, readiness timeout, and `BridgeEndpointSettingsVO`. Update protocol, aggregate, orchestrator, and capability. |
| 3 | 🟡 WARNING | FR-LAU-003 input mentions “confirmation flag for escalation”. Contract uses `force: bool` and `allow_escalation: bool`, but the relationship between force preference, confirmation, and policy is not explicit. | `modules/shared/src/launcher/contract_shutdown_protocol.py:ShutdownProtocol.shutdown` | Define `ShutdownRequestVO` with explicit fields: `force_requested`, `escalation_confirmed`, optional `reason`. Document semantics in FRD and contract. |
| 4 | 🟡 WARNING | FR-LAU-004 output requires “process ref summary, readiness, staleness, uptime”. `RuntimeStatusVO` exposes only `process_id`, not a process/reference summary, bridge endpoint summary, probe duration, or last classification reason. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:RuntimeStatusVO` | Add `process_reference`, `bridge_endpoint_summary`, `probe_duration_ms`, and optional `classification_reason` fields. Keep secrets redacted. |
| 5 | 🟡 WARNING | FR-LAU-005 output requires persistence result with reconciliation warnings. `persist()` returns warnings, but `load()` returns `RuntimeStateVO | None` and silently discards corruption/parse warnings. | `modules/shared/src/launcher/contract_persist_state_protocol.py:PersistStateProtocol.load` | Add `load_with_warnings()` returning `LoadOutcomeVO`, or emit warnings through an injected event sink. Keep old `load()` only as a convenience wrapper if needed. |
| 6 | 🟡 WARNING | FRD defines explicit error categories, but outcome VOs use free-text `error: str | None`. Callers cannot reliably distinguish configuration error, timeout error, validation error, state error, launch error, or termination error. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:RegistrationOutcomeVO`, `LaunchOutcomeVO`, `ShutdownOutcomeVO`, `PersistenceOutcomeVO` | Add `error_code: LauncherErrorCode | None` and keep `error_message` for human-readable detail. Map codes to FRD error categories. |
| 7 | 🟡 WARNING | FRD event payloads require category, state before/after, process ref summary, termination/launch method, duration, redacted reason. `LauncherLifecycleEvent` has fields, but capabilities do not consistently populate `duration_ms`, `method`, or redacted reason. | `modules/shared/src/launcher/taxonomy_launcher_event.py:LauncherLifecycleEvent`, `modules/launcher/src/capabilities_process_launcher.py:_emit`, `modules/launcher/src/capabilities_process_shutdown.py:_emit` | Populate all event fields where applicable. Add a safe redaction step before setting `reason_summary`. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Runtime state persistence is exposed as a manual aggregate operation (`persist(state)`) instead of being integrated into launch/shutdown/registration flows. Surfaces or agents can forget to persist, causing status, idempotency, and stale detection to fail. | `modules/shared/src/launcher/contract_launcher_operate_aggregate.py:ILauncherOperateAggregate.persist`, `modules/launcher/src/agent_launcher_orchestrator.py:persist` | Make persistence an internal launcher responsibility for launch, shutdown, and registration. Keep explicit `persist()` only for advanced reconciliation, not normal lifecycle flow. |
| 2 | 🔴 CRITICAL | Configuration authority is inconsistent. `ExecutableLocator.locate_and_register(config, override)` uses the passed `config` for candidate discovery, but `_register()` uses the injected `config_provider`, which may return a different config or no setter. Caller-supplied config can be ignored for registration. | `modules/launcher/src/capabilities_executable_locator.py:locate_and_register`, `_register` | Remove `config` from public contract and inject a single authoritative config provider. If config must be passed, use the same config object for discovery, validation, and registration. |
| 3 | 🟡 WARNING | Duplicate-launch prevention depends on persisted PID resolved by `RuntimeStatusChecker`. If a running Blender process was started outside launcher, or if state was not persisted, launcher may spawn a duplicate process. | `modules/launcher/src/root_launcher_container.py:_resolve_persisted_pid`, `modules/launcher/src/capabilities_process_launcher.py:launch` | Add a launcher-owned process discovery or bridge-endpoint conflict check before spawn. At minimum, document that launcher authority requires all Blender launches to go through launcher. |
| 4 | 🟡 WARNING | Concurrent shutdown is not coordinated. Two shutdown requests can both observe running state and both send signals/kill. There is no `STOPPING` transition state or lock. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown`, `modules/launcher/src/capabilities_runtime_status.py:check_status` | Introduce a transient `STOPPING` state or shutdown guard. Emit transition state before termination and verify final state after. |
| 5 | 🟡 WARNING | `RuntimeStatusChecker.check_status()` emits a status-checked event on every call when an event sink is present. Health probes may call this frequently and flood observability streams. | `modules/launcher/src/capabilities_runtime_status.py:check_status` | Add emission policy: sample, debug-only, or emit only on state change. Keep full event stream optional for diagnostics. |
| 6 | 🟢 INFO | `RegistrationOutcomeVO.source` defaults to `SYSTEM_PATH`. Failed registration outcomes can misleadingly report `source=SYSTEM_PATH` even when no source was selected. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:RegistrationOutcomeVO` | Make `source` optional or add a `NONE` registration source. Set source only when registration succeeds. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `locate_and_register()` receives `config` and uses it to build candidates, but `_register()` does not use that config. It calls `getattr(self._config_provider, "set_executable_path", None)`, which is absent in the default container wiring. Registration therefore does not persist or update the authoritative config. | `modules/launcher/src/capabilities_executable_locator.py:locate_and_register`, `_register`, `modules/launcher/src/root_launcher_container.py:wire` | Inject `PersistStateProtocol` or a mutable config registry into `ExecutableLocator`. Persist the registered executable path as part of registration. |
| 2 | 🟡 WARNING | `RegistrationOutcomeVO.warning` exists but is never set. FR-LAU-001 requires version compatibility warning for out-of-range versions. | `modules/launcher/src/capabilities_executable_locator.py:locate_and_register`, `_check_compatibility` | Return compatibility warnings in `RegistrationOutcomeVO.warning` when version is outside supported range but policy allows continuation. |
| 3 | 🟡 WARNING | Launch, shutdown, registration, and persistence failures return only free-text `error` strings. The FRD error categories are not machine-readable. | `modules/launcher/src/capabilities_process_launcher.py:launch`, `modules/launcher/src/capabilities_process_shutdown.py:shutdown`, `modules/launcher/src/capabilities_executable_locator.py:locate_and_register` | Add `error_code` fields to outcome VOs and set them using `LauncherErrorCode`. Keep detailed message separate. |
| 4 | 🟡 WARNING | `RuntimeStatusChecker.check_status()` calls the event sink directly. If the event sink raises, the status check fails even though status is a read-only health operation. | `modules/launcher/src/capabilities_runtime_status.py:check_status` | Wrap event emission in try/except and log failure. Observability must not break health checks. |
| 5 | 🟡 WARNING | `StatePersistence._load_impl()` catches `OSError`, `JSONDecodeError`, and `ValueError`, but malformed fields can raise `TypeError` during conversion, e.g. unexpected non-numeric `launch_timestamp`. This can crash instead of falling back to empty state. | `modules/launcher/src/capabilities_state_persistence.py:_load_impl`, `_from_dict` | Catch `TypeError` as well, or validate field types before constructing `RuntimeStateVO`. Emit a corruption warning. |
| 6 | 🟡 WARNING | `process_probe_readiness()` uses a hardcoded 0.2 second poll interval and ignores `LauncherConfigVO.readiness_probe_interval_seconds`. | `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness`, `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO.readiness_probe_interval_seconds` | Pass probe interval from config through the readiness probe boundary, or add a utility parameter with config-derived value. |
| 7 | 🟡 WARNING | `process_spawn()` does not create a new process group/session. FR-LAU-003 requires orphaned child cleanup where detectable and safe, but current spawn mechanics make child discovery/cleanup harder. | `modules/shared/src/launcher/utility_process_ops.py:process_spawn` | Use `start_new_session=True` on POSIX or equivalent platform-safe process group creation. Document Windows behavior. |
| 8 | 🟢 INFO | `StatePersistence._atomic_write()` fsyncs the temporary file but not the containing directory. On some filesystems, rename durability may not be guaranteed after power loss. | `modules/launcher/src/capabilities_state_persistence.py:_atomic_write` | Optionally fsync the directory after `os.replace()` where supported. |
| 9 | 🟢 INFO | `ExecutableLocator._detect_version()` extracts the first numeric token from stdout. This can misinterpret non-Blender output as a version. | `modules/launcher/src/capabilities_executable_locator.py:_detect_version` | Require Blender-specific output markers and parse version only after authenticity is confirmed. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-LAU-002 acceptance criteria for “bridge endpoint settings passed” cannot be tested because the contract has no bridge endpoint input. | `modules/shared/src/launcher/contract_launch_protocol.py:LaunchProtocol.launch` | Add `LaunchRequestVO` with bridge endpoint settings. Write acceptance tests asserting spawn receives endpoint/protocol information without leaking secrets. |
| 2 | 🟡 WARNING | FRD error categories cannot be asserted in tests because outcomes expose only strings. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:LaunchOutcomeVO`, `ShutdownOutcomeVO`, `RegistrationOutcomeVO` | Add `error_code` enum fields. Add tests mapping each failure path to an FRD error category. |
| 3 | 🟡 WARNING | Corrupt-state warning behavior cannot be verified because `load()` returns only `None`. | `modules/shared/src/launcher/contract_persist_state_protocol.py:PersistStateProtocol.load` | Add `LoadOutcomeVO` or event-sink emission. Add tests for corrupt JSON, malformed fields, and missing file. |
| 4 | 🟡 WARNING | Event payload completeness cannot be verified because duration/method/reason are not consistently emitted. | `modules/launcher/src/capabilities_process_launcher.py:launch`, `modules/launcher/src/capabilities_process_shutdown.py:shutdown` | Add tests asserting event category, state transition, method, duration, and redacted reason for each lifecycle event. |
| 5 | 🟡 WARNING | The `locate_and_register(config, override)` signature makes acceptance tests ambiguous: should caller config or injected config win? Current behavior mixes both. | `modules/launcher/src/capabilities_executable_locator.py:locate_and_register` | Define single config authority. Add tests for override, configured path, environment, platform, and system PATH using that authority. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FRD “Depends On security policy” is not traced in launcher code. There is no security/redaction dependency, no auth-material handling boundary, and exception/path strings may be emitted without redaction. | `modules/launcher/FRD.md:Depends On`, `modules/launcher/src/capabilities_process_launcher.py:_emit`, `modules/launcher/src/capabilities_state_persistence.py:_contains_secret` | Introduce a security/redaction port or inject security policy. Redact event reasons, persistence warnings, and bridge endpoint summaries. |
| 2 | 🟡 WARNING | FRD “Depends On config” is only partially traced. `LauncherConfigVO` exists, but there is no integration with a config feature and several config keys are unused. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO`, `modules/launcher/src/root_launcher_container.py:wire` | Wire launcher config from the config feature. Trace each FRD configuration key to code usage. |
| 3 | 🟡 WARNING | FRD “Provides To diagnostics” is not fully traced. Status output lacks diagnostics-friendly metadata and event emission is not wired by default. | `modules/launcher/FRD.md:Provides To`, `modules/shared/src/launcher/taxonomy_launcher_vo.py:RuntimeStatusVO`, `modules/launcher/src/root_launcher_container.py:wire` | Add diagnostics metadata to status VO and wire event sink. Define a health composition contract if diagnostics consumes launcher state. |
| 4 | 🟡 WARNING | FRD error categories are not traced to runtime outcomes. Taxonomy error classes exist but are mostly unused by capabilities. | `modules/shared/src/launcher/taxonomy_launcher_error.py`, capability outcome VOs | Map FRD error categories to `LauncherErrorCode` or use taxonomy errors internally and translate to outcome error codes. |
| 5 | 🟡 WARNING | FRD events are partially traced. Event constants and event VO exist, but some events are missing required payload fields and default container does not wire an event sink. | `modules/shared/src/launcher/taxonomy_launcher_constant.py`, `modules/shared/src/launcher/taxonomy_launcher_event.py`, `modules/launcher/src/root_launcher_container.py:wire` | Wire event sink and ensure each FRD event has complete payload fields. Add integration tests for event emission. |

## Violations
Potential AES-related observations for this second review:

- **Potential AES405 — Agent aggregate boundary leakage**: `LauncherOrchestrator` exposes a `status` property returning `RuntimeStatusProtocol`, but this property is not part of `ILauncherOperateAggregate`. If surfaces consume this property, they bypass the aggregate contract. Prefer exposing diagnostics/status through an explicit aggregate method or a separate diagnostics contract.
- **Potential AES402 concern — primitive error messages in contracts/outcomes**: Outcome VOs use raw `str` error messages. This is not necessarily an AES402 violation because VOs may use primitives, but it weakens contract semantics. Introduce error-code enums or error VOs for domain-meaningful failures.
- **No confirmed AES201 import-boundary violations detected** in the provided launcher files.
- **No confirmed AES304 bypass-comment violations detected** in the provided launcher files.
- **No confirmed AES403 capability protocol violations detected**: capabilities implement their corresponding protocol ABCs.

## Action Items (For Developer)
- [ ] P0 Change `ILauncherOperateAggregate.locate_and_register()` to accept only optional override; inject config internally.
- [ ] P0 Introduce `LaunchRequestVO` and `BridgeEndpointSettingsVO`; update `LaunchProtocol`, aggregate, orchestrator, and `ProcessLauncher`.
- [ ] P0 Make launch/shutdown/registration persist runtime state internally instead of relying on external `persist()` calls.
- [ ] P0 Resolve configuration authority: use one injected config provider or one passed config object consistently.
- [ ] P1 Introduce `LauncherErrorCode` enum and add `error_code` fields to all outcome VOs.
- [ ] P1 Introduce `ShutdownRequestVO` with explicit force/escalation confirmation semantics.
- [ ] P1 Add diagnostics metadata to `RuntimeStatusVO`: process reference, bridge endpoint summary, probe duration, classification reason.
- [ ] P1 Add `LoadOutcomeVO` or warning emission to persistence load path.
- [ ] P1 Make event emission safe: catch event sink errors and never fail status checks because of observability failures.
- [ ] P1 Populate event `duration_ms`, `method`, and redacted `reason_summary` consistently.
- [ ] P1 Integrate security/redaction policy for event reasons, persistence warnings, and endpoint summaries.
- [ ] P2 Use config-driven readiness probe interval instead of hardcoded 0.2 seconds.
- [ ] P2 Create process group/session on spawn to support orphan child cleanup.
- [ ] P2 Add tests for contract alignment, error codes, event payloads, corrupt state warnings, and config authority.

## Proposed Fixes / Reference Code

### `modules/shared/src/launcher/taxonomy_launcher_vo.py`

Add error codes, bridge endpoint settings, request VOs, and load outcome.

```python
class LauncherErrorCode(str, Enum):
    """FRD error categories mapped to machine-readable codes."""

    BLENDER_NOT_RUNNING = "blender_not_running"
    STATE_ERROR = "state_error"
    CONFIGURATION_ERROR = "configuration_error"
    TIMEOUT_ERROR = "timeout_error"
    LAUNCH_ERROR = "launch_error"
    VALIDATION_ERROR = "validation_error"
    TERMINATION_ERROR = "termination_error"


@dataclass(frozen=True)
class BridgeEndpointSettingsVO:
    """Bridge endpoint settings for launcher integration."""

    host: str
    port: int
    protocol_version: str | None = None


@dataclass(frozen=True)
class LaunchRequestVO:
    """FR-LAU-002 launch input."""

    mode: LaunchMode = LaunchMode.INTERFACE
    readiness_timeout: TimeoutSeconds | None = None
    bridge_endpoint: BridgeEndpointSettingsVO | None = None


@dataclass(frozen=True)
class ShutdownRequestVO:
    """FR-LAU-003 shutdown input."""

    force_requested: bool = False
    escalation_confirmed: bool = True


@dataclass(frozen=True)
class LoadOutcomeVO:
    """FR-LAU-005 load result with warnings."""

    state: RuntimeStateVO | None = None
    warnings: tuple[str, ...] = dc_field(default_factory=tuple)
    corrupted: bool = False
```

Add error-code fields to outcomes:

```python
@dataclass(frozen=True)
class RegistrationOutcomeVO:
    executable: ExecutableReferenceVO | None = None
    source: RegistrationSource | None = None
    registered: bool = False
    warning: str | None = None
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class LaunchOutcomeVO:
    success: bool = False
    process_id: int | None = None
    ready: bool = False
    bridge_endpoint: str | None = None
    duration_ms: float = 0.0
    launch_method: LaunchMethod = LaunchMethod.SPAWN
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class ShutdownOutcomeVO:
    success: bool = False
    termination_method: TerminationMethod = TerminationMethod.NONE
    duration_ms: float = 0.0
    final_state: RuntimeState = RuntimeState.NOT_RUNNING
    escalated: bool = False
    error_code: LauncherErrorCode | None = None
    error_message: str | None = None
```

Extend runtime status for diagnostics:

```python
@dataclass(frozen=True)
class RuntimeStatusVO:
    state: RuntimeState = RuntimeState.NOT_RUNNING
    process_id: int | None = None
    process_reference: str = ""
    bridge_endpoint_summary: str | None = None
    ready: bool = False
    stale: bool = False
    uptime_seconds: float | None = None
    probe_duration_ms: float = 0.0
    depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT
```

---

### `modules/shared/src/launcher/contract_launcher_operate_aggregate.py`

Hide config from surface and use request VOs.

```python
class ILauncherOperateAggregate(ABC):
    """Aggregate facade for launcher operations."""

    @abstractmethod
    def locate_and_register(self, override: FilePath | None = None) -> RegistrationOutcomeVO:
        """FR-LAU-001: Locate and register Blender using injected configuration."""
        ...

    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """FR-LAU-002: Launch Blender and confirm readiness."""
        ...

    @abstractmethod
    def shutdown(self, request: ShutdownRequestVO) -> ShutdownOutcomeVO:
        """FR-LAU-003: Graceful-then-force shutdown."""
        ...

    @abstractmethod
    def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
        """FR-LAU-004: Verify true runtime status."""
        ...

    @abstractmethod
    def persist(self, state: RuntimeStateVO) -> PersistenceOutcomeVO:
        """FR-LAU-005: Persist runtime state. Should not be required for normal lifecycle."""
        ...
```

---

### `modules/shared/src/launcher/contract_launch_protocol.py`

```python
class LaunchProtocol(ABC):
    """Protocol interface for launching Blender with bridge readiness."""

    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """Start Blender with integration component active and confirm bridge readiness."""
        ...
```

---

### `modules/launcher/src/agent_launcher_orchestrator.py`

Update orchestration and remove non-aggregate status property or move it to an explicit diagnostics contract.

```python
def locate_and_register(self, override: FilePath | None = None) -> RegistrationOutcomeVO:
    return self._locate.locate_and_register(override)


def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
    return self._launch.launch(request)


def shutdown(self, request: ShutdownRequestVO) -> ShutdownOutcomeVO:
    return self._shutdown.shutdown(request)
```

If diagnostics needs status, define a separate aggregate/protocol instead of exposing `RuntimeStatusProtocol` directly:

```python
# Preferred: add to a diagnostics-facing aggregate, not agent public property.
@abstractmethod
def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO: ...
```

---

### `modules/launcher/src/capabilities_executable_locator.py`

Use one config authority and return categorized errors/warnings.

```python
def locate_and_register(self, override: FilePath | None = None) -> RegistrationOutcomeVO:
    config = self._config_provider()
    candidates = self._build_candidate_order(config, override)

    if not candidates:
        return RegistrationOutcomeVO(
            registered=False,
            error_code=LauncherErrorCode.CONFIGURATION_ERROR,
            error_message="No candidate locations available",
        )

    for source, path in candidates:
        if not path or not os.path.exists(path):
            continue

        try:
            ref, warning = self._validate(path, config)
        except ExecutableValidationError as exc:
            continue

        self._register(config, ref)
        self._emit_registered(source, ref.path)

        return RegistrationOutcomeVO(
            executable=ref,
            source=source,
            registered=True,
            warning=warning,
        )

    return RegistrationOutcomeVO(
        registered=False,
        error_code=LauncherErrorCode.VALIDATION_ERROR,
        error_message="No valid Blender executable found",
    )
```

Registration should persist authoritative state:

```python
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

---

### `modules/launcher/src/capabilities_runtime_status.py`

Make event emission safe and add diagnostics metadata.

```python
def check_status(self, depth: ProbeDepth = ProbeDepth.LIGHTWEIGHT) -> RuntimeStatusVO:
    start = time.monotonic()

    pid = self._resolve_pid()
    if pid is None:
        return RuntimeStatusVO(state=RuntimeState.NOT_RUNNING, depth=depth)

    alive = self._is_alive(pid)
    state = RuntimeState.RUNNING_READY if alive else RuntimeState.NOT_RUNNING

    duration_ms = (time.monotonic() - start) * 1000.0

    status = RuntimeStatusVO(
        state=state,
        process_id=pid,
        process_reference=str(pid),
        ready=alive,
        probe_duration_ms=duration_ms,
        depth=depth,
    )

    self._emit_status_checked(status)
    return status


def _emit_status_checked(self, status: RuntimeStatusVO) -> None:
    if self._events is None:
        return

    try:
        self._events(
            LauncherLifecycleEvent(
                event_category=LAUNCHER_EVENT_STATUS_CHECKED,
                state_before=status.state,
                state_after=status.state,
                process_reference=status.process_reference,
                duration_ms=DurationMs(status.probe_duration_ms),
                reason_summary=f"depth={status.depth.value}",
            )
        )
    except Exception:
        logger.warning("status event emission failed", exc_info=True)
```

---

### `modules/launcher/src/capabilities_state_persistence.py`

Expose warnings from load and catch malformed type errors.

```python
def load_with_warnings(self) -> LoadOutcomeVO:
    with self._lock:
        path = self._resolve_path()
        if not path or not os.path.exists(path):
            return LoadOutcomeVO(state=None)

        try:
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)

            if not isinstance(data, dict):
                return LoadOutcomeVO(
                    state=None,
                    warnings=("Persisted state is not a JSON object",),
                    corrupted=True,
                )

            return LoadOutcomeVO(state=self._from_dict(data))

        except (OSError, json.JSONDecodeError, ValueError, TypeError) as exc:
            return LoadOutcomeVO(
                state=None,
                warnings=(f"Persisted state unreadable: {exc}",),
                corrupted=True,
            )
```

---

### `modules/shared/src/launcher/utility_process_ops.py`

Use configurable probe interval and create process session for cleanup support.

```python
def process_spawn(executable: str, mode: str) -> int:
    args = [executable]

    if mode == "headless":
        args += ["--background", "--python-exit-code", "1"]

    proc = subprocess.Popen(
        args,
        start_new_session=True,
    )
    return proc.pid


def process_probe_readiness(
    process_id: int,
    timeout_seconds: float,
    interval_seconds: float = 0.2,
) -> bool:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if not process_alive(process_id):
            return False
        time.sleep(interval_seconds)

    return True
```

```

```
