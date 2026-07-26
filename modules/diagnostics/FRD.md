# FRD — Diagnostics & Observability Feature

## Purpose

Manages health check, operational metrics, structured logging, audit events, and trace correlation.

## Scope

- Health status composition
- Operational metrics
- Structured local logs
- Audit events
- Trace correlation by tracking ID
- Diagnostics snapshot

## Out of Scope

- Anonymous product analytics
- Business rules
- Settings loading
- Task execution
- Connection mechanics

## Depends On

- `launcher`
- `gateway`
- `dispatcher`
- `job`
- `security`
- `config`

## Provides To

- `cli`
- `mcp`
- Internal observability

## Functional Requirements

### FR-DIA-001: Compose System Health

Diagnostics checks: launcher status, gateway connection status, config validity, asset provider availability (optional), job capacity.

### FR-DIA-002: Collect Operational Metrics

Diagnostics collects: pending operations, reconnect count, execution latency, command latency, failed request count, security violation count, task created/failed/completed count.

### FR-DIA-003: Emit Audit Events

Security violations, connection failures, task failures, and destructive actions must be audit-able.

### FR-DIA-004: Structured Logging Policy

All features send logs through diagnostics policy. Logs must be structured. Logs must not contain raw code, tokens, or secrets.

### FR-DIA-005: Provide Diagnostics Snapshot

CLI and MCP retrieve health/metrics from diagnostics. They do not compute themselves.

## Error Categories

- `StateError` — diagnostics state corruption
- `ConfigurationError` — logging configuration invalid

## Events

- `diagnostics.health` — health check composed
- `diagnostics.metrics` — metrics snapshot taken
- `diagnostics.audit` — audit event emitted

## Configuration Keys

- `diagnostics.log_level` — structured log level
- `diagnostics.log_path` — local log file path
- `diagnostics.metrics_interval` — metrics collection interval
- `diagnostics.audit_enabled` — toggle audit event emission

## QA Checklist

- [ ] Health check composes status from launcher, gateway, config, job
- [ ] Metrics collected: latency, failures, violations, tasks
- [ ] Audit events emitted for violations and failures
- [ ] Structured logs exclude raw code, tokens, secrets
- [ ] CLI/MCP retrieve snapshot from diagnostics (not self-computed)
