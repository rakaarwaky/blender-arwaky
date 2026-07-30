`.agents/issues/issue-integration-business-analyst-2026-07-30-120000.md`

```markdown
# Issue: integration — Business Logic & Requirements Review

## Summary
The end-to-end integration between **CLI**, **Dispatcher**, **Launcher**, and **Gateway** is not aligned with the PRD and feature FRDs. The intended flow is `CLI/MCP → Dispatcher → owning feature aggregate (Launcher/Gateway/etc.)`, with Launcher as the single authority for Blender process lifecycle and Gateway as the transport authority to Blender. The current implementation bypasses this integration: CLI directly launches/kills Blender, keeps its own `registry.json`, and opens a direct socket to Blender using `BlenderSocketClient`. Dispatcher is only used as an action-schema constant source, not as an execution aggregate. Launcher has an aggregate/container, but it is not consumed by CLI and its launch/status/shutdown flows are incomplete for real integration (missing bridge endpoint/filepath contract, bridge readiness, persistence after lifecycle changes, and event wiring). This creates duplicated authority, unsafe shutdown behavior, unreliable status, broken traceability, and AES surface/utility role violations. This integration issue must be resolved before CLI or MCP can safely expose Blender operations.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | PRD says CLI/MCP never call domain modules directly and must submit requests to Dispatcher. CLI FRD says CLI routes to owning feature aggregate. The code does neither: CLI calls process utilities and socket client directly. The integration contract between CLI and Dispatcher is not implemented or clearly wired. | `PRD.md:End-to-End Data Flow Diagram`, `modules/cli/FRD.md:FR-CLI-001`, `modules/cli/src/root_cli_main_entry.py:main()` | Define and implement one integration rule: CLI calls `IDispatcherAggregate` with an action name and params; Dispatcher validates and routes to Launcher/Gateway/other owning aggregates. Remove direct domain/transport calls from CLI. |
| 2 | 🔴 CRITICAL | CLI `init` requires `--filepath` and `--port`, but Launcher aggregate `launch()` only accepts `mode` and `readiness_timeout_seconds`. Dispatcher action schema `launch_blender` accepts `mode` and `port`, but no `filepath`. There is no shared contract for launching a specific `.blend` file with a specific bridge endpoint. | `modules/cli/src/root_cli_main_entry.py:init_parser`, `modules/shared/src/launcher/contract_launcher_operate_aggregate.py:ILauncherOperateAggregate.launch()`, `modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py:DISPATCHER_ACTION_SCHEMAS["launcher"]["launch_blender"]` | Introduce a shared `LaunchRequestVO` containing optional `filepath`, `mode`, `bridge_endpoint` host/port, and readiness timeout. Update Launcher contract, Dispatcher schema, and CLI handler to use it. |
| 3 | 🔴 CRITICAL | CLI `close` implicitly saves the Blender file before killing the process. Launcher FRD explicitly says shutdown must never modify/save Blender scene content unless explicitly requested. The integration behavior is conflicting and unsafe. | `modules/cli/src/surface_close_command.py:handle()`, `modules/launcher/FRD.md:FR-LAU-003` | Remove implicit save from CLI close. If save-before-close is required, add an explicit flag and route it through the owning feature aggregate with clear FRD acceptance. |
| 4 | 🟡 WARNING | CLI `status` reads local `registry.json` and checks PID directly, while Launcher FRD requires true liveness verification and runtime state classification. Ownership of runtime status is ambiguous in the current implementation. | `modules/cli/src/surface_status_command.py:handle()`, `modules/launcher/FRD.md:FR-LAU-004` | Make Launcher the single source of truth for runtime status. CLI should request `get_runtime_status` through Dispatcher and render the result. |
| 5 | 🟡 WARNING | CLI `run`, `screenshot`, and `render` send actions directly to Blender through `BlenderSocketClient`. PRD assigns transport to Gateway and routing to Dispatcher. The CLI-to-Gateway relationship is not defined in code. | `modules/cli/src/surface_run_command.py:handle()`, `modules/cli/src/surface_screenshot_command.py:handle()`, `modules/cli/src/surface_render_command.py:handle()`, `PRD.md:End-to-End Data Flow Diagram` | Route all Blender actions through Dispatcher. Dispatcher should use Gateway transport protocols/aggregate to communicate with Blender. CLI must not import or use socket transport directly. |
| 6 | 🟡 WARNING | Default launch mode is inconsistent: CLI defaults to `headless`, while Launcher config defaults to `INTERFACE`. The integration owner for launch mode default is unclear. | `modules/cli/src/root_cli_main_entry.py:init_parser`, `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO` | Reconcile defaults in PRD/FRDs. If CLI flag is omitted, Launcher/config default should govern unless CLI explicitly passes user intent. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `init` flow bypasses Launcher and Dispatcher. CLI directly finds Blender, spawns process, waits for addon port, and writes `registry.json`. This duplicates Launcher authority and prevents unified lifecycle management. | `modules/cli/src/surface_init_command.py:handle()`, `modules/cli/src/utility_cli_process.py:launch_blender()`, `modules/cli/src/utility_cli_registry.py:Registry` | Correct flow: `CLI init → Dispatcher action launch_blender → Launcher.launch → persist runtime state → return result → CLI render`. Remove CLI-local spawn and registry logic. |
| 2 | 🔴 CRITICAL | `close` flow bypasses Launcher shutdown. CLI directly saves scene, kills PID, and clears local registry. It does not use graceful shutdown, escalation policy, final liveness verification, or Launcher state persistence. | `modules/cli/src/surface_close_command.py:handle()`, `modules/cli/src/utility_cli_process.py:kill_blender()` | Correct flow: `CLI close → Dispatcher action shutdown_blender → Launcher.shutdown → graceful/force escalation → verify stopped → persist stopped state → CLI render`. |
| 3 | 🔴 CRITICAL | `status` flow uses CLI-local state instead of Launcher true status. It cannot detect bridge unresponsiveness, stale PID reuse, or real readiness. | `modules/cli/src/surface_status_command.py:handle()`, `modules/cli/src/utility_cli_registry.py:Registry` | Correct flow: `CLI status → Dispatcher action get_runtime_status → Launcher.check_status → return RuntimeStatusVO → CLI render`. |
| 4 | 🔴 CRITICAL | `run`, `screenshot`, and `render` flows bypass Dispatcher and Gateway. CLI opens a direct TCP connection to Blender and sends action payloads. This breaks action validation, result normalization, security redaction, auditability, and MCP parity. | `modules/cli/src/surface_run_command.py:handle()`, `modules/cli/src/surface_screenshot_command.py:handle()`, `modules/cli/src/surface_render_command.py:handle()` | Correct flow: `CLI command → Dispatcher action → Gateway transport → Blender → Dispatcher result envelope → CLI render`. |
| 5 | 🟡 WARNING | Readiness is split across layers. CLI utility waits for TCP port availability, while Launcher capability only checks process liveness. Neither fully implements FR-LAU-002 readiness as process liveness + bridge readiness signal. | `modules/cli/src/utility_cli_process.py:_wait_for_addon()`, `modules/launcher/src/capabilities_process_launcher.py:launch()`, `modules/shared/src/launcher/utility_process_ops.py:process_probe_readiness()` | Move readiness into Launcher/Gateway-owned integration. Launcher should use a bridge readiness probe supplied by Gateway or a shared bridge-health capability. |
| 6 | 🟡 WARNING | Runtime state is duplicated. CLI maintains `registry.json`; Launcher has `StatePersistence` but it is not used by CLI and not automatically updated after launch/shutdown in the wired flow. | `modules/cli/src/utility_cli_registry.py:Registry`, `modules/launcher/src/capabilities_state_persistence.py:StatePersistence`, `modules/launcher/src/root_launcher_container.py:wire()` | Use Launcher state persistence as the single runtime state store. Remove CLI registry. Persist state after launch, shutdown, and stale reconciliation. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Dispatcher aggregate is not integrated. CLI imports only `DISPATCHER_ACTION_SCHEMAS` for action names. There is no injected `IDispatcherAggregate`, no dispatcher execution call, and no result envelope handling. | `modules/cli/src/surface_run_command.py:_flatten_schemas()`, `modules/shared/src/dispatcher/__init__.py:IDispatcherAggregate` | Implement/wire a Dispatcher aggregate and inject it into CLI. CLI should call Dispatcher `execute_command(action, params)` or equivalent contract method. |
| 2 | 🔴 CRITICAL | Launcher aggregate is not consumed by CLI. `LauncherContainer` can create `ILauncherOperateAggregate`, but CLI never uses it. The process lifecycle authority is bypassed. | `modules/launcher/src/root_launcher_container.py:create_launcher_feature()`, `modules/cli/src/surface_init_command.py:handle()` | Wire Launcher aggregate into the application root and expose it through Dispatcher routing. CLI should not call Launcher directly unless explicitly allowed by integration design; preferred path is CLI → Dispatcher → Launcher. |
| 3 | 🔴 CRITICAL | Gateway transport is used directly as a utility class. `BlenderSocketClient` is stateful and is imported by CLI surface commands. This bypasses Gateway contracts and violates the intended transport boundary. | `modules/shared/src/gateway/utility_socket_client.py:BlenderSocketClient`, `modules/cli/src/__init__.py` | CLI must not import `BlenderSocketClient`. Gateway transport should be behind Dispatcher/Gateway aggregate or protocol implementation. If a socket client is needed, it should be an internal Gateway capability/adapter, not a CLI-imported utility. |
| 4 | 🔴 CRITICAL | Root packaging entry point is broken: `blender-arwaky = "modules.cli.src.surface_cli_main:main"` but the actual file is `modules/cli/src/root_cli_main_entry.py`. The CLI entry cannot be installed/run correctly. | `pyproject.toml:[project.scripts]` | Fix entry point to `modules.cli.src.root_cli_main_entry:main` or create the missing `surface_cli_main.py` as a thin entry that delegates to the composed root. |
| 5 | 🟡 WARNING | Launcher launch implementation does not activate the Blender integration component/addon or pass bridge endpoint settings. CLI utility currently performs addon activation and port waiting. This logic is in the wrong layer. | `modules/launcher/src/root_launcher_container.py:wire()`, `modules/shared/src/launcher/utility_process_ops.py:process_spawn()`, `modules/cli/src/utility_cli_process.py:launch_blender()` | Move Blender bootstrap concerns into Launcher/Gateway-owned flow. Launcher should spawn Blender with integration activation and bridge endpoint configuration, then confirm bridge readiness. |
| 6 | 🟡 WARNING | Launcher shutdown does not verify force termination or update persisted state to stopped. CLI clears its own registry without verifying final process state. | `modules/launcher/src/capabilities_process_shutdown.py:shutdown()`, `modules/cli/src/surface_close_command.py:handle()` | After kill/escalation, poll liveness until stopped. Persist stopped state. Only then return success to Dispatcher/CLI. |
| 7 | 🟡 WARNING | CLI does not normalize results into a stable envelope. `run` returns raw socket response; other commands return ad hoc dictionaries. Dispatcher taxonomy defines `UnifiedResultEnvelopeVO`, but CLI does not use it. | `modules/cli/src/surface_run_command.py:handle()`, `modules/shared/src/dispatcher/__init__.py:UnifiedResultEnvelopeVO` | Dispatcher should return normalized results. CLI should render from the normalized envelope and never expose raw transport payloads directly. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | No integration acceptance tests traceable to PRD data flow: `CLI → Dispatcher → Launcher` for init/close/status. | `tests/` missing | Add integration tests using fake aggregates: CLI command produces Dispatcher action; Dispatcher routes to Launcher; CLI renders normalized result. |
| 2 | 🟡 WARNING | No integration tests for `CLI → Dispatcher → Gateway → Blender` actions such as `run`, `screenshot`, `render`. | `tests/` missing | Add tests with mocked Gateway transport verifying action name, params, result envelope, error categories, and redaction. |
| 3 | 🟡 WARNING | No contract tests verifying Dispatcher action catalog maps to owning aggregate behavior. | `modules/shared/src/dispatcher/taxonomy_dispatcher_constant.py:DISPATCHER_ACTION_SCHEMAS` | Add contract tests: every CLI command mapping has an action schema, Dispatcher route, owning aggregate method, and result envelope shape. |
| 4 | 🟡 WARNING | No tests for secret masking across integration boundaries. CLI FRD requires masking in all output paths, but no security redaction integration exists. | `modules/cli/FRD.md:FR-CLI-002`, `modules/cli/FRD.md:FR-CLI-003` | Inject security redaction policy into CLI/Dispatcher output path and add tests with fake tokens, paths, and credentials. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | PRD data flow `CLI → Dispatcher` is not traceable in code. CLI does not call `IDispatcherAggregate`. | `PRD.md:End-to-End Data Flow Diagram`, `modules/cli/src/root_cli_main_entry.py:main()` | Add root wiring and tests that trace each CLI command to a Dispatcher action call. |
| 2 | 🔴 CRITICAL | CLI FRD command mapping says each CLI command equals one action name equals one aggregate call. Current code maps only to direct socket/process calls, not aggregate calls. | `modules/cli/FRD.md:Command Mapping`, `modules/cli/src/surface_run_command.py:handle()` | Implement command-to-action-to-aggregate traceability. Each CLI command should dispatch one action and render one normalized result. |
| 3 | 🔴 CRITICAL | Launcher FR-LAU-002 and FR-LAU-004 are not traceable to CLI `init` and `status` because CLI bypasses Launcher and Launcher contract lacks required launch inputs. | `modules/launcher/FRD.md:FR-LAU-002`, `modules/launcher/FRD.md:FR-LAU-004`, `modules/cli/src/surface_init_command.py:handle()` | Add `LaunchRequestVO`, wire Launcher through Dispatcher, and add acceptance tests mapping CLI `init`/`status` to Launcher FRs. |
| 4 | 🟡 WARNING | Gateway protocols exist but are not traceable to CLI action execution. CLI uses a socket utility instead of Gateway contract implementations. | `modules/shared/src/gateway/__init__.py`, `modules/cli/src/surface_run_command.py:handle()` | Wire Gateway transport protocols behind Dispatcher. Add tests tracing Blender actions to Gateway transport calls. |

## Violations
- **AES406 — Surface Role:** CLI surface commands perform process lifecycle, direct transport, and scene-save business logic. Surfaces must delegate to aggregates and contain no business calculation/orchestration.
- **AES404 — Utility Role:** `modules/cli/src/utility_cli_registry.py` contains a stateful singleton class. `modules/shared/src/gateway/utility_socket_client.py` contains a stateful socket client class. Utility files must contain stateless standalone functions only.
- **AES502 — Contract Orphan / Unused Aggregate:** `IDispatcherAggregate` is exported but not called by CLI surface. `ILauncherOperateAggregate` is not consumed by CLI/entry in the current flow.
- **AES505 — Agent Orphan risk:** `LauncherOrchestrator` is wired inside `LauncherContainer`, but no surface/entry currently consumes it through the intended application flow.
- **Potential AES201 concern:** CLI surface imports gateway transport utility directly. Even if utility imports may be allowed for smart surfaces in some AES tables, this bypasses the required Dispatcher/Gateway contract boundary and violates PRD/FRD integration intent.

## Action Items (For Developer)
- [ ] P0 Fix root `pyproject.toml` CLI entry point to reference an existing main function.
- [ ] P0 Define integration contract: CLI calls Dispatcher aggregate with action name and params; Dispatcher routes to owning aggregates.
- [ ] P0 Implement/wire Dispatcher aggregate execution, not just action schema constants.
- [ ] P0 Add shared `LaunchRequestVO` with filepath, mode, bridge endpoint host/port, and readiness timeout.
- [ ] P0 Update Launcher `launch()` contract and implementation to accept `LaunchRequestVO`.
- [ ] P0 Wire CLI to Dispatcher; remove direct `BlenderSocketClient`, `utility_cli_process`, and `utility_cli_registry` usage.
- [ ] P0 Move Blender process spawn, addon activation, bridge endpoint configuration, and readiness probing into Launcher/Gateway-owned flow.
- [ ] P0 Make Launcher the single authority for runtime state; remove CLI `registry.json`.
- [ ] P1 Route `run`, `screenshot`, and `render` through Dispatcher and Gateway transport protocols.
- [ ] P1 Normalize all action results into Dispatcher result envelope and render from that envelope in CLI.
- [ ] P1 Remove implicit save-on-close; add explicit save flag only if FRD-approved.
- [ ] P1 Wire Launcher lifecycle events and state persistence after launch/shutdown/stale reconciliation.
- [ ] P1 Integrate security redaction into CLI/Dispatcher output paths.
- [ ] P2 Add integration acceptance tests for CLI → Dispatcher → Launcher and CLI → Dispatcher → Gateway flows.

## Proposed Fixes / Reference Code

### `pyproject.toml`
```toml
[project.scripts]
blender-arwaky = "modules.cli.src.root_cli_main_entry:main"
blender-mcp = "modules.root_mcp_entry:main"
```

### `modules/shared/src/launcher/taxonomy_launcher_vo.py`

```python
from dataclasses import dataclass
from modules.shared.src.common.taxonomy_core_vo import FilePath, Host, PortNumber


@dataclass(frozen=True)
class BridgeEndpointVO:
    host: Host = Host("localhost")
    port: PortNumber = PortNumber(9876)


@dataclass(frozen=True)
class LaunchRequestVO:
    filepath: FilePath | None = None
    mode: LaunchMode = LaunchMode.INTERFACE
    bridge_endpoint: BridgeEndpointVO | None = None
    readiness_timeout_seconds: TimeoutSeconds | None = None
```

### `modules/shared/src/launcher/contract_launch_protocol.py`

```python
from abc import ABC, abstractmethod
from .taxonomy_launcher_vo import LaunchOutcomeVO, LaunchRequestVO


class LaunchProtocol(ABC):
    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """Start Blender with integration component active and confirm bridge readiness."""
        ...
```

### `modules/shared/src/launcher/contract_launcher_operate_aggregate.py`

```python
from abc import ABC, abstractmethod
from .taxonomy_launcher_vo import LaunchOutcomeVO, LaunchRequestVO


class ILauncherOperateAggregate(ABC):
    @abstractmethod
    def launch(self, request: LaunchRequestVO) -> LaunchOutcomeVO:
        """FR-LAU-002: Launch Blender and confirm readiness."""
        ...
```

### `modules/cli/src/root_cli_main_entry.py`

```python
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate


def main(
    argv=None,
    *,
    dispatcher: IDispatcherAggregate | None = None,
) -> int:
    # Parse CLI args.
    # Inject dispatcher into surface handlers.
    # Surface handlers must not import process/socket utilities.
    ...
```

### `modules/cli/src/surface_init_command.py`

```python
def handle(args, dispatcher: IDispatcherAggregate) -> dict:
    params = {
        "filepath": args.filepath,
        "mode": args.mode,
        "port": args.port,
    }
    # Dispatcher routes action "launch_blender" to Launcher aggregate.
    return dispatcher.execute_command(action="launch_blender", params=params)
```

### `modules/cli/src/surface_close_command.py`

```python
def handle(args, dispatcher: IDispatcherAggregate) -> dict:
    params = {
        "force": False,
    }
    # Dispatcher routes action "shutdown_blender" to Launcher aggregate.
    # No implicit scene save.
    return dispatcher.execute_command(action="shutdown_blender", params=params)
```

### `modules/cli/src/surface_status_command.py`

```python
def handle(_args, dispatcher: IDispatcherAggregate) -> dict:
    # Dispatcher routes action "get_runtime_status" to Launcher aggregate.
    return dispatcher.execute_command(action="get_runtime_status", params={})
```

### `modules/cli/src/surface_run_command.py`

```python
def handle(args, dispatcher: IDispatcherAggregate) -> dict:
    # Dispatcher validates action schema and routes to owning aggregate/Gateway.
    return dispatcher.execute_command(action=args.action, params=args.params)
```

### Files to remove from CLI after migration

```text
modules/cli/src/utility_cli_process.py
modules/cli/src/utility_cli_registry.py
```

### `modules/launcher/src/root_launcher_container.py`

```python
def wire(self) -> None:
    state_path = self._state_path or self._config.state_persistence_location

    def event_sink(event):
        logger.info(
            "launcher_event category=%s before=%s after=%s",
            event.event_category,
            event.state_before.value,
            event.state_after.value,
        )

    # Wire persistence, bridge probe, event sink, and lifecycle state updates.
    # Launcher launch/shutdown must persist state and emit events.
    ...
```

```

```
