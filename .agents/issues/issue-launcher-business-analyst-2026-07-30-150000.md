 `.agents/issues/issue-launcher-business-analyst-2026-07-30-150000.md`

```markdown
# Issue: launcher — Business Logic & Requirements Review

## Summary
The launcher module implements 5 FRD requirements (FR-LAU-001 through FR-LAU-005) across 5 capabilities, 5 contracts, 1 aggregate, and 1 utility. Critical gaps exist: the launch capability does not activate the Blender integration component (addon) or pass bridge endpoint settings — making "readiness" equivalent to mere process liveness rather than true integration readiness as specified. The version compatibility check is a no-op (always returns SUPPORTED). The container wires `bridge_probe=None`, rendering FULL-depth status checks incapable of detecting bridge unresponsiveness. No lifecycle events are emitted because no event sink is wired. Post-launch and post-shutdown state persistence is not orchestrated, leaving persisted state stale after every lifecycle transition.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-LAU-002 "Activates integration component during startup" — unclear whether this means passing `--addons` flag, injecting a startup script, or relying on Blender's addon auto-enable. The implementation does none of these. | `modules/launcher/FRD.md`:FR-LAU-002 Rules | Specify the exact activation mechanism (e.g., "pass `--python-use-addon <path>` flag" or "write addon enable command to bridge after spawn"). |
| 2 | 🟡 WARNING | FR-LAU-002 "Readiness = process liveness + bridge readiness signal" — no definition of what constitutes a "bridge readiness signal". Is it a TCP connect success? A specific JSON message? An HTTP health endpoint? | `modules/launcher/FRD.md`:FR-LAU-002 Rules | Define the readiness signal protocol (e.g., "TCP connect to bridge port succeeds AND returns `{"status":"ready"}` within probe timeout"). |
| 3 | 🟡 WARNING | FR-LAU-001 "Must validate as genuine Blender runtime" — no criteria specified for what makes an executable "genuine Blender". Is `--version` output containing "Blender" sufficient? | `modules/launcher/FRD.md`:FR-LAU-001 Rules | Define validation criteria: exit code 0 from `--version` AND stdout contains "Blender" AND version parseable. |
| 4 | 🟢 INFO | FR-LAU-003 "Orphaned child processes cleaned up where detectable + safe" — "safe" is undefined. When is cleanup unsafe? | `modules/launcher/FRD.md`:FR-LAU-003 Rules | Define: "unsafe = child process is not in the Blender process tree OR child has its own session leader". |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-LAU-002 requires "Activates integration component during startup" and "Passes bridge endpoint settings + protocol info". The `ProcessLauncher` calls `self._spawner(executable, mode.value, timeout)` which invokes `process_spawn(executable, mode)` — this only passes `--background --python-exit-code 1` for headless mode. No addon activation, no bridge endpoint config, no protocol info is passed to the Blender process. The launched Blender will NOT have the MCP bridge active. | `modules/launcher/src/capabilities_process_launcher.py`:62-64, `modules/shared/src/launcher/utility_process_ops.py`:72-78 | Extend `process_spawn` to accept bridge config (host, port, addon path) and pass appropriate CLI flags or startup script. |
| 2 | 🔴 CRITICAL | `RuntimeStatusChecker` is wired with `bridge_probe=None` in the container. FULL-depth status checks (`ProbeDepth.FULL`) will always report `ready=True` for any alive process, making it impossible to detect "running but unresponsive" state — a core FR-LAU-004 classification. | `modules/launcher/src/root_launcher_container.py`:52-57 | Wire a real bridge probe (e.g., TCP connect to bridge port with 1s timeout). |
| 3 | 🟡 WARNING | FR-LAU-002 "Process alive without bridge readiness → launch failure or degraded per policy" — `ProcessLauncher` uses `process_probe_readiness(pid, timeout)` which only polls `process_alive(pid)`. It never checks bridge readiness. A Blender process that starts but crashes its addon will be reported as "ready". | `modules/launcher/src/capabilities_process_launcher.py`:66-67, `modules/shared/src/launcher/utility_process_ops.py`:81-90 | Replace liveness-only probe with a bridge readiness probe (TCP connect or protocol handshake). |
| 4 | 🟡 WARNING | FR-LAU-003 "Persisted state updated to stopped" — `ProcessShutdown` never calls `PersistStateProtocol.persist()` after successful shutdown. The persisted state file will still show the old PID as running, causing stale state on next startup. | `modules/launcher/src/capabilities_process_shutdown.py`:entire file | Inject `PersistStateProtocol` into shutdown capability (or orchestrate via agent) and persist `NOT_RUNNING` state after successful termination. |
| 5 | 🟡 WARNING | FR-LAU-002 "Emits lifecycle event" — `ProcessLauncher._emit` checks `if self._events is not None` but the container never injects an event sink. All events are silently dropped. Same applies to `ExecutableLocator`, `ProcessShutdown`, and `RuntimeStatusChecker`. | `modules/launcher/src/root_launcher_container.py`:44-72 | Wire an event sink (e.g., diagnostics event publisher) into all capabilities. |
| 6 | 🟡 WARNING | FR-LAU-003 "Shutdown during launch → resolve launch state first" — no coordination between launch and shutdown. If `shutdown()` is called while `launch()` is in its readiness wait loop, both will race on the same PID with undefined behavior. | `modules/launcher/src/capabilities_process_shutdown.py`, `capabilities_process_launcher.py` | Add a launch-in-progress guard (e.g., threading.Event) that shutdown checks before proceeding. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `ExecutableLocator._check_compatibility` always returns `VersionCompatibility.SUPPORTED` if a version string exists, and `UNKNOWN` if empty. It never parses the version or compares against `config.supported_version_range`. FR-LAU-001 "Version compared against supported range; outside → warning or rejection per policy" is completely unimplemented. | `modules/launcher/src/capabilities_executable_locator.py`:96-99 | Implement semantic version parsing and range comparison. Return WARNING or UNSUPPORTED for out-of-range versions. |
| 2 | 🟡 WARNING | `ExecutableLocator._validate` checks `os.path.isfile(canonical)` and `os.access(canonical, os.X_OK)` but does NOT verify the executable is actually Blender. Any executable file passes validation. FR-LAU-001 "Must validate as genuine Blender runtime" is unimplemented. | `modules/launcher/src/capabilities_executable_locator.py`:88-93 | After path checks, run `--version` and verify output contains "Blender" before accepting. |
| 3 | 🟡 WARNING | `RuntimeStatusChecker` has no PID reuse guard beyond `process_alive()`. On Linux, `os.kill(pid, 0)` returns True for ANY process with that PID — including a completely unrelated process that reused the PID after Blender exited. FR-LAU-004 "guard against PID reuse" requires comparing process start time or command line. | `modules/launcher/src/capabilities_runtime_status.py`:62-64 | Store process start time at launch; on status check, compare `/proc/<pid>/stat` start time (Linux) or use `psutil.Process(pid).create_time()`. |
| 4 | 🟡 WARNING | `ProcessShutdown._wait_exit` polls status every 50ms but `RuntimeStatusChecker.check_status` calls `self._resolve_pid()` which reads persisted state. If persisted state is stale (PID from previous session), shutdown will wait for a PID that may belong to another process. | `modules/launcher/src/capabilities_process_shutdown.py`:89-95 | Use the PID from the initial status check directly in the wait loop, not re-resolved from persisted state each iteration. |
| 5 | 🟢 INFO | `StatePersistence._contains_secret` checks top-level keys only. Nested secret-like keys (e.g., `bridge_endpoint` containing a token in URL query params) are not detected. | `modules/launcher/src/capabilities_state_persistence.py`:72-77 | Apply recursive key scanning or pattern-match values for common secret formats. |
| 6 | 🟢 INFO | `LauncherOrchestrator` is pure 1:1 delegation with no coordination. FR-LAU-002 implies launch should persist state after success; FR-LAU-003 implies shutdown should update persisted state. The orchestrator does not coordinate these cross-capability flows. | `modules/launcher/src/agent_launcher_orchestrator.py`:entire file | Add post-launch persist call and post-shutdown persist call in the orchestrator (orchestration, not business logic). |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-LAU-001 QA "Stale path re-validated before use" — no re-validation trigger exists. The code validates during `locate_and_register` but never re-validates a previously registered path on subsequent launches. Unverifiable. | `modules/launcher/src/capabilities_executable_locator.py` | Add staleness check in `ProcessLauncher.launch()`: if executable mtime changed or path missing, re-run locate before spawn. |
| 2 | 🟡 WARNING | FR-LAU-004 QA "PID reuse guard prevents false alive" — no test can verify this because the guard is not implemented. The acceptance criterion is untestable against current code. | `modules/launcher/src/capabilities_runtime_status.py` | Implement start-time comparison, then write a test that spawns a dummy process, records PID, kills it, spawns another (likely same PID), and verifies stale detection. |
| 3 | 🟡 WARNING | FR-LAU-005 QA "Atomic crash-safe writes" — `StatePersistence._atomic_write` uses `tempfile.mkstemp` + `os.replace` which is atomic on POSIX but not guaranteed on Windows (where `os.replace` may fail if target is locked). No cross-platform test exists. | `modules/launcher/src/capabilities_state_persistence.py`:97-106 | Add Windows-specific handling (retry with backoff on PermissionError) and a cross-platform integration test. |
| 4 | 🟢 INFO | No test files exist for the launcher module. All 5 capabilities, the orchestrator, and the utility lack unit/integration tests. | `modules/launcher/` | Create test suite per create-test-python skill. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-LAU-002 specifies "Passes bridge endpoint settings + protocol info" and "Auth material through security policy, never logged". No code path passes bridge settings to the spawned process. No security policy integration exists. The FR is partially implemented (spawn works) but the critical integration activation is missing. | `modules/launcher/src/capabilities_process_launcher.py`, `modules/shared/src/launcher/utility_process_ops.py`:72-78 | Extend spawn to accept and pass bridge config. Integrate security policy for auth material handling. |
| 2 | 🟡 WARNING | FR-LAU Events section lists 7 events. Event dataclasses exist (`LauncherLifecycleEvent`) and capabilities have `_emit` methods, but the container wires `event_sink=None` for all capabilities. Events are structurally present but never delivered. Traceability from FRD event → runtime emission is broken. | `modules/launcher/src/root_launcher_container.py`:44-72 | Wire a concrete event sink (e.g., `diagnostics.publish_event`) into all capabilities. |
| 3 | 🟡 WARNING | FR-LAU Configuration Keys table lists 10 keys. `LauncherConfigVO` has fields for all 10, but the container hardcodes `LauncherConfigVO()` with defaults. No config feature integration reads actual user configuration. | `modules/launcher/src/root_launcher_container.py`:36 | Accept config from the config feature module rather than defaulting. |
| 4 | 🟢 INFO | `taxonomy_launcher_constant.py` removed `LAUNCHER_SOURCE_FEATURE` with a comment "REMOVED: never imported". This is good cleanup, but the comment itself is noise for production code. | `modules/shared/src/launcher/taxonomy_launcher_constant.py`:33-34 | Remove the comment entirely; git history preserves the rationale. |

## Violations
- **AES405 (Agent Role)**: `LauncherOrchestrator` performs pure 1:1 delegation without coordinating cross-capability flows (launch→persist, shutdown→persist). While not a strict AES violation, it violates the FRD's implied orchestration responsibility.
- **AES201 (Forbidden Import)**: No violations detected.
- **AES403 (Capabilities Role)**: All capabilities implement their protocol ABC. Type count ≤ 3 per file (including internal Protocol helpers). No violations.
- **AES404 (Utility Role)**: `utility_process_ops.py` contains only stateless functions, imports only stdlib + taxonomy. No violations.
- **AES503 (Capabilities Orphan)**: All 5 capabilities are wired in the container. No orphans.
- **AES304 (Bypass Comment)**: No bypass patterns detected.

## Action Items (For Developer)
- [ ] P0: Extend `process_spawn` to accept bridge config (host, port, addon path) and pass activation flags to Blender
- [ ] P0: Wire a real `bridge_probe` in the container (TCP connect to bridge port with timeout)
- [ ] P0: Implement actual version compatibility checking in `ExecutableLocator._check_compatibility`
- [ ] P1: Add Blender authenticity validation (verify `--version` output contains "Blender")
- [ ] P1: Wire event sink into all capabilities from the container
- [ ] P1: Add post-launch and post-shutdown state persistence orchestration in `LauncherOrchestrator`
- [ ] P1: Implement PID reuse guard using process start-time comparison
- [ ] P2: Add launch-in-progress guard to prevent shutdown race during readiness wait
- [ ] P2: Integrate config feature for `LauncherConfigVO` population instead of hardcoded defaults
- [ ] P2: Implement stale path re-validation before launch
- [ ] P3: Add cross-platform atomic write handling for Windows
- [ ] P3: Remove "REMOVED" comment from taxonomy_launcher_constant.py

## Proposed Fixes / Reference Code

### File: `modules/shared/src/launcher/utility_process_ops.py` (extended spawn)

```python
def process_spawn(
    executable: str,
    mode: str,
    bridge_host: str = "localhost",
    bridge_port: int = 9876,
    addon_path: str | None = None,
) -> int:
    """Spawn a Blender process with bridge configuration.

    Passes bridge endpoint settings and optionally activates the
    integration addon via startup script.
    """
    args = [executable]
    if mode == "headless":
        args += ["--background", "--python-exit-code", "1"]

    # Pass bridge endpoint configuration via environment
    env = os.environ.copy()
    env["BLENDER_BRIDGE_HOST"] = bridge_host
    env["BLENDER_BRIDGE_PORT"] = str(bridge_port)

    # Activate integration component if addon path provided
    if addon_path:
        args += ["--python-use-addon", addon_path]

    proc = subprocess.Popen(args, env=env)
    return proc.pid
```

### File: `modules/launcher/src/capabilities_executable_locator.py` (version check fix)

```python
def _check_compatibility(self, version: str, config: LauncherConfigVO) -> VersionCompatibility:
    """Compare detected version against supported range."""
    if not version:
        return VersionCompatibility.UNKNOWN
    if not config.supported_version_range:
        return VersionCompatibility.UNKNOWN

    try:
        major = int(version.split(".")[0])
    except (ValueError, IndexError):
        return VersionCompatibility.UNKNOWN

    # Parse range like "3.0-5.x" or ">=3.0,<6.0"
    # Simplified: extract min/max major versions
    range_str = config.supported_version_range
    if "-" in range_str:
        parts = range_str.split("-")
        min_major = int(parts[0].split(".")[0])
        max_major = int(parts[1].split(".")[0])
    else:
        min_major = max_major = int(range_str.split(".")[0])

    if major < min_major or major > max_major:
        return VersionCompatibility.UNSUPPORTED
    if major == min_major or major == max_major:
        return VersionCompatibility.WARNING  # edge of support
    return VersionCompatibility.SUPPORTED
```

### File: `modules/launcher/src/root_launcher_container.py` (bridge probe + event wiring)

```python
def wire(self) -> None:
    if self._wired:
        return
    logger.info("Wiring launcher feature module")

    # Event sink — wire to diagnostics if available
    event_sink = self._event_sink  # injected from caller

    persist_cap: PersistStateProtocol = StatePersistence(
        path_resolver=lambda: self._state_path,
    )

    # Bridge probe — TCP connect to configured bridge port
    bridge_host = self._config.bridge_host if hasattr(self._config, "bridge_host") else "localhost"
    bridge_port = self._config.bridge_port if hasattr(self._config, "bridge_port") else 9876

    def _bridge_probe(timeout_seconds: float) -> bool:
        import socket

        try:
            with socket.create_connection((bridge_host, bridge_port), timeout=timeout_seconds):
                return True
        except (OSError, ConnectionRefusedError):
            return False

    status_cap: RuntimeStatusProtocol = RuntimeStatusChecker(
        liveness_checker=process_alive,
        pid_resolver=lambda: self._resolve_persisted_pid(persist_cap),
        bridge_probe=_bridge_probe,  # REAL probe, not None
        persisted_state_resolver=persist_cap.load,
        stale_reconciliation_enabled=self._config.stale_reconciliation_enabled,
        event_sink=event_sink,
    )

    locate_cap: LocateRegisterProtocol = ExecutableLocator(
        config_provider=lambda: self._config,
        command_runner=lambda args, timeout=5.0: process_version_check(args, timeout),
        event_sink=event_sink,
    )

    launch_cap: LaunchProtocol = ProcessLauncher(
        executable_resolver=lambda: self._config.executable_path,
        status_protocol=status_cap,
        spawner=lambda executable, mode, _timeout: process_spawn(
            executable,
            mode,
            bridge_host=bridge_host,
            bridge_port=bridge_port,
        ),
        readiness_probe=lambda pid, timeout: process_probe_readiness(pid, timeout),
        event_sink=event_sink,
    )

    shutdown_cap: ShutdownProtocol = ProcessShutdown(
        status_protocol=status_cap,
        signal_sender=process_signal_term,
        killer=process_kill,
        timeout_seconds=self._config.shutdown_timeout_seconds,
        force_enabled=self._config.force_termination_enabled,
        event_sink=event_sink,
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
```

### File: `modules/launcher/src/agent_launcher_orchestrator.py` (post-action persistence)

```python
def launch(
    self, mode: LaunchMode = LaunchMode.INTERFACE, readiness_timeout_seconds: TimeoutSeconds | None = None
) -> LaunchOutcomeVO:
    """Delegate launch, then persist state on success."""
    logger.info("Orchestrating launch (mode=%s)", mode.value)
    outcome = self._launch.launch(mode, readiness_timeout_seconds)
    if outcome.success and outcome.process_id is not None:
        # FR-LAU-005: persist state after successful launch
        import time

        state = RuntimeStateVO(
            executable_path="",  # resolved from config
            process_id=outcome.process_id,
            launch_timestamp=time.time(),
            bridge_endpoint=outcome.bridge_endpoint,
            last_status=RuntimeState.RUNNING_READY if outcome.ready else RuntimeState.STARTING,
        )
        self._persist.persist(state)
    return outcome


def shutdown(self, force: bool = False, allow_escalation: bool = True) -> ShutdownOutcomeVO:
    """Delegate shutdown, then persist stopped state on success."""
    logger.info("Orchestrating shutdown (force=%s)", force)
    outcome = self._shutdown.shutdown(force, allow_escalation)
    if outcome.success:
        # FR-LAU-003/005: update persisted state to stopped
        state = RuntimeStateVO(
            executable_path="",
            process_id=None,
            launch_timestamp=0.0,
            bridge_endpoint=None,
            last_status=RuntimeState.NOT_RUNNING,
        )
        self._persist.persist(state)
    return outcome
```

```

---

Both issue documents are ready for the Developer/Fullstack role to execute. The dispatcher has 3 CRITICAL findings (broken sync dispatch wiring, execution mode override, untyped executor) and the launcher has 3 CRITICAL findings (no addon activation, null bridge probe, no-op version check).
```
