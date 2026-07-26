# FRD — CLI Surface

## Purpose

Provides terminal interface for users. Surface only — no business logic.

## Scope

- Command parsing
- Terminal output formatting
- Human-readable errors
- Command help
- Masking output sensitive values
- Mapping CLI commands to aggregates

## Out of Scope

- Business rules
- Process lifecycle logic
- Connection logic
- Command validation (owner: `dispatcher`)
- Settings loading (owner: `config`)
- Health computation (owner: `diagnostics`)
- Task lifecycle (owner: `job`)

## Depends On

- `dispatcher`
- `launcher`
- `diagnostics`
- `config`
- `job`
- `security`

## Provides To

Users (terminal interface).

## Functional Requirements

### FR-CLI-001: Parse and Route Commands

CLI receives command. CLI translates to aggregate call. CLI does not process business itself.

### FR-CLI-002: Render Terminal Output

CLI displays results in clear format. CLI supports JSON output when requested.

### FR-CLI-003: Display Errors

CLI displays error category and actionable message. CLI does not display secrets.

## Command Mapping

| CLI Command      | Target Feature             |
| ---------------- | -------------------------- |
| `init`           | `launcher`                 |
| `run`            | `launcher`                 |
| `close`          | `launcher`                 |
| `status`         | `diagnostics` + `launcher` |
| `execute`        | `dispatcher`               |
| `list`           | `dispatcher`               |
| `config`         | `config`                   |
| `health`         | `diagnostics`              |
| `task status`    | `job`                      |
| `task cancel`    | `job`                      |

## Error Categories

- `ValidationError` — invalid CLI arguments (surface-level)
- `ConfigurationError` — config not found (displayed from `config`)

## Events

None (surface layer does not emit domain events).

## Configuration Keys

- `cli.output_format` — default output format (text/json)
- `cli.mask_secrets` — toggle secret masking

## QA Checklist

- [ ] Commands parsed and routed to correct aggregate
- [ ] Results rendered in clear terminal format
- [ ] JSON output supported
- [ ] Errors display category and actionable message
- [ ] Secrets masked in output
- [ ] No business logic in CLI layer
