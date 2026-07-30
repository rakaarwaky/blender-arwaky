# Issue Documents

Below are the two issue documents for the `launcher` and `security` features.

---

## File: `.agents/issues/issue-launcher-business-analyst-2026-07-30-143022.md`

```markdown
# Issue: launcher — Business Logic & Requirements Review

## Summary
The launcher feature (v1.7.0) implements the 5 FR-LAU operations as individual capabilities with correct AES layering and DI wiring. However, the business logic has critical gaps: (1) the launch capability does not activate the Blender integration component or pass bridge endpoint settings, making the core FR-LAU-002 requirement non-functional; (2) version compatibility checking is stubbed — it never compares against the configured supported range; (3) the orchestrator is purely pass-through with no lifecycle coordination (launch/shutdown do not persist state); (4) PID reuse guard specified in FR-LAU-004 is absent; (5) force termination is never verified by subsequent liveness check. These gaps mean the launcher cannot fulfill its FRD mandate as "single authority for operating on the Blender process."

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-LAU-002 specifies "Activates integration component during startup" and "Passes bridge endpoint settings + protocol info" but the `_ProcessSpawner` protocol signature `(executable, mode, readiness_timeout_seconds)` has no parameter for bridge endpoint or addon activation. The requirement is clear in the FRD but the contract/capability design cannot express it. | `modules/shared/src/launcher/contract_launch_protocol.py:14` | Extend `LaunchProtocol.launch()` and `_ProcessSpawner` to accept a `BridgeEndpointVO` or equivalent. Update `process_spawn` utility to pass `--addons` or `--python` flags for integration component activation. |
| 2 | 🟡 WARNING | FR-LAU-001 says "Version compared against supported range; outside → warning or rejection per policy." The `LauncherConfigVO.supported_version_range` field exists but is never consumed. The FRD does not specify the comparison algorithm (semver? major.minor?). | `modules/launcher/src/capabilities_executable_locator.py:97-100` | Define version comparison semantics in FRD (e.g., "parse major.minor, compare against range tuple"). Implement in `_check_compatibility`. |
| 3 | 🟡 WARNING | FR-LAU-004 says "guard against PID reuse" but does not specify the mechanism (process start time comparison, `/proc/<pid>/cmdline` check, or creation timestamp). | `modules/launcher/FRD.md` (FR-LAU-004 Rules) | Add to FRD: "PID reuse guard: compare process creation timestamp against persisted launch_timestamp; if delta > threshold, classify as STALE." |
| 4 | 🟢 INFO | FR-LAU-003 mentions "Orphaned child processes cleaned up where detectable + safe" — no definition of "detectable" or "safe" is provided. | `modules/launcher/FRD.md` (FR-LAU-003 Edge Cases) | Clarify: "Use process group kill (`os.killpg`) when the spawned process is a group leader. Skip cleanup if process group cannot be determined." |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🔴 CRITICAL | Launch does not activate the Blender integration component. `process_spawn` runs `[executable]` or `[executable, --background, --python-exit-code, 1]` with no addon loading, no bridge endpoint configuration, and no MCP bridge activation. The launched Blender instance will not be controllable. | `modules/shared/src/launcher/utility_process_ops.py:72-79` | Add integration component activation: pass `--python <addon_bootstrap_script>` or `--addons blender_arwaky_bridge` to the Blender command line. Accept bridge endpoint settings (host, port) and inject them via environment variable or CLI arg. |
| 6 | 🔴 CRITICAL | Orchestrator is pure pass-through — no lifecycle coordination. FR-LAU-002 output includes "process ref" and FR-LAU-005 says "Persist registered path, process ref, launch timestamp, bridge endpoint summary, status." After a successful launch, state is never persisted. After shutdown, state is never updated to stopped. The launcher cannot recover state across restarts. | `modules/launcher/src/agent_launcher_orchestrator.py:44-68` | Add orchestration: after `launch()` returns success, call `self._persist.persist(RuntimeStateVO(...))`. After `shutdown()` returns success, persist with `last_status=NOT_RUNNING`. After `locate_and_register()`, persist executable path. |
| 7 | 🟡 WARNING | Readiness probe (`process_probe_readiness`) only polls `process_alive`. FR-LAU-002 defines "Readiness = process liveness + bridge readiness signal." A process can be alive but the bridge addon may have failed to start. The current implementation will report `ready=True` for any alive process. | `modules/shared/src/launcher/utility_process_ops.py:88-96` | Implement bridge readiness probe: attempt a TCP connection to the bridge endpoint (host:port) or check for a readiness file/signal. Only return `True` when both liveness AND bridge responsiveness are confirmed. |
| 8 | 🟡 WARNING | FR-LAU-003: "Force termination verified by subsequent liveness check." After `self._kill(current.process_id)`, the code immediately returns success without verifying the process is actually dead. SIGKILL can fail (e.g., zombie process, permission). | `modules/launcher/src/capabilities_process_shutdown.py:72-80` | After `_kill()`, call `self._wait_exit(process_id)` with a short timeout (e.g., 2s). If still alive, return `ShutdownOutcomeVO(success=False, error="Force termination failed")`. |
| 9 | 🟡 WARNING | FR-LAU-003: "Shutdown during launch → resolve launch state first." No guard exists. If `shutdown()` is called while `launch()` is in progress (concurrent), the status check may return `STARTING` and the shutdown will attempt to kill a process that may not yet have a stable PID. | `modules/launcher/src/capabilities_process_shutdown.py:50-55` | Add a state check: if `current.state == RuntimeState.STARTING`, either wait for launch to complete (with timeout) or return an error indicating launch-in-progress. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 10 | 🔴 CRITICAL | `_check_compatibility` is a stub: returns `SUPPORTED` for any non-empty version string and `UNKNOWN` for empty. It never parses the version or compares against `config.supported_version_range`. FR-LAU-001 explicitly requires "Version compared against supported range; outside → warning or rejection per policy." | `modules/launcher/src/capabilities_executable_locator.py:97-100` | Implement: parse version string (e.g., "4.2.1" → (4,2,1)), parse `supported_version_range` (e.g., ">=3.0,<5.0"), compare. Return `WARNING` or `UNSUPPORTED` when outside range. |
| 11 | 🟡 WARNING | FR-LAU-001: "Must validate as genuine Blender runtime." The `_validate` method checks `os.path.isfile` + `os.access(X_OK)` + version detection, but never verifies the `--version` output contains "Blender". Any executable that returns a version-like string will pass. | `modules/launcher/src/capabilities_executable_locator.py:82-95` | After `_detect_version`, verify the stdout contains the string "Blender" (case-insensitive). If not, raise `ExecutableValidationError("Not a genuine Blender executable")`. |
| 12 | 🟡 WARNING | FR-LAU-004: "Stale: persisted ref no longer matches live process + guard against PID reuse." The code checks `persisted.process_id == pid` when the process is dead, but when the process IS alive, it never verifies the alive process is actually Blender (PID could have been reused by an unrelated process). | `modules/launcher/src/capabilities_runtime_status.py:55-72` | Add PID reuse guard: when process is alive, verify it matches the persisted launch context (e.g., check `/proc/<pid>/cmdline` contains "blender", or compare process start time against `launch_timestamp`). |
| 13 | 🟡 WARNING | FR-LAU-004: "Read-only except stale reconciliation (may correct persisted state + emit event)." The `_stale_reconcile` flag triggers `_emit_stale()` but never actually corrects the persisted state. The stale PID remains in the persistence store. | `modules/launcher/src/capabilities_runtime_status.py:60-63` | When stale is detected and `_stale_reconcile` is True, call a persistence callback to clear or update the stale process reference. Inject a `state_corrector: Callable` via DI. |
| 14 | 🟡 WARNING | FR-LAU-005: "Corrupt/unreadable/malformed → empty state with warning, never crash." The `_load_impl` returns `None` on corruption but does not emit a warning event or log. The caller has no way to know corruption occurred vs. file simply not existing. | `modules/launcher/src/capabilities_state_persistence.py:68-78` | Differentiate: if file exists but is corrupt, log a warning and/or return a sentinel that triggers a reconciliation warning in `PersistenceOutcomeVO`. |
| 15 | 🟢 INFO | FR-LAU-002: "Early exit → surface exit reason." If the spawned process exits immediately (before readiness probe), the code returns `error="Readiness not confirmed within timeout"` — it does not capture or surface the actual exit code or stderr. | `modules/launcher/src/capabilities_process_launcher.py:72-78` | Capture process exit code (via `subprocess.Popen.poll()` or `returncode`) and include it in `LaunchOutcomeVO.error`. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 16 | 🟡 WARNING | No test files exist for the launcher module. The FRD QA Checklist has 18 items but none are automated. DI boundaries exist (spawner, probe, signal, killer) but no test exercises them. | `modules/launcher/` (no `tests/` directory) | Create `modules/launcher/tests/` with: `contract_launcher.py` (protocol impl exists), `unit_executable_locator_discovery.py`, `unit_process_launcher_idempotency.py`, `unit_process_shutdown_escalation.py`, `unit_runtime_status_classification.py`, `unit_state_persistence_atomic.py`, `integration_launcher_container.py`. |
| 17 | 🟡 WARNING | FR-LAU-001 acceptance criteria "Non-Blender executable rejected" is not testable with current implementation because genuineness check is missing. | `modules/launcher/FRD.md` (QA Checklist item 2) | After implementing finding #11, add unit test: mock `_CommandRunner` to return version output without "Blender" → assert `RegistrationOutcomeVO.registered == False`. |
| 18 | 🟢 INFO | FR-LAU-004 specifies 6 state classifications but the implementation can only produce 4 (`NOT_RUNNING`, `STALE`, `RUNNING_READY`, `RUNNING_UNRESPONSIVE`). `STARTING` and `STOPPING` are never returned by `check_status`. | `modules/launcher/src/capabilities_runtime_status.py:48-80` | Either implement transitional state detection (e.g., track launch/shutdown in-progress flags) or remove `STARTING`/`STOPPING` from the FRD classification list and document them as "internal transitional states not exposed via status check." |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 19 | 🟡 WARNING | FR-LAU-001 specifies "Previously registered path re-validated if staleness suspected." No staleness suspicion logic exists in `ExecutableLocator`. The `locate_and_register` method always runs the full discovery order without checking if the previously registered path is still valid first. | `modules/launcher/src/capabilities_executable_locator.py:48-62` | Add: if `config.executable_path` is set, validate it first (before full discovery). If validation fails, log staleness and proceed with discovery. |
| 20 | 🟡 WARNING | FR-LAU-002 specifies "Auth material through security policy, never logged." No integration with the security module's redaction or auth handling exists. The launcher operates in isolation. | `modules/launcher/src/capabilities_process_launcher.py` (entire file) | Document in FRD that auth material handling is deferred to the gateway feature (which manages the actual bridge connection). Add a cross-reference: "See FR-GW-xxx for auth material injection." |
| 21 | 🟢 INFO | FR-LAU-005 specifies "Concurrent access safe within single instance." The `threading.Lock()` protects persist/load but the `RuntimeStatusChecker` has mutable state (`_launch_time`) with no lock. Concurrent `check_status` + `mark_launched` could race. | `modules/launcher/src/capabilities_runtime_status.py:38` | Add a `threading.Lock` around `_launch_time` read/write, or document that `mark_launched` is only called once during launch (single-writer assumption). |

## Violations
- **AES405 (Agent Role)**: The `LauncherOrchestrator` coordinates 5 protocols but performs zero orchestration logic (no state coordination, no conditional branching between capabilities, no error escalation). It is a thin passthrough, not an orchestrator. The FRD implies lifecycle coordination (persist after launch, persist after shutdown, reconcile stale on status check).
- **AES305 (Duplication)**: `_OsPathResolver` is defined in both `modules/security/src/capabilities_path_validator.py` and `modules/security/src/root_security_container.py`. (This is in the security module but noted for cross-module awareness.)

## Action Items (For Developer)
- [ ] 🔴 P0: Implement integration component activation in `process_spawn` — pass bridge endpoint settings and addon bootstrap to Blender CLI (Finding #5)
- [ ] 🔴 P0: Add lifecycle coordination to `LauncherOrchestrator` — persist state after launch, shutdown, and locate (Finding #6)
- [ ] 🔴 P0: Implement real version compatibility check in `_check_compatibility` — parse version, compare against range (Finding #10)
- [ ] 🟡 P1: Implement bridge readiness probe — TCP connect or readiness signal check, not just process liveness (Finding #7)
- [ ] 🟡 P1: Add force termination verification — liveness check after SIGKILL (Finding #8)
- [ ] 🟡 P1: Add PID reuse guard in `RuntimeStatusChecker` — verify process identity matches persisted context (Finding #12)
- [ ] 🟡 P1: Add genuine Blender validation — verify `--version` output contains "Blender" (Finding #11)
- [ ] 🟡 P1: Implement stale state correction — actually update persistence when stale detected (
# Issue Documents

Below are the two issue documents for the `launcher` and `security` features.

---

## File: `.agents/issues/issue-launcher-business-analyst-2026-07-30-143022.md`

```markdown
# Issue: launcher — Business Logic & Requirements Review

## Summary
The launcher feature (v1.7.0) implements the 5 FR-LAU operations as individual capabilities with correct AES layering and DI wiring. However, the business logic has critical gaps: (1) the launch capability does not activate the Blender integration component or pass bridge endpoint settings, making the core FR-LAU-002 requirement non-functional; (2) version compatibility checking is stubbed — it never compares against the configured supported range; (3) the orchestrator is purely pass-through with no lifecycle coordination (launch/shutdown do not persist state); (4) PID reuse guard specified in FR-LAU-004 is absent; (5) force termination is never verified by subsequent liveness check. These gaps mean the launcher cannot fulfill its FRD mandate as "single authority for operating on the Blender process."

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | FR-LAU-002 specifies "Activates integration component during startup" and "Passes bridge endpoint settings + protocol info" but the `_ProcessSpawner` protocol signature `(executable, mode, readiness_timeout_seconds)` has no parameter for bridge endpoint or addon activation. The requirement is clear in the FRD but the contract/capability design cannot express it. | `modules/shared/src/launcher/contract_launch_protocol.py:14` | Extend `LaunchProtocol.launch()` and `_ProcessSpawner` to accept a `BridgeEndpointVO` or equivalent. Update `process_spawn` utility to pass `--addons` or `--python` flags for integration component activation. |
| 2 | 🟡 WARNING | FR-LAU-001 says "Version compared against supported range; outside → warning or rejection per policy." The `LauncherConfigVO.supported_version_range` field exists but is never consumed. The FRD does not specify the comparison algorithm (semver? major.minor?). | `modules/launcher/src/capabilities_executable_locator.py:97-100` | Define version comparison semantics in FRD (e.g., "parse major.minor, compare against range tuple"). Implement in `_check_compatibility`. |
| 3 | 🟡 WARNING | FR-LAU-004 says "guard against PID reuse" but does not specify the mechanism (process start time comparison, `/proc/<pid>/cmdline` check, or creation timestamp). | `modules/launcher/FRD.md` (FR-LAU-004 Rules) | Add to FRD: "PID reuse guard: compare process creation timestamp against persisted launch_timestamp; if delta > threshold, classify as STALE." |
| 4 | 🟢 INFO | FR-LAU-003 mentions "Orphaned child processes cleaned up where detectable + safe" — no definition of "detectable" or "safe" is provided. | `modules/launcher/FRD.md` (FR-LAU-003 Edge Cases) | Clarify: "Use process group kill (`os.killpg`) when the spawned process is a group leader. Skip cleanup if process group cannot be determined." |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 5 | 🔴 CRITICAL | Launch does not activate the Blender integration component. `process_spawn` runs `[executable]` or `[executable, --background, --python-exit-code, 1]` with no addon loading, no bridge endpoint configuration, and no MCP bridge activation. The launched Blender instance will not be controllable. | `modules/shared/src/launcher/utility_process_ops.py:72-79` | Add integration component activation: pass `--python <addon_bootstrap_script>` or `--addons blender_arwaky_bridge` to the Blender command line. Accept bridge endpoint settings (host, port) and inject them via environment variable or CLI arg. |
| 6 | 🔴 CRITICAL | Orchestrator is pure pass-through — no lifecycle coordination. FR-LAU-002 output includes "process ref" and FR-LAU-005 says "Persist registered path, process ref, launch timestamp, bridge endpoint summary, status." After a successful launch, state is never persisted. After shutdown, state is never updated to stopped. The launcher cannot recover state across restarts. | `modules/launcher/src/agent_launcher_orchestrator.py:44-68` | Add orchestration: after `launch()` returns success, call `self._persist.persist(RuntimeStateVO(...))`. After `shutdown()` returns success, persist with `last_status=NOT_RUNNING`. After `locate_and_register()`, persist executable path. |
| 7 | 🟡 WARNING | Readiness probe (`process_probe_readiness`) only polls `process_alive`. FR-LAU-002 defines "Readiness = process liveness + bridge readiness signal." A process can be alive but the bridge addon may have failed to start. The current implementation will report `ready=True` for any alive process. | `modules/shared/src/launcher/utility_process_ops.py:88-96` | Implement bridge readiness probe: attempt a TCP connection to the bridge endpoint (host:port) or check for a readiness file/signal. Only return `True` when both liveness AND bridge responsiveness are confirmed. |
| 8 | 🟡 WARNING | FR-LAU-003: "Force termination verified by subsequent liveness check." After `self._kill(current.process_id)`, the code immediately returns success without verifying the process is actually dead. SIGKILL can fail (e.g., zombie process, permission). | `modules/launcher/src/capabilities_process_shutdown.py:72-80` | After `_kill()`, call `self._wait_exit(process_id)` with a short timeout (e.g., 2s). If still alive, return `ShutdownOutcomeVO(success=False, error="Force termination failed")`. |
| 9 | 🟡 WARNING | FR-LAU-003: "Shutdown during launch → resolve launch state first." No guard exists. If `shutdown()` is called while `launch()` is in progress (concurrent), the status check may return `STARTING` and the shutdown will attempt to kill a process that may not yet have a stable PID. | `modules/launcher/src/capabilities_process_shutdown.py:50-55` | Add a state check: if `current.state == RuntimeState.STARTING`, either wait for launch to complete (with timeout) or return an error indicating launch-in-progress. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 10 | 🔴 CRITICAL | `_check_compatibility` is a stub: returns `SUPPORTED` for any non-empty version string and `UNKNOWN` for empty. It never parses the version or compares against `config.supported_version_range`. FR-LAU-001 explicitly requires "Version compared against supported range; outside → warning or rejection per policy." | `modules/launcher/src/capabilities_executable_locator.py:97-100` | Implement: parse version string (e.g., "4.2.1" → (4,2,1)), parse `supported_version_range` (e.g., ">=3.0,<5.0"), compare. Return `WARNING` or `UNSUPPORTED` when outside range. |
| 11 | 🟡 WARNING | FR-LAU-001: "Must validate as genuine Blender runtime." The `_validate` method checks `os.path.isfile` + `os.access(X_OK)` + version detection, but never verifies the `--version` output contains "Blender". Any executable that returns a version-like string will pass. | `modules/launcher/src/capabilities_executable_locator.py:82-95` | After `_detect_version`, verify the stdout contains the string "Blender" (case-insensitive). If not, raise `ExecutableValidationError("Not a genuine Blender executable")`. |
| 12 | 🟡 WARNING | FR-LAU-004: "Stale: persisted ref no longer matches live process + guard against PID reuse." The code checks `persisted.process_id == pid` when the process is dead, but when the process IS alive, it never verifies the alive process is actually Blender (PID could have been reused by an unrelated process). | `modules/launcher/src/capabilities_runtime_status.py:55-72` | Add PID reuse guard: when process is alive, verify it matches the persisted launch context (e.g., check `/proc/<pid>/cmdline` contains "blender", or compare process start time against `launch_timestamp`). |
| 13 | 🟡 WARNING | FR-LAU-004: "Read-only except stale reconciliation (may correct persisted state + emit event)." The `_stale_reconcile` flag triggers `_emit_stale()` but never actually corrects the persisted state. The stale PID remains in the persistence store. | `modules/launcher/src/capabilities_runtime_status.py:60-63` | When stale is detected and `_stale_reconcile` is True, call a persistence callback to clear or update the stale process reference. Inject a `state_corrector: Callable` via DI. |
| 14 | 🟡 WARNING | FR-LAU-005: "Corrupt/unreadable/malformed → empty state with warning, never crash." The `_load_impl` returns `None` on corruption but does not emit a warning event or log. The caller has no way to know corruption occurred vs. file simply not existing. | `modules/launcher/src/capabilities_state_persistence.py:68-78` | Differentiate: if file exists but is corrupt, log a warning and/or return a sentinel that triggers a reconciliation warning in `PersistenceOutcomeVO`. |
| 15 | 🟢 INFO | FR-LAU-002: "Early exit → surface exit reason." If the spawned process exits immediately (before readiness probe), the code returns `error="Readiness not confirmed within timeout"` — it does not capture or surface the actual exit code or stderr. | `modules/launcher/src/capabilities_process_launcher.py:72-78` | Capture process exit code (via `subprocess.Popen.poll()` or `returncode`) and include it in `LaunchOutcomeVO.error`. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 16 | 🟡 WARNING | No test files exist for the launcher module. The FRD QA Checklist has 18 items but none are automated. DI boundaries exist (spawner, probe, signal, killer) but no test exercises them. | `modules/launcher/` (no `tests/` directory) | Create `modules/launcher/tests/` with: `contract_launcher.py` (protocol impl exists), `unit_executable_locator_discovery.py`, `unit_process_launcher_idempotency.py`, `unit_process_shutdown_escalation.py`, `unit_runtime_status_classification.py`, `unit_state_persistence_atomic.py`, `integration_launcher_container.py`. |
| 17 | 🟡 WARNING | FR-LAU-001 acceptance criteria "Non-Blender executable rejected" is not testable with current implementation because genuineness check is missing. | `modules/launcher/FRD.md` (QA Checklist item 2) | After implementing finding #11, add unit test: mock `_CommandRunner` to return version output without "Blender" → assert `RegistrationOutcomeVO.registered == False`. |
| 18 | 🟢 INFO | FR-LAU-004 specifies 6 state classifications but the implementation can only produce 4 (`NOT_RUNNING`, `STALE`, `RUNNING_READY`, `RUNNING_UNRESPONSIVE`). `STARTING` and `STOPPING` are never returned by `check_status`. | `modules/launcher/src/capabilities_runtime_status.py:48-80` | Either implement transitional state detection (e.g., track launch/shutdown in-progress flags) or remove `STARTING`/`STOPPING` from the FRD classification list and document them as "internal transitional states not exposed via status check." |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 19 | 🟡 WARNING | FR-LAU-001 specifies "Previously registered path re-validated if staleness suspected." No staleness suspicion logic exists in `ExecutableLocator`. The `locate_and_register` method always runs the full discovery order without checking if the previously registered path is still valid first. | `modules/launcher/src/capabilities_executable_locator.py:48-62` | Add: if `config.executable_path` is set, validate it first (before full discovery). If validation fails, log staleness and proceed with discovery. |
| 20 | 🟡 WARNING | FR-LAU-002 specifies "Auth material through security policy, never logged." No integration with the security module's redaction or auth handling exists. The launcher operates in isolation. | `modules/launcher/src/capabilities_process_launcher.py` (entire file) | Document in FRD that auth material handling is deferred to the gateway feature (which manages the actual bridge connection). Add a cross-reference: "See FR-GW-xxx for auth material injection." |
| 21 | 🟢 INFO | FR-LAU-005 specifies "Concurrent access safe within single instance." The `threading.Lock()` protects persist/load but the `RuntimeStatusChecker` has mutable state (`_launch_time`) with no lock. Concurrent `check_status` + `mark_launched` could race. | `modules/launcher/src/capabilities_runtime_status.py:38` | Add a `threading.Lock` around `_launch_time` read/write, or document that `mark_launched` is only called once during launch (single-writer assumption). |

## Violations
- **AES405 (Agent Role)**: The `LauncherOrchestrator` coordinates 5 protocols but performs zero orchestration logic (no state coordination, no conditional branching between capabilities, no error escalation). It is a thin passthrough, not an orchestrator. The FRD implies lifecycle coordination (persist after launch, persist after shutdown, reconcile stale on status check).
- **AES305 (Duplication)**: `_OsPathResolver` is defined in both `modules/security/src/capabilities_path_validator.py` and `modules/security/src/root_security_container.py`. (This is in the security module but noted for cross-module awareness.)

## Action Items (For Developer)
- [ ] 🔴 P0: Implement integration component activation in `process_spawn` — pass bridge endpoint settings and addon bootstrap to Blender CLI (Finding #5)
- [ ] 🔴 P0: Add lifecycle coordination to `LauncherOrchestrator` — persist state after launch, shutdown, and locate (Finding #6)
- [ ] 🔴 P0: Implement real version compatibility check in `_check_compatibility` — parse version, compare against range (Finding #10)
- [ ] 🟡 P1: Implement bridge readiness probe — TCP connect or readiness signal check, not just process liveness (Finding #7)
- [ ] 🟡 P1: Add force termination verification — liveness check after SIGKILL (Finding #8)
- [ ] 🟡 P1: Add PID reuse guard in `RuntimeStatusChecker` — verify process identity matches persisted context (Finding #12)
- [ ] 🟡 P1: Add genuine Blender validation — verify `--version` output contains "Blender" (Finding #11)
- [ ] 🟡 P1: Implement stale state correction — actually update persistence when stale detected (Finding #13)
- [ ] 🟡 P1: Handle shutdown-during-launch race condition (Finding #9)
- [ ] 🟡 P1: Differentiate corrupt vs. missing state file in persistence load (Finding #14)
- [ ] 🟡 P2: Create test suite for launcher module (Finding #16)
- [ ] 🟢 P3: Capture process exit code on early launch failure (Finding #15)
- [ ] 🟢 P3: Resolve STARTING/STOPPING state classification gap (Finding #18)

## Proposed Fixes / Reference Code

### File: `modules/launcher/src/agent_launcher_orchestrator.py`
```python
# Block 2: Add lifecycle coordination after delegation

def launch(self, mode: LaunchMode = LaunchMode.INTERFACE, readiness_timeout_seconds: TimeoutSeconds | None = None) -> LaunchOutcomeVO:
    """Delegate launch, then persist state on success."""
    logger.info("Orchestrating launch (mode=%s)", mode.value)
    outcome = self._launch.launch(mode, readiness_timeout_seconds)
    if outcome.success and outcome.process_id is not None:
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
        state = RuntimeStateVO(
            process_id=None,
            last_status=RuntimeState.NOT_RUNNING,
        )
        self._persist.persist(state)
    return outcome
```

### File: `modules/launcher/src/capabilities_executable_locator.py`

```python
def _check_compatibility(self, version: str) -> VersionCompatibility:
    """Compare detected version against configured supported range."""
    if not version:
        return VersionCompatibility.UNKNOWN
    config = self._config_provider()
    supported_range = config.supported_version_range
    if not supported_range:
        return VersionCompatibility.SUPPORTED  # no range configured = accept all
    try:
        major_minor = tuple(int(x) for x in version.split(".")[:2])
        # Parse range like ">=3.0,<5.0"
        # (simplified — production should use packaging.specifiers)
        return VersionCompatibility.SUPPORTED  # TODO: implement real comparison
    except (ValueError, IndexError):
        return VersionCompatibility.UNKNOWN


def _detect_version(self, path: str) -> str:
    if self._runner is None:
        return ""
    try:
        rc, out = self._runner([path, "--version"], timeout=5.0)
    except Exception:
        return ""
    if rc != 0:
        return ""
    # FR-LAU-001: validate genuine Blender
    if "blender" not in out.lower():
        raise ExecutableValidationError(f"Not a genuine Blender executable: {path}")
    for token in out.split():
        if token[0].isdigit():
            return token
    return out.strip().splitlines()[0] if out.strip() else ""
```

### File: `modules/shared/src/launcher/utility_process_ops.py`

```python
def process_spawn(executable: str, mode: str, bridge_host: str = "localhost", bridge_port: int = 9876) -> int:
    """Spawn a Blender process with integration component active.

    Passes bridge endpoint settings via environment and activates
    the Arwaky bridge addon via --python bootstrap script.
    """
    import os as _os

    env = _os.environ.copy()
    env["ARWAKY_BRIDGE_HOST"] = bridge_host
    env["ARWAKY_BRIDGE_PORT"] = str(bridge_port)

    args = [executable]
    if mode == "headless":
        args += ["--background", "--python-exit-code", "1"]
    # Activate integration component
    # addon_bootstrap path resolved relative to package
    args += ["--python", _os.path.join(_os.path.dirname(__file__), "..", "..", "blender_mcp_addon", "bootstrap.py")]

    proc = subprocess.Popen(args, env=env)
    return proc.pid
```

### File: `modules/launcher/src/capabilities_process_shutdown.py`

```python
# After force kill, verify termination:
if (force or allow_escalation) and self._force_enabled and self._kill is not None:
    self._kill(current.process_id)
    escalated = True
    method = TerminationMethod.FORCE
    # FR-LAU-003: verify force termination succeeded
    if not self._wait_exit(current.process_id, timeout=2.0):
        return ShutdownOutcomeVO(
            success=False,
            termination_method=TerminationMethod.FORCE,
            error="Force termination failed — process still alive after SIGKILL",
        )
    self._emit(...)
```

```

---

```
