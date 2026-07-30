# FRD — CLI Surface

## Purpose

Terminal interface for blender-arwaky. Parses user input, routes to owning feature aggregate, renders result. Surface only — zero business logic.

## Scope

- Command parsing with surface-level arg validation
- Terminal output formatting (text/JSON)
- Error display with category + actionable message
- Masking of sensitive values in all output
- Mapping CLI commands → owning feature aggregates
- Deterministic exit codes per outcome class
- Progress hints for long-running foreground ops
- Non-interactive output adaptation

## Out of Scope

Business logic, process lifecycle, connection logic, command validation, settings loading, health computation, task lifecycle, path/code safety decisions, interactive wizards, shell completion.

## Depends On

dispatcher (action execution + catalog), launcher (process control), diagnostics (health + status), config (settings), job (task status), security policy (redaction).

## Provides To

Users via terminal.

## Functional Requirements

### FR-CLI-001: Parse and Route Commands

Parse terminal input, validate arg shape at surface, route to owning feature aggregate.

- **Input**: Raw CLI tokens: command, positional args, flags, options
- **Output**: Aggregate call dispatched + exit code
- **Business Rules**:
  - 1 CLI command → exactly 1 owning feature aggregate
  - Surface validates shape only: command recognized, required args present, flags well-formed, arg count in bounds
  - Semantic validation belongs to owning feature — CLI never judges action validity, path safety, or state
  - Unknown command → validation error with closest known commands suggested
  - Every command supports `--help` with usage, args, flags, examples
  - Root command without args → overview + help pointer
  - Exit codes: success, surface validation failure, upstream categorized failure, unexpected failure
  - No retry, reorder, or reinterpretation of aggregate results
  - Non-interactive input accepted for scripts/pipelines
  - Long-running ops may show non-blocking progress hints
- **Edge Cases**: Unknown command, missing required arg, conflicting flags, malformed flag value, extra positional arg, help at any level, empty input, piped/non-interactive invocation, aggregate unavailable at route time
- **Error Handling**: Surface validation error before any aggregate call; upstream errors passed through unchanged; unexpected failure → generic error with diagnostic ref, never raw stack

### FR-CLI-002: Render Terminal Output

Render aggregate results for human reading (default) or machine consumption (JSON flag).

- **Input**: Aggregate result, format preference, terminal capability
- **Output**: Rendered output + exit code
- **Business Rules**:
  - Human-readable text default; JSON via `--json` flag or config
  - JSON output: machine-stable shape, no color codes, errors as structured objects
  - Text output adapts to terminal: color only when supported, decoration suppressed for non-interactive, wide tables condensed
  - List-shaped results → tables with stable column ordering
  - Large payloads truncated in text mode with continuation hint; JSON emits complete data
  - Sensitive values masked via security policy in all output paths
  - Success, partial success with warnings, and failure visually distinguishable
  - Rendering never throws on unexpected data — unknown shapes fall back to safe generic display
  - Progress hints clear on completion/failure without corrupting output
- **Edge Cases**: Non-TTY, narrow terminal, no unicode support, huge result set, binary data in result, JSON + error simultaneously, color policy conflict, piped output, result with unknown fields
- **Error Handling**: Rendering failure → minimal safe display of raw result summary; masking failure → suppress affected value entirely

### FR-CLI-003: Display Errors

Present failures as categorized, actionable guidance. Never display secrets.

- **Input**: Error concept (category, message, optional field detail, optional upstream context)
- **Output**: Rendered error (category label, actionable message, remediation hint, exit code)
- **Business Rules**:
  - Every error shows stable category + actionable message + remediation hint
  - Secrets/tokens/credentials/code/paths masked via security policy before display
  - Upstream categories pass through unchanged — CLI renames nothing
  - Field-level validation detail rendered when present
  - Stack traces hidden by default; verbose flag may reveal structural detail (still masked)
  - Errors distinguish user-correctable from internal failures
  - JSON mode: errors as structured objects with category, message, hint, detail
  - Exit code maps to error category class for deterministic script branching
- **Edge Cases**: Error without category, message containing embedded secret, nested upstream errors, verbose mode, JSON error output, hint unavailable, field detail referencing masked value, multiple errors from one aggregate
- **Error Handling**: Display failure → generic categorized message; masking failure → suppress affected fragment; hint absence → degrade to category + message

## Command Mapping

Setiap aksi punya CLI sub-command sendiri dengan argument khusus. Universal `run --action` sebagai fallback untuk aksi yang belum punya sub-command.

### Launcher

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `init` | `--filepath` (required), `--mode` (gui\|headless), `--port` | `launch_blender` |
| `close` | `--filepath` (required) | `shutdown_blender` |
| `status` | (none) | `get_runtime_status` |
| `register` | `--path` (optional) | `register_executable` |

### Scene

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `scene-info` | (none) | `get_scene_info` |
| `scene-cleanup` | `--mode` (all\|objects\|meshes) | `cleanup_scene` |
| `set-env` | `--hdri-id` (required), `--strength` | `setup_environment` |

### Object

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `object-info` | `--name` (required) | `get_object_info` |
| `create` | `--type` (required), `--location`, `--scale`, `--name` | `create_primitive` |
| `set-transform` | `--name` (required), `--location`, `--rotation`, `--scale` | `set_object_transform` |
| `delete` | `--name` (required) | `delete_object` |
| `set-material` | `--name` (required), `--material` (required) | `set_material` |
| `apply-modifier` | `--name` (required), `--modifier` (required) | `apply_modifier` |

### Viewport & Render

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `screenshot` | `--filepath`, `--output`, `--max-size`, `--view-angle`, `--shading`, `--no-overlays`, `--focus-object` | `get_viewport_screenshot` |
| `render` | `--filepath`, `--output`, `--resolution-x`, `--resolution-y` | `render` |

### Import / Export / Asset

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `import` | `--file` (required), `--name` | `import_glb` |
| `export` | `--name` (required), `--output` (required), `--format` | `export_model` |
| `place-asset` | `--asset-id` (required), `--location`, `--rotation`, `--scale` | `place_asset` |

### Job

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `task-status` | `--task-id` (required) | `get_task_status` |
| `cancel-task` | `--task-id` (required) | `cancel_task` |

### Config

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `config` | `--key` (optional) | `get_config` |
| `set-config` | `--key` (required), `--value` (required) | `set_config` |

### Code Execution

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `run-code` | `--code` (required) | `execute_blender_code` |

### Universal Fallback

| CLI | Arguments | Action Name |
|-----|-----------|-------------|
| `run` | `--filepath` (required), `--action` (required), `--params` (JSON) | `run.action` |

Mapping rules: 1 CLI sub-command = 1 action name = 1 aggregate call. The action name is the shared identifier between CLI and MCP (`execute_command(action=...)`). Adding a capability means adding a row — semantics live in target feature, not CLI.

## Error Categories

- **Owned**: validation error (surface-level arg problems), configuration error (settings unavailable)
- **Displayed but unowned**: not_found, capacity, timeout, security_violation, connection, state, task — pass through from owning features with CLI remediation hints attached (hints carry no logic authority)

## Events

None. CLI does not emit domain events.

## Configuration Keys


| Key                   | Description                 | Default                 |
| ----------------------- | ----------------------------- | ------------------------- |
| default_output_format | text or json                | text                    |
| secret_masking        | always enabled              | enabled                 |
| color_policy          | auto/always/never           | auto                    |
| list_page_size        | row limit before truncation | conservative            |
| progress_hints        | show for long operations    | enabled for interactive |

## QA Checklist

- [ ]  Commands parse + route to correct aggregate
- [ ]  Unknown command → validation error with suggestions
- [ ]  Every command supports --help
- [ ]  Surface validation before routing
- [ ]  Semantic validation by owning feature only
- [ ]  Results rendered in clear text format
- [ ]  JSON output: machine-stable, no decoration
- [ ]  JSON errors: structured objects
- [ ]  Large payloads truncated in text, complete in JSON
- [ ]  Color suppressed for non-TTY
- [ ]  Errors: category + actionable message + remediation hint
- [ ]  Stack traces hidden by default
- [ ]  Secrets masked in all output paths
- [ ]  Exit codes deterministic per outcome class
- [ ]  Progress hints clear on completion/failure
- [ ]  No business logic in CLI layer
- [ ]  New capability reachable via mapping only, no CLI logic changes
