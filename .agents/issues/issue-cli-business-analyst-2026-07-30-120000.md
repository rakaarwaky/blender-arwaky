`.agents/issues/issue-cli-business-analyst-2026-07-30-120000.md`

```markdown
# Issue: cli — Business Logic & Requirements Review

## Summary
The CLI module is specified by `modules/cli/FRD.md` as a **surface-only** terminal adapter: parse commands, perform surface-level validation, route each command to the owning feature aggregate, render results, and display categorized errors. The current implementation instead embeds substantial business and infrastructure behavior: Blender process launch/kill, local registry persistence, direct socket transport to Blender, implicit scene saving on close, and partial command coverage. This breaks the FRD scope, weakens traceability from FRD to code, duplicates Launcher/Gateway/Dispatcher responsibilities, and introduces user-facing risk (incorrect close behavior, missing secret redaction, missing error remediation, packaging entry-point failure). This issue must be addressed before the CLI can be considered a compliant AES surface.

## Findings by Category

### Requirements Clarity
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FRD “Command Mapping” defines many CLI subcommands (`register`, `scene-info`, `scene-cleanup`, `set-env`, `object-info`, `create`, `set-transform`, `delete`, `set-material`, `apply-modifier`, `import`, `export`, `place-asset`, `task-status`, `cancel-task`, `config`, `set-config`, `run-code`), but only `init`, `run`, `screenshot`, `render`, `close`, `status` are implemented. There is no documented scope reduction. | `modules/cli/src/root_cli_main_entry.py:main()` | Either implement all mapped subcommands or update the CLI FRD to state explicitly which commands are deferred and how `run --action` covers them. |
| 2 | 🔴 CRITICAL | FRD says CLI depends on dispatcher (action execution + catalog), launcher (process control), diagnostics, config, job, and security policy. The code only uses dispatcher action-schema constants and a direct socket client. Required aggregate dependencies are not named, injected, or traceable. | `modules/cli/src/__init__.py`, `modules/cli/src/root_cli_main_entry.py` | Add explicit injected aggregate contracts (`ILauncherOperateAggregate`, `IDispatcherAggregate`, security/redaction protocol) and document them in the FRD dependency section. |
| 3 | 🟡 WARNING | FRD requires `--quiet`, progress hints, color policy, list truncation, and non-interactive adaptation. Only non-TTY JSON fallback is implemented. The acceptance meaning of “progress hints” and “conservative truncation” is undefined. | `modules/cli/src/root_cli_main_entry.py:main()` | Define measurable acceptance criteria in FRD (e.g., no progress hints in non-TTY, truncate text tables at N rows, JSON never truncates) and implement minimum behavior. |
| 4 | 🟡 WARNING | `status` is mapped to action `get_runtime_status`, but implementation reads a local `registry.json` and OS PID only. The FRD does not clarify whether CLI may cache status locally or must query Launcher/Diagnostics. | `modules/cli/src/surface_status_command.py:handle()` | Clarify that `status` must delegate to Launcher/Diagnostics aggregate, then remove local process inference. |
| 5 | 🟡 WARNING | CLI default launch mode is `headless`, while Launcher config default is `INTERFACE`. The FRDs do not state which default owns precedence. | `modules/cli/src/root_cli_main_entry.py:init_parser`, `modules/shared/src/launcher/taxonomy_launcher_vo.py:LauncherConfigVO` | Reconcile defaults in PRD/FRDs. If CLI is explicit user intent, pass it to Launcher; otherwise use Launcher default when flag omitted. |
| 6 | 🟢 INFO | `modules/cli/pyproject.toml` version is `1.6.5` while root version is `1.7.0`. | `modules/cli/pyproject.toml` | Align module version with release version or document independent versioning. |

### Business Flow
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | `init`, `close`, and `status` manage Blender process lifecycle directly through CLI-local utilities (`utility_cli_process.py`, `utility_cli_registry.py`). FRD assigns process lifecycle to Launcher. CLI is surface-only and must delegate. | `modules/cli/src/surface_init_command.py:handle()`, `modules/cli/src/surface_close_command.py:handle()`, `modules/cli/src/surface_status_command.py:handle()` | Inject `ILauncherOperateAggregate` and delegate launch/shutdown/status. Remove CLI-local process authority. |
| 2 | 🔴 CRITICAL | `run`, `screenshot`, and `render` send commands directly to Blender via `BlenderSocketClient`. FRD and PRD require CLI/MCP to route through Dispatcher/owning aggregates, not directly to Blender transport. | `modules/cli/src/surface_run_command.py:handle()`, `modules/cli/src/surface_screenshot_command.py:handle()`, `modules/cli/src/surface_render_command.py:handle()` | Inject `IDispatcherAggregate` (or owning feature aggregate where FRD explicitly allows) and submit action commands through contracts. Remove direct socket usage from CLI surface. |
| 3 | 🔴 CRITICAL | `close` implicitly executes `bpy.ops.wm.save_mainfile()` before killing Blender. This is a business decision and conflicts with Launcher FRD: shutdown must not modify/save scene content unless explicitly requested. | `modules/cli/src/surface_close_command.py:handle()` | Remove implicit save. If save-before-close is desired, add explicit CLI flag and route through the owning feature aggregate with clear FRD acceptance. |
| 4 | 🟡 WARNING | `close` clears registry even if `kill_blender()` fails and does not verify final process liveness. This can report success while Blender remains running. | `modules/cli/src/surface_close_command.py:handle()` | Delegate to Launcher shutdown, which must verify final liveness and only clear persisted state after confirmed stop. |
| 5 | 🟡 WARNING | Active filepath comparison is exact string equality. `init` stores `os.path.abspath(args.filepath)`, but later commands compare raw user input. Relative paths, symlinks, or case-insensitive filesystems can produce false “not registered” errors. | `modules/cli/src/utility_cli_registry.py:assert_active()` | If any local state remains temporarily, normalize with `os.path.realpath(os.path.abspath(...))` and use platform-safe comparison. Long term, remove CLI registry. |
| 6 | 🟡 WARNING | Global `--json` and `--quiet` are registered on the root parser only. Depending on argparse invocation order, flags after subcommand may fail. FRD implies command-level usability. | `modules/cli/src/root_cli_main_entry.py:main()` | Add shared parent parser with `--json`/`--quiet` to each subparser or use `parse_known_args` carefully. Add tests for `blender-arwaky init --filepath x --json`. |

### Logic Implementation
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | Root packaging entry point points to missing module: `blender-arwaky = "modules.cli.src.surface_cli_main:main"`. Actual entry is `modules/cli/src/root_cli_main_entry.py:main`. Installed CLI will fail. | `pyproject.toml:[project.scripts]` | Change entry point to `modules.cli.src.root_cli_main_entry:main` or create `surface_cli_main.py` as a thin surface entry that delegates. |
| 2 | 🔴 CRITICAL | Secret masking/security redaction is required for all output paths but is not implemented. Errors, params, paths, and JSON results can leak sensitive values. | `modules/cli/src/root_cli_main_entry.py:main()`, all `surface_*_command.py` | Inject security redaction policy and apply to text/JSON/error output before printing. Add tests with fake tokens/paths. |
| 3 | 🟡 WARNING | `run` validates only that action name exists in schema. It does not validate required parameters, parameter types, enums, or arg count at surface level. FR-CLI-001 requires surface-level shape validation. | `modules/cli/src/surface_run_command.py:handle()` | Validate required fields and basic type/enum shape from `DISPATCHER_ACTION_SCHEMAS` before dispatch. Return `validation_error` with field details. |
| 4 | 🟡 WARNING | `run` returns raw socket response directly. If response lacks `success`/`category`, exit-code mapping and error rendering become inconsistent. FR-CLI-002/003 require stable CLI result envelope. | `modules/cli/src/surface_run_command.py:handle()` | Normalize aggregate/dispatcher results into a CLI output envelope: `success`, `message`, `data`, `error`, `category`, `ref`, `warnings`. |
| 5 | 🟡 WARNING | Unknown command handling relies on argparse and does not provide closest known command suggestions as required by FR-CLI-001. | `modules/cli/src/root_cli_main_entry.py:main()` | Implement suggestion logic (`difflib.get_close_matches`) and return validation error with suggestions. |
| 6 | 🟡 WARNING | `init` catches all exceptions as generic `unexpected`, losing categorized upstream errors (`configuration_error`, `validation_error`, `timeout`, etc.). | `modules/cli/src/surface_init_command.py:handle()` | Catch Launcher/domain error categories and map to FRD error categories. Preserve remediation hints. |
| 7 | 🟢 INFO | `_mask_error()` is duplicated across multiple surface command files. | `modules/cli/src/surface_close_command.py`, `surface_init_command.py`, `surface_render_command.py`, `surface_run_command.py`, `surface_screenshot_command.py` | Extract to a small CLI rendering/utility helper or, preferably, replace with shared error VO mapping. |

### Testability & Acceptance Criteria
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🟡 WARNING | No acceptance tests traceable to FR-CLI-001 for command parsing, routing, unknown command suggestions, help output, and exit codes. | `tests/` (missing) | Add `tests/acceptance_FR_CLI_001.py` covering each implemented command, unknown command, missing required args, invalid JSON, and exit-code classes. |
| 2 | 🟡 WARNING | No tests for FR-CLI-002 rendering modes: text vs JSON, non-TTY suppression, large payload truncation, stable JSON error shape. | `tests/` (missing) | Add rendering tests with captured stdout/stderr and mocked aggregate results. |
| 3 | 🟡 WARNING | No tests for FR-CLI-003 error display: category label, actionable message, remediation hint, secret masking, verbose stack suppression. | `tests/` (missing) | Add error-rendering tests using fake secrets and categorized upstream errors. |
| 4 | 🟡 WARNING | Direct socket/process behavior is hard to test and couples CLI to runtime Blender. | `modules/cli/src/utility_cli_process.py`, `modules/shared/src/gateway/utility_socket_client.py` | Replace with aggregate mocks in tests; CLI tests should not require real Blender or socket. |

### Traceability (FRD → Code)
| # | Severity | Issue | Location (File:Line) | Recommendation |
|---|----------|-------|----------------------|----------------|
| 1 | 🔴 CRITICAL | FR-CLI-001 “route to owning feature aggregate” is not traceable: no aggregate injection, no container wiring, no command-to-aggregate map. | `modules/cli/src/root_cli_main_entry.py:main()` | Add explicit command mapping to aggregates/actions and trace each CLI command to one aggregate call. |
| 2 | 🔴 CRITICAL | FR-CLI-002 rendering requirements are mostly unimplemented: tables, truncation, color policy, progress hints, safe fallback rendering. | `modules/cli/src/root_cli_main_entry.py:main()` | Implement a CLI renderer component and map FR-CLI-002 bullets to renderer functions/tests. |
| 3 | 🔴 CRITICAL | FR-CLI-003 error display requirements are unimplemented: remediation hints, category labels, masked secrets, verbose structural detail, JSON error objects. | `modules/cli/src/root_cli_main_entry.py:main()` | Implement error view with category, message, hint, optional detail, and redaction. |
| 4 | 🟡 WARNING | FRD command mapping says each CLI command equals one action name equals one aggregate call. Current `screenshot`/`render` call socket action names directly, not aggregate/dispatcher execution. | `modules/cli/src/surface_screenshot_command.py:handle()`, `modules/cli/src/surface_render_command.py:handle()` | Trace each command to dispatcher action execution or owning aggregate; remove direct transport calls. |

## Violations
- **AES406 — Surface Role (HIGH):** Smart surface commands perform process lifecycle, direct transport orchestration, and implicit scene-save logic. Surface should delegate to aggregates and contain no business calculation/orchestration.
- **AES404 — Utility Role (MEDIUM):** `modules/cli/src/utility_cli_registry.py` contains a stateful singleton class (`Registry`) and file persistence. Utility layer must use stateless standalone functions only.
- **AES305 — Duplication Code (MEDIUM):** `_mask_error()` is duplicated across multiple CLI surface files.
- **Potential AES201 concern:** CLI surface directly imports and uses gateway transport utility. Even if filename prefix is `utility_`, the business flow bypasses required Dispatcher/Gateway contracts and should be removed from CLI.

## Action Items (For Developer)
- [ ] P0 Fix root `pyproject.toml` CLI entry point to reference an existing main function.
- [ ] P0 Remove process launch/kill and registry authority from CLI; delegate to `ILauncherOperateAggregate`.
- [ ] P0 Remove direct `BlenderSocketClient` usage from CLI; delegate action execution to `IDispatcherAggregate` or owning feature aggregate.
- [ ] P0 Remove implicit save-on-close behavior unless an explicit FRD-approved flag and owning-feature flow are added.
- [ ] P0 Implement security redaction/masking for all CLI text and JSON output.
- [ ] P1 Implement missing CLI subcommands from FRD command mapping or update FRD with deferred-command scope.
- [ ] P1 Implement surface-level parameter validation for `run --action` using dispatcher schema.
- [ ] P1 Implement CLI result/error rendering with category, message, remediation hint, warnings, and stable JSON error object.
- [ ] P1 Normalize filepaths if any temporary local registry remains; preferably delete CLI registry entirely.
- [ ] P2 Add acceptance tests for FR-CLI-001/002/003 and command mapping.

## Proposed Fixes / Reference Code

### `pyproject.toml`
```toml
[project.scripts]
blender-arwaky = "modules.cli.src.root_cli_main_entry:main"
blender-mcp = "modules.root_mcp_entry:main"
```

### `modules/cli/src/root_cli_main_entry.py`

```python
from collections.abc import Sequence
from modules.shared.src.launcher.contract_launcher_operate_aggregate import ILauncherOperateAggregate
from modules.shared.src.dispatcher.contract_dispatcher_aggregate import IDispatcherAggregate


def main(
    argv: Sequence[str] | None = None,
    *,
    launcher: ILauncherOperateAggregate | None = None,
    dispatcher: IDispatcherAggregate | None = None,
    redactor: "RedactionProtocol | None" = None,
) -> int:
    # Parse args, then pass injected aggregates into handlers.
    # Handlers must not import process/socket utilities directly.
    ...
```

### `modules/cli/src/surface_init_command.py`

```python
def handle(args: Any, launcher: ILauncherOperateAggregate) -> dict[str, Any]:
    # Requires Launcher contract to accept filepath or LaunchRequestVO.
    # See launcher issue for LaunchRequestVO addition.
    outcome = launcher.launch(
        mode=args.mode,
        readiness_timeout_seconds=args.timeout,
    )
    if not outcome.success:
        return {
            "success": False,
            "error": outcome.error or "Launch failed",
            "category": "timeout" if "timeout" in (outcome.error or "").lower() else "upstream_error",
            "ref": "cli-init",
        }
    return {"success": True, "message": "Blender session started", "data": {"pid": outcome.process_id}}
```

### `modules/cli/src/surface_close_command.py`

```python
def handle(args: Any, launcher: ILauncherOperateAggregate) -> dict[str, Any]:
    outcome = launcher.shutdown(force=False, allow_escalation=True)
    if not outcome.success:
        return {
            "success": False,
            "error": outcome.error or "Shutdown failed",
            "category": "state",
            "ref": "cli-close",
        }
    return {"success": True, "message": "Blender closed"}
```

### `modules/cli/src/surface_status_command.py`

```python
def handle(_args: Any, launcher: ILauncherOperateAggregate) -> dict[str, Any]:
    status = launcher.check_status()
    return {
        "success": True,
        "data": {
            "state": status.state.value,
            "pid": status.process_id,
            "ready": status.ready,
            "stale": status.stale,
        },
    }
```

### `modules/cli/src/surface_run_command.py`

```python
def handle(args: Any, dispatcher: IDispatcherAggregate) -> dict[str, Any]:
    # Validate surface shape using schema, then submit through dispatcher.
    # Do not open sockets in CLI.
    ...
```

### Files to remove from CLI after migration

```text
modules/cli/src/utility_cli_process.py
modules/cli/src/utility_cli_registry.py
```

```

`
```
