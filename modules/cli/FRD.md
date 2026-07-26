# FRD — CLI Surface

## Purpose

Provides the terminal interface for users of **blender-arwaky**. Surface only — no business logic.

This feature is the thinnest possible layer between a human at a terminal and the system's real capabilities. It parses what the user typed, hands the intent to the feature that actually owns it, and renders whatever comes back in a form a person can act on. It decides nothing: not whether an action is valid, not whether Blender is healthy, not whether a path is safe. Those judgments live in dispatcher, diagnostics, and security policy features. The CLI merely translates — arguments in, aggregate calls down, results up, readable output out.

The value of this discipline is that every capability available in the terminal is automatically available through the MCP layer with identical semantics, because both surfaces call the same aggregates and neither surface invents behavior.

## Scope

- Command parsing with surface-level argument validation
- Terminal output formatting for humans and machines
- Human-readable errors with actionable guidance
- Command help and per-command usage documentation
- Masking of sensitive values in all rendered output
- Mapping CLI commands to owning feature aggregates
- Deterministic exit codes per outcome class
- Output adaptation for non-interactive terminals
- Progress hints for long-running foreground operations

## Out of Scope

- Business rules of any kind
- Process lifecycle logic, owned by launcher feature
- Connection logic, owned by gateway feature
- Command validation, owned by dispatcher feature
- Settings loading, owned by config feature
- Health computation, owned by diagnostics feature
- Task lifecycle, owned by job feature
- Path and code safety decisions, owned by security policy feature
- Interactive wizards or guided flows
- Shell completion generation

## Depends On

- dispatcher feature for action execution and catalog discovery
- launcher feature for application process control
- diagnostics feature for health and status snapshots
- config feature for settings display and output preferences
- job feature for task status and cancellation
- security policy feature for redaction rules applied to rendered output

## Provides To

Users through the terminal interface.

## Functional Requirements

### FR-CLI-001: Parse and Route Commands

CLI receives command. CLI translates to aggregate call. CLI does not process business itself.

- **Description**: Parse terminal input into a typed command intent, validate argument shape at the surface, and route to the owning feature aggregate
- **Input**: Raw command line tokens: command name, positional arguments, flags, and options
- **Output**: Aggregate call concept dispatched to the owning feature, plus eventual exit code for the shell
- **Business Rules**:
  - Each CLI command maps to exactly one owning feature aggregate; no command composes business logic across features
  - Parsing validates surface shape only:
    - command name recognized
    - required arguments present
    - flags syntactically well-formed
    - argument count within declared bounds
  - Semantic validation belongs to the owning feature; the CLI never judges whether an action is valid, a path is safe, or a state permits the operation
  - Unknown command produces validation error with the closest recognized commands suggested
  - Every command supports help flag returning usage, arguments, flags, and examples
  - Root command with no arguments returns command overview and help pointer
  - Routing passes caller-supplied context such as output format preference and tracking context onward
  - Exit codes are deterministic by outcome class:
    - success
    - surface validation failure
    - upstream categorized failure
    - unexpected internal failure
  - Long-running foreground operations may display non-blocking progress hints while waiting for the aggregate
  - The CLI must not retry, reorder, or reinterpret aggregate results; rendering is the only post-processing permitted
  - Non-interactive input is accepted so commands compose in scripts and pipelines
- **Edge Cases**: Unknown command, missing required argument, conflicting flags, malformed flag value, extra positional argument, help requested at any level, empty input, ambiguous command abbreviation, piped or non-interactive invocation, aggregate unavailable at route time, progress hint interrupted by early aggregate failure
- **Error Handling**: Validation error for surface-level argument problems, raised before any aggregate call; upstream errors passed through unchanged for display; unexpected internal failure produces generic error display with diagnostic reference, never raw stack by default

### FR-CLI-002: Render Terminal Output

CLI displays results in clear format. CLI supports JSON output when requested.

- **Description**: Render aggregate results for human reading by default and for machine consumption when JSON output is requested
- **Input**: Aggregate result concept, output format preference, terminal capability context
- **Output**: Rendered terminal output with exit code reflecting outcome
- **Business Rules**:
  - Human-readable text is the default format; JSON is produced when requested by flag or configuration
  - JSON output must be machine-stable:
    - consistent field shape across runs
    - no color codes or decorative characters
    - errors rendered as structured JSON objects, not text
  - Text output adapts to terminal capability:
    - color applied only when terminal supports it and policy allows
    - decoration suppressed entirely for non-interactive output
    - wide tables condensed or wrapped for narrow terminals
  - List-shaped results such as action catalogs and task records render as tables with stable column ordering
  - Large payloads are truncated in text mode with explicit continuation hint; JSON mode always emits complete data
  - Sensitive values are masked through security policy rules before any rendering path, in both text and JSON modes
  - Success, partial success with warnings, and failure must be visually distinguishable at a glance
  - Warning lists accompanying results are rendered distinctly from errors
  - Rendering must never throw on unexpected data; unknown shapes fall back to safe generic display
  - Progress hints for long operations must not corrupt final output and must clear themselves on completion or failure
- **Edge Cases**: Non-TTY output, narrow terminal width, terminal without unicode support, huge result set, binary or non-printable data in result, JSON requested while error occurs, color policy conflicting with terminal capability, piped output consumed by another tool, result containing fields added after this CLI version
- **Error Handling**: Rendering failure falls back to minimal safe display of the raw result summary; masking failure suppresses the affected value entirely rather than risking exposure; exit code reflects aggregate outcome regardless of rendering path

### FR-CLI-003: Display Errors

CLI displays error category and actionable message. CLI does not display secrets.

- **Description**: Present failures as categorized, human-actionable guidance while guaranteeing that sensitive content never reaches the terminal
- **Input**: Error concept containing category, message, optional field-level detail, and optional upstream context
- **Output**: Rendered error display with category label, actionable message, remediation hint, and corresponding exit code
- **Business Rules**:
  - Every displayed error shows its category in stable, recognizable form
  - Every displayed error includes an actionable message: what failed, and what the user can plausibly do about it
  - Remediation hints map common categories to concrete next steps, such as launching the application when the process is not running or checking settings when configuration is invalid
  - Secrets, tokens, credentials, raw code, and sensitive paths are masked through security policy rules before display, in both text and JSON modes
  - Upstream error categories are displayed as received; the CLI renames nothing and invents nothing
  - Field-level validation detail from owning features is rendered when present, pointing the user at the offending argument
  - Stack traces are never displayed by default; verbose flag may reveal additional structural detail, still masked
  - Errors distinguish user-correctable problems from internal failures; internal failures reference diagnostics output rather than dumping internals
  - JSON mode renders errors as structured objects with category, message, hint, and detail fields
  - Exit code corresponds to error category class so scripts can branch deterministically
- **Edge Cases**: Error without category, error message containing embedded secret, nested upstream error chain, verbose mode active, JSON error output requested, hint data unavailable for category, field detail referencing masked value, multiple errors returned from one aggregate call
- **Error Handling**: Display failure falls back to generic categorized message rather than silence; masking failure suppresses the affected fragment entirely; hint absence degrades to category and message without fabricated guidance

## Command Mapping

| CLI Command Concept | Target Feature |
| ------------------- | -------------- |
| Initialize workspace and locate application | launcher feature |
| Launch application | launcher feature |
| Shut down application | launcher feature |
| Show runtime status | diagnostics feature composed with launcher feature |
| Execute action | dispatcher feature |
| List available actions | dispatcher feature |
| Show settings and settings metadata | config feature |
| Show system health | diagnostics feature |
| Show task status | job feature |
| Cancel task | job feature |

Mapping discipline:

- One command corresponds to one aggregate call; the status command reads from two sources but computes nothing
- Command names and arguments are presentation choices; semantics live entirely in the target feature
- Adding a capability to the system never requires CLI changes beyond mapping a new command to the existing aggregate
- Any command whose semantics would require cross-feature judgment must be rejected at design review, not implemented

## Error Categories

Owned by this feature:

- validation error — invalid CLI arguments, unrecognized command, or malformed flags, detected at the surface before routing
- configuration error — settings unavailable or invalid, displayed from config feature with remediation toward configuration commands

Displayed but owned elsewhere:

- not found, capacity, timeout, security violation, connection, state, and task categories pass through from owning features unchanged
- the CLI attaches remediation hints for display purposes only; hint text carries no authority and no logic

## Events

None. The surface layer does not emit domain events.

Command invocation and exit outcomes may appear in structured logs through the diagnostics logging policy when diagnostics is available, but the CLI contributes no events to the domain event stream and consumes none for its own behavior.

## Configuration Keys

| Configuration Concept | Description | Typical Default |
| --------------------- | ----------- | --------------- |
| Default output format | Rendering format when no flag overrides it: text or JSON | Text |
| Secret masking toggle | Whether security policy masking applies to rendered output | Always enabled, not user-disableable for secrets |
| Color output policy | Color behavior: automatic by terminal capability, always, or never | Automatic |
| Default verbosity | Whether additional structural detail accompanies errors | Standard |
| List page size | Row limit for table rendering before truncation hint | Conservative row count |
| Progress hints toggle | Whether long operations display non-blocking progress indication | Enabled for interactive terminals |

## QA Checklist

- [ ] Commands parsed and routed to correct owning feature aggregate
- [ ] Unknown command produces validation error with closest command suggestions
- [ ] Every command supports help with usage, arguments, flags, and examples
- [ ] Surface validation catches argument shape problems before routing
- [ ] Semantic validation performed by owning feature, never by CLI
- [ ] Results rendered in clear terminal format with stable table columns
- [ ] JSON output supported with machine-stable shape and no decorative characters
- [ ] JSON errors rendered as structured objects matching success envelope conventions
- [ ] Large payloads truncated in text mode with continuation hint, complete in JSON mode
- [ ] Color suppressed for non-interactive terminals and unsupported environments
- [ ] Errors display category and actionable message with remediation hint
- [ ] Field-level validation detail points at offending argument when provided
- [ ] Stack traces hidden by default and masked even in verbose mode
- [ ] Secrets masked in all output paths, text and JSON alike
- [ ] Masking failure suppresses affected value rather than exposing it
- [ ] Exit codes deterministic per outcome class for script consumption
- [ ] Progress hints clear themselves on completion or failure without corrupting output
- [ ] Long-running foreground operations display non-blocking progress indication
- [ ] No business logic in CLI layer: no retries, no reordering, no cross-feature composition
- [ ] Capability added to system reachable through new mapping without CLI logic changes