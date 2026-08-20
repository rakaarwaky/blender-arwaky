# FRD — CLI Surface

## System Overview
The CLI Surface is the terminal interface for blender-arwaky. It parses user input, routes commands to owning feature aggregates via the Dispatcher, and renders results. It contains zero business logic and acts strictly as a presentation and routing layer.

## Functional Requirements

### FR-001: Parse and Route Commands
- **Description**: Parse terminal input, validate argument shape at the surface, and route to the owning feature aggregate.
- **Input**: Raw CLI tokens: command, positional args, flags, options.
- **Output**: Aggregate call dispatched + deterministic exit code.
- **Business Rules**: 1 CLI command maps to exactly 1 owning feature aggregate. Surface validates shape only (command recognized, required args present). Semantic validation belongs to owning features. Unknown commands suggest closest known commands.
- **Edge Cases**: Unknown command; missing required arg; conflicting flags; piped/non-interactive invocation.
- **Error Handling**: `validation_error` for surface arg problems; `configuration_error` for settings unavailable; upstream errors passed through unchanged.

### FR-002: Render Terminal Output
- **Description**: Render aggregate results for human reading (default) or machine consumption (JSON flag).
- **Input**: Aggregate result, format preference, terminal capability.
- **Output**: Rendered output + exit code.
- **Business Rules**: Human-readable text default; JSON via `--json`. JSON output is machine-stable with no color codes. Text output adapts to terminal (color only when supported). Sensitive values masked via `security` policy.
- **Edge Cases**: Non-TTY; narrow terminal; huge result set; binary data in result; piped output.
- **Error Handling**: Rendering failure falls back to minimal safe display; masking failure suppresses affected value entirely.

### FR-003: Display Errors
- **Description**: Present failures as categorized, actionable guidance without displaying secrets.
- **Input**: Error concept (category, message, optional field detail, upstream context).
- **Output**: Rendered error (category label, actionable message, remediation hint, exit code).
- **Business Rules**: Every error shows stable category + actionable message + remediation hint. Secrets masked before display. Stack traces hidden by default.
- **Edge Cases**: Error without category; message containing embedded secret; JSON error output.
- **Error Handling**: Display failure degrades to generic categorized message; hint absence degrades to category + message.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `execute_blender_code` | `--code` | `CodeExecutionResult` | Execute raw Python via Gateway; raises `security_violation`, `execution_error`, `connection_error` |
| `get_scene_info` | None | `SceneSummary` | Retrieve scene summary via Scene module; raises `connection_error`, `scene_state_error` |
| `cleanup_scene` | `--mode` | `CleanupReport` | Bulk scene cleanup via Scene policy; raises `protection_error`, `confirmation_error`, `delegated_deletion_error` |
| `create_primitive` | `--primitive-type`, `--location` | `BlenderObjectRef` | Create basic 3D object via Object module; raises `validation_error`, `execution_error` |
| `render` | `--output-path`, `--resolution-x` | `RenderArtifact | TaskRef` | Execute scene render via Render module; long renders auto-submit to Job and return `TaskRef`; raises `render_output_error`, `security_violation`, `capacity_error`, `scene_state_error` |
| `search_assets` | `--query`, `--limit` | `AssetSearchResult[]` | Search external providers via Asset module; raises `provider_error`, `validation_error`, `authentication_error` |
| `launch_blender` | `--filepath`, `--mode` | `LaunchResult` | Start Blender process via Launcher; raises `configuration_error`, `validation_error`, `timeout_error` |
| `submit_task` | `--operation-type` | `TaskRecord` | Create background job via Job module; raises `capacity_error`, `validation_error` |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `dispatcher` (action execution), `launcher` (process control), `diagnostics` (health status), `config` (settings), `security` (redaction).

## Non-functional Requirements (Detailed)

- **Performance**: CLI parsing and routing must complete in <50ms before aggregate handoff. Output rendering handles large payloads via truncation hints in text mode.
- **Security**: Secret masking is always enabled. Secrets/tokens/credentials never appear in stdout/stderr.
- **Scalability**: Non-interactive output adaptation ensures scripts/pipelines receive clean JSON without TTY decoration overhead.

## Test Scenarios / QA Checklist

- [ ] Verify unknown command returns `validation_error` with closest known command suggestions.
- [ ] Verify `--json` flag outputs machine-stable JSON with no color codes or decoration.
- [ ] Verify secrets are masked in all output paths, including error messages.
- [ ] Verify exit codes are deterministic per outcome class (success, surface validation, upstream failure).

## Assumptions & Constraints

- CLI contains zero business logic; it never judges action validity, path safety, or state.
- Module names are converted from canonical snake_case to kebab-case for CLI flags.
- The `--confirm` flag is enforced by the action contract for destructive operations.

## Glossary

- **Aggregate**: The domain feature responsible for executing a specific canonical action.
- **Surface Validation**: Checking the shape and presence of arguments without evaluating domain semantics.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: `dispatcher`, `launcher`, `diagnostics`, `config`, `job`, `plugin`, `security`
