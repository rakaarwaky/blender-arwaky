# FRD — Diagnostics & Observability Feature

## System Overview
The Diagnostics module is the single observability authority. Every other feature reports into it. It turns scattered runtime signals into one honest, redacted, point-in-time picture of system health, metrics, and audit events, available to CLI, MCP, and internal consumers.

## Functional Requirements

### FR-001: Compose System Health
- **Description**: Aggregate subsystem states into one composed health view with bounded probes.
- **Input**: Health request (optional subsystem filter, probe depth).
- **Output**: Composed health (overall status, per-subsystem map, staleness indicators).
- **Business Rules**: Covers launcher, gateway, config, job capacity. Each probe bounded by timeout. Overall status: healthy/degraded/unhealthy. Slow subsystem degrades status, never stalls composition.
- **Edge Cases**: Launcher not started; gateway mid-reconnect; subsystem unresponsive; clock skew.
- **Error Handling**: `probe_timeout_error` degrades subsystem; `state_error` for corrupt diagnostics state.

### FR-002: Collect Operational Metrics
- **Description**: Pull counters/gauges/latency summaries from features at configured intervals.
- **Input**: Collection cycle (interval-driven); snapshot request.
- **Output**: Metrics snapshot (counters, gauges, latency summaries, freshness indicators).
- **Business Rules**: Pull-based. Counters monotonic per lifetime. Latency summaries include count, min, max, median. Slow/missing source marked stale, not fatal.
- **Edge Cases**: Source unavailable; interval skew; counter reset; high-cardinality labels.
- **Error Handling**: `collection_error` warns and marks source stale; snapshot still produced from remaining sources.

### FR-003: Emit Audit Events and Structured Logging
- **Description**: Immutable audit records and structured logging with ingestion-time redaction.
- **Input**: Audit context, Log record.
- **Output**: Audit record + emission status, Sanitized structured log entry.
- **Business Rules**: Auditable: security violations, connection failures, task failures, destructive actions. Redaction before emission. Non-blocking; sink trouble triggers fallback buffering.
- **Edge Cases**: Sink unavailable; buffer overflow; sensitive value in free-text; oversized record.
- **Error Handling**: `emission_error` engages fallback buffer; `log_redaction_failure` masks entire payload.

## API Contract
| Operation | Input | Output | Description |
|---|---|---|---|
| `health_check` | None | `HealthSnapshot` | Composed system health with bounded per-subsystem probes (launcher, gateway, config, job capacity); timed-out probe yields `degraded` status, never stalls composition |
## Integration Points

- **3rd Party**: No 3rd party integrations.
- **Internal**: `launcher`, `gateway`, `dispatcher`, `job`, `security`, `config` (all report into diagnostics).

## Non-functional Requirements (Detailed)

- **Performance**: Health probes bounded by `health_probe_timeout`. Metrics collection is lightweight and non-blocking.
- **Security**: Redaction at ingestion for all logs and audit events. No raw code/tokens/secrets at any level.
- **Scalability**: Backpressure drops oldest logs with counter exposed. Audit flood rate-limited with suppression count.

## Test Scenarios / QA Checklist

- [ ] Verify health composition returns `degraded` if a subsystem probe times out, without stalling.
- [ ] Verify metrics counters reset after restart with a reset indicator.
- [ ] Verify security violations are audited regardless of the general audit toggle.
- [ ] Verify sink failure engages fallback buffer without impacting the originating operation.
- [ ] Verify structured logs redact sensitive values at ingestion.

## Assumptions & Constraints

- No feature maintains a private log format or computes its own health.
- Diagnostics is strictly read-only regarding subsystem state (never repairs/restarts).

## Glossary

- **Staleness Indicator**: Metadata flag showing when a subsystem probe or metric source last responded successfully.
- **Fallback Buffer**: In-memory ring buffer used when primary log/audit sinks are unavailable.
- **UnifiedEnvelope**: The standardized JSON response wrapper containing success indicator, data payload, error category, tracking ID, and warnings.
- **TrackingID**: UUIDv4 string for request correlation across logs, metrics, and audit events.

## Reference

- PRD: `./PRD.md`
- Depends On: `launcher`, `gateway`, `dispatcher`, `job`, `security`, `config`
