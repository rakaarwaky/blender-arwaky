Create file: `.agents/issues/issue-gateway-launcher-integration-business-analyst-2026-07-30-000000.md`

```markdown
# Issue: gateway-launcher-integration — Business Logic & Requirements Review

## Summary
The `gateway` and `launcher` modules each contain plausible feature-level implementations, but the business integration between them is incomplete and partially contradictory. The PRD explicitly shows `Gateway -->|liveness| Launcher`, and the Launcher FRD states that Launcher provides readiness and endpoint state to Gateway before transport. However, the Gateway FRD does not declare Launcher as a dependency, and the Gateway code opens a socket directly without consulting Launcher for process liveness, bridge readiness, or endpoint resolution. In addition, Launcher does not model or populate bridge endpoint information, does not verify bridge readiness, and does not persist or expose a registered executable path in a way Gateway can consume. Endpoint defaults also conflict (`50051` in Gateway code vs `9876` in constants/README). These gaps break the end-to-end business flow: CLI/MCP → Dispatcher → Gateway → Blender, especially when Blender is not already running, when it crashes, or when reconnection requires process-level recovery. This issue must be addressed to make the Gateway/Launcher integration traceable, testable, and operationally reliable.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | PRD says Gateway depends on Launcher for liveness, and Launcher FRD says it provides readiness + endpoint state to Gateway, but Gateway FRD omits Launcher from “Depends On” and says process launching is out of scope. Ownership of “Blender must be running before transport” is contradictory. | `PRD.md:End-to-End Data Flow Diagram`; `modules/launcher/FRD.md:Provides To`; `modules/gateway/FRD.md:Depends On / Out of Scope` | Reconcile PRD/FRDs. Either declare Launcher as an upstream dependency of Gateway and define the integration contract, or remove the PRD edge and explicitly state that Gateway only connects to an already-running Blender. |
| 2 | 🟡 WARNING | FR-LAU-002 requires launch to pass bridge endpoint settings and protocol info, and defines readiness as process liveness + bridge readiness. Launcher taxonomy does not model bridge host/port/protocol, and `LauncherConfigVO` has no endpoint fields. | `modules/launcher/FRD.md:FR-LAU-002`; `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO` | Add a shared `BridgeEndpointVO` (host, port, protocol version) to Launcher taxonomy and include it in `LauncherConfigVO`, `LaunchOutcomeVO`, and `RuntimeStateVO`. |
| 3 | 🟡 WARNING | Gateway endpoint defaults conflict: `ConnectionConfigVO.port` defaults to `50051`, `DEFAULT_PORT` constant is `9876`, README configuration uses `9876`, and `GatewayContainer` hardcodes `50051`. | `modules/shared/src/gateway/taxonomy_gateway_vo.py:ConnectionConfigVO`; `modules/shared/src/gateway/taxonomy_gateway_constant.py:DEFAULT_PORT`; `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__`; `README.md:Configuration` | Choose one canonical default endpoint, preferably driven by config feature. Align `ConnectionConfigVO`, constants, root wiring, and documentation. |
| 4 | 🟡 WARNING | Protocol version defaults conflict: Gateway `ConnectionConfigVO.protocol_version` defaults to `"1.0"`, while `DEFAULT_PROTOCOL_VERSION` and `ServerConfig.protocol_version` use `"2.0.0"`. | `modules/shared/src/gateway/taxonomy_gateway_vo.py:ConnectionConfigVO`; `modules/shared/src/gateway/taxonomy_gateway_constant.py:DEFAULT_PROTOCOL_VERSION`; `modules/shared/src/gateway/taxonomy_gateway_vo.py:ServerConfig` | Use one protocol version source. Gateway connection config should default to the current supported protocol version. |
| 5 | 🟡 WARNING | FR-GWY-002 requires that missed heartbeats during long-running execution not trigger reconnect unless transport is closed or execution timeout exceeded. The sync maintenance capability has `set_active_operation`, but it is not part of `ConnectionMaintenanceProtocol` and is never called by the orchestrator. | `modules/gateway/FRD.md:FR-GWY-002`; `modules/shared/src/gateway/contract_maintenance_protocol.py:ConnectionMaintenanceProtocol`; `modules/gateway/src/capabilities_connection_maintenance.py:MaintenanceExecutor.set_active_operation`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator` | Add active-operation signaling to the maintenance contract and have the orchestrator mark active operations around transport, queue execution, and code execution. |
| 6 | 🟢 INFO | Both FRDs require observability events, but the supplied root containers do not wire any event publisher or diagnostics sink. Event requirements are therefore ambiguous at the integration level. | `modules/gateway/FRD.md:Events`; `modules/launcher/FRD.md:Events`; `modules/gateway/src/root_gateway_container.py:GatewayContainer`; `modules/launcher/src/root_launcher_container.py:LauncherContainer` | Define event wiring expectations in FRDs and wire a shared diagnostics/event publisher in root composition. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Gateway establishment does not ensure Blender is launched or ready. `GatewayContainer` creates a direct socket connection, and `GatewayOrchestrator.establish_connection` only calls `ConnectionProtocol.establish_connection`. If Blender is not running, the business flow fails instead of coordinating with Launcher. | `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.establish_connection` | Wire Launcher readiness into Gateway startup. At minimum, Gateway should fail with a deterministic “Blender runtime not ready” error; preferably, root composition should ensure Launcher readiness before Gateway connection. |
| 2 | 🔴 CRITICAL | Launcher spawn does not activate the integration component or pass bridge endpoint/protocol information. `process_spawn` only starts Blender, optionally with `--background`. FR-LAU-002 explicitly requires activation of the integration component and bridge settings. | `modules/shared/src/launcher/utility_process_ops.py:process_spawn`; `modules/launcher/src/capabilities_process_launcher.py:ProcessLauncher.launch` | Implement Blender startup arguments or startup script that enables the bridge/addon and passes host/port/protocol. Make launch outcome include the resolved bridge endpoint. |
| 3 | 🔴 CRITICAL | Launcher readiness currently means “process alive”, not “bridge ready”. Root wires `process_probe_readiness`, which only polls `process_alive`. `RuntimeStatusChecker.bridge_probe` is left `None`, so full-depth status still reports ready when the process is alive. | `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness`; `modules/launcher/src/root_launcher_container.py:LauncherContainer.wire`; `modules/launcher/src/capabilities_runtime_status.py:RuntimeStatusChecker.check_status` | Define and wire a real bridge readiness probe, e.g. TCP connect + bridge status/ping response. Readiness must require both process liveness and bridge response. |
| 4 | 🟡 WARNING | Gateway reconnection ignores process lifecycle. `MaintenanceExecutor.attempt_reconnect` only calls `ConnectionExecutor.establish_connection`. If Blender crashed, Gateway retries socket connection until failure without checking Launcher status or requesting relaunch. | `modules/gateway/src/capabilities_connection_maintenance.py:MaintenanceExecutor.attempt_reconnect`; `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__` | Reconnect flow should consult Launcher runtime status. If state is `not_running` or `stale`, either relaunch via Launcher or return a categorized process-not-running error. |
| 5 | 🟡 WARNING | Shutdown is not coordinated. Launcher can shut down Blender while Gateway still believes it is connected. Gateway disconnect does not drain/fail queued operations, and Launcher shutdown does not notify Gateway. | `modules/launcher/src/capabilities_process_shutdown.py:ProcessShutdown.shutdown`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.disconnect`; `modules/gateway/src/capabilities_scene_queue.py:SceneQueueExecutor` | Define shutdown coordination: Gateway should fail/drain pending operations and close transport before Launcher terminates Blender, or Launcher should emit a stopping event consumed by Gateway/root. |
| 6 | 🟡 WARNING | Gateway scene queue does not fail pending operations on disconnect. FR-GWY-002/FR-GWY-004 require deterministic failure of in-flight and queued operations on connection loss. `SceneQueueExecutor` has no disconnect/connection-loss handler. | `modules/gateway/FRD.md:FR-GWY-002`; `modules/gateway/FRD.md:FR-GWY-004`; `modules/gateway/src/capabilities_scene_queue.py:SceneQueueExecutor`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.disconnect` | Add `fail_pending(error)` to scene queue contract and implementation. Orchestrator should call it on disconnect and on connection-loss detection. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Executable registration is not actually persisted. `ExecutableLocator._register` tries to call a nonexistent `set_executable_path` on a lambda-provided config object, so “registered” is only returned in the outcome but not stored. | `modules/launcher/src/capabilities_executable_locator.py:ExecutableLocator._register` | Inject a real config/state persistence boundary. Persist the registered executable path via `PersistStateProtocol` or a config update contract, and make registration outcome reflect actual persistence. |
| 2 | 🔴 CRITICAL | Launcher bridge endpoint is never populated. `LaunchOutcomeVO.bridge_endpoint` and `RuntimeStateVO.bridge_endpoint` exist but are never set by launch or status logic. Gateway therefore cannot consume Launcher endpoint state. | `modules/launcher/src/capabilities_process_launcher.py:ProcessLauncher.launch`; `modules/shared/src/launcher/taxonomy_launcher_vo
Create file: `.agents/issues/issue-gateway-launcher-integration-business-analyst-2026-07-30-000000.md`

```markdown
# Issue: gateway-launcher-integration — Business Logic & Requirements Review

## Summary
The `gateway` and `launcher` modules each contain plausible feature-level implementations, but the business integration between them is incomplete and partially contradictory. The PRD explicitly shows `Gateway -->|liveness| Launcher`, and the Launcher FRD states that Launcher provides readiness and endpoint state to Gateway before transport. However, the Gateway FRD does not declare Launcher as a dependency, and the Gateway code opens a socket directly without consulting Launcher for process liveness, bridge readiness, or endpoint resolution. In addition, Launcher does not model or populate bridge endpoint information, does not verify bridge readiness, and does not persist or expose a registered executable path in a way Gateway can consume. Endpoint defaults also conflict (`50051` in Gateway code vs `9876` in constants/README). These gaps break the end-to-end business flow: CLI/MCP → Dispatcher → Gateway → Blender, especially when Blender is not already running, when it crashes, or when reconnection requires process-level recovery. This issue must be addressed to make the Gateway/Launcher integration traceable, testable, and operationally reliable.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | PRD says Gateway depends on Launcher for liveness, and Launcher FRD says it provides readiness + endpoint state to Gateway, but Gateway FRD omits Launcher from “Depends On” and says process launching is out of scope. Ownership of “Blender must be running before transport” is contradictory. | `PRD.md:End-to-End Data Flow Diagram`; `modules/launcher/FRD.md:Provides To`; `modules/gateway/FRD.md:Depends On / Out of Scope` | Reconcile PRD/FRDs. Either declare Launcher as an upstream dependency of Gateway and define the integration contract, or remove the PRD edge and explicitly state that Gateway only connects to an already-running Blender. |
| 2 | 🟡 WARNING | FR-LAU-002 requires launch to pass bridge endpoint settings and protocol info, and defines readiness as process liveness + bridge readiness. Launcher taxonomy does not model bridge host/port/protocol, and `LauncherConfigVO` has no endpoint fields. | `modules/launcher/FRD.md:FR-LAU-002`; `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO` | Add a shared `BridgeEndpointVO` (host, port, protocol version) to Launcher taxonomy and include it in `LauncherConfigVO`, `LaunchOutcomeVO`, and `RuntimeStateVO`. |
| 3 | 🟡 WARNING | Gateway endpoint defaults conflict: `ConnectionConfigVO.port` defaults to `50051`, `DEFAULT_PORT` constant is `9876`, README configuration uses `9876`, and `GatewayContainer` hardcodes `50051`. | `modules/shared/src/gateway/taxonomy_gateway_vo.py:ConnectionConfigVO`; `modules/shared/src/gateway/taxonomy_gateway_constant.py:DEFAULT_PORT`; `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__`; `README.md:Configuration` | Choose one canonical default endpoint, preferably driven by config feature. Align `ConnectionConfigVO`, constants, root wiring, and documentation. |
| 4 | 🟡 WARNING | Protocol version defaults conflict: Gateway `ConnectionConfigVO.protocol_version` defaults to `"1.0"`, while `DEFAULT_PROTOCOL_VERSION` and `ServerConfig.protocol_version` use `"2.0.0"`. | `modules/shared/src/gateway/taxonomy_gateway_vo.py:ConnectionConfigVO`; `modules/shared/src/gateway/taxonomy_gateway_constant.py:DEFAULT_PROTOCOL_VERSION`; `modules/shared/src/gateway/taxonomy_gateway_vo.py:ServerConfig` | Use one protocol version source. Gateway connection config should default to the current supported protocol version. |
| 5 | 🟡 WARNING | FR-GWY-002 requires that missed heartbeats during long-running execution not trigger reconnect unless transport is closed or execution timeout exceeded. The sync maintenance capability has `set_active_operation`, but it is not part of `ConnectionMaintenanceProtocol` and is never called by the orchestrator. | `modules/gateway/FRD.md:FR-GWY-002`; `modules/shared/src/gateway/contract_maintenance_protocol.py:ConnectionMaintenanceProtocol`; `modules/gateway/src/capabilities_connection_maintenance.py:MaintenanceExecutor.set_active_operation`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator` | Add active-operation signaling to the maintenance contract and have the orchestrator mark active operations around transport, queue execution, and code execution. |
| 6 | 🟢 INFO | Both FRDs require observability events, but the supplied root containers do not wire any event publisher or diagnostics sink. Event requirements are therefore ambiguous at the integration level. | `modules/gateway/FRD.md:Events`; `modules/launcher/FRD.md:Events`; `modules/gateway/src/root_gateway_container.py:GatewayContainer`; `modules/launcher/src/root_launcher_container.py:LauncherContainer` | Define event wiring expectations in FRDs and wire a shared diagnostics/event publisher in root composition. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Gateway establishment does not ensure Blender is launched or ready. `GatewayContainer` creates a direct socket connection, and `GatewayOrchestrator.establish_connection` only calls `ConnectionProtocol.establish_connection`. If Blender is not running, the business flow fails instead of coordinating with Launcher. | `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.establish_connection` | Wire Launcher readiness into Gateway startup. At minimum, Gateway should fail with a deterministic “Blender runtime not ready” error; preferably, root composition should ensure Launcher readiness before Gateway connection. |
| 2 | 🔴 CRITICAL | Launcher spawn does not activate the integration component or pass bridge endpoint/protocol information. `process_spawn` only starts Blender, optionally with `--background`. FR-LAU-002 explicitly requires activation of the integration component and bridge settings. | `modules/shared/src/launcher/utility_process_ops.py:process_spawn`; `modules/launcher/src/capabilities_process_launcher.py:ProcessLauncher.launch` | Implement Blender startup arguments or startup script that enables the bridge/addon and passes host/port/protocol. Make launch outcome include the resolved bridge endpoint. |
| 3 | 🔴 CRITICAL | Launcher readiness currently means “process alive”, not “bridge ready”. Root wires `process_probe_readiness`, which only polls `process_alive`. `RuntimeStatusChecker.bridge_probe` is left `None`, so full-depth status still reports ready when the process is alive. | `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness`; `modules/launcher/src/root_launcher_container.py:LauncherContainer.wire`; `modules/launcher/src/capabilities_runtime_status.py:RuntimeStatusChecker.check_status` | Define and wire a real bridge readiness probe, e.g. TCP connect + bridge status/ping response. Readiness must require both process liveness and bridge response. |
| 4 | 🟡 WARNING | Gateway reconnection ignores process lifecycle. `MaintenanceExecutor.attempt_reconnect` only calls `ConnectionExecutor.establish_connection`. If Blender crashed, Gateway retries socket connection until failure without checking Launcher status or requesting relaunch. | `modules/gateway/src/capabilities_connection_maintenance.py:MaintenanceExecutor.attempt_reconnect`; `modules/gateway/src/root_gateway_container.py:GatewayContainer.__init__` | Reconnect flow should consult Launcher runtime status. If state is `not_running` or `stale`, either relaunch via Launcher or return a categorized process-not-running error. |
| 5 | 🟡 WARNING | Shutdown is not coordinated. Launcher can shut down Blender while Gateway still believes it is connected. Gateway disconnect does not drain/fail queued operations, and Launcher shutdown does not notify Gateway. | `modules/launcher/src/capabilities_process_shutdown.py:ProcessShutdown.shutdown`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.disconnect`; `modules/gateway/src/capabilities_scene_queue.py:SceneQueueExecutor` | Define shutdown coordination: Gateway should fail/drain pending operations and close transport before Launcher terminates Blender, or Launcher should emit a stopping event consumed by Gateway/root. |
| 6 | 🟡 WARNING | Gateway scene queue does not fail pending operations on disconnect. FR-GWY-002/FR-GWY-004 require deterministic failure of in-flight and queued operations on connection loss. `SceneQueueExecutor` has no disconnect/connection-loss handler. | `modules/gateway/FRD.md:FR-GWY-002`; `modules/gateway/FRD.md:FR-GWY-004`; `modules/gateway/src/capabilities_scene_queue.py:SceneQueueExecutor`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator.disconnect` | Add `fail_pending(error)` to scene queue contract and implementation. Orchestrator should call it on disconnect and on connection-loss detection. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Executable registration is not actually persisted. `ExecutableLocator._register` tries to call a nonexistent `set_executable_path` on a lambda-provided config object, so “registered” is only returned in the outcome but not stored. | `modules/launcher/src/capabilities_executable_locator.py:ExecutableLocator._register` | Inject a real config/state persistence boundary. Persist the registered executable path via `PersistStateProtocol` or a config update contract, and make registration outcome reflect actual persistence. |
| 2 | 🔴 CRITICAL | Launcher bridge endpoint is never populated. `LaunchOutcomeVO.bridge_endpoint` and `RuntimeStateVO.bridge_endpoint` exist but are never set by launch or status logic. Gateway therefore cannot consume Launcher endpoint state. | `modules/launcher/src/capabilities_process_launcher.py:ProcessLauncher.launch`; `modules/shared/src/launcher/taxonomy_launcher_vo.py:LaunchOutcomeVO`; `modules/shared/src/launcher/taxonomy_launcher_vo.py:RuntimeStateVO` | Populate bridge endpoint from configuration and/or bridge readiness probe. Persist it in runtime state and expose it to Gateway/root composition. |
| 3 | 🟡 WARNING | Orphan transport responses are logged as discarded but are actually returned. FR-GWY-003 requires uncorrelated/orphan responses to be discarded safely. | `modules/gateway/FRD.md:FR-GWY-003`; `modules/gateway/src/capabilities_transport_executor.py:TransportExecutor._parse_response` | Change transport receive logic to loop until the tracking ID matches or timeout occurs. Mismatched responses should be logged and discarded, not returned. |
| 4 | 🟡 WARNING | Scene queue wait-timeout can leave the operation in the queue. `enqueue_operation` puts the operation into the queue, then times out on lock acquisition without removing the queued item. | `modules/gateway/src/capabilities_scene_queue.py:SceneQueueExecutor.enqueue_operation` | If lock acquisition times out, remove the enqueued operation or reject it atomically. Emit `OperationRejected` and return a deterministic timeout error. |
| 5 | 🟡 WARNING | Launcher version compatibility is effectively unimplemented. `_check_compatibility` returns `SUPPORTED` for any non-empty version string, while FR-LAU-001 requires comparison against a supported range. | `modules/launcher/FRD.md:FR-LAU-001`; `modules/launcher/src/capabilities_executable_locator.py:ExecutableLocator._check_compatibility` | Implement version parsing and comparison against `supported_version_range`. Return `WARNING` or `UNSUPPORTED` according to policy. |
| 6 | 🟡 WARNING | Code execution output is always truncated to 500 characters in the outcome, even when under the configured max output. FR-GWY-005 requires bounded output with truncation indicator, not unconditional 500-character loss. | `modules/gateway/FRD.md:FR-GWY-005`; `modules/gateway/src/capabilities_code_execution.py:CodeExecutionExecutor.execute_code` | Return full bounded output up to `max_output_bytes`, set `truncated=True` only when truncation occurs, and use a separate diagnostic preview field if a short preview is needed. |
| 7 | 🟡 WARNING | Background code execution handoff is ignored. `CodeExecutionVO.as_background_task` exists, but `CodeExecutionExecutor.execute_code` always executes synchronously and never returns a task reference. FR-GWY-005 requires background submission to return a task handoff reference. | `modules/gateway/FRD.md:FR-GWY-005`; `modules/shared/src/gateway/taxonomy_gateway_vo.py:CodeExecutionVO`; `modules/gateway/src/capabilities_code_execution.py:CodeExecutionExecutor.execute_code` | If `as_background_task` is true, delegate to Job feature through a contract or return an explicit unsupported/background-not-configured error. Never silently ignore the flag. |
| 8 | 🟢 INFO | Sync Gateway executors and Launcher capabilities do not emit FRD events because root containers do not wire event sinks. This weakens operational traceability. | `modules/gateway/src/capabilities_transport_executor.py:TransportExecutor`; `modules/gateway/src/capabilities_connection_manager.py:ConnectionExecutor`; `modules/launcher/src/root_launcher_container.py:LauncherContainer.wire` | Add event publisher/event sink wiring in root composition for both modules. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | No end-to-end integration acceptance flow is defined or traceable: Launcher locate/register → launch → bridge readiness → Gateway connect → heartbeat → reconnect after Blender crash. | `modules/gateway/FRD.md:QA Checklist`; `modules/launcher/FRD.md:QA Checklist` | Add integration acceptance tests using fake Launcher/bridge and real DI wiring. Verify startup, crash recovery, and deterministic failure categories. |
| 2 | 🟡 WARNING | “Bridge readiness” is not measurable. FR-LAU-002 uses the term but does not define the exact signal, timeout, or failure classification. | `modules/launcher/FRD.md:FR-LAU-002` | Define readiness as: process alive + bridge status response within `readiness_probe_interval_seconds` and `launch_timeout`. Add explicit acceptance criteria. |
| 3 | 🟡 WARNING | Endpoint and protocol version conflicts make configuration tests ambiguous. A test cannot determine whether the canonical default port is `50051` or `9876`, or protocol `"1.0"` vs `"2.0.0"`. | `modules/shared/src/gateway/taxonomy_gateway_vo.py:ConnectionConfigVO`; `modules/shared/src/gateway/taxonomy_gateway_constant.py:DEFAULT_PORT`; `modules/shared/src/gateway/taxonomy_gateway_constant.py:DEFAULT_PROTOCOL_VERSION` | Add config schema/default tests asserting one canonical endpoint and protocol version. |
| 4 | 🟡 WARNING | Orphan response handling is not testable as specified because implementation returns mismatched responses instead of discarding them. | `modules/gateway/FRD.md:FR-GWY-003`; `modules/gateway/src/capabilities_transport_executor.py:TransportExecutor._parse_response` | Add tests that send mismatched tracking IDs and assert discard + eventual timeout or next valid response. |
| 5 | 🟢 INFO | Queue deterministic failure on disconnect is not covered by explicit acceptance criteria in code or FRD mapping. | `modules/gateway/FRD.md:FR-GWY-004` | Add tests: enqueue mutation, disconnect, assert pending operations fail with connection error and queue depth becomes zero. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | PRD integration edge `Gateway -->|liveness| Launcher` is not traceable to code. Gateway has no import, contract, or root wiring to Launcher. | `PRD.md:End-to-End Data Flow Diagram`; `modules/gateway/src/root_gateway_container.py:GatewayContainer`; `modules/gateway/src/agent_gateway_orchestrator.py:GatewayOrchestrator` | Add explicit integration wiring or contract consumption. If descoped, update PRD and FRDs. |
| 2 | 🟡 WARNING | Launcher FRD “Provides To: gateway” is not traced to any Gateway consumer. | `modules/launcher/FRD.md:Provides To` | Add Gateway consumer code/root wiring, or remove Gateway from Launcher’s “Provides To” section. |
| 3 | 🟡 WARNING | FR-LAU-002 bridge endpoint/protocol passing is not traceable to taxonomy, capability, or root wiring. | `modules/launcher/FRD.md:FR-LAU-002`; `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO`; `modules/launcher/src/capabilities_process_launcher.py:ProcessLauncher.launch` | Add endpoint VO, launch arguments/startup script, and outcome population. Link FR-LAU-002 to tests. |
| 4 | 🟡 WARNING | FR-GWY event requirements are not traced to wired implementations for the sync stack used by `GatewayContainer`. | `modules/gateway/FRD.md:Events`; `modules/gateway/src/root_gateway_container.py:GatewayContainer` | Wire event publisher into sync capabilities or document that only async adapters emit events. |
| 5 | 🟢 INFO | `RuntimeStateVO.bridge_endpoint` is persisted/loadable but never consumed by Gateway endpoint resolution. | `modules/shared/src/launcher/taxonomy_launcher_vo.py:RuntimeStateVO`; `modules/launcher/src/capabilities_state_persistence.py:StatePersistence`; `modules/gateway/src/root_gateway_container.py:GatewayContainer` | Use persisted bridge endpoint during Gateway startup/reconnect, or remove the field if not needed. |

## Violations
Potential AES/traceability concerns observed from supplied sources:

1. **AES503 — Potential Capabilities Orphan**
   - `BlenderConnection`, `BlenderCommandAdapter`, `OperationQueue`, and `CodeExecutionAdapter` are exported from Gateway but are not wired in the supplied `GatewayContainer`. If they are not wired by another entry point, they are orphan capabilities.
   - Location: `modules/gateway/src/__init__.py`; `modules/gateway/src/root_gateway_container.py`.

2. **AES502 — Potential Contract/Event Orphan**
   - Gateway and Launcher event taxonomies exist, and `IEventPublisher` exists, but sync capabilities/root wiring do not consume them. Event contracts may be partially orphaned in the delivered composition.
   - Location: `modules/shared/src/gateway/contract_event_protocol.py`; `modules/shared/src/gateway/taxonomy_gateway_event.py`; `modules/shared/src/launcher/taxonomy_launcher_event.py`.

3. **AES402 — INFO: Primitive Contract Parameters**
   - Launcher aggregate/protocol shutdown signatures use primitive `bool` values: `force`, `allow_escalation`. Consider replacing with a `ShutdownRequestVO` containing semantic flags or enums for stronger contract typing.
   - Location: `modules/shared/src/launcher/contract_launcher_operate_aggregate.py:ILauncherOperateAggregate.shutdown`; `modules/shared/src/launcher/contract_shutdown_protocol.py:ShutdownProtocol.shutdown`.

4. **AES305 — INFO: Duplicated Transport/Framing Concerns**
   - Async `BlenderConnection` and sync `TransportExecutor` both implement length-prefixed framing and response reading. If both stacks remain, extract shared framing mechanics into a utility to reduce duplication.
   - Location: `modules/gateway/src/capabilities_connection_manager.py:BlenderConnection`; `modules/gateway/src/capabilities_transport_executor.py:TransportExecutor`.

No critical AES import-boundary violations were conclusively identified from the supplied excerpts alone; the primary problem is missing business integration and FRD/PRD traceability.

## Action Items (For Developer)
- [ ] P0 Reconcile PRD/Gateway FRD/Launcher FRD ownership: define whether Gateway must consult Launcher before connection and reconnection.
- [ ] P0 Introduce a shared bridge endpoint VO and make it the single source for Gateway connection config and Launcher launch/readiness state.
- [ ] P0 Align Gateway default endpoint and protocol version: remove hardcoded `localhost:50051`, use canonical config-driven endpoint, default port `9876` unless changed by config, protocol `"2.0.0"`.
- [ ] P0 Wire Launcher readiness into Gateway startup/reconnect composition. Gateway must not silently attempt transport when Launcher reports `not_running` or `stale`.
- [ ] P0 Implement real Launcher bridge readiness: process alive + bridge response. Do not mark launch ready based only on OS process liveness.
- [ ] P0 Implement Launcher integration-component activation during spawn, including bridge endpoint/protocol passing.
- [ ] P1 Persist and expose registered Blender executable path from `ExecutableLocator` through state persistence or config contract.
- [ ] P1 Populate `LaunchOutcomeVO.bridge_endpoint` and `RuntimeStateVO.bridge_endpoint`; consume them in Gateway/root endpoint resolution.
- [ ] P1 Add `fail_pending(error)` to `SceneQueueProtocol` and fail queued scene operations deterministically on Gateway disconnect/connection loss.
- [ ] P1 Add `set_active_operation(active)` to `ConnectionMaintenanceProtocol` and mark active operations in `GatewayOrchestrator` for transport, scene queue, and code execution.
- [ ] P1 Fix orphan transport response handling: discard mismatched tracking IDs and continue waiting until valid response or timeout.
- [ ] P1 Fix scene queue wait-timeout cleanup so timed-out operations do not remain queued.
- [ ] P1 Implement version compatibility checking against `supported_version_range` in Launcher executable locator.
- [ ] P2 Implement background code execution handoff or return explicit unsupported error when `as_background_task` is true.
- [ ] P2 Wire event publishers/event sinks for sync Gateway executors and Launcher capabilities into diagnostics.
- [ ] P2 Add integration tests covering: locate/register → launch → bridge ready → Gateway connect → heartbeat → Blender crash → reconnect/recovery.

## Proposed Fixes / Reference Code

### 1. `modules/shared/src/launcher/taxonomy_launcher_vo.py`

Add a bridge endpoint VO and use it in Launcher config/outcome/state.

```python
from modules.shared.src.common.taxonomy_core_vo import (
    Host,
    PortNumber,
    ProtocolVersion,
)

@dataclass(frozen=True)
class BridgeEndpointVO:
    """Bridge endpoint shared by Launcher and Gateway."""

    host: Host = Host("localhost")
    port: PortNumber = PortNumber(9876)
    protocol_version: ProtocolVersion = ProtocolVersion("2.0.0")
```

Update relevant VOs:

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
    bridge: BridgeEndpointVO = dc_field(default_factory=BridgeEndpointVO)


@dataclass(frozen=True)
class LaunchOutcomeVO:
    success: bool = False
    process_id: int | None = None
    ready: bool = False
    bridge_endpoint: BridgeEndpointVO | None = None
    duration_ms: float = 0.0
    launch_method: LaunchMethod = LaunchMethod.SPAWN
    error: str | None = None


@dataclass(frozen=True)
class RuntimeStateVO:
    executable_path: str = ""
    process_id: int | None = None
    launch_timestamp: float = 0.0
    bridge_endpoint: BridgeEndpointVO | None = None
    last_status: RuntimeState = RuntimeState.NOT_RUNNING
```

---

### 2. `modules/shared/src/gateway/taxonomy_gateway_vo.py`

Align Gateway defaults with canonical bridge endpoint.

```python
@dataclass(frozen=True)
class ConnectionConfigVO:
    """Unified connection request — input and output in one VO."""

    host: str = "localhost"
    port: int = 9876
    transport_type: TransportType = TransportType.LOCAL_SOCKET
    timeout_seconds: float = 30.0
    protocol_version: str = "2.0.0"
    auth_enabled: bool = False
    auth_material: str | None = None
```

---

### 3. `modules/gateway/src/root_gateway_container.py`

Wire Launcher readiness into Gateway composition. Root may depend on all layers, so this is the correct place for cross-feature composition.

```python
from modules.shared.src.launcher.contract_launcher_operate_aggregate import (
    ILauncherOperateAggregate,
)
from modules.shared.src.launcher.taxonomy_launcher_vo import (
    ProbeDepth,
    RuntimeState,
)
from modules.shared.src.gateway.taxonomy_gateway_error import (
    BlenderConnectionFailure,
)


class GatewayContainer:
    def __init__(
        self,
        launcher: ILauncherOperateAggregate | None = None,
        connection_config: ConnectionConfigVO | None = None,
    ) -> None:
        self._launcher = launcher
        self._connection_config = connection_config or ConnectionConfigVO(
            host="localhost",
            port=9876,
            protocol_version="2.0.0",
        )

        self._transport = TransportExecutor(max_payload_bytes=10_485_760)
        self._connection = ConnectionExecutor(
            transport=self._transport,
            config=self._connection_config,
        )
        self._maintenance = MaintenanceExecutor(
            max_retries=3,
            base_backoff_seconds=1.0,
            max_backoff_seconds=16.0,
            reconnect_fn=self._reconnect_with_runtime,
        )
        self._scene_queue = SceneQueueExecutor(
            max_depth=50,
            wait_timeout_seconds=30.0,
        )
        self._code_executor = CodeExecutionExecutor(
            security_policy=CodeValidator(policy=SecurityPolicyVO()),
            transport=self._transport,
            max_output_bytes=1_048_576,
            execution_timeout_seconds=30.0,
        )
        self._orchestrator = GatewayOrchestrator(
            connection=self._connection,
            maintenance=self._maintenance,
            transport=self._transport,
            scene_queue=self._scene_queue,
            code_executor=self._code_executor,
        )

    def _reconnect_with_runtime(self):
        if self._launcher is not None:
            status = self._launcher.check_status(ProbeDepth.FULL)
            if status.state in (RuntimeState.NOT_RUNNING, RuntimeState.STALE):
                launch = self._launcher.launch()
                if not launch.success or not launch.ready:
                    raise BlenderConnectionFailure(
                        message="Blender runtime not ready during Gateway reconnect",
                        details={"launcher_state": status.state.value},
                    )
        return self._connection.establish_connection()
```

---

### 4. `modules/shared/src/gateway/contract_maintenance_protocol.py`

Expose active-operation signaling through the contract.

```python
class ConnectionMaintenanceProtocol(ABC):
    @abstractmethod
    def get_connection_status(self) -> ConnectionStatusVO: ...

    @abstractmethod
    def send_heartbeat(self) -> None: ...

    @abstractmethod
    def attempt_reconnect(self) -> ConnectionStatusVO: ...

    @abstractmethod
    def set_state(self, state: ConnectionState) -> None: ...

    @abstractmethod
    def set_active_operation(self, active: bool) -> None:
        """Mark whether a long-running operation is in progress."""
        ...
```

---

### 5. `modules/gateway/src/agent_gateway_orchestrator.py`

Mark active operations and fail pending queue work on disconnect.

```python
def disconnect(self) -> None:
    logger.info("Disconnecting gateway")
    self._scene_queue.fail_pending(ConnectionClosedError())
    self._connection.disconnect()
    self._maintenance.set_state(ConnectionState.CLOSED)


def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
    logger.debug("Sending transport request: %s", request.tracking_id)
    self._maintenance.set_active_operation(True)
    try:
        return self._transport.send_request(request)
    finally:
        self._maintenance.set_active_operation(False)


def enqueue_scene_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
    self._maintenance.set_active_operation(True)
    try:
        return self._scene_queue.enqueue_operation(operation)
    finally:
        self._maintenance.set_active_operation(False)


def execute_code(self, request: CodeExecutionVO) -> CodeExecutionOutcomeVO:
    logger.debug("Executing code: tracking_id=%s", request.tracking_id)
    self._maintenance.set_active_operation(True)
    try:
        return self._code_executor.execute_code(request)
    finally:
        self._maintenance.set_active_operation(False)
```

---

### 6. `modules/shared/src/gateway/contract_scene_queue_protocol.py`

Add deterministic pending-failure contract method.

```python
class SceneQueueProtocol(ABC):
    @abstractmethod
    def enqueue_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO: ...

    @abstractmethod
    def get_queue_status(self) -> QueueStatusVO: ...

    @abstractmethod
    def fail_pending(self, error: Exception) -> int:
        """Fail all pending queued operations deterministically."""
        ...
```

---

### 7. `modules/gateway/src/capabilities_scene_queue.py`

Implement pending failure and timeout cleanup.

```python
def fail_pending(self, error: Exception) -> int:
    with self._queue.mutex:
        count = len(self._queue.queue)
        self._queue.queue.clear()
        self._queue.unfinished_tasks = 0
    if count:
        logger.warning("Failed %d pending scene operations: %s", count, error)
    return count


def enqueue_operation(self, operation: SceneOperationVO) -> SceneOperationOutcomeVO:
    if not operation.is_mutation:
        return self._execute_directly(operation)

    try:
        self._queue.put_nowait(operation)
    except queue.Full:
        raise ChannelConflictError(f"Queue depth limit {self._max_depth} reached") from None

    acquired = self._execution_lock.acquire(timeout=self._wait_timeout_seconds)
    if not acquired:
        # Remove the operation that was just enqueued to avoid stale depth.
        with self._queue.mutex:
            if operation in self._queue.queue:
                self._queue.queue.remove(operation)
                self._queue.unfinished_tasks = max(0, self._queue.unfinished_tasks - 1)
        raise TimeoutError(f"Queue wait timeout exceeded after {self._wait_timeout_seconds}s")

    self._processing = True
    try:
        return self._execute_mutation(operation)
    finally:
        self._processing = False
        self._execution_lock.release()
```

---

### 8. `modules/gateway/src/capabilities_transport_executor.py`

Discard orphan responses instead of returning them.

```python
def send_request(self, request: TransportMessageVO) -> TransportOutcomeVO:
    # Existing payload limit/tracking normalization remains unchanged.
    start_time = time.time()
    timeout = request.timeout_override_seconds or 30.0
    deadline = start_time + timeout

    self._pending_tracking_ids[request.tracking_id] = True
    frame = self._create_frame(request)

    if self._socket:
        self._socket.settimeout(timeout)
        self._socket.sendall(frame)

    while time.time() < deadline:
        remaining = max(0.1, deadline - time.time())
        data = self._receive_response(remaining)
        outcome = self._parse_response(data, request.tracking_id)

        if outcome.tracking_id == request.tracking_id:
            outcome.duration_ms = (time.time() - start_time) * 1000
            outcome.request_size_bytes = len(frame)
            return outcome

        logger.warning(
            "Orphan response discarded: expected=%s, got=%s",
            request.tracking_id,
            outcome.tracking_id,
        )

    raise TimeoutError(f"No correlated response for tracking_id={request.tracking_id}")
```

---

### 9. `modules/shared/src/launcher/utility_process_ops.py`

Replace process-only readiness with bridge-aware readiness. Exact Blender startup arguments should be defined by the addon/bridge design.

```python
def process_spawn(
    executable: str,
    mode: str,
    bridge_host: str,
    bridge_port: int,
    protocol_version: str,
) -> int:
    args = [executable]

    if mode == "headless":
        args += ["--background", "--python-exit-code", "1"]

    # TODO: Replace with the real bridge/addon startup mechanism.
    # The launcher must activate the integration component and pass
    # bridge endpoint + protocol information.
    args += [
        "--python",
        "bridge_startup_script.py",
        "--",
        f"--bridge-host={bridge_host}",
        f"--bridge-port={bridge_port}",
        f"--protocol-version={protocol_version}",
    ]

    proc = subprocess.Popen(args)
    return proc.pid


def process_probe_readiness(
    process_id: int,
    bridge_host: str,
    bridge_port: int,
    timeout_seconds: float,
) -> bool:
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        if not process_alive(process_id):
            return False

        if bridge_is_responsive(bridge_host, bridge_port, timeout_seconds=0.5):
            return True

        time.sleep(0.2)

    return False


def bridge_is_responsive(host: str, port: int, timeout_seconds: float) -> bool:
    import socket

    try:
        with socket.create_connection((host, port), timeout=timeout_seconds):
            return True
    except OSError:
        return False
```

---

### 10. `modules/launcher/src/capabilities_process_launcher.py`

Populate bridge endpoint and use bridge-aware readiness.

```python
def launch(
    self,
    mode: LaunchMode = LaunchMode.INTERFACE,
    readiness_timeout_seconds: TimeoutSeconds | None = None,
) -> LaunchOutcomeVO:
    timeout = readiness_timeout_seconds or 30.0
    bridge = self._config_provider().bridge

    current = self._status.check_status(depth=ProbeDepth.FULL)
    if current.state in (
        RuntimeState.RUNNING_READY,
        RuntimeState.RUNNING_UNRESPONSIVE,
        RuntimeState.STARTING,
    ):
        return LaunchOutcomeVO(
            success=True,
            process_id=current.process_id,
            ready=(current.state == RuntimeState.RUNNING_READY),
            bridge_endpoint=bridge,
            launch_method=LaunchMethod.IDEMPOTENT,
        )

    executable = self._resolve_executable()
    if not executable:
        return LaunchOutcomeVO(success=False, error="No registered executable path")

    start = time.monotonic()
    pid = self._spawner(
        executable,
        mode.value,
        bridge.host,
        bridge.port,
        bridge.protocol_version,
    )

    ready = self._probe(pid, bridge.host, bridge.port, timeout)
    duration_ms = (time.monotonic() - start) * 1000.0

    if not ready:
        return LaunchOutcomeVO(
            success=False,
            process_id=pid,
            ready=False,
            bridge_endpoint=bridge,
            duration_ms=duration_ms,
            error="Bridge readiness not confirmed within timeout",
        )

    return LaunchOutcomeVO(
        success=True,
        process_id=pid,
        ready=True,
        bridge_endpoint=bridge,
        launch_method=LaunchMethod.SPAWN,
        duration_ms=duration_ms,
    )
```
```